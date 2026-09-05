# WO 0006 — Transparencia do match na tabela e agrupamento da aba «Sem correspondencia»

> **Tipo:** WO de CODIGO (so `main.py`). Nao toca `meta/`, `UTILITÁRIOS/` nem `test/`.
> **Config sugerida:** modelo capaz, `/effort` medio. Quatro edicoes, todas ja aplicadas e exercitadas no sandbox do chat.
> **Pre-requisito:** HEAD `547936f`, `origin/main` sincronizado, arvore limpa. `main.py` com **1298 linhas**. Se qualquer um dos tres nao bater, **PARE e reporte**.
> **Base:** item «Transparencia do match na UI» do `meta/STATUS.md` (Em Progresso) + o item de backlog «Decidir tratamento do `código_ausente` na UI» — esta WO fecha os dois. A decisao de UX foi delegada ao assistente pelo dono («aceito a forma que voce recomendar»); as escolhas e os custos estao na secao 2.
> **Depende de:** WO 0005 (aplicada, `7199443`), que ja deixa `componentes`, `codigo_casado` e `ambiguo` chegando ao dicionario da correspondencia. **Esta WO nao muda o motor** — so mostra o que ele ja devolve.
> **Ancora semantica:** se um trecho-ancora nao bater EXATAMENTE, **PARE e reporte**.
> **Idempotencia:** antes de cada edicao, procure a frase-chave do texto NOVO (`IDX_PORQUE`, `resumir_match`, `"motivo": res.metodo`, `CÓDIGO NÃO CADASTRADO`). Se ja existir, PULE e diga no relatorio.
> **Ancoras lidas em:** 2026-09-05, no `main.py` de 1298 linhas do mount (`_MANIFEST_OAI.md` gerado em 2026-09-05 11:15, commit `547936f`). **As quatro edicoes foram aplicadas de verdade num clone deste arquivo**, com assercao de ancora unica em cada uma; nenhuma falhou. Resultado: 1298 -> **1395** linhas.
> **Fim de linha:** `main.py` e LF puro.
> **Proximo comando:** `/wrap`

> **Canal dos meta neste ciclo = CODE, mas so no `/wrap`.** Nao faca append em `meta/` durante o `/apply-wo`.

---

## 1. Por que

Desde a WO 0005 o `main.py` carrega `componentes`, `codigo_casado` e `ambiguo` no dicionario de cada correspondencia — e **nada disso aparece na tela**. O usuario ve um numero de score e a palavra «fuzzy», sem nenhuma forma de saber *por que* aquela linha casou. Quando o motor erra, ele nao tem como descobrir onde; quando acerta, nao tem como confiar.

Junto vai a segunda metade do mesmo problema: `código_ausente` hoje cai na aba «Sem correspondencia» com uma anotacao **enfiada dentro da string do caminho** (`[código não cadastrado]`), que foi um paliativo explicito da WO 0005. Isso mistura dois casos que pedem **acoes diferentes** e nao dá para contar nem agrupar sem parsear texto de volta.

## 2. As decisoes de UX, e o que cada uma custa

O dono delegou a forma. Foram quatro escolhas, todas com alternativa real:

**(a) Uma coluna nova, «Por quê» — nao cinco.** `componentes` tem cinco campos, mas eles ficam **todos vazios num match por codigo**, que e a maioria dos casos (11 correspondencias na referencia: a esmagadora maioria por codigo). Cinco colunas vazias na maior parte das linhas custam legibilidade e nao pagam nada. A tabela iria de 9 para 14 colunas.
*Custo aceito:* o resumo curto e uma linha de texto, nao numeros ordenaveis. Quem quiser ordenar por `cobertura` nao consegue.
*Mitigacao:* o detalhe completo vai no **tooltip**, na celula «Por quê» e tambem na de «Score» — tooltip nao ocupa espaco nenhum.

