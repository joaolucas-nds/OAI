# DECISIONS.md — Registro de Decisões

> Arquivo que **cresce devagar**. Guarda o PORQUÊ — o que o código sozinho não conta.
> Duas naturezas: **DEC** (decisões de arquitetura/design) e **FIX** (bugs graves resolvidos, para não repetir).
> Não reescreva entradas antigas; se uma decisão for substituída, marque «SUPERADA por DEC-N» e adicione a nova.
> Quando passar de ~700 linhas, mova as mais antigas para `DECISIONS-archive.md`.

---

## Como usar
Cada decisão recebe um ID sequencial (DEC-001, DEC-002…) e segue o formato ADR simplificado. Bugs graves usam FIX-001, FIX-002… com sintoma/causa/solução/lição.

---

## DEC-001 — Matching hierárquico: código antes de fuzzy
**Data:** 2026-05-31 · **Status:** aceita

### Contexto
Os nomes dos arquivos seguem o padrão `Marca - Código Referência - Descrição`, mas a descrição diverge da planilha (abreviações: RETAN vs RETANGULAR; BR vs BRANCO) e há sufixos de variação. Comparar só por nome (fuzzy) erra muito. O código de referência é a informação mais estável e única.

### Decisão
Matching em duas prioridades: (P1) tenta casar por código de referência extraído do nome; se acertar, confiança 100. (P2) só se P1 falhar, usa comparação aproximada por descrição.

### Alternativas consideradas
- **Só fuzzy** — simples, mas erra demais com abreviações e descrições parciais.
- **Só código** — não cobre arquivos sem código no nome (ex: `ROCHA FORTE - PISO BRIL RETIF HD 70070` sem código na planilha).

### Consequências
O acerto por código é praticamente perfeito quando o código existe nos dois lados. A qualidade do P2 (fuzzy) passa a importar só para a minoria de casos sem código — mas essa minoria ainda precisa funcionar bem (ver DEC-002).

---

## DEC-002 — Reescrever o scoring fuzzy (abandonar token_set_ratio puro)
**Data:** 2026-05-31 · **Status:** aceita (implementação pendente — motor v2)

### Contexto
Relato do usuário: "o fuzzy está dando alto valor para pouca semelhança". Investigado nesta sessão. Causa raiz confirmada na documentação oficial do RapidFuzz: `token_set_ratio` retorna **100 sempre que uma string é subconjunto da outra**, independentemente de quanto texto extra exista na maior. Ex: `token_set_ratio("fuzzy was a bear but not a dog", "fuzzy was a bear") == 100`. Aplicado ao nosso caso, um nome de arquivo curto/genérico (poucos tokens) que apareça dentro de uma entrada longa da planilha ganha ~100, gerando falsos positivos com altíssima confiança.

### Decisão
No motor v2, abandonar `token_set_ratio` como scorer único. Adotar **score ponderado** combinando:
- `token_sort_ratio` (sensível a conteúdo extra, não infla com subconjunto) como base;
- `WRatio` (escolhe estratégia conforme razão de comprimento) como reforço;
- **penalização por diferença de comprimento de tokens** (quanto mais tokens da planilha ficam "sem par", menor o score), para matar o efeito subconjunto;
- bônus quando dimensões/medidas (ex: `70X70`, `32X62`) coincidem.
Threshold de seleção e threshold de exibição passam a ser separados.

### Alternativas consideradas
- **Manter token_set_ratio e só subir o threshold** — não resolve: o problema é nota 100 falsa, subir corte não distingue verdadeiro de falso 100.
- **TF-IDF + similaridade de cosseno** — robusto para catálogos, penaliza tokens comuns (PISO, CX, RETIF aparecem em tudo) e valoriza tokens raros (o modelo/medida). Mais poderoso, porém mais complexo e mais pesado. Fica registrado como evolução possível (ver IDEAS), não para o v2 imediato.
- **token_sort_ratio sozinho** — melhor que set, mas não pondera tokens comuns nem aproveita medidas; insuficiente isolado.

