# WO 0002 — Fecha a migracao KCM e registra a triagem dos dois bugs de zero a esquerda

> **Tipo:** WO de DOC (registro). Nao toca codigo.
> **Config sugerida:** modelo leve, esforco baixo. Sao tres insercoes de texto e dois commits.
> **Pre-requisito:** commit `a1ccb74` na `main`, sincronizado com `origin/main`, com a migracao KCM v1.122.0 aplicada em disco e ainda NAO commitada (9 modificados + 8 nao rastreados).
> **Base:** conversa de 2026-09-04 (raia de chat). Nota do dono `../260814-1021.txt` de 2026-08-14 + reproducao deterministica da causa raiz feita nesta conversa.
> **Depende de:** WO 0001 (aplicada, commit `0658523`).
> **Ancora semantica:** se um trecho-ancora nao bater EXATAMENTE, **PARE e reporte** — nunca chute um lugar proximo.
> **Idempotencia:** antes de cada insercao, procure a frase-chave do texto NOVO. Se ja existir, **PULE** o item e diga no relatorio.
> **Ancoras lidas em:** 2026-09-04, pelo mount achatado do Projeto (`_MANIFEST_OAI.md` gerado em 2026-09-04 01:42), arquivo por arquivo:
> - `meta/DECISIONS.md` — ultima linha do arquivo: `Estrutura alinhada ao KCM v1.122.0. Os 4 carimbos de versão conferem em v1.122.0. Próximo trabalho já roda sob o contrato novo (ritual por turno, modo Code com WOs).`
> - `meta/IDEAS.md` — linha `## ✅ Concluídas` (ocorre 1 vez).
> - `meta/STATUS.md` — linhas `- **Pesos não calibrados formalmente**: os pesos atuais (\`PesosScore\`) passam no golden set, mas não foram otimizados; valores são razoáveis, não ótimos.`, `- [ ] Decidir tratamento do \`código_ausente\` na UI: aba separada "Código não cadastrado"?` e `**2026-05-31 (2ª sessão)** — Construído o motor v2 modular, o golden set (24 casos reais) e o harness.` (cada uma ocorre 1 vez).
> - Fim de linha conferido: os tres arquivos sao **LF puro**, sem CRLF.
> **Proximo comando:** `/wrap`

> **Canal dos meta neste ciclo = CODE.** Esta WO **e** o registro: aplique os appends previstos e nao espere documento do chat. O chat nao entrega DECISIONS/IDEAS/STATUS inteiros neste ciclo.

---

## 1. Por que

Duas coisas ficaram penduradas e as duas custam a proxima conversa.

**(1)** A migracao KCM v1.122.0 esta aplicada em disco desde 2026-09-03 e **nunca foi commitada**. O repositorio e o que a proxima conversa le; enquanto o trabalho estiver so na copia de trabalho, ele nao existe para ela.

**(2)** Os dois bugs que o dono relatou em 2026-08-14 nunca foram registrados em lugar nenhum alem de uma nota `.txt` fora do repositorio. Nesta conversa a **causa raiz dos dois foi encontrada, e e uma so**. Isso precisa virar registro agora, porque a correcao vai acontecer na frente seguinte (integracao do motor na GUI) e quem for aplica-la precisa saber o que esta consertando.

## 2. Contexto factual

Na ordem em que aconteceu:

1. *[relatado pelo dono — nota `../260814-1021.txt`, 2026-08-14]* Dois defeitos na GUI: **(a)** quando o nome escolhido para renomear comeca com `0`, o zero e "comido"; **(b)** um match cujo codigo tem `00` (dois zeros seguidos) foi ignorado.
2. *[medido por instrumento — 2026-09-04, leitura do mount]* `main.py:1300` carrega CSV com `pd.read_csv(caminho, encoding=enc, sep=sep, on_bad_lines="skip", low_memory=False)` e `main.py:1305` carrega XLSX com `pd.read_excel(caminho, engine="openpyxl")`. **Nenhum dos dois passa `dtype`.** `UTILITÁRIOS/test_matching.py:31` tem o mesmo defeito: `pd.read_csv(caminho, encoding=enc, sep=None, engine="python")`.
3. *[medido por instrumento — 2026-09-04, reproducao deterministica com pandas 3.0.2]* Sem `dtype=str`, uma coluna cujos valores sao todos numericos e inferida como `int64` e `00611` vira `611` **antes** de qualquer `str()` ou `.astype(str)` do codigo. Com `dtype=str`, `00611` sobrevive.
4. *[medido por instrumento — 2026-09-04, mesma reproducao]* Aplicando a regra de match por codigo dos dois motores sobre o valor degradado: `REGEX_CODIGO` (`\b([A-Za-z]{0,4}\d[\dA-Za-z]{3,})\b`) exige 4 caracteres no minimo, entao `611` **nao produz codigo nenhum**. A linha da planilha fica com lista de codigos vazia, o arquivo tem `00611`, e nao ha match por codigo. No motor v2 a guarda DEC-006 entao devolve `código_ausente` e o produto e ignorado — que e exatamente o sintoma (b).
5. *[medido por instrumento — 2026-09-04, leitura do mount]* O golden set nao pega isso porque `test_matching.py` casa contra a coluna `"Atual: 14/04/2026 - Anterior: 14/04/2026"`, cujos valores contem texto (` - `). O pandas a le como string e o zero sobrevive. O defeito so aparece quando a coluna escolhida e **puramente numerica** — que e a configuracao do dono na GUI.
6. *[medido por instrumento — 2026-09-04, varredura de `main.py`]* Nenhuma coluna do DataFrame e usada como numero. As unicas leituras sao `df[col_matching].fillna("").astype(str)` (linha 241), `str(linha[self.col_novo_nome])` (377) e `str(linha[self.col_pasta_destino]).strip()` (393). Logo, `dtype=str` nao quebra nada.
7. *[deduzido, nao medido]* Nao tenho a planilha real do dono, entao **nao esta provado qual coluna ele tinha selecionado** quando viu os sintomas. A causa raiz esta provada; o mapeamento sintoma→coluna e a explicacao mais economica que cobre os dois relatos de uma vez.

