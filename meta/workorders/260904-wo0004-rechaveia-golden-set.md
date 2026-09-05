# WO 0004 — Fecha a Parte A (FIX-005) e rechaveia o golden set por codigo interno

> **Tipo:** mista — codigo/teste + registro nos `meta/`.
> **Config sugerida:** modelo capaz, `/effort` medio. As edicoes sao substituicoes de arquivo inteiro e appends ancorados; o julgamento pesado ja foi feito e medido no chat.
> **Pre-requisito:** HEAD `efcdf3d`, `origin/main` sincronizado, e a **Parte A da WO 0003 aplicada na arvore de trabalho e NAO commitada** (`main.py` e `UTILITÁRIOS/test_matching.py` modificados, `.claude/settings.json` modificado, `UTILITÁRIOS/spreadsheet_loader.py` nao rastreado). Se a arvore estiver limpa, a Parte A ja foi commitada por alguem: **PARE e reporte**.
> **Base:** relatorio `260904-1725-code-oai.txt` (WO 0003 parada apos a Parte A) + sonda determinística rodada no chat em 2026-09-04 sobre os tres exports do dono.
> **Depende de:** WO 0003, Parte A (aplicada, sem commit). A **Parte B da WO 0003 continua pendente** e nao entra aqui — ela volta na WO 0005, agora com um harness capaz de valida-la.
> **Ancora semantica:** se um trecho-ancora nao bater EXATAMENTE, **PARE e reporte**.
> **Idempotencia:** antes de cada insercao, procure a frase-chave do texto NOVO. Se ja existir, PULE e diga no relatorio.
> **Ancoras lidas em:** 2026-09-04, pelo mount achatado (`_MANIFEST_OAI.md` gerado em 2026-09-04 19:46, commit `efcdf3d`, 3 modificados + 3 nao rastreados). Trechos literais lidos NESTE turno:
> - `meta/STATUS.md` linha 20: `- **Golden set + harness** (\`test_matching.py\`): 24/24 (100%) e auto-match 80/80.`
> - `meta/STATUS.md` linha 31: o item `- **Zero à esquerda comido na carga da planilha (FIX-005)**: ...`
> - `meta/STATUS.md` linhas 40-41: os dois itens de backlog criados pela WO 0002
> - `meta/CHANGELOG.md` linha 13: `## [0.4.1] — 2026-09-03`
> - `meta/DECISIONS.md`: ultima linha do arquivo (bloco `## FIX-005`, ultimo bullet, comecando por `- **Lição:** planilha é TEXTO.`)
> - `CLAUDE.md` linhas 11-12: as duas linhas PLACEHOLDER de build/validacao
> - `.gitignore`: bloco de 5 linhas apos o comentario de cabecalho
> **Proximo comando:** `/wrap`

> **Canal dos meta neste ciclo = CODE.** Esta WO **e** o registro. Aplique os appends previstos; o chat nao entrega STATUS/DECISIONS/CHANGELOG inteiros neste ciclo.

---

## 1. Por que

A WO 0003 parou certo, mas parou com trabalho bom preso. A **Parte A esta aplicada, provada e sem commit**: o par negativo confirmou o FIX-005 (`'00611'` novo contra `np.int64(611)` antigo) e o antes/depois nao mostrou regressao nenhuma. O que impediu o commit foi o golden set dar 13/24 — e isso **nao era regressao, era o teste medindo outra coisa**.

A causa: o harness procura a coluna `"Atual: 14/04/2026 - Anterior: 14/04/2026"`, que **nao existe mais** nos exports de hoje, e cai num fallback que escolhe *a primeira coluna cujos valores contenham `" - "`*. Nos exports atuais isso e `Descrição` — descricao curta, sem marca e sem codigo. A coluna certa e `Nome Imagem`. **O teste trocou em silencio o que estava medindo.** Somado a isso, a chave de verdade era o **indice absoluto da linha**, que muda a cada reexport.

Esta WO fecha a Parte A e conserta o instrumento: referencia congelada dentro do repositorio, chave por **codigo interno**, e fim do fallback silencioso.

## 2. Contexto factual

*[medido por instrumento — sonda determinística no chat, 2026-09-04, `matching_engine.py` + `golden_set.csv` + os tres exports do mount]*

