# IDEAS.md — Brainstorm e Visão

> **Segundo cérebro** do projeto. Captura TUDO que for mencionado, mesmo solto ou no meio de outro assunto.
> Nunca perde: ideia implementada vai para «Concluídas»; ideia recusada vai para «Descartadas» com o motivo.
> Separar por autor (você × assistente) ajuda a lembrar de onde veio cada coisa.

---

## 💡 Ideias Ativas — Usuário
### 2026-05 — Duplicação controlada em múltiplos destinos
Renomear por uma coluna, copiar para pasta por material, e depois mover para outra pasta por marca — liberdade de encadear ações sobre o mesmo arquivo. Aceito como caso de uso legítimo (log registra todos os destinos). Parcialmente atendido pelas 5 ações; falta um modo "encadear ações" numa só passada.

### 2026-05 — Organização "flat" por GRUPO + busca por filtro
Em vez de pastas profundas (marca→tipo→…), jogar tudo numa pasta por GRANDE GRUPO (PISOS, LOUÇAS) e achar por filtro de nome. O nome `Marca - Código - Descrição` já ordena por marca. Influencia o design: pasta-destino é opcional e rasa, não hierárquica.

### 2026-05 — ID interno como "caixa" de metadados dos arquivos
Desejo de marcar todos os arquivos de um produto com o código interno do sistema (não no nome), para achar tudo de um produto de uma vez. Esbarra na limitação do Windows (não há campo de metadado fácil/portável). Ideia em aberto — possível via sidecar (`.json`/`.txt` por arquivo) ou tag NTFS (frágil). Não decidido.

### 2026-05 — Limpeza dos marcadores `* # +` na origem
O usuário pretende remover os marcadores de descontinuado da planilha/arquivos mais tarde. Enquanto não remove, a ferramenta já os ignora (`limpar_valor_planilha`).

### 2026-05 — Testes e exemplos para aprimorar acerto
Reconhecimento de que o matching vai precisar de casos reais para calibrar. Vira base do golden set (ver ROADMAP F2).

### 2026-05 — Tratamento rico de variações de piso
Pisos têm imagem do produto + imagem de ambiente `(A)`, às vezes múltiplos ambientes, e `v2` tanto do piso quanto do ambiente, além de variação de face. A ferramenta precisa preservar e reescrever todas essas variações com liberdade. Parcialmente atendido pelo sistema de sufixos; combinações (ex: `(A)v2`) podem precisar de regra composta.

---

## 🤖 Ideias Ativas — Assistente
### 2026-05-31 — Scoring por TF-IDF + cosseno (evolução do fuzzy)
Tokens como PISO, CX, RETIF, MT² aparecem em quase todas as linhas e não ajudam a distinguir; o modelo/medida (`32HDA60`, `70X70`) é que discrimina. TF-IDF dá peso baixo ao comum e alto ao raro; cosseno mede semelhança ignorando ordem. Mais robusto que qualquer scorer do RapidFuzz para catálogo. Registrado como evolução pós-v2 (o v2 usa score ponderado mais simples primeiro).

### 2026-05-31 — Mostrar o "porquê" do match na tabela
Exibir qual código/token casou e o score parcial de cada componente. Transparência ajuda o usuário a confiar (ou desconfiar) e a calibrar o threshold.

### 2026-05-31 — Alerta de ambiguidade
Quando duas linhas da planilha têm score muito próximo para o mesmo arquivo, acender sinal (a "luz amarela" que o usuário mencionou) e pedir decisão manual em vez de escolher silenciosamente.

### 2026-05-31 — Threshold de exibição ≠ threshold de seleção
Mostrar matches fracos (para revisão) sem selecioná-los automaticamente. Dois controles separados.

### 2026-05-31 — Golden set versionado
Guardar pares (nome_arquivo → linha_esperada) num CSV de teste para medir % de acerto a cada mudança no motor. Permite evoluir sem regressão.

### 2026-05-31 — Modularizar: motor de matching sem PySide6
Separar `matching_engine.py` (puro Python, testável) de `gui.py`. Hoje tudo é um monólito de ~1400 linhas; isso bloqueia testes unitários do que mais importa.

### 2026-05-31 — Modo "encadear ações" numa passada
UI para definir uma sequência (renomear → copiar p/ material → mover p/ marca) e executar de uma vez, com log de todos os destinos. Atende diretamente a ideia de duplicação controlada do usuário.

### 2026-05-31 — Normalização de sinônimos/abreviações
Dicionário configurável: RETAN→RETANGULAR, BR→BRANCO, POL→POLIDO. Expandir abreviações antes do fuzzy aumenta o acerto sem inflar score.

### 2026-05-31 (2ª sessão) — Medida como campo discriminante com penalidade
Validado nos dados: 27 medidas distintas em 80 linhas. Medida divergente penaliza forte o score — separa produtos de mesma família e formato diferente. Implementado (DEC-005).

### 2026-05-31 (2ª sessão) — Guarda de código ausente
Código de referência claro sem par na planilha = produto não cadastrado → não casar. Decisão do usuário (DEC-006). Ideia derivada: na UI, aba/filtro "Código não cadastrado" separado de "sem correspondência" genérico.

### 2026-05-31 (2ª sessão) — Calibração formal de pesos (futuro)
Os pesos de `PesosScore` passam no golden set mas não são ótimos. Com um golden set maior, dá para fazer busca em grade (grid search) ou otimização para achar os pesos que maximizam acerto. Vira possível tarefa quando o golden set crescer.

### 2026-05-31 (2ª sessão) — UX de revisão (pesquisa)
Padrões coletados: barra de ações contextual flutuante ao selecionar linhas (Jira/ClickUp), colunas-âncora fixas (pinned) ao rolar horizontalmente, edição inline com confirmação clara, feedback visual + undo para operações em massa. Aplicar quando reformar a GUI.

---

## ✅ Concluídas
> Ideia que virou realidade. Mantida aqui para histórico (com referência à versão/decisão).
- **Match hierárquico código→fuzzy** — implementado / ver DEC-001.
- **Sufixos configuráveis e persistidos** — implementado em 0.3.x / ver DEC-004.
- **Match por código bidirecional** — implementado em 0.3.1 / ver FIX-001.
- **Ignorar `* # +` da planilha** — implementado em 0.3.1.
- **5 ações de arquivo com preview e log** — implementado / ver DEC-003.
- **Modularizar: motor de matching sem PySide6** — implementado em 0.4.0 (`matching_engine.py`) / ROADMAP F2.
- **Golden set versionado + harness** — implementado em 0.4.0 (`golden_set.csv`, `test_matching.py`) / ROADMAP F2.
- **Score ponderado substituindo token_set_ratio** — implementado em 0.4.0 / ver DEC-002, DEC-005.

---

## 🚫 Descartadas
> Ideia avaliada e recusada. O motivo evita reabrir a discussão depois.
- **`token_set_ratio` como scorer principal** — descartado porque retorna 100 para subconjuntos, inflando score de pouca semelhança (DEC-002).
- **Hierarquia de pastas por marca** — descartada porque o nome já ordena por marca alfabeticamente; pastas profundas atrapalham o fluxo do usuário.
- **Atalhos `.lnk` em vez de duplicar** — descartado para este caso porque os arquivos são abertos em outros programas (ex: Figma) que não tratam atalho como o arquivo real.
- **CustomTkinter como framework de UI** — descartado em favor de PySide6 (tabela editável, threads e sinais mais robustos) — ver DEC-003.
