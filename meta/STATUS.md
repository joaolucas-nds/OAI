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

## 📋 Backlog (curto prazo — itens acionáveis)
- [ ] Integrar `matching_engine.py` na GUI (`main.py`), removendo o `MotorMatching` embutido.
- [ ] Exibir na tabela: componentes do score, código/token que casou, e alerta de ambiguidade (flag já existe).
- [ ] Expandir o golden set com a pasta real completa e com louças.
- [ ] Dois thresholds separados (exibição × seleção) na UI.
- [ ] Tornar `PesosScore` editável/persistível na aba Configurações.
- [ ] Decidir tratamento do `código_ausente` na UI: aba separada "Código não cadastrado"?

## 📁 Arquivos Críticos (não mexer sem contexto)
- `matching_engine.py` → coração do acerto v2. Ler CONTEXT «MOTOR DE MATCHING» + DEC-001/002/005/006 antes de tocar. Mudou? Rodar `test_matching.py` antes de aceitar.
- `main.py` → `ThreadAcao.run()` — operações destrutivas; ler FIX-002 antes de mexer.
- `golden_set.csv` → fonte de verdade dos testes; toda mudança no motor passa por ele.

## 💬 Última Sessão
**2026-05-31 (2ª sessão)** — Construído o motor v2 modular, o golden set (24 casos reais) e o harness. Partindo de 54% → 100% no golden set após 3 correções fundamentadas: (1) excluir medidas da extração de código, (2) medida como campo discriminante com penalidade de divergência (DEC-005), (3) guarda de código ausente (DEC-006, decisão do usuário). Pesquisa de record linkage (Fellegi-Sunter) confirmou a abordagem field-weighted. **Correção importante recebida do usuário:** a ferramenta NÃO é só para pisos, e medidas NÃO são quase todas iguais (27 distintas em 80 linhas) — premissa minha estava errada, dados confirmaram. Próximo passo óbvio: integrar o motor v2 na GUI e exibir a transparência do match.