**(b) Ambiguidade e alerta, nao coluna.** Vira um `⚠ ambíguo ·` na frente do resumo e pinta a celula de Score de ambar, mesmo quando o score e alto. Coluna de alerta some no meio das outras oito; cor faz o olho parar.
*Custo aceito:* a cor ambar da ambiguidade **sobrescreve** a cor verde/amarela/vermelha do score naquela celula. Perde-se a leitura de faixa naquela linha especifica — de proposito, porque «alto mas ambiguo» e exatamente o caso que nao pode parecer tranquilo.

**(c) O checkbox NAO e desmarcado automaticamente em linha ambigua.** Desmarcar mudaria o conjunto que vai ser renomeado sem o usuario pedir, e um arquivo desmarcado sem ele notar simplesmente nao acontece — falha silenciosa.
*Custo aceito:* se ele executar sem olhar, a linha ambigua entra junto. O alerta e visual, nao um bloqueio.

**(d) `código_ausente` NAO vira aba nova.** Vira uma **secao com contagem** dentro da aba que ja existe. Uma terceira aba fragmenta um fluxo que hoje tem duas, para um caso que continua sendo o mesmo destino: «arquivos que nao foram renomeados». O que muda entre os dois grupos e a **acao**: «codigo nao cadastrado» e trabalho na planilha (cadastrar o produto); «sem correspondencia» e trabalho no matching (conferir nome, baixar threshold).
*Custo aceito:* com muitos arquivos, a aba vira um `QTextEdit` longo com dois blocos — nao ha filtro nem busca. Se isso incomodar na pasta real de 164 pisos, a aba vira tabela numa WO futura. **Nao adiantar isso agora**: e refactor de widget sem evidencia de que incomoda.

**Efeito colateral estrutural:** o sinal `sem_match` deixa de ser `list[str]` e passa a ser `list[dict]` com `caminho`, `motivo` e `score`. Isso e necessario — agrupar e contar parseando `[código não cadastrado]` de volta da string seria fragil. **Quem consome esse sinal e so `AbaSemMatch.popular`** *(conferido: `grep -n "sem_match" main.py` -> a definicao do Signal, o `.emit` e a unica conexao, em `_escanear`)*.

## 3. O que ja foi medido — nao repita este trabalho

*[medido por instrumento — sandbox do chat com PySide6 6.11.2 em modo `offscreen`, 2026-09-05]*

1. **Ancoras:** as quatro bateram, cada uma com **exatamente 1 ocorrencia**.
2. `pyflakes` depois: **0** nomes indefinidos.
3. **Tabela real montada** com as 11 correspondencias da referencia: `columnCount()` = **10**, `COLUNAS_TABELA[IDX_PORQUE]` = `'Por quê'`, `IDX_PORQUE` = **7**.
4. **Render da coluna, um por metodo:**
   ```
   [código] código PR12147
   [fuzzy]  sort 83.5 · wratio 95.0 · cob 85.7 · medida coincide
   ```
5. **Tooltip do caso fuzzy**, como saiu:
   ```
   Sem código utilizável — casou por score ponderado (DEC-002).
     token_sort    83.5
     WRatio        95.0
     cobertura     85.7%  (tokens da planilha presentes no arquivo)
     medida        coincide  (ajuste 6.0)
   Medida divergente penaliza forte — ver DEC-005.
   ```
6. **Aba agrupada**, com os dois blocos e a lista vazia:
   ```
   CÓDIGO NÃO CADASTRADO (1)
   ...
   ──────────────────────────────────────────────────────────────────────
   SEM CORRESPONDÊNCIA (2)
   Nenhuma linha passou do threshold. Confira o nome do arquivo ou baixe o threshold.

   C:\imgs\SEM CODIGO NENHUM AQUI.jpg   (melhor score: 61.4)
   ```
   Lista vazia -> `'(Nenhum arquivo sem correspondência — ótimo!)'`, inalterado.
7. **Ambiguidade:** render forcado deu celula `⚠ ambíguo · código PR12147` e fundo de score `#ffe0b2`.
8. **Golden set depois de tudo:** exit **0**.

**O que isso NAO prova:** a maquina do dono, a janela de verdade, o tooltip aparecendo ao passar o mouse, e a leitura das cores num monitor. Tooltip e cor **so existem de fato quando alguem olha** — por isso o teste manual e obrigatorio.

