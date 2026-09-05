# CHANGELOG

> Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/) e versionamento [SemVer](https://semver.org/lang/pt-BR/).
> **Cresce**: entradas novas no topo. Registra só o que foi de fato concluído/entregue.

## [Não lançado]
### Planejado
- Reescrita do motor de matching (scoring ponderado) — ver DEC-002 e ROADMAP F2.
- Suíte de testes com golden set da pasta real de pisos.

---

## [0.4.2] — 2026-09-04
### Corrigido
- **FIX-005 — planilha lida sempre como texto.** `dtype=str` + `keep_default_na=False` num loader único (`UTILITÁRIOS/spreadsheet_loader.py`) usado pela GUI e pelo harness. Antes o pandas inferia `int64` numa coluna de código e `00611` virava `611`, o que comia o zero no nome final e matava o match por código. Verificado por par negativo.
- **Harness escolhia a coluna sozinho.** O fallback "primeira coluna com ` - `" passou a apontar para `Descrição` quando o esquema do export mudou, e o teste seguiu dando número medindo outra coisa. Agora as colunas são explícitas e coluna ausente aborta — ver DEC-008.

### Modificado
- **Golden set rechaveado** de índice de linha para `Interno` (código interno), e `-1` virou `SEM_MATCH`. Índice absoluto muda a cada reexport e não é propriedade do produto.
- **Referência congelada** em `test/planilha_referencia.csv` (119 linhas). O harness roda sem argumentos e devolve código de saída 0/1/2.
- `CLAUDE.md` ganhou os comandos reais de build e validação, que eram PLACEHOLDER desde a migração.

### Notas
- A integração do motor v2 na GUI (Parte B da WO 0003) **não** entrou nesta versão. `main.py` ainda faz matching com o motor antigo.

---

## [0.4.1] — 2026-09-03
### Modificado
- **Migração para o contrato KCM v1.122.0** — layout `meta/` + `.claude/`, modo Code ligado, ASU desligado. Ver DEC-007.
- `CLAUDE.md` antigo (CEREBRO antigo) descartado e substituído por `meta/CEREBRO.md` (novo) + `CLAUDE.md` raiz (guia do Claude Code).
- `HISTORICO.md` renomeado para `meta/HISTORY.md`.
- Demais docs vivos preservados e reposicionados em `meta/`.
### Adicionado
- `.claude/skills/apply-wo/SKILL.md` e `.claude/skills/wrap/SKILL.md` (comandos do modo Code).
- `.claude/settings.json`, `.gitignore`, `.flatdropignore`, `meta/SPEC.md`, `meta/workorders/_TEMPLATE.md`.
### Removido
- Seção `## Saída de código via ASU (patch)` (sobra do modo ASU, agora desligado).
- Linhas revogadas REV-2/REV-3/REV-4 (eliminadas junto com o CEREBRO antigo).

## [0.4.0] — 2026-05-31
### Adicionado
- **Motor de matching v2 modular** (`matching_engine.py`): puro Python, sem PySide6, testável isoladamente — ver DEC-002 e ROADMAP F2.
- **Golden set** (`golden_set.csv`) com 24 casos reais da pasta de pisos + **harness** (`test_matching.py`) que reporta % de acerto e lista erros. Resultado: 24/24 (100%); auto-match 80/80.
- **Score ponderado**: token_sort + WRatio + cobertura de tokens + medida discriminante (substitui o `token_set_ratio` que inflava score) — ver DEC-002.
- **Medida como campo discriminante** com penalidade de divergência — ver DEC-005.
- **Guarda de código ausente**: código de referência claro sem par na planilha não casa por fuzzy — ver DEC-006.
- Transparência do motor: `Resultado` devolve `componentes` (scores parciais), `codigo_casado` e flag `ambiguo` (ainda não exibidos na UI).
### Corrigido
- Código de referência não ancora mais em dimensões/medidas (`33X57`, `50MT²`) — resolve falsos positivos como `61838↔39182` — ver FIX-004.
### Notas
- A GUI (`main.py` 0.3.1) ainda usa o motor antigo embutido; integração com o v2 é o próximo passo (ver STATUS).

## [0.3.1] — 2026-05-31
### Corrigido
- Match por código agora é **bidirecional**, resolvendo códigos encurtados na planilha (`PR70671↔PR7067`, `R70181↔R7018`) — ver FIX-001.
- `renomear_copiar`/`renomear_mover` não copiam mais o arquivo sobre si mesmo quando a pasta destino é a mesma do original — ver FIX-002.
- Barra superior reorganizada em `QGroupBox` com sub-linhas; rótulos de coluna e Threshold não se sobrepõem mais — ver FIX-003.
### Modificado
- Limpeza de marcadores internos `* # + !` do FINAL dos valores da planilha, antes do matching e ao gerar o novo nome (`limpar_valor_planilha`).
- Scorer fuzzy trocado de `token_sort_ratio` para `token_set_ratio` (NOTA: posteriormente identificado como fonte de inflação de score — será revertido/substituído no motor v2, ver DEC-002).

## [0.3.0] — 2026-05-31
### Adicionado
- Sistema de documentação do projeto (CONTEXT, STATUS, DECISIONS, CHANGELOG, IDEAS, ROADMAP, GLOSSARY, HISTORICO, LOG-TEMPLATE, logs/).

## [0.2.0] — (protótipo "main v2 FUNCIONAL", anterior a esta sessão)
### Adicionado
- Versão funcional: carregamento CSV/XLSX, seleção de colunas, scan em thread, tabela de preview com checkbox, 5 ações de arquivo, filtro de score por slider.
### Notas
- Identificava 164/164 arquivos em pasta-teste, mas falhava ao nomear alguns (códigos encurtados) — base para os fixes da 0.3.1.

## [0.1.0] — (protótipo inicial)
### Adicionado
- Primeira versão com fuzzy básico; identificava 143/164 arquivos. Base do projeto.
