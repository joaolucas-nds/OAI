# STATUS.md — Estado Atual

> Arquivo **rolante**: descreve só o AGORA. O assistente lê no início para saber onde retomar.
> Item resolvido SAI daqui — vai para o CHANGELOG (se foi entrega) e/ou para o log da sessão.
> Médio e longo prazo NÃO ficam aqui — ficam no ROADMAP.

---

## Versão Atual
**[0.4.3]** — 2026-09-05 — GUI (`main.py`) passa a usar o motor de matching v2. Removidos o `MotorMatching` embutido, a `REGEX_CODIGO` duplicada e os cinco utilitários atrasados; `ThreadVarredura` recebe `df`/`sufixos_cfg` por fora e consome o `Resultado` do motor. Conserta de quebra o `NameError` deixado pelo corte Parte A/Parte B da WO 0003 (`carregar_planilha` chamado sem import). `main.py` de 1458 para 1298 linhas.

## ✅ Funcionando
- **GUI usa o motor v2** — `main.py` importa `matching_engine.py` e `spreadsheet_loader.py` de `UTILITÁRIOS/`; nada de motor embutido restando (WO 0005, 2026-09-05).
- **Motor v2 modular (`matching_engine.py`)** — puro Python, sem PySide6, testável isoladamente.
- **Score ponderado (DEC-002)**: token_sort + WRatio + cobertura de tokens + medida como campo discriminante. Nota alta agora = semelhança real.
- **Medida como campo discriminante (DEC-005)**: bônus se coincide, **penalidade forte se diverge** (27 medidas distintas nos dados reais → discrimina de verdade).
- **Guarda de código ausente (DEC-006)**: arquivo com código de referência claro que não existe na planilha → NÃO casa (evita `39184`→`39182`). Só atua quando a planilha tem códigos.
- **Código não ancora em medidas**: `33X57`, `50MT²` excluídos da extração de código (corrige `61838`→`39182`).
- **Match por código bidirecional** (P1) — resolve `PR70671↔PR7067`, `R70181↔R7018`.
- **Sufixos compostos** (`(A)v2`) detectados e reescritos preservando ordem.
- **Golden set + harness** (`UTILITÁRIOS/test_matching.py`): **24/24 (100%)** contra a referência congelada `test/planilha_referencia.csv`. Roda **sem argumentos** e devolve código de erro (0/1/2) — ver DEC-008. Chave é o `Interno`, não o índice da linha.
- (Herdado da GUI, agora 0.4.3) carregamento CSV/XLSX, 5 ações, log+desfazer, sufixos configuráveis, persistência.

## 🔧 Em Progresso
- **Transparência do match na UI**: o motor já devolve `componentes` (scores parciais, código casado, estado da medida) e flag `ambiguo`, e desde a WO 0005 o `main.py` já carrega essas chaves no dicionário da correspondência — falta exibir na tabela (colunas novas + decisão de UX, WO 0006).

## ❌ Quebrado / Com Problema
- **Golden set pequeno (24 casos)**: cobre os casos críticos conhecidos, mas precisa crescer com a pasta real completa (164 pisos) e com outros grupos (louças) para medir generalização.
- **Pesos não calibrados formalmente**: os pesos atuais (`PesosScore`) passam no golden set, mas não foram otimizados; valores são razoáveis, não ótimos.