1. **A Parte A nao regrediu nada.** Seis combinacoes (3 planilhas × 2 colunas), carga antiga contra carga nova, criterio de indice do harness: `antes=13/24 depois=13/24` em **todas as seis**. O 13/24 identico em tres catalogos diferentes ja e a assinatura de falha estrutural, nao de conteudo — se dependesse do conteudo, tres catalogos dariam tres numeros.
2. **O esquema do export mudou.** As colunas de hoje sao `Interno`, `Marca`, `Código Referência`, `Descrição`, ..., `Nome Imagem`. A coluna que o harness procurava nao existe em nenhum dos tres.
3. **A conclusao do relatorio 1725 sobre `PR12147` estava errada, e o motivo foi a coluna.** `grep` na `Descrição`: nenhuma linha. `grep` em `Nome Imagem`: linha 21, `DAMME - 27224 - PR12147 - PISO PORC POL RETIF CAPRAIA 61X120 CX 2,20MT²`. O codigo nunca sumiu.
4. **`011 - Pisos e Revestimentos` e a referencia certa.** Contem 6 dos 7 codigos com match esperado; `planilha completa` contem 5; `010 - Portas e Janelas` contem **0 de 7** e nunca deveria ter sido usada para esta validacao.
5. **`Código Referência` NAO serve como chave**: 7 vazios e 111 valores unicos em 119 linhas. **`Interno` serve**: 0 vazios e 119 unicos em 119 — e o mesmo vale nos outros dois exports (92/92 e 99/99). E a chave primaria da loja, e o GLOSSARY ja separa os dois conceitos.
6. **`R70031` derrubou a chave ingenua e provou o motor.** A derivacao por substring dizia `SEM_MATCH`; o motor devolve a linha `ROCHA FORTE - 16737 - PISO BRIL RETIF R7003 70X70 CX 3,43MT²` com `codigo_casado='R70031~R7003'` — match bidirecional correto (FIX-001), numa linha **sem `Código Referência`**. O motor estava certo e a derivacao errada. E foi esse caso que mostrou que a chave tem de ser `Interno`.
7. **Com a referencia congelada + `Nome Imagem` + `Interno`: 24/24.** Os 24 casos foram conferidos um a um contra o texto da linha casada, nao aceitos por contagem.
8. *[deduzido, nao medido]* A convencao de nome mudou de 3 campos (`MARCA - CODIGO - DESCRICAO`) para 4 (`MARCA - INTERNO - CODIGO - DESCRICAO`) na coluna `Nome Imagem`. **Nao sei** se os arquivos de imagem do dono seguiram essa mudanca — vira pergunta no backlog, nao decisao aqui.

## Inventario — de onde saiu a lista de edicoes

A pergunta feita ao repositorio foi *"que lugares afirmam algo sobre o golden set, o harness ou o FIX-005?"*, grepando o fato (`test_matching.py`, `golden_set`, `FIX-005`, `24/24`, `indice_esperado`) e nao a prosa.

**Sao 8 pontos**, todos cobertos abaixo: `.gitignore` (1), `test/golden_set.csv` (2), `test/planilha_referencia.csv` (3), `UTILITÁRIOS/test_matching.py` (4), `CLAUDE.md` (5), `meta/DECISIONS.md` (6), `meta/STATUS.md` (7, com tres sub-ancoras), `meta/CHANGELOG.md` (8). **Confira esta contagem.** Achou um nono: **PARE e reporte**.

---

## Passo 0 — Fechar a Parte A com commit, ANTES de qualquer edicao

A Parte A esta provada e sem commit. Ela vai sozinha, num commit proprio, para que ela continue sendo o ponto de retorno se algo abaixo der errado.

Confira antes (`git status --porcelain`): `main.py` e `UTILITÁRIOS/test_matching.py` modificados, `.claude/settings.json` modificado, `UTILITÁRIOS/spreadsheet_loader.py` nao rastreado. **Se a arvore estiver limpa, PARE** — alguem ja commitou e esta WO precisa ser reavaliada.

`UTILITÁRIOS/__pycache__/` tambem aparece como nao rastreado. **Nao tente apaga-lo** (`rm -rf` esta no `deny`, e esta certo que esteja): a edicao 1 o manda para o `.gitignore`, entao ele some do `git status` sozinho. Rode a edicao 1 ANTES do `git add` deste passo.

```
git add .gitignore main.py UTILITÁRIOS/test_matching.py UTILITÁRIOS/spreadsheet_loader.py .claude/settings.json
```