**E um vazio honesto:** *[medido]* **os dados da referencia produzem ZERO casos ambiguos** (`ambiguo=True` em 0 das 11 correspondencias). O caminho (b) so foi verificado por render forcado, injetando a flag num item. **Ninguem consegue exercitar ambiguidade com a referencia congelada** — nem voce. O checklist reflete isso.

---

## Edicao 1 — coluna «Por quê» e o helper `resumir_match`

**Ancora** (bloco contiguo, do `COLUNAS_TABELA` ate `IDX_PASTA_DEST`):

```
COLUNAS_TABELA = [
    "✔", "Nome original", "Base detectada", "Sufixo", "Correspondência planilha",
    "Score", "Método", "Novo nome (editável)", "Pasta destino",
]
IDX_CHECK = 0
IDX_NOME_ORIG = 1
IDX_BASE = 2
IDX_SUFIXO = 3
IDX_MATCH = 4
IDX_SCORE = 5
IDX_METODO = 6
IDX_NOVO_NOME = 7
IDX_PASTA_DEST = 8
```

**Substituir por:**

```
COLUNAS_TABELA = [
    "✔", "Nome original", "Base detectada", "Sufixo", "Correspondência planilha",
    "Score", "Método", "Por quê", "Novo nome (editável)", "Pasta destino",
]
IDX_CHECK = 0
IDX_NOME_ORIG = 1
IDX_BASE = 2
IDX_SUFIXO = 3
IDX_MATCH = 4
IDX_SCORE = 5
IDX_METODO = 6
IDX_PORQUE = 7
IDX_NOVO_NOME = 8
IDX_PASTA_DEST = 9


def resumir_match(item: dict) -> tuple[str, str]:
    """
    Traduz a transparência do motor em (texto curto da célula, tooltip detalhado).

    Uma coluna só, e não uma por componente: `componentes` traz cinco campos que
    ficam TODOS vazios num match por código — e match por código é a maioria dos
    casos. Cinco colunas vazias na maior parte das linhas custam legibilidade e
    não pagam nada. O detalhe completo vai no tooltip, que não ocupa espaço.
    """
    metodo = item.get("metodo", "")
    comp = item.get("componentes") or {}
    ambiguo = bool(item.get("ambiguo"))

    if metodo == "código":
        curto = f"código {item.get('codigo_casado', '')}".strip()
        detalhe = (
            f"Casou pelo código de referência: {item.get('codigo_casado', '—')}\n"
            f"Match por código é exato ou bidirecional (FIX-001) e vale 100 —\n"
            f"os componentes do score fuzzy não são calculados neste caminho."
        )
    elif metodo == "fuzzy" and comp:
        curto = (
            f"sort {comp.get('token_sort', '?')} · "
            f"wratio {comp.get('wratio', '?')} · "
            f"cob {comp.get('cobertura', '?')} · "
            f"medida {comp.get('medida', '?')}"
        )
        detalhe = (
            f"Sem código utilizável — casou por score ponderado (DEC-002).\n"
            f"  token_sort    {comp.get('token_sort', '?')}\n"
            f"  WRatio        {comp.get('wratio', '?')}\n"
            f"  cobertura     {comp.get('cobertura', '?')}%  (tokens da planilha presentes no arquivo)\n"
            f"  medida        {comp.get('medida', '?')}  (ajuste {comp.get('ajuste_medida', 0)})\n"
            f"Medida divergente penaliza forte — ver DEC-005."
        )
    else:
        curto = comp.get("motivo", "—")
        detalhe = curto

    if ambiguo:
        curto = f"⚠ ambíguo · {curto}"
        detalhe += (
            "\n\nAMBÍGUO: o segundo melhor candidato ficou dentro da margem.\n"
            "A linha continua marcada, mas confira antes de executar."
        )
    return curto, detalhe
```

> **Armadilha:** `IDX_NOVO_NOME` e `IDX_PASTA_DEST` **mudam de valor** (7->8, 8->9). Eles sao usados em outros pontos do arquivo; como sao constantes nomeadas, nada mais precisa mudar — mas **nao troque nenhum `IDX_*` por numero literal** ao aplicar.