### Consequências
Acerto do fuzzy deve subir e — mais importante — os scores passam a ser confiáveis (nota alta = semelhança real), o que torna o threshold significativo. Exige a suíte de testes (golden set) para validar sem regressão. Aumenta um pouco a complexidade do motor, reforçando a necessidade de separá-lo da GUI (ROADMAP F2).

---

## DEC-003 — GUI em abas + 2 QThreads
**Data:** 2026-05-31 · **Status:** aceita

### Contexto
Varredura de pastas grandes e operações de arquivo em massa travariam a interface se rodassem na thread principal.

### Decisão
Interface em abas (Correspondências / Sem correspondência / Configurações / Log). Varredura+matching em `ThreadVarredura`; ações de arquivo em `ThreadAcao`. Sinais Qt comunicam progresso/resultados.

### Alternativas consideradas
- **Tudo na thread principal** — congela a UI; inviável.
- **CustomTkinter** (sugerido por outras IAs) — interface mais "moderna" out-of-the-box, mas PySide6 oferece tabela editável, threads e sinais nativos mais robustos para este caso.

### Consequências
UI responsiva. Custo: cuidado com acesso a widgets fora da thread principal (só via sinais).

---

## DEC-004 — Sufixos de variação configuráveis e persistidos
**Data:** 2026-05-31 · **Status:** aceita

### Contexto
O usuário cria variações marcando o fim do nome: `(A)` para ambiente, `v2` para segunda imagem, `face 2`, etc. Esses marcadores não podem entrar no matching (viram ruído) nem ser perdidos. E o usuário quer liberdade de reescrevê-los (`(A)`→`(Ambiente)` ou `_ambiente`, conforme preferir).

### Decisão
Tabela editável de sufixos (detectar → reescrever) na aba Configurações, salva em `config.json`. `separar_sufixos()` destaca o sufixo antes do match; `reescrever_sufixo()` recoloca o formato escolhido depois.

### Alternativas consideradas
- **Lista fixa no código** — sem liberdade; cada mudança exigiria editar o fonte.
- **Detecção automática de variação** — frágil e imprevisível; o usuário prefere controle explícito.

### Consequências
Liberdade total de mapeamento sem tocar no código. O match acontece na base limpa, melhorando o acerto dos pares produto/ambiente.

---

## FIX-001 — Match por código falhava em códigos "encurtados" na planilha
**Data:** 2026-05-31

- **Sintoma:** arquivos como `ROCHA FORTE - PR70671 - ...` e `ROCHA FORTE - R70181 - ...` não eram movidos/renomeados; ficavam sem match apesar de existir a linha correta na planilha.
- **Causa raiz:** a planilha tinha o código encurtado (`PR7067`, `R7018`) e o arquivo o completo (`PR70671`, `R70181`). O código só verificava `cod_arq in cod_plan` (um sentido). O caso real era o inverso: `cod_plan in cod_arq`.
- **Solução:** comparação **bidirecional** — match exato OU `cod_plan in cod_arq` OU `cod_arq in cod_plan` (com guarda de comprimento mínimo 4 para evitar casar fragmentos curtos). Preferência pelo código mais longo (mais específico).
- **Lição:** códigos de fabricante não são estáveis em comprimento entre sistemas; nunca assumir direção da continência. Virou armadilha #4 em CONTEXT.

---

## FIX-002 — `renomear_copiar`/`renomear_mover` copiavam arquivo sobre si mesmo
**Data:** 2026-05-31

- **Sintoma:** ao escolher renomear+copiar sem pasta base de destino definida, a operação tentava copiar o arquivo para a própria pasta com o mesmo nome — gerando erro ou duplicata indevida (`_01`).
- **Causa raiz:** a lógica não verificava se a pasta de destino final era a mesma do arquivo já renomeado in-place.
- **Solução:** após renomear in-place, só copiar/mover se `pasta_final.resolve() != origem.parent.resolve()`. Em "copiar" puro, se destino resolve para a origem, anexa `_copia` ao nome.
- **Lição:** operações compostas (renomear+X) precisam tratar o caso degenerado em que X não tem para onde ir. Virou armadilha #5 em CONTEXT.