```
git commit -m "fix: le a planilha sempre como texto (FIX-005)" -m "Carga passa por um loader unico com dtype=str e keep_default_na=False, usado pela GUI e pelo harness. Sem isso o pandas inferia int64 numa coluna de codigo e 00611 virava 611, o que comia o zero no nome final e matava o match por codigo. Verificado por par negativo: carga nova devolve 00611, pandas cru devolve 611. Antes x depois do golden set: 13/24 em ambos, nas tres planilhas e nas duas colunas testadas - a Parte A nao regrediu nada. Libera Bash(python) no settings do executor. Ver meta/DECISIONS.md FIX-005."
```

```
git push
```

> **Por que `test_matching.py` entra num commit e e substituido logo depois:** o estado da Parte A e um fato do historico — ele documenta que a correcao do FIX-005 chegou aos dois lados. Commitar e depois reescrever custa um commit a mais e nada de valor; pular o commit apagaria a etapa.

---

## Edicao 1 — `.gitignore` · ignora o bytecode

**Ancora** (bloco contiguo, as cinco linhas atuais):

```
.DS_Store
Thumbs.db
*.swp
.vscode/
.idea/
```

**Substituir por:**

```
.DS_Store
Thumbs.db
*.swp
.vscode/
.idea/

# Bytecode do Python. Aparece assim que o harness roda e nao tem por que
# ser versionado. Nao ha `rm -rf` disponivel ao executor (deny no settings),
# entao ignorar e a unica limpeza barata.
__pycache__/
*.py[cod]
```

## Edicao 2 — `test/planilha_referencia.csv` · **criar arquivo novo**

**Nao gere este arquivo.** Ele foi entregue inteiro pelo chat nesta rodada — e o export `011 - Pisos e Revestimentos`, exatamente o mesmo conteudo contra o qual o 24/24 foi medido. Salve-o em `test/planilha_referencia.csv`.

**Se ele ja existir, PARE e reporte** em vez de sobrescrever: um arquivo de referencia diferente do medido invalida o numero desta WO.

**Confira apos salvar:**

```
python -c "import pandas as pd; d=pd.read_csv('test/planilha_referencia.csv',dtype=str,keep_default_na=False,sep=None,engine='python'); print(len(d),'linhas',len(d.columns),'colunas', d['Interno'].nunique()==len(d))"
```

Esperado: `119 linhas 19 colunas True`. Diferente disso: **PARE**.

## Edicao 3 — `test/golden_set.csv` · **substituir o arquivo inteiro**

Entregue pelo chat nesta rodada. O formato muda de `arquivo,indice_esperado,observacao` para `arquivo,interno_esperado,observacao`, e `-1` vira `SEM_MATCH`.

Os 24 nomes de arquivo sao **os mesmos de antes** — sao entradas reais e nao se inventam. O que muda e so a chave e a observacao.

## Edicao 4 — `UTILITÁRIOS/test_matching.py` · **substituir o arquivo inteiro**

Entregue pelo chat nesta rodada, **ja testado**: rodado contra a referencia congelada com resultado 24/24, e rodado nas quatro situacoes de falha para conferir que ele reprova (ver o checklist).

Tres mudancas de comportamento, todas deliberadas:
- **Sem fallback de coluna.** `COL_MATCHING = "Nome Imagem"` e `COL_IDENTIDADE = "Interno"` sao constantes. Coluna ausente = morre com codigo 2 e imprime as colunas que achou.
- **Roda sem argumentos.** O padrao e a referencia congelada em `test/`. O harness deixa de depender de alguem achar um export solto — foi isso que custou o ciclo da WO 0003.
- **Devolve codigo de erro.** `0` tudo passou · `1` algum caso falhou · `2` insumo invalido. Instrumento que nao reprova ninguem nao roda.

## Edicao 5 — `CLAUDE.md` · preenche os PLACEHOLDER de build/validacao

**Ancora** (bloco contiguo, duas linhas):

```
- Build: `<seu comando de build, ex.: npm run build>`  (PLACEHOLDER — troque pelo do seu projeto)
- Testes/validação: `<seu comando de teste>` — rode antes de commitar mudança de código.
```

**Substituir por:**

```
- Build: `pyinstaller --onefile --windowed main.py` — gera o `.exe` em `dist/`. **Só quando o dono pedir**; não faz parte da validação de rotina.
- Testes/validação: `python UTILITÁRIOS/test_matching.py` — **sem argumentos**. Roda contra a referência congelada em `test/` e sai com código 0 (tudo passou), 1 (algum caso falhou) ou 2 (insumo inválido). Alvo: **24/24**. Rode antes de commitar qualquer mudança em `main.py`, `UTILITÁRIOS/matching_engine.py` ou `UTILITÁRIOS/spreadsheet_loader.py`. Se sair 2, o problema é o insumo e não o motor — leia a mensagem antes de mexer em código.
```

