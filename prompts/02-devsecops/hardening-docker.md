---
id: DSO-004
titulo: Hardening de Dockerfile e docker-compose
versao: 1.0.0
categoria: devsecops
uso: Colar Dockerfile e compose. Validar o resultado com checkov, hadolint e trivy config antes do merge.
modelo_testado: Claude / GPT / Qwen 2.5 Coder 14B+
classificacao: interno
owasp_llm: [LLM04, LLM06]
autor: Letícia Saraiva, Nicolas Di Prospero, Matheus Caleiro, Kauã Soares
atualizado: 2026-10-26
---
Você é um engenheiro de plataforma focado em segurança de containers (CIS Docker Benchmark, NIST SP 800-190).

<dockerfile>
{{COLE O DOCKERFILE}}
</dockerfile>

<compose>
{{COLE O DOCKER-COMPOSE.YML}}
</compose>

## Verifique e corrija
**Imagem**
- Imagem base fixada por digest (`@sha256:`), não só por tag.
- Multi-stage: ferramentas de build fora da imagem final.
- `USER` não-root com UID fixo (>= 10000); nada de `sudo`.
- Dependências instaladas com `--require-hashes`; sem cache do pip na camada final.
- Sem segredos em `ENV`, `ARG` ou camadas (`COPY .env` é bloqueante).
- `HEALTHCHECK` definido; `EXPOSE` só da porta necessária.
- `.dockerignore` excluindo `.git`, `.env`, testes e artefatos.

**Runtime (compose)**
- `read_only: true` + `tmpfs` só onde precisa.
- `cap_drop: [ALL]` e `security_opt: [no-new-privileges:true]`.
- Limites de CPU/memória/pids (protege contra consumo ilimitado do LLM).
- Porta publicada só em `127.0.0.1` (atrás de reverse proxy com TLS).
- Serviço do LLM (Ollama) sem porta exposta ao host e em rede separada.
- Imagens de terceiros (ex.: ollama/ollama) com versão fixa, nunca `latest`.

## Saída
1. Tabela: | Item | Status (OK/FALHA) | Risco | Correção |
2. Dockerfile e compose corrigidos **completos**, prontos para colar.
3. Comandos para validar: `checkov -f Dockerfile`, `hadolint Dockerfile`, `trivy config .`, `docker inspect --format '{{.Config.User}}' <imagem>`.

Não remova funcionalidades existentes. Se uma recomendação quebrar algo (ex.: read_only com app que grava em disco), explique e proponha o ajuste.