---

## FIX-003 — Combos e slider sobrepostos na barra superior
**Data:** 2026-05-31

- **Sintoma:** rótulos das caixas de seleção de coluna e do Threshold ficavam sobrescritos pelos próprios controles em larguras menores de janela.
- **Causa raiz:** todos os controles empilhados numa única `QHBoxLayout` sem largura fixa de rótulo, comprimindo tudo.
- **Solução:** agrupar em `QGroupBox("Mapeamento de colunas")` com duas sub-linhas; `setFixedWidth` nos rótulos; `setMinimumWidth` nos combos.
- **Lição:** em PySide6, layouts horizontais densos precisam de larguras fixas nos rótulos ou quebram em telas estreitas. Virou armadilha #6 em CONTEXT.

---

## DEC-005 — Medida (dimensão) como campo discriminante, não como bônus fraco
**Data:** 2026-05-31 · **Status:** aceita

### Contexto
Na 1ª versão do motor v2, a medida (`70X70`, `32X62`) entrava só como bônus pequeno quando coincidia. Suposição inicial (errada) do assistente: "quase todo piso tem a mesma medida, então medida é ruído". O usuário corrigiu: (1) a ferramenta não é só para pisos; (2) os pisos NÃO têm quase a mesma medida. Análise dos dados reais confirmou o usuário: **27 medidas distintas em 80 linhas**, a mais comum (70X70) em apenas 11. Medida tem poder discriminante real.

### Decisão
Tratar medida como **campo discriminante** no estilo record linkage (Fellegi-Sunter): quando ambos os lados têm medida, coincidência dá bônus (+6) e **divergência dá penalidade forte (−25)**. A penalidade é o que de fato separa produtos de descrição parecida mas formato diferente (ex: um `33X57` não casa com um `70X70` só porque compartilham "PISO BOLD HD").

### Alternativas consideradas
- **Bônus só na coincidência (sem penalidade)** — não discrimina: dois produtos diferentes de mesma família ainda casavam alto.
- **Remover medida do score** — descartado; jogaria fora um discriminador comprovadamente forte.
- **TF-IDF tratando medida como token** — daria peso por raridade automaticamente; mais robusto porém mais pesado. Fica para F4 (já em IDEAS).

### Consequências
Score passou a separar corretamente produtos de mesma família e formato diferente. Penalidade calibrada empiricamente (−25) contra o golden set; não é ótimo formal. Pesos ficam em `PesosScore` (dataclass), prontos para virar config editável.

---

## DEC-006 — Guarda de código ausente: código claro sem par na planilha NÃO casa por fuzzy
**Data:** 2026-05-31 · **Status:** aceita (decisão do usuário)

### Contexto
Arquivos com código de referência claro cujo código não existe em nenhuma linha da planilha (ex: `39184` quando a planilha tem `39182`; `PR40201` quando há `PR4011`). O fuzzy "resgatava" com a linha de nome mais parecido — mas é outro produto (1 dígito de diferença no código, 1 palavra na descrição). Falso positivo de alta confiança.

### Decisão
Quando o arquivo TEM código de referência (não-medida) e esse código não casa com nenhum da planilha, retornar `código_ausente` (sem match) em vez de cair no fuzzy. **Guarda condicional:** só atua se a planilha tem códigos em geral; se o catálogo é descrição-pura (nenhuma linha tem código), o fuzzy roda normalmente. Caso `R70031`: o código `R70031` não existe, mas o modelo `70070` (presente no arquivo e na linha 59 sem código de referência) ancora corretamente via P1 — então a linha 59 casa por código de modelo, não é bloqueada.

### Alternativas consideradas
- **Casar por fuzzy normalmente** — gera os falsos positivos `39184→39182`; rejeitado pelo usuário.
- **Casar mas marcar "ambíguo/revisar"** — opção intermediária; o usuário preferiu não casar (produto não cadastrado é informação útil por si).