## Edicao 6 — `meta/DECISIONS.md` · acrescenta DEC-008 no fim

**Ancora** (ultima linha do arquivo, ultimo bullet do bloco `## FIX-005`):

```
- **Lição:** planilha é TEXTO. A inferência de tipo do pandas é uma armadilha silenciosa em qualquer coluna que seja identificador — não dá erro, não avisa, e o dano só aparece no nome do arquivo final. Vira armadilha em `CONTEXT.md` **junto com a correção**, não antes.
```

**Inserir IMEDIATAMENTE APOS:**

```

---

## DEC-008 — Golden set com referência congelada e chave por código interno
**Data:** 2026-09-04 · **Status:** aceita (decisão do usuário: "a forma mais profissional e completa")

### Contexto
A WO 0003 parou com 13/24 no golden set e a suspeita registrada foi "a ordem das linhas mudou no reexport". Medindo em vez de aceitar, a causa era outra e pior: o **esquema do export mudou**. A coluna que o harness procurava (`"Atual: 14/04/2026 - Anterior: 14/04/2026"`) não existe mais, e o fallback — *a primeira coluna cujos valores contenham `" - "`* — passou a escolher `Descrição`, uma descrição curta sem marca e sem código. A coluna certa é `Nome Imagem`. O teste **trocou em silêncio o que estava medindo** e continuou dando um número.

Somava-se a isso o índice absoluto da linha como chave de verdade, que muda a cada reexport, e a dependência de um arquivo que não está no repositório — o harness só rodava se alguém achasse um export solto no disco.

### Decisão
Três mudanças, juntas:
1. **Referência congelada** em `test/planilha_referencia.csv` (o export `011 - Pisos e Revestimentos`, 119 linhas). O harness roda **sem argumentos** e não depende de mais ninguém.
2. **Chave por `Interno`** (código interno da loja), não por índice de linha. Medido nos três exports: `Interno` tem 0 vazios e é 100% único (119/119, 92/92, 99/99). `Código Referência` **não serve** — 7 vazios e 111 únicos em 119.
3. **Fim do fallback silencioso.** Colunas explícitas em constantes; coluna ausente aborta com código 2 e imprime as colunas encontradas. O harness passa a devolver código de erro (0/1/2).

### Alternativas consideradas
- **Só rechavear, sem congelar referência** — resolve a reordenação, mas mantém o harness dependente de um arquivo externo, que foi o que queimou o ciclo da WO 0003.
- **Só congelar, mantendo o índice** — determinístico, mas o golden set morre de novo assim que a referência for regenerada.
- **Chave por `Código Referência`** — descartada por medição: 7 linhas do catálogo não têm código, e uma delas (`Interno` 16737) é justamente o alvo do caso `R70031`.

### Consequências
O harness volta a 24/24 e passa a ser reexecutável por qualquer um, a qualquer hora, sem insumo externo. O preço é conhecido e aceito: a referência congelada envelhece — quando ela for atualizada, o `interno_esperado` continua válido (é a chave primária da loja), mas os casos `SEM_MATCH` precisam ser reconferidos, porque um produto antes ausente pode ter sido cadastrado.

**Achado que sobreviveu à investigação:** o caso `R70031` derrubou a derivação ingênua por substring e provou o motor. O esperado derivado dizia `SEM_MATCH`; o motor devolveu `Interno` 16737 via `codigo_casado='R70031~R7003'` — match bidirecional correto (FIX-001) numa linha **sem código de referência**. O motor estava certo e a derivação errada; foi esse caso que definiu a chave.
```

## Edicao 7a — `meta/STATUS.md` · atualiza a linha do harness

**Ancora:**

```
- **Golden set + harness** (`test_matching.py`): 24/24 (100%) e auto-match 80/80.
```

**Substituir por:**

```
- **Golden set + harness** (`UTILITÁRIOS/test_matching.py`): **24/24 (100%)** contra a referência congelada `test/planilha_referencia.csv`. Roda **sem argumentos** e devolve código de erro (0/1/2) — ver DEC-008. Chave é o `Interno`, não o índice da linha.
```

## Edicao 7b — `meta/STATUS.md` · o FIX-005 sai de «Quebrado»

**Ancora** (o item inteiro, uma linha):

