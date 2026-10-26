---
id: CMP-002
titulo: Matriz de conformidade — controles x OWASP LLM 2026 x LGPD x NIST SSDF x NIST AI RMF
versao: 1.0.0
categoria: compliance
uso: Gera/atualiza docs/compliance-matrix.md a partir do repositório. Rodar a cada release.
modelo_testado: Claude / GPT
classificacao: interno
owasp_llm: [LLM01, LLM02, LLM03, LLM04, LLM05, LLM06, LLM07, LLM08, LLM09, LLM10]
autor: Letícia Saraiva, Nicolas Di Prospero, Matheus Caleiro, Kauã Soares
atualizado: 2026-10-26
---
Você é auditor de segurança e conformidade. Monte uma matriz de rastreabilidade entre os **controles implementados** e os frameworks.

<evidencias>
{{COLE: lista de arquivos e trechos relevantes — workflows, Dockerfile, compose, guardrails.py, SECURITY.md, resultados dos scanners}}
</evidencias>

## Frameworks de referência
- OWASP Top 10 for LLM Applications 2026 (LLM01–LLM10)
- LGPD — Lei 13.709/2018 (arts. 6º, 37, 38, 46, 48)
- NIST SP 800-218 (SSDF) — grupos PO, PS, PW, RV
- NIST AI RMF 1.0 — funções GOVERN, MAP, MEASURE, MANAGE
- CIS Docker Benchmark (controles de imagem e runtime)

## Saída
1. Tabela principal:
   | Controle | Onde está (arquivo/job) | Evidência verificável | OWASP LLM | LGPD | SSDF | AI RMF | Status |
   Status: ✅ implementado · 🟡 parcial · ❌ ausente.
2. **Gaps**: controles exigidos pelos frameworks que não aparecem nas evidências, com prioridade e esforço (P/M/G).
3. **Evidência para auditoria**: para cada ✅, qual artefato provar (SARIF no Security tab, SBOM CycloneDX, assinatura Cosign, log do job).

## Regras
- Só marque ✅ se houver evidência no material colado. Na dúvida, 🟡 e explique.
- Não atribua número de controle CIS se não tiver certeza da versão do benchmark; descreva o controle em palavras.