## Edicao 2 — preenchimento da linha: coluna, tooltip e alerta de ambiguidade

**Ancora** (bloco contiguo, dentro de `popular_tabela`):

```
            self.tabela.setItem(row, IDX_SCORE, score_item)

            self.tabela.setItem(row, IDX_METODO, _cell(item["metodo"]))
```

**Substituir por:**

```
            # Ambiguidade e ALERTA, nao nota: mesmo com score alto a celula vai
            # de ambar, para o olho parar nela. O checkbox NAO e desmarcado —
            # mudar selecao por conta propria esconderia arquivo do usuario.
            if item.get("ambiguo"):
                score_item.setBackground(QColor("#ffe0b2"))
                score_item.setForeground(QColor("#8a4b00"))
            self.tabela.setItem(row, IDX_SCORE, score_item)

            self.tabela.setItem(row, IDX_METODO, _cell(item["metodo"]))

            # Por que esta linha casou — resumo na celula, detalhe no tooltip.
            curto, detalhe = resumir_match(item)
            porque_item = _cell(curto)
            porque_item.setToolTip(detalhe)
            score_item.setToolTip(detalhe)
            if item.get("ambiguo"):
                porque_item.setForeground(QColor("#8a4b00"))
            self.tabela.setItem(row, IDX_PORQUE, porque_item)
```

> O bloco de ambiguidade fica **antes** do `setItem` do score de proposito: depois de inserido na tabela, o `score_item` ja pertence ao widget e mexer nele fica mais fragil.

## Edicao 3 — `sem_match` passa a carregar o motivo estruturado

**Ancora** (bloco contiguo, dentro de `ThreadVarredura.run`):

```
                if res.indice is None:
                    if res.metodo == "código_ausente":
                        sem_match.append(f"{arq}  [código não cadastrado]")
                    else:
                        sem_match.append(str(arq))
                    continue
```

**Substituir por:**

```
                if res.indice is None:
                    # Motivo ESTRUTURADO, nao embutido no texto: a aba precisa
                    # agrupar e contar, e parsear string de volta seria frágil.
                    sem_match.append({
                        "caminho": str(arq),
                        "motivo": res.metodo,   # "código_ausente" | "nenhum"
                        "score": res.score,
                    })
                    continue
```

> O comentario acima da declaracao `sem_match = Signal(list)` ainda diz «arquivos sem correspondência» — continua verdadeiro e **nao precisa mudar**. O tipo `list` do Signal tambem nao muda.

## Edicao 4 — a aba agrupa por motivo e conta

**Ancora** (bloco contiguo, metodo inteiro de `AbaSemMatch`):

```
    def popular(self, arquivos: list[str]):
        if arquivos:
            self.lista.setPlainText("\n".join(arquivos))
        else:
            self.lista.setPlainText("(Nenhum arquivo sem correspondência — ótimo!)")
```

**Substituir por:**

```
    def popular(self, arquivos: list[dict]):
        """
        Agrupa por MOTIVO, porque os dois grupos pedem ações diferentes:
        "código não cadastrado" é trabalho na planilha (cadastrar o produto);
        "nenhuma correspondência" é trabalho no matching (baixar o threshold,
        conferir o nome). Misturar os dois numa lista só esconde essa diferença.
        Não vira aba separada: continuam sendo o mesmo destino do usuário.
        """
        if not arquivos:
            self.lista.setPlainText("(Nenhum arquivo sem correspondência — ótimo!)")
            return

        ausentes = [a for a in arquivos if a.get("motivo") == "código_ausente"]
        outros = [a for a in arquivos if a.get("motivo") != "código_ausente"]

        blocos = []
        if ausentes:
            blocos.append(
                f"CÓDIGO NÃO CADASTRADO ({len(ausentes)})\n"
                "O arquivo tem um código de referência claro que não existe na "
                "planilha.\nO motor NÃO tenta adivinhar por semelhança (DEC-006) — "
                "provavelmente\nfalta cadastrar o produto.\n\n"
                + "\n".join(a["caminho"] for a in ausentes)
            )
        if outros:
            blocos.append(
                f"SEM CORRESPONDÊNCIA ({len(outros)})\n"
                "Nenhuma linha passou do threshold. Confira o nome do arquivo ou "
                "baixe o threshold.\n\n"
                + "\n".join(
                    f"{a['caminho']}   (melhor score: {a.get('score', 0)})"
                    for a in outros
                )
            )
        self.lista.setPlainText(("\n\n" + "─" * 70 + "\n\n").join(blocos))
```

