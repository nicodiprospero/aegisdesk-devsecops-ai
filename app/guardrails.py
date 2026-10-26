"""Guardrails de entrada e saída do LLM.

Mapeamento OWASP Top 10 for LLM Applications 2026:
- LLM01 Prompt Injection ............ detect_injection() + delimitação de dados em wrap_user_content()
- LLM02 Sensitive Info Disclosure ... redact_pii() na entrada E na saída (minimização — LGPD art. 6º, III)
- LLM08 Hidden Context Exposure ..... detecção do token canário em sanitize_output()
- LLM10 Improper Output Handling .... remoção de ANSI, HTML ativo e imagens/links externos (canal de exfiltração)
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

# --------------------------------------------------------------------------------------
# Normalização — atacantes usam caracteres invisíveis e homógrafos para driblar filtros
# --------------------------------------------------------------------------------------
_ZERO_WIDTH = re.compile("[\u200b-\u200f\u202a-\u202e\u2060-\u2064\ufeff]")  # escapes ASCII (Bandit B613)


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = _ZERO_WIDTH.sub("", text)
    return text


def _strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


# --------------------------------------------------------------------------------------
# LLM01 — heurísticas de prompt injection (PT-BR + EN). Defesa em camadas: isto NÃO é a
# única barreira; o prompt de sistema e a ausência de ferramentas perigosas também contam.
# --------------------------------------------------------------------------------------
INJECTION_RULES: dict[str, re.Pattern[str]] = {
    "override_instructions": re.compile(
        r"\b(ignore|desconsidere|esqueca|esqueça|disregard|forget)\b.{0,40}"
        r"\b(instruc\w*|instruç\w*|regras|rules|instructions|prompt|orientac\w*)\b",
        re.IGNORECASE | re.DOTALL,
    ),
    "reveal_system_prompt": re.compile(
        r"(system\s*prompt|prompt\s+(de|do)\s+sistema|suas\s+instruc\w*\s+(iniciais|originais|ocultas)"
        r"|mostre\s+(seu|o)\s+prompt|repita\s+.{0,30}acima|repeat\s+.{0,30}above|initial\s+instructions)",
        re.IGNORECASE,
    ),
    "role_hijack": re.compile(
        r"\b(voce|você|you)\s+(agora\s+)?(e|é|sera|será|are\s+now|is\s+now)\s+(um|uma|o|a|an?|the)?\s*"
        r"(dan|desenvolvedor|developer|admin\w*|root|sistema|jailbroken|sem\s+restric\w*)",
        re.IGNORECASE,
    ),
    "mode_switch": re.compile(
        r"\b(modo|mode)\s+(desenvolvedor|developer|dan|jailbreak|deus|god|irrestrito|unrestricted)\b",
        re.IGNORECASE,
    ),
    "fake_delimiters": re.compile(
        r"(<\s*/?\s*(system|sistema|instructions?|dados_do_usuario)\s*>|\[/?INST\]|<\|im_(start|end)\|>"
        r"|###\s*(system|instruction))",
        re.IGNORECASE,
    ),
    "exfil_markdown": re.compile(r"!\[[^\]]*\]\(\s*https?://", re.IGNORECASE),
}


def detect_injection(text: str) -> list[str]:
    """Retorna os IDs das regras disparadas (lista vazia = nada suspeito)."""
    norm = normalize(text)
    candidates = (norm, _strip_accents(norm))
    hits = [rule for rule, rx in INJECTION_RULES.items() if any(rx.search(c) for c in candidates)]
    return hits


# --------------------------------------------------------------------------------------
# LLM02 / LGPD — redação de dados pessoais antes de enviar ao modelo e antes de logar
# --------------------------------------------------------------------------------------
_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_CNPJ = re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")
_CPF = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
_CARD = re.compile(r"\b(?:\d[ -]?){13,19}\b")
_PHONE_BR = re.compile(r"(?:\+?55\s?)?\(?\b\d{2}\)?\s?9?\d{4}[-\s]?\d{4}\b")


def _luhn_ok(number: str) -> bool:
    digits = [int(d) for d in number if d.isdigit()]
    if not 13 <= len(digits) <= 19:
        return False
    checksum = 0
    parity = len(digits) % 2
    for i, d in enumerate(digits):
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


@dataclass
class RedactionResult:
    text: str
    counts: dict[str, int] = field(default_factory=dict)

    @property
    def total(self) -> int:
        return sum(self.counts.values())


def redact_pii(text: str) -> RedactionResult:
    counts: dict[str, int] = {}

    def _sub(label: str, rx: re.Pattern[str], value: str, validator=None) -> str:
        def repl(m: re.Match[str]) -> str:
            if validator and not validator(m.group(0)):
                return m.group(0)
            counts[label] = counts.get(label, 0) + 1
            return f"[{label}_REMOVIDO]"

        return rx.sub(repl, value)

    out = _sub("EMAIL", _EMAIL, text)
    out = _sub("CARTAO", _CARD, out, validator=_luhn_ok)  # antes de CPF/telefone para não fatiar o número
    out = _sub("CNPJ", _CNPJ, out)
    out = _sub("CPF", _CPF, out)
    out = _sub("TELEFONE", _PHONE_BR, out)
    return RedactionResult(out, counts)


# --------------------------------------------------------------------------------------
# LLM01 — conteúdo do usuário vai SEMPRE dentro de uma fronteira de dados explícita
# --------------------------------------------------------------------------------------
def wrap_user_content(text: str) -> str:
    # Remove qualquer tentativa de fechar a tag manualmente
    safe = re.sub(r"<\s*/?\s*dados_do_usuario\s*>", "", text, flags=re.IGNORECASE)
    return f"<dados_do_usuario>\n{safe}\n</dados_do_usuario>"


# --------------------------------------------------------------------------------------
# LLM08 / LLM10 — saneamento da saída no "sink" (o que vai para o cliente/WhatsApp/web)
# --------------------------------------------------------------------------------------
_ANSI = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b\][^\x07]*\x07")
_MD_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_MD_EXT_LINK = re.compile(r"\[([^\]]+)\]\(\s*https?://[^)]*\)")
_BARE_URL = re.compile(r"\bhttps?://[^\s<>()\[\]]+", re.IGNORECASE)
_ACTIVE_HTML = re.compile(r"<\s*/?\s*(script|iframe|img|object|embed|svg|style|link|meta)\b[^>]*>", re.IGNORECASE)


@dataclass
class OutputResult:
    text: str
    flags: list[str]
    blocked: bool


def sanitize_output(text: str, canary: str) -> OutputResult:
    flags: list[str] = []

    if canary and canary in text:
        return OutputResult("", ["canary_leak"], blocked=True)

    out = text
    if _ANSI.search(out):
        out = _ANSI.sub("", out)
        flags.append("ansi_removed")
    if _MD_IMAGE.search(out):
        out = _MD_IMAGE.sub("[imagem removida]", out)
        flags.append("image_removed")
    if _MD_EXT_LINK.search(out):
        out = _MD_EXT_LINK.sub(r"\1", out)
        flags.append("external_link_removed")
    if _BARE_URL.search(out):
        out = _BARE_URL.sub("[link removido]", out)
        if "external_link_removed" not in flags:
            flags.append("external_link_removed")
    if _ACTIVE_HTML.search(out):
        out = _ACTIVE_HTML.sub("", out)
        flags.append("active_html_removed")

    red = redact_pii(out)
    if red.total:
        flags.append("pii_redacted_output")
    return OutputResult(red.text.strip(), flags, blocked=False)
