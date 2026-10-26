# Matriz de Conformidade — AegisDesk

Rastreabilidade entre os **controles implementados** e os frameworks. Gerada com o prompt [CMP-002](../prompts/03-compliance/matriz-conformidade.md) e revisada manualmente.
Legenda: ✅ implementado · 🟡 parcial · ❌ ausente

## 1. Controles × frameworks

| Controle | Onde está | Evidência verificável | OWASP LLM 2026 | LGPD | NIST SSDF (SP 800-218) | NIST AI RMF | Status |
|---|---|---|---|---|---|---|---|
| Detecção de prompt injection + fronteira de dados | `app/guardrails.py` | `tests/test_guardrails.py`, promptfoo RT-01..04 | LLM01 | art. 46 | PW.5, PW.8 | MEASURE | ✅ |
| Redação de PII antes do LLM e do log | `redact_pii()` | testes de CPF/CNPJ/cartão | LLM02 | art. 6º III (necessidade), art. 46 | PW.5 | MANAGE | ✅ |
| LLM local (Ollama), sem envio a terceiros | `docker-compose.yml` | rede `llm` sem portas expostas | LLM02 | art. 6º VII; evita transferência internacional (art. 33) | PO.5 | MAP | ✅ |
| Sem ferramentas/ações no LLM (só texto) | prompt SYS-001 + API | ausência de tool calling | LLM03 | — | PW.1 | MAP | ✅ |
| Actions fixadas por SHA + Dependabot | `.github/workflows/*`, `dependabot.yml` | zizmor 0 achados, Checkov 252/252 | LLM04 | art. 46 | PS.1, PW.4 | GOVERN | ✅ |
| Lockfile com hash (`--require-hashes`) | `requirements.txt`, `Dockerfile` | build falha se hash divergir | LLM04 | — | PW.4 | — | ✅ |
| SBOM CycloneDX + assinatura Cosign + proveniência SLSA | job `build` | artefato `sbom.cdx.json`, `cosign verify` | LLM04 | art. 37 | PS.2, PS.3 | GOVERN | ✅ |
| Verificação de integridade do modelo baixado | — | — | LLM04, LLM05 | — | PW.4 | MAP | 🟡 digest registrado manualmente |
| Limites de consumo no servidor (entrada, saída, corpo, rate limit) | `config.py`, `security.py`, `llm.py` | testes 413/422/429 | LLM06 | — | PW.5 | MANAGE | ✅ |
| Escopo fechado + não inventar dados | prompt SYS-001 | promptfoo RT-08/RT-09 | LLM07 | art. 6º V (qualidade dos dados) | — | MEASURE | 🟡 depende do modelo |
| Canário no prompt de sistema; prompt sem segredos | `sanitize_output()`, `lint_prompts.py` | teste de canário, lint no CI | LLM08 | art. 46 | PW.7 | MEASURE | ✅ |
| Saneamento de saída (ANSI, HTML, imagens/links) | `sanitize_output()` | testes LLM10 | LLM10 | — | PW.5 | MANAGE | ✅ |
| Log de auditoria sem PII (hash da entrada) | `app/main.py` | log JSON | — | art. 37 (registro), art. 46 | PO.5 | GOVERN | ✅ |
| SAST (Semgrep, Bandit) | job `sast` | SARIF na aba Security | — | art. 46 | PW.7 | MEASURE | ✅ |
| SCA (pip-audit, Trivy fs) | job `sca` | SARIF | LLM04 | art. 46 | RV.1 | MEASURE | ✅ |
| Varredura de segredos (Gitleaks, histórico completo) | job `secrets` | log do job | LLM02 | art. 46 | PS.1 | — | ✅ |
| Scan da imagem (Trivy) com gate CRITICAL/HIGH | job `build` | SARIF | LLM04 | art. 46 | RV.1 | MEASURE | ✅ |
| DAST (OWASP ZAP baseline) | job `build` | relatório `zap-report` | LLM10 | art. 46 | PW.8 | MEASURE | ✅ |
| Container non-root, read-only, sem capabilities | `Dockerfile`, `compose` | `docker inspect`, Checkov | — | art. 46 | PW.9 | — | ✅ |
| Guarda contra Trojan Source (Unicode invisível/bidirecional) em todo o repo | `scripts/check_unicode.py` | job `prompt-governance` | LLM04 | art. 46 | PW.7 | MEASURE | ✅ |
| Governança de prompts (versionamento, revisão, lint) | `prompts/`, `CODEOWNERS` | job `prompt-governance` | LLM01, LLM08 | art. 37 | PO.3 | GOVERN | ✅ |
| Red team automatizado | `llm-redteam.yml` | `redteam-results.json` | LLM01–LLM10 | — | PW.8 | MEASURE | ✅ |
| RIPD (Relatório de Impacto) | prompt CMP-001 | rascunho a ser assinado pelo DPO | — | art. 38 | — | MAP | 🟡 rascunho |
| Plano de resposta a incidente | prompt INC-001, `SECURITY.md` | playbook | LLM04 | art. 48 | RV.2, RV.3 | MANAGE | ✅ |
| Revisão humana de decisões automatizadas | — | bot não decide sobre o titular | — | art. 20 | — | GOVERN | ✅ n/a (sem decisão automatizada) |

## 2. Gaps priorizados

| Gap | Prioridade | Esforço | Ação |
|---|---|---|---|
| Digest do modelo Ollama no AIBOM | Alta | P | Registrar `ollama show --modelfile` + digest no release |
| RIPD assinado | Alta | M | Revisar rascunho CMP-001 com o encarregado |
| Imagem base por digest | Média | P | `make pin-base` |
| Rate limit distribuído | Média | M | Redis |

## 3. Contexto regulatório (out/2026)
- **LGPD (Lei 13.709/2018)** — em vigor; ANPD fiscaliza uso de dados pessoais em IA.
- **PL 2.338/2023 (Marco Legal da IA)** — aprovado no Senado em dez/2024, em análise em Comissão Especial na Câmara; abordagem baseada em risco. O projeto já segue os princípios previstos (transparência, segurança, governança).
- **OWASP Top 10 for LLM Applications 2026** — publicado em 04/08/2026; usado aqui como checklist técnico.
