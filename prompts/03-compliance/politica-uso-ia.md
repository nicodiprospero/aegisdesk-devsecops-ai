---
id: CMP-003
titulo: Política interna de uso seguro de IA generativa pela equipe
versao: 1.0.0
categoria: compliance
uso: Gera a política de uso de IA para devs/atendimento. Revisar com jurídico e DPO antes de publicar.
modelo_testado: Claude / GPT
classificacao: interno
owasp_llm: [LLM02, LLM04, LLM07]
autor: Letícia Saraiva, Nicolas Di Prospero, Matheus Caleiro, Kauã Soares
atualizado: 2026-10-26
---
Você é um gestor de GRC (Governança, Risco e Conformidade). Escreva uma política curta e aplicável (máx. 2 páginas) de uso de IA generativa pela equipe.

<contexto>
- Empresa: {{nome, setor, tamanho}}
- Ferramentas aprovadas: {{ex.: Ollama interno (dados de clientes permitidos), assistente de código corporativo (sem dados de clientes)}}
- Ferramentas proibidas: {{ex.: contas pessoais de chatbots públicos para dados da empresa}}
</contexto>

## A política deve ter
1. Objetivo e escopo (quem e quais ferramentas).
2. **Classificação de dados x ferramenta** em tabela: | Classificação | Exemplos | Pode usar em IA interna? | Pode usar em IA externa? |
3. Regras para código gerado por IA: passa pelo mesmo pipeline (SAST, SCA, revisão humana), proibido aceitar dependência sugerida sem checar se existe e quem mantém (ataque de "slopsquatting"/pacote alucinado).
4. Regras para prompts: prompts de produção ficam versionados no acervo (`prompts/`), com front-matter, revisão por PR e sem segredos.
5. Verificação de saída: IA pode errar (OWASP LLM07 — Misinformation); responsabilidade final é humana.
6. Incidentes: o que reportar, para quem, em quanto tempo.
7. Sanções e revisão periódica (a cada 6 meses).

Linguagem simples, verbos no imperativo, sem juridiquês. Português do Brasil.
