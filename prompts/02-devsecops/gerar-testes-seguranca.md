---
id: DSO-006
titulo: Geração de testes de segurança (pytest) para guardrails de LLM
versao: 1.0.0
categoria: devsecops
uso: Colar o módulo de guardrails. Os testes gerados entram em tests/ e rodam no job "tests" do pipeline.
modelo_testado: Claude / GPT / Qwen 2.5 Coder 14B+
classificacao: interno
owasp_llm: [LLM01, LLM02, LLM08, LLM10]
autor: Letícia Saraiva, Nicolas Di Prospero, Matheus Caleiro, Kauã Soares
atualizado: 2026-10-26
---
Você é engenheiro de QA de segurança. Escreva testes `pytest` para o módulo abaixo.

<codigo>
{{COLE app/guardrails.py}}
</codigo>

## Requisitos dos testes
- Usar `@pytest.mark.parametrize` com casos positivos (deve detectar/bloquear) e negativos (não pode gerar falso positivo em frases normais de atendimento, ex.: "quero ignorar a taxa de entrega?", "qual o prazo do pedido 12345?").
- Cobrir técnicas de evasão: caracteres de largura zero, letras com acento/sem acento, MAIÚSCULAS, quebra de linha no meio da frase, tags falsas `</dados_do_usuario>`, `[INST]`, `<|im_start|>`.
- PII brasileira: CPF com e sem pontuação, CNPJ, telefone com DDD, e-mail, cartão válido pelo algoritmo de Luhn (4111 1111 1111 1111) e um número de 16 dígitos INVÁLIDO no Luhn (não deve ser mascarado como cartão).
- Saída: token canário bloqueia a resposta; imagem markdown com URL externa é removida; sequência ANSI é removida; `<script>` é removido.
- Nada de chamadas reais ao LLM — usar fake/stub.
- Cada teste com nome descritivo em português ou inglês e uma linha de docstring dizendo qual risco OWASP LLM ele cobre.

Entregue o arquivo completo `tests/test_guardrails_extra.py`, pronto para rodar com `pytest -q`.
