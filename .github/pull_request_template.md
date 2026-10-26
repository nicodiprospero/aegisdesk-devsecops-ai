## O que muda
<!-- 1-3 linhas -->

## Checklist de segurança
- [ ] Pipeline DevSecOps verde (secrets, SAST, SCA, IaC, prompt-governance, testes, build/scan)
- [ ] Nenhum segredo, chave ou dado pessoal real no diff
- [ ] Dependência nova? Conferi que o pacote existe, é mantido e está no lockfile com hash
- [ ] Mudou prompt em `prompts/`? Subi a `versao` no front-matter e rodei o **LLM Red Team**
- [ ] Mudou `guardrails.py`? Adicionei teste para o caso novo (positivo e falso positivo)
- [ ] Endpoint novo usa `Depends(enforce_rate_limit)`
- [ ] Saída do LLM passa por `sanitize_output` antes de qualquer sink

## Riscos OWASP LLM 2026 afetados
<!-- ex.: LLM01, LLM06 — ou "nenhum" -->