```
- **Zero à esquerda comido na carga da planilha (FIX-005)**: `read_csv`/`read_excel` sem `dtype=str` convertem coluna numérica em `int64` e `00611` vira `611`. Quebra o novo nome **e** mata o match por código (`611` tem 3 chars e nem casa com a regex, então a linha fica sem código e o produto é ignorado). Causa raiz reproduzida em 2026-09-04; atinge `main.py` e `test_matching.py`. Correção vai junto com a integração do motor na GUI.
```

**Substituir por:**

```
- **Motor v2 ainda NÃO está na GUI**: `main.py` continua com o `MotorMatching` embutido, o `token_set_ratio` e os cinco utilitários duplicados. A carga da planilha já é a nova (FIX-005 corrigido), mas o matching que a interface roda ainda é o antigo. É a Parte B da WO 0003, que volta na WO 0005.
```

## Edicao 7c — `meta/STATUS.md` · troca os dois itens de backlog obsoletos

**Ancora** (bloco contiguo, duas linhas):

```
- [ ] Corrigir a carga da planilha (FIX-005): `dtype=str` + `keep_default_na=False` num loader único usado pela GUI e pelo harness. Vai junto com a integração do motor.
- [ ] Ampliar o golden set com um caso de código de zero à esquerda contra uma coluna de código **pura** — a coluna descritiva usada hoje esconde o defeito.
```

**Substituir por:**

```
- [ ] **Confirmar a convenção de nome dos arquivos de imagem.** A coluna `Nome Imagem` passou de 3 campos (`MARCA - CÓDIGO - DESCRIÇÃO`) para 4 (`MARCA - INTERNO - CÓDIGO - DESCRIÇÃO`), mas os 24 nomes do golden set ainda são do formato de 3. Não sabemos se os arquivos reais do dono acompanharam. Se acompanharam, o golden set precisa de casos no formato novo. *[pergunta aberta, não medida]*
- [ ] **Rebaselinar o "auto-match 80/80".** Aquele número era contra um export de 80 linhas que não existe mais; a referência de hoje tem 119. Enquanto não for remedido, não citar 80/80 como estado atual.
- [ ] Ampliar o golden set com um caso de código de zero à esquerda cuja coluna de matching seja **puramente numérica** — a referência congelada usa `Nome Imagem`, que é texto e não exercita o FIX-005.
```

## Edicao 8 — `meta/CHANGELOG.md` · entrada 0.4.2

**Ancora:**

```
## [0.4.1] — 2026-09-03
```

**Inserir IMEDIATAMENTE ANTES:**

```
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

```

---

## Fora de escopo

- **Parte B da WO 0003** (motor v2 no lugar do embutido). Volta na WO 0005, agora com um harness que sabe valida-la. Nao "aproveite a viagem".
- **Atualizar `meta/CONTEXT.md`** com a armadilha do `dtype`. Vai junto com a WO 0005, quando o `main.py` estiver inteiro no motor novo — armadilha registrada em cima de um arquivo que ainda vai mudar envelhece antes de ser lida.
- **Regenerar os nomes do golden set** para a convencao de 4 campos. E pergunta aberta no backlog, nao decisao desta WO.
- **Remedir o auto-match.** Idem — entrou no backlog com a ressalva de nao citar o numero velho.

## Armadilhas desta WO

- **A edicao 1 vem antes do `git add` do passo 0.** Se inverter, o `__pycache__/` entra no commit e sair dele depois da trabalho.
- **A edicao 2 e a unica que PROIBE sobrescrever.** Referencia diferente da medida = o 24/24 desta WO deixa de valer.
- **`test/golden_set.csv` e o arquivo NOVO, com `interno_esperado`.** Se o harness novo rodar contra o golden antigo, ele sai com codigo 2 e a mensagem cita DEC-008 — isso e o comportamento certo, nao um erro de aplicacao.
- **Nao "arrume" o `# noqa: E402`** no topo do `test_matching.py`: os imports dependem do `sys.path` alterado na linha acima.
- **`grep -c` conta LINHA.** `FIX-005` e citado por varias edicoes desta WO; as conferencias abaixo usam frases exclusivas.

---

## Depois de aplicar — conferencia antes do commit B

