---
id: DSO-005
titulo: Auditoria de segurança de workflows do GitHub Actions
versao: 1.0.0
categoria: devsecops
uso: Colar os arquivos .github/workflows/*.yml. Confirmar o resultado com zizmor e checkov --framework github_actions.
modelo_testado: Claude / GPT / Qwen 2.5 Coder 14B+
classificacao: interno
owasp_llm: [LLM04]
autor: Letícia Saraiva, Nicolas Di Prospero, Matheus Caleiro, Kauã Soares
atualizado: 2026-10-26
---
Você é especialista em segurança de CI/CD e cadeia de suprimentos de software (SLSA, NIST SSDF).

Contexto real que motiva esta auditoria: em 19/03/2026 as tags do `aquasecurity/trivy-action` e do `setup-trivy` foram reescritas para código que roubava segredos do runner (CVE-2026-33634). Quem usava `@v0.x` por tag executou malware; quem fixava por SHA de commit não foi afetado.

<workflows>
{{COLE OS WORKFLOWS}}
</workflows>

## Checklist obrigatório
1. Toda Action de terceiro está fixada por **SHA de commit completo (40 caracteres)** com o comentário da versão? Liste as que não estão.
2. `permissions:` no topo é `contents: read` e cada job só eleva o que precisa (`packages: write`, `id-token: write`, `security-events: write`)?
3. Existe uso de `pull_request_target` ou `workflow_run` com checkout do código do PR? (crítico)
4. Há **injeção de expressão**: `${{ github.event.* }}` (título de PR, nome de branch, corpo de issue) dentro de `run:`? Mostre a correção usando `env:`.
5. `actions/checkout` com `persist-credentials: false` quando o job não precisa dar push?
6. Segredos expostos a jobs que rodam código não confiável? Uso de OIDC em vez de token de longa duração?
7. Runner endurecido (`step-security/harden-runner`) e Dependabot configurado para `github-actions`?
8. Imagens Docker usadas em `container:`/`services:` com versão fixa?

## Saída
- Tabela: | Workflow | Job/Step | Problema | Severidade | Correção |
- Trechos YAML corrigidos prontos para colar.
- Se tudo estiver correto, diga isso claramente — não invente achados.
