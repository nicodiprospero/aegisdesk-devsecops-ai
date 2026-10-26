# Política de Segurança

## Reportando uma vulnerabilidade
Não abra issue pública. Use **Security → Report a vulnerability** (GitHub Private Vulnerability Reporting).
Inclua: componente, passos para reproduzir, impacto e, se for prompt injection, a entrada exata e a resposta obtida.

| Severidade | Primeira resposta | Correção |
|---|---|---|
| Crítica | 24 h | 7 dias |
| Alta | 48 h | 15 dias |
| Média | 5 dias | 30 dias |
| Baixa | 10 dias | próximo ciclo |

## Escopo
- API (`app/`), imagem Docker, workflows de CI/CD e prompts de produção (`prompts/01-sistema/`).
- Fuga de escopo do assistente, vazamento do prompt de sistema (token canário) e exfiltração via saída do LLM **estão no escopo**.

## Incidentes
Playbook de cadeia de suprimentos: [`prompts/05-incidentes/resposta-supply-chain.md`](prompts/05-incidentes/resposta-supply-chain.md).
Se houver risco a dados pessoais, o encarregado (DPO) avalia a comunicação à ANPD e aos titulares (LGPD, art. 48).

## Verificando uma imagem publicada
```bash
cosign verify ghcr.io/nicodiprospero/aegisdesk-devsecops-ai@sha256:<digest> \
  --certificate-identity-regexp 'https://github.com/nicodiprospero/aegisdesk-devsecops-ai/.github/workflows/devsecops.yml@.*' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```