- [ ] Passo 0 commitado e empurrado ANTES das edicoes; `git log -1 --oneline` mostra o commit `fix:`.
- [ ] `git diff --stat` das edicoes mostra **exatamente** `.gitignore`, `test/golden_set.csv`, `test/planilha_referencia.csv`, `UTILITÁRIOS/test_matching.py`, `CLAUDE.md`, `meta/DECISIONS.md`, `meta/STATUS.md`, `meta/CHANGELOG.md` e a propria WO. Nada alem — em especial, **`main.py` nao pode aparecer**.
- [ ] `python -c "import pandas as pd; d=pd.read_csv('test/planilha_referencia.csv',dtype=str,keep_default_na=False,sep=None,engine='python'); print(len(d),len(d.columns),d['Interno'].nunique()==len(d))"` -> `119 19 True`.
- [ ] `grep -c "interno_esperado" test/golden_set.csv` -> **1** (so o cabecalho).
- [ ] `grep -c "SEM_MATCH" test/golden_set.csv` -> **15**.
- [ ] `grep -c "DEC-008 — Golden set com referência congelada" meta/DECISIONS.md` -> **1**.
- [ ] `grep -c "^## \[0.4.2\]" meta/CHANGELOG.md` -> **1**, e a entrada ficou ACIMA de `## [0.4.1]`.
- [ ] `grep -c "indice_esperado" meta/ test/ UTILITÁRIOS/ -r` -> **0** fora do texto historico do DECISIONS. Se aparecer em `test/` ou `UTILITÁRIOS/`, ficou sobra do formato antigo.

### Validacao — a rede desta WO e o proprio harness

- **Quem roda:** quem aplica. E execucao local reversivel.
- **Caso feliz:** `python UTILITÁRIOS/test_matching.py` (sem argumentos) -> **24/24**, codigo de saida **0**.
- **Chega no ramo?** `test_matching.main()` -> `carregar_planilha()` (Parte A, commit do passo 0) -> `MotorMatching.buscar()` -> comparacao por `Interno` (edicoes 3 e 4). O caminho passa por tudo que esta WO tocou.
- **Prova de vida — obrigatoria, quatro casos negativos.** "24/24" so significa alguma coisa depois de ver o mesmo instrumento reprovar. Rode os quatro e confira o codigo de saida com `echo %ERRORLEVEL%` (CMD) ou `echo $?` (Git Bash), **sem `tail` na frente** — cano mascara o codigo de saida do Python:

  | caso | como | codigo esperado |
  |---|---|---|
  | tudo certo | `python UTILITÁRIOS/test_matching.py` | **0** |
  | golden no formato antigo | apontar para uma copia do golden com `indice_esperado` | **2** |
  | planilha sem `Nome Imagem` | copia da referencia com a coluna removida | **2** |
  | expectativa errada | copia do golden com um `interno_esperado` trocado | **1** |

  Os quatro foram rodados no chat antes desta WO, com esses exatos codigos. Se algum divergir na maquina do dono, **PARE**: a diferenca e o achado.
  **Limpeza:** as copias de teste vao para `../` (pasta-pai) e sao apagadas ao terminar. O que sobrar entra no relatorio com o caminho.
- **Esta e qual pergunta?** «presta?», para o instrumento. Ela **nao responde** nada sobre a GUI: `main.py` nao foi tocado por esta WO e continua com o motor antigo. E tambem nao responde se as 24 linhas casadas sao o produto certo aos olhos de quem vende — o harness compara chave, nao julga catalogo.

## Relatorio de aplicacao *(quem aplica preenche ao terminar)*

O que foi feito · o que fugiu do texto literal · arquivos tocados · **o resultado dos quatro casos de prova de vida, com os codigos de saida** · os dois commits e os dois pushes.

## Commit B — depois de aplicar as edicoes

```
git add .gitignore test/golden_set.csv test/planilha_referencia.csv UTILITÁRIOS/test_matching.py CLAUDE.md meta/DECISIONS.md meta/STATUS.md meta/CHANGELOG.md meta/workorders/260904-wo0004-rechaveia-golden-set.md
```

```
git commit -m "test: rechaveia o golden set por codigo interno e congela a referencia" -m "O harness procurava uma coluna que o export nao tem mais e caia num fallback que escolhia Descricao em vez de Nome Imagem, medindo outra coisa em silencio. Agora as colunas sao explicitas, coluna ausente aborta com codigo 2, a chave e o Interno (0 vazios e 100 por cento unico nos tres exports) e a referencia esta congelada em test/, entao o harness roda sem argumentos. Volta a 24/24. Preenche os comandos de build e validacao no CLAUDE.md. Ver meta/DECISIONS.md DEC-008."
```

```
git push
```

*Formato do Kit de Contexto Universal v1.122.0.*
