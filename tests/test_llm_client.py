import asyncio
import json

import httpx
import pytest

from app.llm import LLMError, OllamaClient


def _client(handler) -> OllamaClient:
    return OllamaClient("http://ollama:11434", "qwen2.5:3b", 128, 5.0, transport=httpx.MockTransport(handler))


def test_limites_sao_definidos_no_servidor():
    """LLM06: num_predict vem da config do servidor, nunca do cliente."""
    seen = {}

    def handler(req: httpx.Request) -> httpx.Response:
        seen.update(json.loads(req.content))
        return httpx.Response(200, json={"message": {"content": "ok"}})

    assert asyncio.run(_client(handler).chat("sys", "user")) == "ok"
    assert seen["options"]["num_predict"] == 128 and seen["stream"] is False
    assert [m["role"] for m in seen["messages"]] == ["system", "user"]


@pytest.mark.parametrize(
    "response",
    [httpx.Response(500), httpx.Response(200, json={"inesperado": True}), httpx.Response(200, content=b"nao-json")],
)
def test_erros_viram_llm_error(response):
    with pytest.raises(LLMError):
        asyncio.run(_client(lambda req: response).chat("s", "u"))


def test_ready():
    assert asyncio.run(_client(lambda req: httpx.Response(200, json={"models": []})).ready()) is True

    def boom(req):
        raise httpx.ConnectError("down")

    assert asyncio.run(_client(boom).ready()) is False
