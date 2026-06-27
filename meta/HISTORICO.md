# HISTORICO.md — Conhecimento Consolidado

> **Opcional.** Arquivo-baú para conhecimento denso que já foi aprendido e não muda mais — guias técnicos, análises de viabilidade, notas de migração — que tornariam o CONTEXT pesado demais.
> Não é lido no início da sessão; o assistente consulta sob demanda quando o assunto aparece.

---

## 1. Análise de scorers de fuzzy matching (RapidFuzz) — por que o set_ratio falha aqui
Pesquisa consolidada em 2026-05-31 (origem do DEC-002).

**O problema central do `token_set_ratio`:** a documentação oficial do RapidFuzz é explícita — a função retorna 100 quando uma string é subconjunto da outra, **independentemente do conteúdo extra na string maior**. Exemplos da própria doc: `token_set_ratio("fuzzy was a bear but not a dog", "fuzzy was a bear") = 100`; o score só cai quando há desacordo explícito entre os tokens (`"...but not a dog"` vs `"...but not a cat"` = ~92). Para um catálogo, isso significa que um nome de arquivo curto cujos tokens todos aparecem numa entrada longa da planilha recebe 100 — falso positivo de alta confiança.

**Famílias de algoritmos (resumo para escolha):**
- **Baseados em caractere** (Levenshtein, Jaro-Winkler): bons para typos e identificadores curtos; Jaro-Winkler dá bônus a prefixos iguais — útil para códigos/nomes.
- **Baseados em token** (token_sort, token_set, Jaccard): lidam com ordem/espaçamento; populares em varejo/e-commerce e títulos de produto. Jaccard mede sobreposição de conjuntos de tokens.
- **Vetoriais** (TF-IDF + cosseno): pesam tokens por raridade — ideal quando muitos tokens são comuns (PISO, CX, RETIF) e poucos discriminam (modelo, medida).
- **WRatio**: combinação ponderada que escolhe a estratégia conforme a razão de comprimento — bom default equilibrado.

**Decisão derivada (DEC-002):** para o motor v2, score ponderado = base `token_sort_ratio` + reforço `WRatio` + penalização por tokens da planilha sem par (mata o efeito subconjunto) + bônus quando medidas (`70X70`, `32X62`) coincidem. TF-IDF+cosseno fica como evolução posterior (F4) por ser mais pesado.

**Princípio prático aprendido:** "não há melhor algoritmo universal — depende dos dados e do problema". Por isso o golden set é obrigatório antes de calibrar: medir, não adivinhar.

## 2. Estrutura do CSV real (pisos) — observações
- Encoding: UTF-8 (sem BOM) no arquivo testado; Google Sheets costuma exportar com BOM → usar detecção (chardet) com fallback `utf-8-sig`.
- Separador: vírgula; valores com vírgula interna (`"R$ 287,30"`, `"1,95MT²"`) vêm entre aspas e o pandas trata sozinho.
- Coluna usada para matching no teste: `Atual: 14/04/2026 - Anterior: 14/04/2026` (contém o nome completo `Marca - Código - Descrição`).
- Coluna `Código Referência` tem códigos puramente numéricos (`00491`, `39182`) e alfanuméricos (`PR4011`, `R7018`). Alguns aparecem "encurtados" vs. o arquivo (origem do FIX-001).
- Há linhas sem código (`ROCHA FORTE - PISO BRIL RETIF HD 70070 ...`) que só casam por descrição → dependem do fuzzy bom.
- Marcadores `*`, `#`, `+` aparecem no fim de algumas descrições (status interno) → removidos no matching e no novo nome.

## 3. Histórico de versões do protótipo (antes da documentação)
- **v1:** fuzzy básico, identificava 143/164 arquivos na pasta de teste.
- **v2 (FUNCIONAL):** thread de scan, tabela com checkbox, 5 ações, filtro por slider; identificava 164/164 mas falhava em nomear alguns (códigos encurtados).
- **v3 (Gemini, não funcional):** tentou adicionar config de sufixos mas quebrou a execução; descartada.
- **0.3.1 (esta linha):** corrigidos bidirecional, limpeza `*#+`, layout, self-copy; base para o motor v2.