### Consequências
Acaba com a classe de falso positivo "código quase igual". Arquivos de produtos não cadastrados vão para "sem correspondência" — sinal útil de catálogo incompleto. Risco: se o usuário digitar o código errado no arquivo, vai para sem-match em vez de casar pela descrição (aceitável; erro de digitação no código é raro e revisável). Na UI, considerar aba/filtro separado para `código_ausente` (backlog).

---

## FIX-004 — Código de referência ancorando em dimensões/medidas
**Data:** 2026-05-31

- **Sintoma:** `ROCHA FORTE - 61838 - ... 33X57` casava (confiança 100) com `ROCHA FORTE - 39182 - ... 33X57`, produtos diferentes. Idem `789669`→`39182`.
- **Causa raiz:** `extrair_codigos` capturava `33X57` e `50MT` (de `2,50MT²`) como se fossem códigos de referência; a comparação bidirecional então casava qualquer par que compartilhasse a mesma medida.
- **Solução:** excluir de `extrair_codigos` tudo que seja medida (`extrair_medidas`), fragmento de medida (`\d{2}MT\d*`) ou dimensão isolada (`\d{1,3}X\d{1,3}`). Medida passou a ser tratada só como campo discriminante (DEC-005), nunca como âncora de código.
- **Lição:** a regex de código é permissiva por necessidade (códigos têm formatos variados); por isso precisa de uma lista de exclusão explícita para tokens que PARECEM código mas são dimensão. Virou armadilha #8 em CONTEXT.

---

## DEC-007 — Migração para o contrato KCM v1.122.0 (layout meta/ + modo Code)
**Data:** 2026-09-03 · **Status:** aceita

### Contexto
O projeto estava no layout flat antigo do KCM (pré-v1.90): todos os `.md` na raiz, um `CLAUDE.md` que era na verdade o CEREBRO (comportamento), sem `.claude/` nem `meta/`. Chegou o template-update v1.122.0 com o contrato novo.

### Decisão
Migração completa para o contrato atual:
1. **`CLAUDE.md` antigo (= CEREBRO antigo) descartado** e substituído. Varredura confirmou que continha 100% regra genérica do KCM — nenhum princípio/decisão personalizado do projeto. As convenções que tinha já vivem no CONTEXT (específicas) e no CEREBRO novo (genéricas refinadas).
2. **`meta/CEREBRO.md`** (novo) assume o comportamento do assistente; **`CLAUDE.md`** (raiz, novo) assume o papel de guia raiz do Claude Code — necessário porque o Claude Code exige `CLAUDE.md` na raiz.
3. **`HISTORICO.md` → `meta/HISTORY.md`** (renomeação do contrato novo).
4. **Demais docs vivos** (CONTEXT, STATUS, DECISIONS, CHANGELOG, IDEAS, ROADMAP, GLOSSARY) preservados integralmente, reposicionados em `meta/`.
5. **Modo Code ligado** (skills `apply-wo` e `wrap` adotadas); **ASU desligado** (removido; projeto com Code não usa ASU).

### Linhas revogadas eliminadas por substituição
REV-2 (bloco git pronto para copiar), REV-3 (par sessão/turno), REV-4 (nunca blocos soltos) viviam no CLAUDE.md/CEREBRO antigos — morreram com o descarte, sem edição manual. A varredura por fato confirmou que não se espalharam para outros arquivos vivos, exceto como relato histórico (preservado). REV-1 (esperar sinal de upload) não estava presente.

### Carimbo de modos
Detectada SOBRA do modo ASU (marcador `## Saída de código via ASU (patch)` presente no CEREBRO antigo com ASU declarado `não`). Eliminada na substituição — o CEREBRO novo nasce sem a seção.

### Pendências de limpeza (decisão do usuário)
Artefatos do ASU no repo antigo — `INSTRUCTION_GUIDE.md`, `PROMPT_IA.md`, `demo.yaml` — ficam fora de `meta/`. Candidatos a remoção já que o ASU foi desativado; confirmar se algum tem valor de referência antes de apagar.

