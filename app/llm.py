"""Cliente do LLM. A aplicação depende de um Protocol, então os testes trocam o Ollama por um fake."""

from __future__ import annotations

from typing import Protocol

import httpx


class LLMError(RuntimeError):
    """Falha ao consultar o modelo (timeout, indisponível, resposta inválida)."""


class LLMClient(Protocol):
    async def chat(self, system: str, user: str) -> str: ...

    async def ready(self) -> bool: ...


class OllamaClient:
    def __init__(
        self,
        base_url: str,
        model: str,
        max_tokens: int,
        timeout_s: float,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._model = model
        self._max_tokens = max_tokens
        self._http = httpx.AsyncClient(base_url=base_url, timeout=timeout_s, transport=transport)

    async def chat(self, system: str, user: str) -> str:
        payload = {
            "model": self._model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            # Limites definidos NO SERVIDOR — o cliente nunca controla num_predict (LLM06)
            "options": {"num_predict": self._max_tokens, "temperature": 0.2},
        }
        try:
            resp = await self._http.post("/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return str(data["message"]["content"])
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            raise LLMError(f"falha ao consultar o modelo: {type(exc).__name__}") from exc

    async def ready(self) -> bool:
        try:
            resp = await self._http.get("/api/tags", timeout=5.0)
            return resp.status_code == 200
        except httpx.HTTPError:
            return False

    async def aclose(self) -> None:
        await self._http.aclose()
