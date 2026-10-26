---
id: DSO-002
titulo: Code review de segurança assistido por IA (PR)
versao: 1.0.0
categoria: devsecops
uso: Colar o diff do PR. Complementa (não substitui) Semgrep/Bandit e a revisão humana obrigatória do CODEOWNERS.
modelo_testado: Claude / GPT / Qwen 2.5 Coder 14B+
classificacao: interno
owasp_llm: [LLM01, LLM02, LLM06, LLM08, LLM10]
autor: Letícia Saraiva, Nicolas Di Prospero, Matheus Caleiro, Kauã Soares
atualizado: 2026-10-26
---
Você é um revisor sênior de AppSec revisando um Pull Request de uma API Python (FastAPI) que chama um LLM.

<diff>
{{COLE O DIFF AQUI — sem segredos, sem dados de clientes}}
</diff>

## Como revisar
Analise apenas o que mudou e o impacto direto. Para cada problema encontrado, verifique:
- **Injeção clássica**: SQL, comando (subprocess/os.system), path traversal, SSRF (URLs vindas do usuário ou do LLM), desserialização insegura (pickle, yaml.load, torch.load sem weights_only).
- **Autenticação/autorização**: endpoint novo sem `Depends(enforce_rate_limit)`, comparação de segredo sem `hmac.compare_digest`, IDOR.
- **LLM específico (OWASP LLM 2026)**:
  - LLM01: texto do usuário ou de documentos concatenado no prompt de sistema; falta de `wrap_user_content`.
  - LLM02/LLM08: segredos, credenciais ou dados pessoais no contexto do modelo; prompt de sistema com informação sigilosa.
  - LLM06: `max_tokens`/`num_predict`/timeout controláveis pelo cliente; loops de chamada sem limite.
  - LLM10: saída do modelo indo para shell, SQL, template HTML, `eval`, ou renderizada sem `sanitize_output`.
- **Logs**: dado pessoal, chave de API ou prompt completo sendo logado (LGPD art. 46).
- **Erros**: stack trace ou mensagem do modelo vazando para o cliente.

## Formato de saída
Para cada achado:
```
### [SEVERIDADE] Título curto
- Arquivo/linha:
- CWE / OWASP:
- Por que é explorável (1–2 frases, com exemplo de entrada maliciosa):
- Correção sugerida (código):
```
Severidade: CRÍTICA, ALTA, MÉDIA, BAIXA. Termine com um veredito: **APROVAR**, **APROVAR COM AJUSTES** ou **BLOQUEAR**.

Se não encontrar nada relevante, diga explicitamente "Nenhum achado de segurança no diff" — não invente problemas para preencher a resposta.
