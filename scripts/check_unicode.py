#!/usr/bin/env python3
"""Guarda contra Trojan Source (CVE-2021-42574, CWE-838) em TODOS os arquivos do repositório.

O Bandit (B613) só olha .py; este script também cobre Markdown, YAML, TOML, prompts e docs.
Reprova (exit 1) se encontrar caracteres de controle bidirecional ou de largura zero.
Para representar esses caracteres no código, use escapes ASCII (barra invertida + u + código).
"""

from __future__ import annotations

import sys
import unicodedata
from pathlib import Path

SUSPICIOUS = (
    set(range(0x200B, 0x2010))  # zero-width space/joiners, LRM, RLM
    | set(range(0x202A, 0x202F))  # LRE, RLE, PDF, LRO, RLO
    | set(range(0x2060, 0x2065))  # word joiner, invisible operators
    | set(range(0x2066, 0x206A))  # LRI, RLI, FSI, PDI
    | {0xFEFF}  # BOM / zero-width no-break space
)


ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}


def tracked_files() -> list[str]:
    # Sem subprocess/git: varre a árvore do projeto (Bandit B404/B603/B607 limpo)
    return sorted(
        str(p.relative_to(ROOT))
        for p in ROOT.rglob("*")
        if p.is_file() and not SKIP_DIRS.intersection(p.relative_to(ROOT).parts)
    )


def main() -> int:
    problems = 0
    files = tracked_files()
    for path in files:
        try:
            with open(ROOT / path, encoding="utf-8") as fh:
                lines = fh.read().splitlines()
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue  # binário ou removido
        for n, line in enumerate(lines, 1):
            hits = sorted({ord(c) for c in line if ord(c) in SUSPICIOUS})
            if hits:
                problems += 1
                names = ", ".join(f"U+{cp:04X} {unicodedata.name(chr(cp), '?')}" for cp in hits)
                print(f"::error file={path},line={n}::caractere invisível/bidirecional: {names}")
    print(f"{len(files)} arquivos verificados, {problems} linha(s) com problema.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
