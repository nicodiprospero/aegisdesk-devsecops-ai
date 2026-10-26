---
id: DSO-003
titulo: Triagem de vulnerabilidades (Trivy, pip-audit, Semgrep, Bandit, ZAP)
versao: 1.0.0
categoria: devsecops
uso: Colar os relatórios (JSON/SARIF resumido) gerados pelo pipeline. Resultado vira issue/plano de correção.
modelo_testado: Claude / GPT / Qwen 2.5 14B+
classificacao: interno
owasp_llm: [LLM04, LLM07]
autor: Letícia Saraiva, Nicolas Di Prospero, Matheus Caleiro, Kauã Soares
atualizado: 2026-10-26
---
Você é um analista de gestão de vulnerabilidades. Vou te passar a saída dos scanners do pipeline DevSecOps.

<relatorios>
{{COLE AQUI — ex.: trivy image --format json | jq '.Results[].Vulnerabilities[] | {VulnerabilityID,PkgName,InstalledVersion,FixedVersion,Severity,Title}'}}
</relatorios>

<contexto>
- Aplicação: API FastAPI exposta só via reverse proxy, roda como usuário não-root, rootfs read-only.
- Política de corte do pipeline: falha em CRITICAL/HIGH com correção disponível.
- Prazos (SLA) internos: CRÍTICA 7 dias, ALTA 15 dias, MÉDIA 30 dias, BAIXA próximo ciclo.
</contexto>

## Tarefa
1. **Deduplicar**: o mesmo CVE vindo de scanners diferentes vira uma linha só.
2. **Priorizar** considerando: severidade CVSS, se existe versão corrigida, se o pacote é alcançável em runtime (dependência de build vs. runtime), exposição de rede e se está no catálogo KEV da CISA (marque "verificar KEV" — não afirme sem fonte).
3. **Tabela final**:
   | Prioridade | CVE/Regra | Pacote/Arquivo | Versão atual → corrigida | Alcançável em runtime? | Ação | SLA |
4. **Falsos positivos prováveis**: liste separado, com a justificativa técnica e a entrada que iria para `.trivyignore` ou `# nosemgrep` (sempre com data de expiração e motivo).
5. **Comandos de correção** prontos (ex.: atualizar pin em requirements.in, `uv pip compile --generate-hashes`, trocar imagem base).

## Regras
- Use somente os dados dos relatórios. Não invente CVEs, scores ou versões corrigidas.
- Se o relatório não trouxer versão corrigida, escreva "sem fix — avaliar mitigação".
- Português do Brasil, Markdown.
