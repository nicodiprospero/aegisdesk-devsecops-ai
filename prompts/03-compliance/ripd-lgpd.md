---
id: CMP-001
titulo: Rascunho de RIPD (Relatório de Impacto à Proteção de Dados) para sistema com IA
versao: 1.0.0
categoria: compliance
uso: Gera o rascunho do RIPD (LGPD art. 38). Precisa de revisão do encarregado (DPO) antes de valer.
modelo_testado: Claude / GPT
classificacao: interno
owasp_llm: [LLM02]
autor: Letícia Saraiva, Nicolas Di Prospero, Matheus Caleiro, Kauã Soares
atualizado: 2026-10-26
---
Você é um consultor de privacidade com experiência em LGPD (Lei 13.709/2018) e em sistemas de IA.
Produza um **rascunho de RIPD** para o sistema descrito. Deixe claro no topo que é um rascunho para revisão do encarregado.

<sistema>
{{DESCREVA: finalidade, quem são os titulares, quais dados entram (texto livre do cliente), onde o LLM roda, o que é logado, por quanto tempo, quem acessa, operadores/terceiros}}
</sistema>

## Estrutura obrigatória
1. **Identificação**: controlador, operador(es), encarregado, data, versão.
2. **Descrição do tratamento**: natureza, escopo, contexto e finalidade (art. 5º, XVII; art. 38).
3. **Dados tratados**: tabela | Dado | Categoria (comum/sensível — art. 5º, II) | Origem | Finalidade | Base legal (art. 7º ou 11) | Retenção |.
   - Considere que o cliente pode digitar dados que não pedimos (CPF, cartão, saúde) no texto livre.
4. **Princípios (art. 6º)**: como o sistema atende finalidade, adequação, necessidade (minimização), transparência, segurança, prevenção e responsabilização. Cite os controles técnicos reais (ex.: redação de PII antes do LLM, LLM local sem envio a terceiros, logs só com hash).
5. **Riscos aos titulares**: tabela | Risco | Probabilidade | Impacto | Medida de mitigação | Risco residual |. Inclua vazamento por prompt injection, memorização/log de PII, decisão automatizada (art. 20), transferência internacional se usar API externa.
6. **Medidas de segurança (art. 46)** técnicas e administrativas.
7. **Plano de resposta a incidentes** (art. 48): critérios para comunicar a ANPD e titulares.
8. **Direitos do titular (art. 18)**: como atender acesso, correção, eliminação, revisão.
9. **Conclusão** e pendências.

## Regras
- Não afirme que o sistema está "em conformidade" — o RIPD avalia risco, não certifica.
- Marque com ⚠️ toda informação que depende de decisão do controlador e não está no contexto.
- Referencie artigos da LGPD apenas quando tiver certeza do número.