---

## Fora de escopo

- **Mexer no motor.** `matching_engine.py` nao e tocado. Se a transparencia revelar que um score esta errado, isso e achado para a proxima WO, nao conserto nesta.
- **Transformar a aba «Sem correspondencia» em tabela** com filtro e ordenacao. Ver custo (d): so quando houver evidencia de que o `QTextEdit` incomoda na pasta real.
- **Dois thresholds** (exibicao × selecao) e **`PesosScore` editavel**. Seguem no backlog.
- **Exportar a transparencia no log/CSV.** O `componentes` fica no dicionario e nao vai para o export. Nao pedido.
- **Desmarcar linha ambigua automaticamente.** Decisao (c), explicitamente recusada.

## Armadilhas desta WO

- **`IDX_NOVO_NOME` e `IDX_PASTA_DEST` mudam de numero.** Se alguem tiver escrito um indice literal em vez da constante, ele quebra em silencio — a celula errada e preenchida, sem excecao. `grep -n "setItem(row, [0-9]" main.py` deve devolver **0 linhas**.
- **A edicao 2 depende da edicao 1** (`IDX_PORQUE` e `resumir_match`). Aplicar fora de ordem deixa `NameError`.
- **As edicoes 3 e 4 andam juntas.** Aplicar so a 3 faz a aba tentar `"\n".join(dict)` e levantar `TypeError` na varredura; aplicar so a 4 faz o agrupamento receber strings e cair no bloco «outros» com `.get` em `str`. **Nao commite entre as duas.**
- **Nao rode o teste com cano.** `python ... | tail` devolve o codigo de saida do `tail`.
- **`grep -c` conta LINHA.** `ambiguo` aparece varias vezes; as conferencias abaixo usam simbolos exclusivos.

---

## Depois de aplicar — conferencia antes do commit

- [ ] `git diff --stat` mostra **exatamente** `main.py` e a propria WO. `UTILITÁRIOS/`, `test/` e `meta/` **nao podem aparecer**.
- [ ] `python -m pyflakes main.py` -> **nenhuma linha com `undefined name`**. (O `pyflakes` ja ficou instalado na WO 0005.)
- [ ] `grep -c "^IDX_PORQUE = 7" main.py` -> **1**.
- [ ] `grep -c "^def resumir_match" main.py` -> **1**.
- [ ] `grep -c "CÓDIGO NÃO CADASTRADO" main.py` -> **1**.
- [ ] `grep -c "código não cadastrado\]" main.py` -> **0** (a anotacao paliativa da WO 0005 tem de ter sumido).
- [ ] `grep -n "setItem(row, [0-9]" main.py` -> **nenhuma linha** (ninguem usa indice literal).
- [ ] `wc -l main.py` -> **1395** *(era 1298)*. Numero diferente nao reprova sozinho, mas **explique a diferenca no relatorio** antes de commitar.
- [ ] **Validacao do projeto:** `python UTILITÁRIOS/test_matching.py` (sem cano) -> **24/24**, exit **0**.
      *Chega no ramo?* **Nao chega.** O harness nao importa `main.py`; ele so prova que nada em `UTILITÁRIOS/` foi danificado por acidente. Quem valida esta WO e o teste manual.