## 📋 Backlog (curto prazo — itens acionáveis)
- [ ] Exibir na tabela: componentes do score, código/token que casou, e alerta de ambiguidade (chaves já chegam ao dict desde a WO 0005 — falta só a UI, ver WO 0006).
- [ ] Expandir o golden set com a pasta real completa e com louças.
- [ ] Dois thresholds separados (exibição × seleção) na UI.
- [ ] Tornar `PesosScore` editável/persistível na aba Configurações.
- [ ] Decidir tratamento do `código_ausente` na UI: aba separada "Código não cadastrado"?
- [ ] **Confirmar a convenção de nome dos arquivos de imagem.** A coluna `Nome Imagem` passou de 3 campos (`MARCA - CÓDIGO - DESCRIÇÃO`) para 4 (`MARCA - INTERNO - CÓDIGO - DESCRIÇÃO`), mas os 24 nomes do golden set ainda são do formato de 3. Não sabemos se os arquivos reais do dono acompanharam. Se acompanharam, o golden set precisa de casos no formato novo. *[pergunta aberta, não medida]*
- [ ] **Rebaselinar o "auto-match 80/80".** Aquele número era contra um export de 80 linhas que não existe mais; a referência de hoje tem 119. Enquanto não for remedido, não citar 80/80 como estado atual.
- [ ] Ampliar o golden set com um caso de código de zero à esquerda cuja coluna de matching seja **puramente numérica** — a referência congelada usa `Nome Imagem`, que é texto e não exercita o FIX-005.

## 📁 Arquivos Críticos (não mexer sem contexto)
- `matching_engine.py` → coração do acerto v2. Ler CONTEXT «MOTOR DE MATCHING» + DEC-001/002/005/006 antes de tocar. Mudou? Rodar `test_matching.py` antes de aceitar.
- `main.py` → `ThreadAcao.run()` — operações destrutivas; ler FIX-002 antes de mexer.
- `golden_set.csv` → fonte de verdade dos testes; toda mudança no motor passa por ele.

## 💬 Última conversa
**Fecho (2026-09-05, sessão Code):** WO 0005 aplicada e fechada (`/apply-wo` + `/wrap`, mesma sessão) — commit `7199443`, push OK. Consertou de quebra o `NameError` que a Parte A da WO 0003 tinha deixado no `main.py` (chamava `carregar_planilha` sem importar) e completou a Parte B: GUI passa a importar `matching_engine.py`/`spreadsheet_loader.py` de `UTILITÁRIOS/`, removendo o `MotorMatching` embutido, a `REGEX_CODIGO` duplicada e os cinco utilitários atrasados (1458 → 1298 linhas). `ThreadVarredura` passa a receber `df`/`sufixos_cfg` por fora (o motor v2 não carrega pandas, DEC-002) e a consumir o `Resultado` do motor; sem-match por código ausente ganha a anotação `[código não cadastrado]`. Nove edições, todas as âncoras únicas, nenhum desvio. Validado: `pyflakes` 0 undefined-name, cinco contagens de sobra do motor antigo em 0, golden set 24/24, e teste manual dirigindo a `JanelaPrincipal` de verdade em modo offscreen — as 3 linhas do preview batem byte a byte com o esperado (incluindo o caso do sufixo composto `(A)v2` → `(Ambiente) _v2`, o risco mais traiçoeiro da WO) e o caso negativo caiu em sem-correspondência. **Correção de higiene:** a "Versão Atual" deste arquivo estava travada em `[0.4.0]` desde 2026-05-31, apesar do CHANGELOG já ter `[0.4.1]`/`[0.4.2]` registrados — corrigida para `[0.4.3]` nesta atualização. Transparência do match (`componentes`/`codigo_casado`/`ambiguo`) chega ao dict mas segue fora da UI, de propósito — é a WO 0006.

**Fecho (2026-09-04, sessão Code):** WO 0004 aplicada e fechada (`/apply-wo` + `/wrap`, mesma sessão). Passo 0 fechou em commit próprio a Parte A da WO 0003 que estava presa sem commit desde a sessão anterior — `39d3fb6` (FIX-005: leitura da planilha sempre como texto, loader único `spreadsheet_loader.py` usado pela GUI e pelo harness). Golden set rechaveado por `Interno` com referência congelada em `test/planilha_referencia.csv` e harness sem fallback silencioso — `8c677e6` (DEC-008). Harness volta a **24/24**, roda **sem argumentos** e devolve código de saída 0/1/2; os quatro casos de prova de vida (feliz, golden no formato antigo, coluna ausente, expectativa errada) bateram exatamente 0/2/2/1. **Achado:** o checklist da própria WO citava 15 casos `SEM_MATCH`; o medido foi 13, número que já era o total em HEAD antes da WO (mapeamento 1:1 preservado) — tratado como erro de redação da WO, não como regressão (ver relatório em arquivo). A Parte B da WO 0003 (motor v2 na GUI) segue **fora de escopo**, vira WO 0005.

