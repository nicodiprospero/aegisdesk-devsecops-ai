# 📚 Acervo de Prompts — AegisDesk DevSecOps

Prompts versionados como código: cada um passa por Pull Request, revisão do CODEOWNERS e pelo job
`prompt-governance` do pipeline (`scripts/lint_prompts.py`), que bloqueia o merge se faltar metadado,
se houver segredo/dado pessoal no texto ou se o prompt de sistema não tiver o token canário.

## Índice

| ID | Prompt | Categoria | Para que serve |
|---|---|---|---|
| SYS-001 | [Assistente de atendimento](01-sistema/assistente-atendimento.v1.md) | sistema | Prompt de produção carregado pela API |
| DSO-001 | [Threat modeling STRIDE + OWASP LLM](02-devsecops/threat-modeling-stride-llm.md) | devsecops | Modelagem de ameaças acionável |
| DSO-002 | [Code review de segurança](02-devsecops/code-review-seguranca.md) | devsecops | Revisão de PR com foco em AppSec + LLM |
| DSO-003 | [Triagem de vulnerabilidades](02-devsecops/triagem-vulnerabilidades.md) | devsecops | Prioriza saída de Trivy/pip-audit/Semgrep/ZAP |
| DSO-004 | [Hardening Docker](02-devsecops/hardening-docker.md) | devsecops | Dockerfile/compose no padrão CIS |
| DSO-005 | [Auditoria GitHub Actions](02-devsecops/auditoria-github-actions.md) | devsecops | SHA pinning, permissões, injeção de expressão |
| DSO-006 | [Testes de segurança](02-devsecops/gerar-testes-seguranca.md) | devsecops | Gera pytest para guardrails |
| CMP-001 | [RIPD LGPD](03-compliance/ripd-lgpd.md) | compliance | Rascunho do Relatório de Impacto (art. 38) |
| CMP-002 | [Matriz de conformidade](03-compliance/matriz-conformidade.md) | compliance | Controles × OWASP × LGPD × SSDF × AI RMF |
| CMP-003 | [Política de uso de IA](03-compliance/politica-uso-ia.md) | compliance | Regras para a equipe |
| RT-001 | [Casos de prompt injection](04-red-team/casos-prompt-injection.md) | red-team | Banco de testes adversariais |
| RT-002 | [LLM-as-judge](04-red-team/avaliador-respostas.md) | red-team | Avaliação automática de respostas |
| INC-001 | [Incidente de supply chain](05-incidentes/resposta-supply-chain.md) | incidentes | Playbook (caso Trivy / CVE-2026-33634) |

## Padrão de um prompt

Todo arquivo começa com front-matter YAML. Campos obrigatórios:

```yaml
---
id: DSO-007            # prefixo da categoria + número
titulo: ...
versao: 1.0.0          # SemVer: MAJOR muda comportamento, MINOR adiciona, PATCH corrige texto
categoria: devsecops   # sistema | devsecops | compliance | red-team | incidentes
uso: Quando e como usar
modelo_testado: ...
classificacao: interno # publico | interno | restrito
owasp_llm: [LLM01]     # riscos que o prompt trata
autor: Nome
atualizado: AAAA-MM-DD
---
```

Use o [template](_template.md) para criar um novo.

## Regras do acervo
1. **Nada de segredo** (chave, token, senha) nem dado pessoal real — o lint bloqueia.
2. **Variáveis** sempre em `{{MAIUSCULAS}}`; conteúdo colado pelo usuário vai dentro de tags (`<diff>`, `<relatorios>`), para separar dado de instrução.
3. **Prompt de sistema não é controle de segurança**: assuma que ele pode vazar (OWASP LLM08) — por isso ele não contém nada sigiloso além do canário.
4. Mudou o comportamento? Suba a versão MAJOR e rode o red team (`llm-redteam.yml`) antes do merge.
