#!/usr/bin/env python3
"""Cria o .env a partir do .env.example, gerando a chave de API, o hash e o token canário.

A chave em texto puro é exibida UMA vez e não é gravada em lugar nenhum: o servidor guarda só o hash.
Uso:  python3 scripts/setup_env.py            (Windows: py scripts\\setup_env.py)
      python3 scripts/setup_env.py --force    (recria o .env)
"""

from __future__ import annotations

import hashlib
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    env_file = ROOT / ".env"
    if env_file.exists() and "--force" not in sys.argv:
        print(".env já existe. Use --force para recriar (a chave antiga deixa de funcionar).")
        return 1

    api_key = secrets.token_urlsafe(32)
    generated = {
        "AEGIS_API_KEY_HASHES": hashlib.sha256(api_key.encode("utf-8")).hexdigest(),
        "AEGIS_CANARY_TOKEN": f"CANARY-{secrets.token_hex(8)}",
    }

    lines = []
    for line in (ROOT / ".env.example").read_text(encoding="utf-8").splitlines():
        name = line.split("=", 1)[0].strip()
        lines.append(f"{name}={generated[name]}" if name in generated and not line.startswith("#") else line)
    env_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(".env criado com o hash da chave e o token canário.")
    print("Sua chave de API (guarde agora — ela não fica salva no servidor):")
    print(api_key)
    return 0


if __name__ == "__main__":
    sys.exit(main())