**2026-09-03** — Migração para o contrato KCM v1.122.0 concluída e aplicada em disco pelo dono (ver DEC-007). Estrutura passou do layout flat antigo para `meta/` + `.claude/`; `CEREBRO.md` novo em v1.122.0 sem seção ASU; skills `apply-wo` e `wrap` adotadas; `HISTORICO.md` → `meta/HISTORY.md`. As linhas revogadas REV-2/REV-3/REV-4 morreram junto com o CEREBRO/CLAUDE antigos (substituição, não edição); o resíduo de REV-3 que sobrevivia neste arquivo foi corrigido por esta WO. Modo ASU desligado por decisão do dono. **Pendência de repositório [medido em 2026-09-03 22:30, `_MANIFEST_OAI.md`]:** a árvore tinha 10 modificados e 8 não rastreados sobre o commit `72f38c5`, com 5 arquivos de `meta/` fora do commit — confirmar `git add -A && git commit && git push` antes de abrir a próxima conversa **[RESOLVIDO em 2026-09-04, commit `b2d1c73`]**. Nenhuma linha de código foi tocada nesta conversa; o backlog de código segue intacto, com a integração do `matching_engine.py` na GUI como item 1.

**Fecho (2026-09-03, sessão Code):** WO 0001 aplicada — âncoras exatas, verificações 1-4 OK — e empurrada no commit `0658523` (apenas `meta/STATUS.md` + `meta/CONTEXT.md`). O log do dia ganhou a seção da Conversa 2 no mesmo commit de fecho. O resto da migração KCM (**resolvido em 2026-09-04**, commit `b2d1c73`) estava FORA deste commit e era o próximo gesto do dono: modificados `meta/CEREBRO.md` / `meta/CHANGELOG.md` / `meta/DECISIONS.md` / `meta/IDEAS.md`; deleções `meta/CLAUDE.md` / `meta/HISTORICO.md` / `meta/INSTRUCTION_GUIDE.md` / `meta/PROMPT_IA.md` / `meta/demo.yaml`; não rastreados `.claude/` / `.gitignore` / `.flatdropignore` / `CLAUDE.md` / `INSTRUCOES-DO-PROJETO.md` / `meta/HISTORY.md` / `meta/SPEC.md` / `meta/workorders/` — o fecho inclui colar `INSTRUCOES-DO-PROJETO.md` na caixa de instruções do Projeto.

**2026-09-04** — Fecho da migração KCM commitado (o passo que faltava desde 2026-09-03) e **triagem dos dois bugs órfãos da nota `260814-1021.txt`**: os dois têm a MESMA causa raiz, agora reproduzida — a planilha é carregada sem `dtype=str`, o pandas infere `int64` numa coluna numérica e come o zero à esquerda. Registrado em FIX-005. A correção NÃO foi aplicada nesta conversa de propósito: ela cai em `main.py` na mesma região que a integração do motor v2 vai refatorar, e fazer as duas de uma vez evita dois diffs conflitantes no mesmo arquivo. Nenhuma linha de código tocada. Próxima frente: integrar `matching_engine.py` na GUI **com** a correção da carga.

**2026-05-31 (2ª sessão)** — Construído o motor v2 modular, o golden set (24 casos reais) e o harness. Partindo de 54% → 100% no golden set após 3 correções fundamentadas: (1) excluir medidas da extração de código, (2) medida como campo discriminante com penalidade de divergência (DEC-005), (3) guarda de código ausente (DEC-006, decisão do usuário). Pesquisa de record linkage (Fellegi-Sunter) confirmou a abordagem field-weighted. **Correção importante recebida do usuário:** a ferramenta NÃO é só para pisos, e medidas NÃO são quase todas iguais (27 distintas em 80 linhas) — premissa minha estava errada, dados confirmaram. Próximo passo óbvio: integrar o motor v2 na GUI e exibir a transparência do match.
