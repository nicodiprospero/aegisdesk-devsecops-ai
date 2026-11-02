# syntax=docker/dockerfile:1
# AegisDesk API — imagem endurecida (multi-stage, non-root, sem ferramentas de build no runtime)
#
# Imagem base escrita literalmente no FROM (sem ARG): assim o Checkov valida a tag (CKV_DOCKER_7)
# e o Dependabot (ecosystem docker) consegue abrir PR quando a base receber correções.
# Para build reprodutível, fixe por digest:  make pin-base

# ---------------------------------------------------------------- build
FROM python:3.15-slim-trixie AS builder
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /build
COPY requirements.txt .
# --require-hashes: cada pacote é verificado contra o hash SHA-256 do lockfile (anti-typosquatting/tampering)
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --require-hashes --no-deps -r requirements.txt \
 && /opt/venv/bin/pip uninstall -y pip

# ---------------------------------------------------------------- runtime
FROM python:3.15-slim-trixie AS runtime
LABEL org.opencontainers.image.title="AegisDesk API" \
      org.opencontainers.image.description="API de atendimento com IA e pipeline DevSecOps" \
      org.opencontainers.image.licenses="MIT"

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AEGIS_ENV=prod

# Patches de segurança do Debian publicados depois da imagem base + runtime sem gerenciador de pacotes Python
RUN apt-get update \
 && apt-get -y upgrade --no-install-recommends \
 && rm -rf /var/lib/apt/lists/* \
 && python -m pip uninstall -y pip \
 && groupadd --system --gid 10001 aegis \
 && useradd --system --uid 10001 --gid aegis --no-create-home --shell /usr/sbin/nologin aegis

WORKDIR /srv
COPY --from=builder /opt/venv /opt/venv
# Código pertence ao root: o processo (UID 10001) só lê, não consegue alterar a si mesmo
COPY --chown=root:root app ./app
COPY --chown=root:root prompts/01-sistema ./prompts/01-sistema

USER 10001:10001
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import sys, urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=2).status == 200 else 1)"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-server-header", "--proxy-headers", "--forwarded-allow-ips", "127.0.0.1"]
