#!/usr/bin/env python3
"""Governança do acervo de prompts — roda no CI (job prompt-governance) e no pre-commit.

Falha (exit 1) se algum prompt:
  - não tiver front-matter com todos os campos obrigatórios e válidos;
  - tiver ID duplicado ou categoria diferente da pasta;
  - contiver segredo (token, chave privada) ou dado pessoal real (CPF/cartão);
  - for prompt de sistema sem o placeholder {{CANARY}}.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "prompts"
REQUIRED = ("id", "titulo", "versao", "categoria", "uso", "modelo_testado", "classificacao", "owasp_llm", "autor", "atualizado")
FOLDER_CATEGORY = {
    "01-sistema": "sistema",
    "02-devsecops": "devsecops",
    "03-compliance": "compliance",
    "04-red-team": "red-team",
    "05-incidentes": "incidentes",
}
ID_RX = re.compile(r"^(SYS|DSO|CMP|RT|INC)-\d{3}$")
SEMVER_RX = re.compile(r"^\d+\.\d+\.\d+$")
OWASP_IDS = {f"LLM{n:02d}" for n in range(1, 11)}
CLASSIFICATIONS = {"publico", "interno", "restrito"}

SECRET_PATTERNS = {
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "github_token": re.compile(r"\b(ghp|gho|ghs|ghu)_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{40,}\b"),
    "openai_like_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "slack_token": re.compile(r"\bxox[abpr]-[A-Za-z0-9-]{10,}\b"),
    "private_key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "generic_assignment": re.compile(r"(?i)\b(api[_-]?key|secret|token|senha|password)\s*[:=]\s*['\"][A-Za-z0-9/+_=-]{16,}['\"]"),
}
CPF_RX = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")
CARD_RX = re.compile(r"\b(?:\d[ -]?){13,19}\b")
TEST_CARDS = {"4111111111111111", "4242424242424242", "5555555555554444"}


def luhn_ok(digits: str) -> bool:
    total, parity = 0, len(digits) % 2
    for i, ch in enumerate(digits):
        d = int(ch)
        if i % 2 == parity:
            d = d * 2 - 9 if d > 4 else d * 2
        total += d
    return total % 10 == 0


def parse_front_matter(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    meta: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta


def lint_file(path: Path, seen_ids: dict[str, Path]) -> list[str]:
    errs: list[str] = []
    rel = path.relative_to(ROOT.parent)
    text = path.read_text(encoding="utf-8")
    meta = parse_front_matter(text)
    if meta is None:
        return [f"{rel}: sem front-matter YAML"]

    for key in REQUIRED:
        if not meta.get(key):
            errs.append(f"{rel}: campo obrigatório ausente/vazio: {key}")

    pid = meta.get("id", "")
    if pid and not ID_RX.match(pid):
        errs.append(f"{rel}: id inválido '{pid}' (esperado ex.: DSO-001)")
    if pid in seen_ids:
        errs.append(f"{rel}: id duplicado '{pid}' (também em {seen_ids[pid]})")
    seen_ids[pid] = rel

    if meta.get("versao") and not SEMVER_RX.match(meta["versao"]):
        errs.append(f"{rel}: versao '{meta['versao']}' não é SemVer")

    expected_cat = FOLDER_CATEGORY.get(path.parent.name)
    if expected_cat and meta.get("categoria") != expected_cat:
        errs.append(f"{rel}: categoria '{meta.get('categoria')}' não bate com a pasta ({expected_cat})")

    if meta.get("classificacao") and meta["classificacao"] not in CLASSIFICATIONS:
        errs.append(f"{rel}: classificacao inválida '{meta['classificacao']}'")

    owasp = {x.strip() for x in meta.get("owasp_llm", "").strip("[]").split(",") if x.strip()}
    if not owasp or not owasp <= OWASP_IDS:
        errs.append(f"{rel}: owasp_llm deve listar IDs entre LLM01 e LLM10 (atual: {meta.get('owasp_llm')})")

    try:
        date.fromisoformat(meta.get("atualizado", ""))
    except ValueError:
        errs.append(f"{rel}: atualizado deve ser AAAA-MM-DD")

    for name, rx in SECRET_PATTERNS.items():
        if rx.search(text):
            errs.append(f"{rel}: possível segredo detectado ({name})")
    if CPF_RX.search(text):
        errs.append(f"{rel}: possível CPF real no texto — use placeholder")
    for m in CARD_RX.finditer(text):
        digits = re.sub(r"\D", "", m.group(0))
        if 13 <= len(digits) <= 19 and luhn_ok(digits) and digits not in TEST_CARDS:
            errs.append(f"{rel}: possível número de cartão real ({digits[:4]}…)")

    if meta.get("categoria") == "sistema" and "{{CANARY}}" not in text:
        errs.append(f"{rel}: prompt de sistema precisa do placeholder {{{{CANARY}}}} (detecção de vazamento LLM08)")

    return errs


def main() -> int:
    files = sorted(p for p in ROOT.rglob("*.md") if p.name != "README.md" and not p.name.startswith("_"))
    seen: dict[str, Path] = {}
    errors = [e for f in files for e in lint_file(f, seen)]
    for e in errors:
        print(f"::error::{e}")
    print(f"{len(files)} prompts verificados, {len(errors)} problema(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
