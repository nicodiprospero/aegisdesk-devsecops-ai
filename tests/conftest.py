import hashlib
import os

import pytest

TEST_KEY = "chave-de-teste-nao-usar-em-producao"
CANARY = "CANARY-teste-7f3a9c"

os.environ.setdefault("AEGIS_ENV", "ci")
os.environ["AEGIS_API_KEY_HASHES"] = hashlib.sha256(TEST_KEY.encode()).hexdigest()
os.environ["AEGIS_CANARY_TOKEN"] = CANARY
os.environ["AEGIS_RATE_LIMIT_PER_MINUTE"] = "1000"


class FakeLLM:
    """Substitui o Ollama nos testes. Guarda o que recebeu para inspecionar."""

    def __init__(self, reply: str = "Seu pedido está a caminho e chega em até 5 dias úteis.") -> None:
        self.reply = reply
        self.calls: list[tuple[str, str]] = []
        self.fail = False

    async def chat(self, system: str, user: str) -> str:
        from app.llm import LLMError

        if self.fail:
            raise LLMError("indisponível")
        self.calls.append((system, user))
        return self.reply

    async def ready(self) -> bool:
        return not self.fail


@pytest.fixture
def fake_llm() -> FakeLLM:
    return FakeLLM()


@pytest.fixture
def client(fake_llm):
    from fastapi.testclient import TestClient

    from app.main import create_app
    from app.security import limiter

    limiter._hits.clear()
    app = create_app()
    app.state.llm = fake_llm
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth() -> dict[str, str]:
    return {"X-API-Key": TEST_KEY}
