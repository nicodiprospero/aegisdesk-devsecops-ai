---
id: INC-001
titulo: Playbook de resposta a incidente de cadeia de suprimentos em CI/CD
versao: 1.0.0
categoria: incidentes
uso: Acionar quando uma Action, pacote ou imagem usada no pipeline for reportada como comprometida.
modelo_testado: Claude / GPT
classificacao: interno
owasp_llm: [LLM04]
autor: Letícia Saraiva, Nicolas Di Prospero, Matheus Caleiro, Kauã Soares
atualizado: 2026-10-26
---
Você é um líder de resposta a incidentes (IR) de segurança de software.
Um componente da nossa cadeia de suprimentos foi reportado como comprometido.

<alerta>
{{COLE: advisory/CVE, componente afetado, versões afetadas, janela de exposição. Ex.: CVE-2026-33634 — trivy-action < 0.35.0 e setup-trivy, tags reescritas em 19/03/2026, malware lia memória do runner e exfiltrava segredos}}
</alerta>

<nosso_uso>
{{COLE: workflows que usam o componente, como é referenciado (tag ou SHA), quais segredos estão disponíveis nesses jobs, execuções na janela}}
</nosso_uso>

## Entregue um plano em fases, com comandos
1. **Triagem (primeira hora)**: estamos expostos? Critério objetivo (ex.: referência por tag mutável + execução dentro da janela). Comandos para listar execuções: `gh run list --workflow <arquivo> --created <data>..<data> --json databaseId,createdAt,headSha`.
2. **Contenção**: desabilitar workflows afetados (`gh workflow disable`), revogar e rotacionar TODOS os segredos acessíveis ao job (GITHUB_TOKEN expira sozinho; PATs, tokens de registry, chaves de nuvem não), bloquear o componente.
3. **Erradicação**: fixar por SHA de commit verificado, atualizar para versão segura, habilitar exigência de SHA pinning na organização, Dependabot para `github-actions`.
4. **Investigação**: verificar pushes inesperados no registry, novos repositórios/forks estranhos na organização, logs de acesso do provedor de nuvem na janela.
5. **Comunicação**: se dados pessoais puderem ter sido afetados, avaliar comunicação à ANPD e aos titulares (LGPD art. 48) com o encarregado.
6. **Lições aprendidas**: controles que teriam evitado (SHA pinning, harden-runner com egress bloqueado, segredos com escopo mínimo, OIDC).

Formato: checklist Markdown com responsável e prazo por item. Não invente fatos sobre o incidente que não estejam no alerta.