## Inventario — de onde saiu a lista de edicoes

A pergunta feita ao repositorio foi *"que lugares carregam planilha para dentro do programa?"*, grepando o fato (`read_csv`, `read_excel`, `dtype`) e nao a frase. **Sao dois lugares de leitura**, ambos defeituosos: `main.py` (1300 e 1305, mesma funcao) e `UTILITÁRIOS/test_matching.py` (31). Nao ha terceiro. Esta WO **nao corrige** nenhum dos dois — registra os dois; a contagem esta aqui para a WO de correcao herdar sem refazer o levantamento.

Os tres arquivos de registro que precisam mudar sairam do papel de cada documento (CEREBRO, tabela «Como manter os documentos»): a causa raiz de um bug grave vai para `DECISIONS`; o defeito aberto e o proximo passo vao para `STATUS`; a ideia nova que nasceu do diagnostico vai para `IDEAS`. `CONTEXT` **nao** entra: a armadilha so vira armadilha quando a correcao existir, e entra junto com ela.

---

## Passo 0 — ANTES de qualquer edicao: fechar a migracao KCM

Este passo nao tem ancora e nao edita arquivo: ele so commita o que ja esta no disco. Rode-o **primeiro**, para que as edicoes desta WO caiam numa arvore limpa e entrem no proprio commit.

O que deve estar pendente antes (confira com `git status --porcelain`): 4 modificados (`meta/CEREBRO.md`, `meta/CHANGELOG.md`, `meta/DECISIONS.md`, `meta/IDEAS.md`), 5 delecoes (`meta/CLAUDE.md`, `meta/HISTORICO.md`, `meta/INSTRUCTION_GUIDE.md`, `meta/PROMPT_IA.md`, `meta/demo.yaml`) e 8 nao rastreados (`.claude/`, `.flatdropignore`, `.gitignore`, `CLAUDE.md`, `INSTRUCOES-DO-PROJETO.md`, `meta/HISTORY.md`, `meta/SPEC.md`, `meta/workorders/`).

**Se a contagem vier diferente disso, PARE e reporte** — alguem mexeu na arvore entre a escrita desta WO e a aplicacao, e o `git add -A` deixaria de ser seguro.

Se esta WO e o log do dia ja estiverem no disco quando o passo 0 rodar, eles entram neste commit junto. **Isso e esperado e nao e erro** — o `-A` varre a arvore inteira de proposito.

```
git add -A
```

```
git commit -m "chore: fecha a migracao para o contrato KCM v1.122.0" -m "Descarta CEREBRO e CLAUDE antigos (eram 100 por cento regra generica), remove o modo ASU, renomeia HISTORICO para HISTORY, adota as skills apply-wo e wrap. Acrescenta .claude/, .gitignore, .flatdropignore, CLAUDE.md raiz, INSTRUCOES-DO-PROJETO.md, meta/SPEC.md e meta/workorders/. Ver meta/DECISIONS.md DEC-007."
```

```
git push
```

---

## Edicao 1 — `meta/DECISIONS.md` · acrescenta FIX-005 no fim do arquivo

**Ancora** (ultima linha do arquivo, dentro de `## DEC-007`, secao `### Consequências`):

```
Estrutura alinhada ao KCM v1.122.0. Os 4 carimbos de versão conferem em v1.122.0. Próximo trabalho já roda sob o contrato novo (ritual por turno, modo Code com WOs).
```

**Inserir IMEDIATAMENTE APOS** (com uma linha em branco antes do `---`, como nas entradas anteriores):

