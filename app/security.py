"""Autenticação por API key (hash), rate limit e cabeçalhos de segurança."""

from __future__ import annotations

import hashlib
import hmac
import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import Depends, Header, HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from app.config import Settings, get_settings


def hash_key(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    settings: Settings = Depends(get_settings),
) -> str:
    """Valida a chave comparando hashes em tempo constante. Retorna um ID curto para auditoria."""
    if not x_api_key:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "API key ausente")
    candidate = hash_key(x_api_key)
    if not any(hmac.compare_digest(candidate, allowed) for allowed in settings.allowed_key_hashes):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "API key inválida")
    return candidate[:12]  # nunca logar a chave nem o hash completo


class SlidingWindowLimiter:
    """Rate limit por chave (janela deslizante de 60s). Em produção multi-réplica, trocar por Redis."""

    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str, limit: int, window_s: float = 60.0) -> bool:
        now = time.monotonic()
        with self._lock:
            q = self._hits[key]
            while q and now - q[0] > window_s:
                q.popleft()
            if len(q) >= limit:
                return False
            q.append(now)
            return True


limiter = SlidingWindowLimiter()


def enforce_rate_limit(
    key_id: str = Depends(require_api_key), settings: Settings = Depends(get_settings)
) -> str:
    if not limiter.check(key_id, settings.rate_limit_per_minute):
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Limite de requisições excedido",
            headers={"Retry-After": "60"},
        )
    return key_id


SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Cross-Origin-Resource-Policy": "same-origin",
    "Cross-Origin-Opener-Policy": "same-origin",
}
API_CSP = "default-src 'none'; frame-ancestors 'none'"
# O Swagger UI (só fora de produção) precisa carregar JS/CSS do CDN padrão do FastAPI
DOCS_CSP = (
    "default-src 'none'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https://fastapi.tiangolo.com; "
    "connect-src 'self'; frame-ancestors 'none'"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        for k, v in SECURITY_HEADERS.items():
            response.headers.setdefault(k, v)
        is_docs = request.url.path in ("/docs", "/redoc")
        response.headers["Content-Security-Policy"] = DOCS_CSP if is_docs else API_CSP
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        return response


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    """Rejeita corpos grandes antes de parsear JSON (LLM06 / DoS)."""

    def __init__(self, app, max_bytes: int) -> None:
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next) -> Response:
        length = request.headers.get("content-length")
        if length is not None:
            try:
                too_big = int(length) > self.max_bytes
            except ValueError:
                return JSONResponse({"detail": "Content-Length inválido"}, status_code=400)
            if too_big:
                return JSONResponse({"detail": "Corpo da requisição muito grande"}, status_code=413)
        elif request.method in ("POST", "PUT", "PATCH"):
            body = await request.body()
            if len(body) > self.max_bytes:
                return JSONResponse({"detail": "Corpo da requisição muito grande"}, status_code=413)
        return await call_next(request)
