"""Configuração centralizada (12-factor). Nada de segredo hardcoded: tudo vem de variáveis de ambiente."""

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AEGIS_", env_file=".env", extra="ignore")

    env: str = Field(default="dev", description="dev | ci | prod")

    # Chaves de API são guardadas como hash SHA-256 (hex), separadas por vírgula.
    # Gere com: python -c "import hashlib,sys;print(hashlib.sha256(sys.argv[1].encode()).hexdigest())" 'minha-chave'
    api_key_hashes: SecretStr = SecretStr("")

    # LLM local via Ollama — os dados do cliente não saem da infraestrutura (LGPD, art. 6º, III e VII)
    ollama_url: str = "http://ollama:11434"
    ollama_model: str = "qwen2.5:3b"
    llm_timeout_s: float = 60.0

    # Limites de consumo aplicados no servidor (OWASP LLM06 — Unbounded Consumption)
    max_input_chars: int = 2000
    max_output_tokens: int = 512
    max_body_bytes: int = 16_384
    rate_limit_per_minute: int = 20

    # Token canário inserido no prompt de sistema; se aparecer na saída, houve vazamento de contexto (LLM08)
    canary_token: SecretStr = SecretStr("CANARY-trocar-em-producao")

    system_prompt_path: str = "prompts/01-sistema/assistente-atendimento.v1.md"

    @property
    def allowed_key_hashes(self) -> set[str]:
        raw = self.api_key_hashes.get_secret_value()
        return {h.strip().lower() for h in raw.split(",") if h.strip()}

    @property
    def docs_enabled(self) -> bool:
        return self.env != "prod"


@lru_cache
def get_settings() -> Settings:
    return Settings()