### Consequências
Estrutura alinhada ao KCM v1.122.0. Os 4 carimbos de versão conferem em v1.122.0. Próximo trabalho já roda sob o contrato novo (ritual por turno, modo Code com WOs).

---

## FIX-005 — Zero à esquerda comido na carga da planilha (dois sintomas, uma causa)
**Data:** 2026-09-04 · **Status:** causa raiz identificada e reproduzida; correção ainda NÃO aplicada

- **Sintoma** *[relatado pelo dono — nota `260814-1021.txt`, 2026-08-14]*: (a) quando o nome escolhido para renomear começa com `0`, o zero some do nome final; (b) um match cujo código tem `00` (dois zeros seguidos) foi ignorado.
- **Causa raiz** *[medido por instrumento — reprodução determinística com pandas 3.0.2 em 2026-09-04]*: a planilha é carregada **sem `dtype=str`** (`main.py:1300` `read_csv`, `main.py:1305` `read_excel`, `test_matching.py:31` `read_csv`). Coluna cujos valores são todos numéricos é inferida como `int64`, e `00611` vira `611` **antes** de qualquer `str()` ou `.astype(str)` do código. Os dois sintomas são o mesmo defeito visto em duas colunas diferentes.
- **Como (a) acontece:** a coluna do NOVO NOME é numérica → o valor já chega degradado em `main.py:377` (`str(linha[self.col_novo_nome])`) → o arquivo é renomeado para `611`.
- **Como (b) acontece:** a coluna de MATCHING é numérica → a linha passa a valer `611`, que tem 3 caracteres e **não casa com `REGEX_CODIGO`** (`\b([A-Za-z]{0,4}\d[\dA-Za-z]{3,})\b` exige 4+). A linha fica com **zero códigos**; o arquivo tem `00611`; não há match por código; no motor v2 a guarda DEC-006 devolve `código_ausente` e o produto é ignorado. No motor antigo do `main.py` a contenção também falha (`len(cod_plan) >= 4` barra `611`) e sobra um fuzzy fraco contra a string `611`, abaixo do threshold.
- **Por que o golden set não pegou:** `test_matching.py` casa contra a coluna `"Atual: 14/04/2026 - Anterior: 14/04/2026"`, cujos valores contêm texto — o pandas a lê como string e o zero sobrevive. O defeito só aparece com coluna **puramente numérica**, que é a configuração do dono na GUI. O harness tem o mesmo defeito de leitura e o exporia se o golden set exercitasse uma coluna de código pura.
- **Correção prevista** (vai junto com a integração do motor v2 na GUI, para não editar `main.py` duas vezes): carregar com `dtype=str` **e** `keep_default_na=False`, num **único ponto compartilhado** pela GUI e pelo harness — hoje são duas cópias que já divergiram (`sep` detectado à mão × `sep=None`) e que voltariam a divergir.
- **Efeito colateral que a mesma correção resolve:** `main.py:377` faz `str(linha[self.col_novo_nome])` sem `fillna` — célula vazia vira `NaN` e o nome sai com o literal `nan`. `keep_default_na=False` mata essa classe inteira.
- **Risco da correção:** nenhum. *[medido — varredura de `main.py` em 2026-09-04]* nenhuma coluna do DataFrame é usada como número; as únicas leituras são `df[col_matching].fillna("").astype(str)` (241), `str(linha[self.col_novo_nome])` (377) e `str(linha[self.col_pasta_destino]).strip()` (393).
- **O que NÃO está provado:** não tenho a planilha real do dono, então qual coluna ele tinha selecionado ao ver cada sintoma é *dedução*, não medição. A causa raiz está reproduzida; o mapeamento sintoma→coluna é a explicação mais econômica que cobre os dois relatos.
- **Lição:** planilha é TEXTO. A inferência de tipo do pandas é uma armadilha silenciosa em qualquer coluna que seja identificador — não dá erro, não avisa, e o dano só aparece no nome do arquivo final. Vira armadilha em `CONTEXT.md` **junto com a correção**, não antes.