- [ ] **Teste manual da GUI — a unica rede real desta WO.**
      - **Quem roda:** quem aplica (`python main.py`).
      - **Preparo:** `..\wo0006-imgs\` (**FORA do repo**) com quatro arquivos vazios:
        ```
        ALMEIDA - 00611 - PISO ACET RETIF 32HDA60 32X62 CX 1,95MT².jpg
        VIVA - VPC CREMA MI - PISO BRIL BOLD VPC CREMA MI 58X58 CX 2,35MT².jpg
        EMBRAMACO - P63005 - PISO POL RETIF MONT BLANC LUX 63X122 CX 2,30MT².jpg
        FOTO SEM CODIGO NENHUM.jpg
        ```
      - **O que fazer:** carregar `test\planilha_referencia.csv`, `Nome Imagem` como coluna de matching e de novo nome, apontar a pasta, escanear. **Nao execute renomeacao.**
      - **Esperado, aba «Correspondencias» — 2 linhas:**
        - `00611` -> Método `código`, «Por quê» = `código 00611`
        - `VPC CREMA MI` -> Método `fuzzy`, «Por quê» no formato `sort NN · wratio NN · cob NN · medida coincide`
        - **Passe o mouse** sobre a celula «Por quê» da linha fuzzy: o tooltip tem de abrir com as quatro linhas de componentes. Passe tambem sobre a celula «Score» da mesma linha — **o mesmo tooltip**. Tooltip que nao abre e o defeito mais provavel desta WO, e nenhum `grep` pega.
      - **Esperado, aba «Sem correspondencia» — dois blocos separados por uma regua:**
        - `CÓDIGO NÃO CADASTRADO (1)` com o `P63005`
        - `SEM CORRESPONDÊNCIA (1)` com o `FOTO SEM CODIGO NENHUM.jpg` e um `(melhor score: NN)`
        - Se aparecer `[código não cadastrado]` colado no caminho, a edicao 3 nao pegou.
      - **Prova de vida:** confirme **2 linhas** na tabela e **os dois blocos** na aba. Tabela vazia tambem «roda sem erro» — foi assim que o `NameError` da WO 0005 passou batido.
      - **Ambiguidade — nao da para testar com estes dados** *[medido: 0 casos ambiguos na referencia]*. **Nao invente um caso.** Rode este render forcado e cole a saida no relatorio:
        ```
        python -c "import sys;sys.path.insert(0,'UTILITÁRIOS');import main;print(main.resumir_match({'metodo':'código','codigo_casado':'X1','ambiguo':True})[0])"
        ```
        Esperado: `⚠ ambíguo · código X1`. Isso prova o **render**, nao o caminho de deteccao — declare no relatorio que a ambiguidade fim-a-fim segue **sem verificacao**.
      - **Limpeza:** apague `..\wo0006-imgs\` ao terminar. **Apague tambem o `config.json`** que a GUI grava na raiz ao carregar planilha (aconteceu na WO 0005 e nao entra no commit).
- [ ] Nada aberto fora do repositorio: sem processo, porta ou pasta pendurada.

## Relatorio de aplicacao *(quem aplica preenche ao terminar)*

O que foi feito · o que fugiu do texto literal · `wc -l` final · `pyflakes` · as contagens · golden set com exit code · **o texto das duas celulas «Por quê», o tooltip da linha fuzzy e os dois blocos da aba, copiados como apareceram** · a saida do render forcado de ambiguidade · o commit e o push.

## Commit

```
git add main.py meta/workorders/260905-wo0006-transparencia-na-tabela.md
```

```
git commit -m "feat: mostra na tabela por que cada arquivo casou" -m "Coluna Por que com resumo curto por metodo e tooltip com os componentes do score, na celula do resumo e na do score. Ambiguidade vira alerta visual (ambar na celula de score, prefixo na coluna) e nao desmarca o checkbox, para nao esconder arquivo do usuario. O sinal sem_match passa a carregar caminho, motivo e score em vez de string decorada, e a aba Sem correspondencia agrupa em CODIGO NAO CADASTRADO e SEM CORRESPONDENCIA com contagem, porque os dois pedem acoes diferentes: cadastrar o produto na planilha versus conferir nome ou baixar o threshold. Motor nao foi tocado. main.py de 1298 para 1395 linhas."
```

```
git push
```

*Formato do Kit de Contexto Universal v1.122.0.*