```

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
```

## Edicao 2 — `meta/IDEAS.md` · captura a ideia do loader unico

**Ancora** (cabecalho da secao de ideias concluidas; ocorre 1 vez):

```
## ✅ Concluídas
```

**Inserir IMEDIATAMENTE ANTES** (o texto novo termina com uma linha em branco e o separador `---` que ja existia acima permanece onde esta):

```
### 2026-09-04 — Loader único de planilha (GUI + harness)
Hoje a planilha é carregada em dois lugares independentes — `main.py` (detecta encoding e separador à mão) e `test_matching.py` (`sep=None`) — e os dois carregam errado da mesma forma (FIX-005: sem `dtype=str`). Reunir num `carregar_planilha()` compartilhado faz a correção acontecer uma vez só, torna a carga testável isoladamente (hoje ela vive dentro de um método Qt) e tira uma duplicação que a integração do motor na GUI herdaria. Entra junto com essa integração.

```

## Edicao 3a — `meta/STATUS.md` · registra o defeito na secao «Quebrado»

**Ancora** (ultimo item da secao `## ❌ Quebrado / Com Problema`; ocorre 1 vez):

```
- **Pesos não calibrados formalmente**: os pesos atuais (`PesosScore`) passam no golden set, mas não foram otimizados; valores são razoáveis, não ótimos.
```

**Inserir IMEDIATAMENTE APOS:**

```
- **Zero à esquerda comido na carga da planilha (FIX-005)**: `read_csv`/`read_excel` sem `dtype=str` convertem coluna numérica em `int64` e `00611` vira `611`. Quebra o novo nome **e** mata o match por código (`611` tem 3 chars e nem casa com a regex, então a linha fica sem código e o produto é ignorado). Causa raiz reproduzida em 2026-09-04; atinge `main.py` e `test_matching.py`. Correção vai junto com a integração do motor na GUI.
```

## Edicao 3b — `meta/STATUS.md` · acrescenta os dois itens de backlog

**Ancora** (ultimo item do `## 📋 Backlog`; ocorre 1 vez):

```
- [ ] Decidir tratamento do `código_ausente` na UI: aba separada "Código não cadastrado"?
```

**Inserir IMEDIATAMENTE APOS:**

```
- [ ] Corrigir a carga da planilha (FIX-005): `dtype=str` + `keep_default_na=False` num loader único usado pela GUI e pelo harness. Vai junto com a integração do motor.
- [ ] Ampliar o golden set com um caso de código de zero à esquerda contra uma coluna de código **pura** — a coluna descritiva usada hoje esconde o defeito.
```

## Edicao 3c — `meta/STATUS.md` · acrescenta o paragrafo da conversa de 2026-09-04

**Ancora** (abertura do paragrafo de 2026-05-31 dentro de `## 💬 Última conversa`; ocorre 1 vez):

```
**2026-05-31 (2ª sessão)** — Construído o motor v2 modular, o golden set (24 casos reais) e o harness.
```

**Inserir IMEDIATAMENTE ANTES** (o texto novo termina com uma linha em branco, separando-o do paragrafo de 2026-05-31):

```
**2026-09-04** — Fecho da migração KCM commitado (o passo que faltava desde 2026-09-03) e **triagem dos dois bugs órfãos da nota `260814-1021.txt`**: os dois têm a MESMA causa raiz, agora reproduzida — a planilha é carregada sem `dtype=str`, o pandas infere `int64` numa coluna numérica e come o zero à esquerda. Registrado em FIX-005. A correção NÃO foi aplicada nesta conversa de propósito: ela cai em `main.py` na mesma região que a integração do motor v2 vai refatorar, e fazer as duas de uma vez evita dois diffs conflitantes no mesmo arquivo. Nenhuma linha de código tocada. Próxima frente: integrar `matching_engine.py` na GUI **com** a correção da carga.

```

---

## Fora de escopo

- **Corrigir o defeito.** Esta WO registra; nao aplica `dtype=str` em lugar nenhum. A correcao cai na frente de integracao do motor na GUI, para nao editar `main.py` duas vezes com dois diffs que se atropelam.
- **Criar o loader compartilhado.** Ficou como ideia em IDEAS, nao como arquivo.
- **Mexer em `meta/CONTEXT.md`.** A armadilha nova entra la junto com a correcao, nao antes: armadilha que descreve um defeito ainda vivo confunde quem le a lista para saber o que ja esta protegido.
- **Ampliar o golden set.** Depende da planilha real do dono com uma coluna de codigo pura, que nao esta a mao.
- **Limpar `INSTRUCTION_GUIDE.md` / `PROMPT_IA.md` / `demo.yaml`.** Ja estao deletados na copia de trabalho e o passo 0 commita a delecao; a decisao de valor de referencia (DEC-007, «Pendencias de limpeza») ja foi tomada na pratica.

