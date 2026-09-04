# STATUS.md — Estado Atual

> Arquivo **rolante**: descreve só o AGORA. O assistente lê no início para saber onde retomar.
> Item resolvido SAI daqui — vai para o CHANGELOG (se foi entrega) e/ou para o log da sessão.
> Médio e longo prazo NÃO ficam aqui — ficam no ROADMAP.

---

## Versão Atual
**[0.4.0]** — 2026-05-31 — motor de matching v2 modular e testável (`matching_engine.py`), separado da GUI. Score ponderado substitui o `token_set_ratio`. Golden set de 24 casos reais passa 100%. GUI 0.3.1 ainda não integrada ao motor v2.

## ✅ Funcionando
- **Motor v2 modular (`matching_engine.py`)** — puro Python, sem PySide6, testável isoladamente.
- **Score ponderado (DEC-002)**: token_sort + WRatio + cobertura de tokens + medida como campo discriminante. Nota alta agora = semelhança real.
- **Medida como campo discriminante (DEC-005)**: bônus se coincide, **penalidade forte se diverge** (27 medidas distintas nos dados reais → discrimina de verdade).
- **Guarda de código ausente (DEC-006)**: arquivo com código de referência claro que não existe na planilha → NÃO casa (evita `39184`→`39182`). Só atua quando a planilha tem códigos.
- **Código não ancora em medidas**: `33X57`, `50MT²` excluídos da extração de código (corrige `61838`→`39182`).
- **Match por código bidirecional** (P1) — resolve `PR70671↔PR7067`, `R70181↔R7018`.
- **Sufixos compostos** (`(A)v2`) detectados e reescritos preservando ordem.
- **Golden set + harness** (`test_matching.py`): 24/24 (100%) e auto-match 80/80.
- (Herdado da GUI 0.3.1) carregamento CSV/XLSX, 5 ações, log+desfazer, sufixos configuráveis, persistência.

## 🔧 Em Progresso
- **Integração motor v2 ↔ GUI**: a GUI (`main.py` 0.3.1) ainda usa o `MotorMatching` antigo embutido. Próximo passo é trocar pela importação do `matching_engine.py`.
- **Transparência do match na UI**: o motor já devolve `componentes` (scores parciais, código casado, estado da medida) e flag `ambiguo` — falta exibir na tabela.

## ❌ Quebrado / Com Problema
- **GUI ainda no motor antigo**: enquanto não integrar, a interface não se beneficia do score ponderado nem da guarda de código ausente.
- **Golden set pequeno (24 casos)**: cobre os casos críticos conhecidos, mas precisa crescer com a pasta real completa (164 pisos) e com outros grupos (louças) para medir generalização.
- **Pesos não calibrados formalmente**: os pesos atuais (`PesosScore`) passam no golden set, mas não foram otimizados; valores são razoáveis, não ótimos.
- **Zero à esquerda comido na carga da planilha (FIX-005)**: `read_csv`/`read_excel` sem `dtype=str` convertem coluna numérica em `int64` e `00611` vira `611`. Quebra o novo nome **e** mata o match por código (`611` tem 3 chars e nem casa com a regex, então a linha fica sem código e o produto é ignorado). Causa raiz reproduzida em 2026-09-04; atinge `main.py` e `test_matching.py`. Correção vai junto com a integração do motor na GUI.

## 📋 Backlog (curto prazo — itens acionáveis)
- [ ] Integrar `matching_engine.py` na GUI (`main.py`), removendo o `MotorMatching` embutido.
- [ ] Exibir na tabela: componentes do score, código/token que casou, e alerta de ambiguidade (flag já existe).
- [ ] Expandir o golden set com a pasta real completa e com louças.
- [ ] Dois thresholds separados (exibição × seleção) na UI.
- [ ] Tornar `PesosScore` editável/persistível na aba Configurações.
- [ ] Decidir tratamento do `código_ausente` na UI: aba separada "Código não cadastrado"?
- [ ] Corrigir a carga da planilha (FIX-005): `dtype=str` + `keep_default_na=False` num loader único usado pela GUI e pelo harness. Vai junto com a integração do motor.
- [ ] Ampliar o golden set com um caso de código de zero à esquerda contra uma coluna de código **pura** — a coluna descritiva usada hoje esconde o defeito.

