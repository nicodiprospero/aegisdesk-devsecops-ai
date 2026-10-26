"""AegisDesk — API de atendimento com IA, construída para passar por um pipeline DevSecOps."""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app import __version__
from app.config import Settings, get_settings
from app.guardrails import detect_injection, redact_pii, sanitize_output, wrap_user_content
from app.llm import LLMClient, LLMError, OllamaClient
from app.security import BodySizeLimitMiddleware, SecurityHeadersMiddleware, enforce_rate_limit

# --------------------------------------------------------------------------------------
# Log de auditoria estruturado (LGPD art. 37 — registro das operações), SEM dados pessoais
# --------------------------------------------------------------------------------------
audit = logging.getLogger("aegisdesk.audit")
if not audit.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("%(message)s"))
    audit.addHandler(_h)
audit.setLevel(logging.INFO)
audit.propagate = False

REFUSAL = (
    "Desculpe, não posso ajudar com esse pedido. Posso te ajudar com dúvidas sobre pedidos, "
    "entregas, trocas ou pagamentos?"
)
FALLBACK = "Estou com instabilidade agora. Tente de novo em alguns minutos ou fale com um atendente humano."


def load_system_prompt(path: str, canary: str) -> str:
    """Carrega o prompt versionado do acervo (prompts/), removendo o front-matter YAML."""
    raw = Path(path).read_text(encoding="utf-8")
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        raw = parts[2] if len(parts) == 3 else raw
    return raw.replace("{{CANARY}}", canary).strip()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    session_id: str | None = Field(default=None, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")


class ChatResponse(BaseModel):
    request_id: str
    answer: str
    blocked: bool
    flags: list[str]


@asynccontextmanager
async def lifespan(app: FastAPI):
    s = get_settings()
    app.state.system_prompt = load_system_prompt(s.system_prompt_path, s.canary_token.get_secret_value())
    if not getattr(app.state, "llm", None):
        app.state.llm = OllamaClient(s.ollama_url, s.ollama_model, s.max_output_tokens, s.llm_timeout_s)
    yield
    close = getattr(app.state.llm, "aclose", None)
    if close:
        await close()


async def unhandled_error(_: Request, exc: Exception) -> JSONResponse:
    # Nunca devolver stack trace ao cliente
    audit.error(json.dumps({"event": "unhandled_error", "type": type(exc).__name__}))
    return JSONResponse({"detail": "Erro interno"}, status_code=500)


def get_llm(request: Request) -> LLMClient:
    return request.app.state.llm


router = APIRouter()


@router.get("/healthz", include_in_schema=False)
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readyz", include_in_schema=False)
async def readyz(llm: LLMClient = Depends(get_llm)) -> JSONResponse:
    ok = await llm.ready()
    return JSONResponse({"status": "ready" if ok else "llm_unavailable"}, status_code=200 if ok else 503)


@router.post("/v1/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    request: Request,
    key_id: str = Depends(enforce_rate_limit),
    settings: Settings = Depends(get_settings),
    llm: LLMClient = Depends(get_llm),
) -> ChatResponse:
    started = time.perf_counter()
    rid = uuid.uuid4().hex
    if len(body.message) > settings.max_input_chars:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Mensagem muito longa")

    flags: list[str] = []
    injection = detect_injection(body.message)
    redacted = redact_pii(body.message)
    if redacted.total:
        flags.append("pii_redacted_input")

    blocked = False
    if injection:
        flags += [f"injection:{r}" for r in injection]
        answer, blocked = REFUSAL, True
    else:
        try:
            raw = await llm.chat(request.app.state.system_prompt, wrap_user_content(redacted.text))
            out = sanitize_output(raw, settings.canary_token.get_secret_value())
            flags += out.flags
            answer, blocked = (REFUSAL, True) if out.blocked else (out.text or REFUSAL, False)
        except LLMError:
            flags.append("llm_error")
            answer = FALLBACK

    audit.info(
        json.dumps(
            {
                "event": "chat",
                "request_id": rid,
                "key_id": key_id,
                "session_id": body.session_id,
                "input_sha256": hashlib.sha256(body.message.encode()).hexdigest(),
                "input_chars": len(body.message),
                "pii_counts": redacted.counts,
                "blocked": blocked,
                "flags": flags,
                "latency_ms": round((time.perf_counter() - started) * 1000, 1),
            },
            ensure_ascii=False,
        )
    )
    # Para o cliente vão só flags genéricas — o detalhe da regra fica no log (não ensina o atacante a evadir)
    public_flags = sorted({f.split(":")[0] for f in flags})
    return ChatResponse(request_id=rid, answer=answer, blocked=blocked, flags=public_flags)


def create_app() -> FastAPI:
    s = get_settings()
    app = FastAPI(
        title="AegisDesk API",
        version=__version__,
        lifespan=lifespan,
        docs_url="/docs" if s.docs_enabled else None,
        redoc_url=None,
        openapi_url="/openapi.json" if s.docs_enabled else None,
    )
    app.add_middleware(BodySizeLimitMiddleware, max_bytes=s.max_body_bytes)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_exception_handler(Exception, unhandled_error)
    app.include_router(router)
    return app


app = create_app()