## Armadilhas desta WO

- **O passo 0 usa `git add -A`.** E deliberado — a migracao envolve 5 delecoes, que `git add .` de versoes antigas do git nao pega. Mas por isso ele **exige a conferencia da contagem antes**: se a arvore tiver algo que voce nao esperava, o `-A` leva junto.
- **Dois commits, nao um.** Fechar a migracao e registrar a triagem sao naturezas diferentes (`chore` e `docs`). Um commit so faria o registro do FIX-005 desaparecer dentro de um commit de migracao de 17 arquivos.
- **As tres ancoras do STATUS estao em secoes diferentes do mesmo arquivo.** Aplique 3a, 3b e 3c uma de cada vez, conferindo a secao em que cada uma caiu — os itens de backlog e os de «Quebrado» tem formatos parecidos e trocar de secao passa despercebido no `git diff`.
- **Contagem de `grep` desta WO:** a frase `dtype=str` e citada por VARIAS edicoes (FIX-005, STATUS 3a, STATUS 3b, IDEAS). Nao use `grep -c "dtype=str"` como verificacao de uma edicao isolada; as verificacoes abaixo usam frases exclusivas de cada edicao.
- **Os tres arquivos sao LF puro** *(conferido em 2026-09-04)*. Ainda assim, todas as ancoras acima sao de **uma linha so**, entao fim de linha nao morde.

---

## Depois de aplicar — conferencia antes do commit

- [ ] `git status --porcelain` **antes** do passo 0 bate com a lista prevista (4 modificados, 5 delecoes, 8 nao rastreados). Diferente: **PARE e reporte**.
- [ ] Passo 0 commitado e empurrado; `git log -1 --oneline` mostra o commit `chore:`.
- [ ] `git diff` das edicoes mostra **exatamente** `meta/DECISIONS.md`, `meta/IDEAS.md` e `meta/STATUS.md`, e nada alem.
- [ ] `grep -c "FIX-005 — Zero à esquerda" meta/DECISIONS.md` -> esperado **1**.
- [ ] `grep -c "Loader único de planilha" meta/IDEAS.md` -> esperado **1**, e a entrada ficou dentro de `## 🤖 Ideias Ativas — Assistente`, ANTES de `## ✅ Concluídas` — nao dentro das concluidas.
- [ ] `grep -c "Zero à esquerda comido na carga da planilha" meta/STATUS.md` -> esperado **1**, e o item ficou na secao `## ❌ Quebrado / Com Problema`.
- [ ] `grep -c "Ampliar o golden set com um caso de código de zero" meta/STATUS.md` -> esperado **1**, dentro de `## 📋 Backlog`.
- [ ] `grep -c "^\*\*2026-09-04\*\*" meta/STATUS.md` -> esperado **1**, e o paragrafo ficou ANTES do de `**2026-05-31 (2ª sessão)**`.
- [ ] **WO so de doc:** nao precisa de build — a rede e o `git diff`. **Nenhum teste roda nesta WO**, e isso e correto: nenhuma linha de codigo mudou, entao o golden set nao tem o que dizer. Se voce sentiu vontade de rodar `test_matching.py`, o resultado seria 24/24 exatamente como antes, e nao provaria nada sobre esta WO.
- [ ] **Esta WO responde «esta la?», nao «presta?».** Os `grep` acima provam que o texto entrou e onde; nenhum deles verifica que o diagnostico do FIX-005 esta certo. Quem confere isso e a correcao, na WO seguinte, rodando com uma coluna de codigo pura.
- [ ] **Nada foi criado fora do repositorio** por esta WO (sem processo, porta, servidor ou arquivo temporario). Se voce criou algo para conferir, declare no relatorio com o caminho.

## Relatorio de aplicacao *(quem aplica preenche ao terminar)*

O que foi feito · o que fugiu do texto literal da WO · arquivos tocados · os DOIS commits e os dois pushes. Escreva-o depois de resolver o segundo push.

## Commit 2 — depois de aplicar as edicoes

```
git add meta/DECISIONS.md meta/IDEAS.md meta/STATUS.md logs/2026-09-04.md meta/workorders/260904-wo0002-triagem-bugs-zero-a-esquerda.md
```

```
git commit -m "docs: registra FIX-005 (zero a esquerda na carga da planilha)" -m "Os dois bugs relatados pelo dono em 2026-08-14 tem a mesma causa raiz, agora reproduzida: read_csv e read_excel sem dtype=str convertem coluna numerica em int64 e comem o zero a esquerda, o que quebra o novo nome e mata o match por codigo. Registra em DECISIONS, STATUS e IDEAS. A correcao fica para a frente de integracao do motor v2 na GUI, para nao editar main.py duas vezes."
```

```
git push
```

*Formato do Kit de Contexto Universal v1.122.0.*