## 📁 Arquivos Críticos (não mexer sem contexto)
- `matching_engine.py` → coração do acerto v2. Ler CONTEXT «MOTOR DE MATCHING» + DEC-001/002/005/006 antes de tocar. Mudou? Rodar `test_matching.py` antes de aceitar.
- `main.py` → `ThreadAcao.run()` — operações destrutivas; ler FIX-002 antes de mexer.
- `golden_set.csv` → fonte de verdade dos testes; toda mudança no motor passa por ele.

## 💬 Última conversa
**2026-09-03** — Migração para o contrato KCM v1.122.0 concluída e aplicada em disco pelo dono (ver DEC-007). Estrutura passou do layout flat antigo para `meta/` + `.claude/`; `CEREBRO.md` novo em v1.122.0 sem seção ASU; skills `apply-wo` e `wrap` adotadas; `HISTORICO.md` → `meta/HISTORY.md`. As linhas revogadas REV-2/REV-3/REV-4 morreram junto com o CEREBRO/CLAUDE antigos (substituição, não edição); o resíduo de REV-3 que sobrevivia neste arquivo foi corrigido por esta WO. Modo ASU desligado por decisão do dono. **Pendência de repositório [medido em 2026-09-03 22:30, `_MANIFEST_OAI.md`]:** a árvore tinha 10 modificados e 8 não rastreados sobre o commit `72f38c5`, com 5 arquivos de `meta/` fora do commit — confirmar `git add -A && git commit && git push` antes de abrir a próxima conversa **[RESOLVIDO em 2026-09-04, commit `b2d1c73`]**. Nenhuma linha de código foi tocada nesta conversa; o backlog de código segue intacto, com a integração do `matching_engine.py` na GUI como item 1.

**Fecho (2026-09-03, sessão Code):** WO 0001 aplicada — âncoras exatas, verificações 1-4 OK — e empurrada no commit `0658523` (apenas `meta/STATUS.md` + `meta/CONTEXT.md`). O log do dia ganhou a seção da Conversa 2 no mesmo commit de fecho. O resto da migração KCM (**resolvido em 2026-09-04**, commit `b2d1c73`) estava FORA deste commit e era o próximo gesto do dono: modificados `meta/CEREBRO.md` / `meta/CHANGELOG.md` / `meta/DECISIONS.md` / `meta/IDEAS.md`; deleções `meta/CLAUDE.md` / `meta/HISTORICO.md` / `meta/INSTRUCTION_GUIDE.md` / `meta/PROMPT_IA.md` / `meta/demo.yaml`; não rastreados `.claude/` / `.gitignore` / `.flatdropignore` / `CLAUDE.md` / `INSTRUCOES-DO-PROJETO.md` / `meta/HISTORY.md` / `meta/SPEC.md` / `meta/workorders/` — o fecho inclui colar `INSTRUCOES-DO-PROJETO.md` na caixa de instruções do Projeto.

**2026-09-04** — Fecho da migração KCM commitado (o passo que faltava desde 2026-09-03) e **triagem dos dois bugs órfãos da nota `260814-1021.txt`**: os dois têm a MESMA causa raiz, agora reproduzida — a planilha é carregada sem `dtype=str`, o pandas infere `int64` numa coluna numérica e come o zero à esquerda. Registrado em FIX-005. A correção NÃO foi aplicada nesta conversa de propósito: ela cai em `main.py` na mesma região que a integração do motor v2 vai refatorar, e fazer as duas de uma vez evita dois diffs conflitantes no mesmo arquivo. Nenhuma linha de código tocada. Próxima frente: integrar `matching_engine.py` na GUI **com** a correção da carga.

**2026-05-31 (2ª sessão)** — Construído o motor v2 modular, o golden set (24 casos reais) e o harness. Partindo de 54% → 100% no golden set após 3 correções fundamentadas: (1) excluir medidas da extração de código, (2) medida como campo discriminante com penalidade de divergência (DEC-005), (3) guarda de código ausente (DEC-006, decisão do usuário). Pesquisa de record linkage (Fellegi-Sunter) confirmou a abordagem field-weighted. **Correção importante recebida do usuário:** a ferramenta NÃO é só para pisos, e medidas NÃO são quase todas iguais (27 distintas em 80 linhas) — premissa minha estava errada, dados confirmaram. Próximo passo óbvio: integrar o motor v2 na GUI e exibir a transparência do match.
