# WO 0005 — Motor v2 na GUI (Parte B da WO 0003) e conserto do `main.py` quebrado

> **Tipo:** WO de CODIGO. Nao toca `meta/` — o registro vem no chat depois da validacao.
> **Config sugerida:** modelo capaz, `/effort` medio-alto. As nove edicoes sao substituicoes e remocoes com borda literal, todas ja aplicadas e testadas no sandbox do chat; o julgamento pesado esta feito. O que sobra e precisao.
> **URGENCIA:** o `main.py` em `main` esta **quebrado agora**. A Parte A trocou a leitura da planilha por uma chamada a `carregar_planilha()`, mas o `import` dessa funcao morava na Parte B, que nunca foi aplicada. A GUI levanta `NameError` na hora em que alguem carrega uma planilha. *[medido — `python -m pyflakes main.py` -> `main.py:1280:23: undefined name 'carregar_planilha'`, unico nome indefinido do arquivo]*
> **Pre-requisito:** HEAD `847a1dc`, `origin/main` sincronizado, arvore limpa exceto o nao rastreado `meta/workorders/260904-wo0003-integra-motor-v2-na-gui.md`. Se `main.py` aparecer modificado, **PARE e reporte**.
> **Base:** Parte B da WO 0003 (nunca aplicada), reancorada no `main.py` de hoje — a Parte A moveu tudo em ~28 linhas e as ancoras antigas **nao servem mais**.
> **Ancora semantica:** se um trecho-ancora nao bater EXATAMENTE, **PARE e reporte**.
> **Idempotencia:** antes de cada edicao, procure a frase-chave do texto NOVO. Se ja existir, PULE e diga no relatorio.
> **Ancoras lidas em:** 2026-09-05, no `main.py` de 1458 linhas do mount (`_MANIFEST_OAI.md` gerado em 2026-09-05 07:08, commit `847a1dc`). **Todas as nove edicoes foram aplicadas de verdade num clone deste mesmo arquivo**, com assercao de ancora unica em cada uma; nenhuma falhou. Resultado: 1458 -> 1298 linhas.
> **Fim de linha:** `main.py` e LF puro.
> **Proximo comando:** `/wrap`

> **Canal dos meta neste ciclo = CHAT.** Nao faca append em `meta/`. O chat entrega STATUS/DECISIONS/CHANGELOG depois de ver o relatorio.

---

## 1. Por que

Dois motivos, e o primeiro e urgente.

**O `main.py` esta quebrado no repositorio.** A Parte A (commit `39d3fb6`) substituiu o bloco de leitura por `self.df = carregar_planilha(caminho)` e removeu o `detectar_encoding` orfao. O `import` de `carregar_planilha` estava na **edicao B1**, do outro lado do corte Parte A / Parte B. A validacao da Parte A era `ast.parse`, que so ve sintaxe — `NameError` e de execucao. O golden set nao toca `main.py`. O teste manual da GUI estava na Parte B. Nenhuma das tres redes cobria esse ponto, e o defeito passou.

**Isso e erro de desenho da WO 0003**, nao de quem aplicou: a chamada e o import de uma mesma funcao foram separados em commits diferentes, criando um estado intermediario quebrado.

**O segundo motivo e o de sempre:** a GUI ainda casa arquivos com o motor antigo — `token_set_ratio`, sem exclusao de medida na extracao de codigo, sem guarda de codigo ausente, com deteccao de um sufixo so. O motor certo passa no golden set e nunca foi exercitado pela interface.

## 2. O que ja foi medido — nao repita este trabalho

Todas as nove edicoes foram aplicadas num clone do `main.py` atual e o resultado foi exercitado de cabeca, com PySide6 em modo `offscreen`. *[medido por instrumento — sandbox do chat, 2026-09-05]*

1. **Ancoras:** as nove bateram, cada uma com **exatamente 1 ocorrencia**. Nenhuma ambigua.
2. **Nomes indefinidos depois:** `pyflakes` -> **0**. Antes era 1 (`carregar_planilha`).
3. **Sobras do motor antigo:** `self.motor.df` 0 · `token_set_ratio` 0 · `class MotorMatching` 0 · `REGEX_CODIGO` 0 · `match["` 0. A unica ocorrencia de `rapidfuzz` que fica e o comentario de `pip install` no rodape, que continua correto (o motor v2 depende dele).
4. **Varredura de ponta a ponta**, contra a referencia congelada e uma pasta com os 24 nomes do golden set: **11 correspondencias + 13 sem match = 24**, batendo com o golden set. Metodos vistos: `código` e `fuzzy`. Os 13 sem match sairam **todos** anotados com `[código não cadastrado]`.
5. **As chaves de transparencia chegam** ao dicionario da tabela: `componentes`, `codigo_casado`, `ambiguo`.
6. **A regressao do sufixo composto foi provada consertada** — era o risco mais traicoeiro da Parte B, porque nao levanta excecao, so produz nome errado:

   ```
   sufixo detectado -> reescrito        novo nome
     '(A)'        -> '(Ambiente)'     ALMEIDA - 29102 - 00611 - ... (Ambiente).jpg
     '(A) v2'     -> '(Ambiente) _v2' ALMEIDA - 29102 - 00611 - ... (Ambiente) _v2.jpg
     ''           -> ''               ALMEIDA - 29102 - 00611 - ....jpg
   ```

7. **Golden set depois de tudo:** `python UTILITÁRIOS/test_matching.py` -> codigo de saida **0**.

**O que isso NAO prova:** a maquina do dono, a GUI de verdade (janela, cliques, preview, desfazer) e as pastas reais dele. O sandbox rodou `ThreadVarredura.run()` direto, sincrono, sem interface. Por isso o teste manual continua obrigatorio no checklist.

## Inventario — de onde saiu a lista de edicoes

A pergunta feita ao codigo foi *"o que no `main.py` depende do motor embutido?"*, grepando simbolo e nao prosa: `grep -n "fuzz\.\|rapidfuzz"`, `grep -n "limpar_valor_planilha(\|normalizar_texto(\|extrair_codigos(\|separar_sufixos(\|reescrever_sufixo(\|REGEX_CODIGO"`, `grep -n "MotorMatching(\|ThreadVarredura(\|self\.motor\."`.

**Sao 9 edicoes.** Fora do `MotorMatching` removido, os unicos usos dos utilitarios duplicados eram `limpar_valor_planilha` e `reescrever_sufixo`, ambos dentro de `ThreadVarredura.run()` — por isso o import novo traz **so esses dois**, e nao os cinco. **Confira a contagem.** Achou uma decima: **PARE e reporte**.

---

## Edicao 1 — imports (conserta o `NameError`)

**Ancora** (linha unica, ocorre 1 vez):

```
from rapidfuzz import fuzz, process
```

**Substituir por:**

```
# O motor v2 e o loader vivem em UTILITÁRIOS/. A pasta entra no sys.path em vez
# de virar pacote: nao renomeia nada e nao depende de o nome da pasta ser um
# identificador Python valido (ele tem acento).
sys.path.insert(0, str(Path(__file__).resolve().parent / "UTILITÁRIOS"))

from matching_engine import (  # noqa: E402  (depende do sys.path acima)
    MotorMatching,
    PesosScore,
    limpar_valor_planilha,
    reescrever_sufixo,
)
from spreadsheet_loader import carregar_planilha, coluna_como_texto  # noqa: E402
```

> **Armadilha:** `sys` (linha 6) e `Path` (linha 11) sao importados ANTES desta linha — confira que continuam la. Se algum tiver saido, **PARE**.
> **Nao "arrume" o `# noqa: E402`.** O import depende do `sys.path` da linha acima e nao pode subir.

## Edicao 2 — remove a `REGEX_CODIGO` duplicada

**Ancora** (bloco contiguo, quatro linhas + as duas linhas em branco seguintes):

```
# Regex para extração de código:
# Captura sequências alfanuméricas com 4+ chars que contenham ao menos 1 dígito
# Ex: 1660730013300, 00491, PR12147, 32HDA60
REGEX_CODIGO = re.compile(r'\b([A-Za-z]{0,4}\d[\dA-Za-z]{3,})\b')


```

**Remover o bloco inteiro.** A versao do motor exclui medidas (FIX-004); esta aqui nunca recebeu essa correcao.

> `REGEX_CHARS_PROIBIDOS`, logo acima, **fica** — e da GUI, nao do motor.

## Edicao 3 — remove os cinco utilitarios duplicados

**Borda inicial:**

```
def limpar_valor_planilha(texto: str) -> str:
```

**Borda final** (ultimas linhas de `reescrever_sufixo`, inclusive as duas linhas em branco):

```
        if entrada["detectar"].strip().lower() == sufixo_original.strip().lower():
            return entrada["reescrever"].strip()
    return sufixo_original


```

**Remover da borda inicial ate a borda final, inclusive.** Sao **84 linhas** *(contadas no sandbox)*. Saem: `limpar_valor_planilha`, `normalizar_texto`, `extrair_codigos`, `separar_sufixos`, `reescrever_sufixo`.

> **Nao remova** `sanitizar_nome_arquivo`, que vem logo depois, nem `carregar_config`/`salvar_config`/`nome_sem_colisao`. Essas sao da GUI e nao existem no motor.
> **Por que sair e nao ficar:** as versoes daqui estao ATRASADAS, nao apenas repetidas. `extrair_codigos` nao exclui medidas e `separar_sufixos`/`reescrever_sufixo` tratam um sufixo so.

## Edicao 4 — remove a classe `MotorMatching` embutida

**Borda inicial** (o divisor da secao entra junto, para nao sobrar titulo sem conteudo):

```
# ─────────────────────────────────────────────────────────────────────────────
# MOTOR DE MATCHING
# ─────────────────────────────────────────────────────────────────────────────

class MotorMatching:
```

**Borda final** (o `return` do bloco fuzzy, inclusive as duas linhas em branco):

```
        nome_match, score, idx = resultado
        return {
            "indice_df": idx,
            "nome_planilha": self.nomes_planilha[idx],
            "score": int(score),
            "metodo": "fuzzy",
            "base_arquivo": base,
            "sufixo_original": sufixo_original,
        }


```

**Remover da borda inicial ate a borda final, inclusive.** Sao **108 linhas** *(contadas no sandbox)*.

## Edicao 5 — `ThreadVarredura.__init__` recebe o `df` por fora

**Ancora** (bloco contiguo):

```
                 threshold: int, col_novo_nome: str, col_pasta_destino: str):
        super().__init__()
        self.pasta_raiz = Path(pasta_raiz)
        self.motor = motor
        self.threshold = threshold
```

**Substituir por:**

```
                 df, sufixos_cfg: list[dict], threshold: int,
                 col_novo_nome: str, col_pasta_destino: str):
        super().__init__()
        self.pasta_raiz = Path(pasta_raiz)
        self.motor = motor
        # O motor v2 e puro Python e NAO carrega o DataFrame (DEC-002), entao o
        # df e a config de sufixos vem por fora — antes vinham por dentro do
        # motor antigo (motor.df, motor.sufixos_cfg).
        self.df = df
        self.sufixos_cfg = sufixos_cfg
        self.threshold = threshold
```

## Edicao 6 — `run()` passa a consumir o `Resultado`

**Ancora** (bloco contiguo):

```
                match = self.motor.buscar(arq.name, self.threshold)
                if match is None:
                    sem_match.append(str(arq))
                    continue

                idx = match["indice_df"]
                linha = self.motor.df.iloc[idx]

                # Determina novo nome (limpa * # + da planilha)
                if self.col_novo_nome and self.col_novo_nome in self.motor.df.columns:
                    novo_nome_base = limpar_valor_planilha(str(linha[self.col_novo_nome]))
                else:
                    novo_nome_base = match["nome_planilha"]  # já foi limpo no MotorMatching

                # Aplica mapeamento de sufixo
                sufixo_reescrito = reescrever_sufixo(
                    match["sufixo_original"], self.motor.sufixos_cfg
                )
```

**Substituir por:**

```
                res = self.motor.buscar(arq.name, self.threshold)

                # O v2 sempre devolve um Resultado; "sem match" e indice None.
                # metodo pode ser "código_ausente" (DEC-006): arquivo com codigo
                # claro que nao existe na planilha. Por ora cai em "Sem
                # correspondência" como qualquer outro, mas levando o motivo.
                if res.indice is None:
                    if res.metodo == "código_ausente":
                        sem_match.append(f"{arq}  [código não cadastrado]")
                    else:
                        sem_match.append(str(arq))
                    continue

                idx = res.indice
                linha = self.df.iloc[idx]

                # Determina novo nome (limpa * # + da planilha)
                if self.col_novo_nome and self.col_novo_nome in self.df.columns:
                    novo_nome_base = limpar_valor_planilha(str(linha[self.col_novo_nome]))
                else:
                    novo_nome_base = self.motor.nomes_planilha[idx]  # ja limpo no motor

                # Aplica mapeamento de sufixo. O v2 detecta sufixos COMPOSTOS e
                # devolve "(A) v2"; o reescrever_sufixo do motor trata cada parte
                # e preserva a ordem — o do main.py nao tratava.
                sufixo_reescrito = reescrever_sufixo(
                    res.sufixo_original, self.sufixos_cfg
                )
```

## Edicao 7 — `run()`, coluna de pasta destino

**Ancora** (linha unica):

```
                if self.col_pasta_destino and self.col_pasta_destino in self.motor.df.columns:
```

**Substituir por:**

```
                if self.col_pasta_destino and self.col_pasta_destino in self.df.columns:
```

## Edicao 8 — `run()`, o dicionario da correspondencia

**Ancora 8a** (bloco contiguo):

```
                    "base_detectada": match["base_arquivo"],
                    "sufixo_detectado": match["sufixo_original"],
                    "sufixo_reescrito": sufixo_reescrito,
                    "nome_planilha": match["nome_planilha"],
                    "score": match["score"],
                    "metodo": match["metodo"],
```

**Substituir por:**

```
                    "base_detectada": res.base,
                    "sufixo_detectado": res.sufixo_original,
                    "sufixo_reescrito": sufixo_reescrito,
                    "nome_planilha": self.motor.nomes_planilha[idx],
                    "score": res.score,
                    "metodo": res.metodo,
```

**Ancora 8b** (bloco contiguo, fecho do mesmo dicionario):

```
                    "indice_df": idx,
                })
```

**Substituir por:**

```
                    "indice_df": idx,
                    # Transparencia do match — ainda NAO exibida na tabela.
                    # Guardada agora para a WO seguinte nao mexer aqui de novo.
                    "componentes": res.componentes,
                    "codigo_casado": res.codigo_casado,
                    "ambiguo": res.ambiguo,
                })
```

## Edicao 9 — instanciacao do motor e da thread

**Ancora 9a** (linha unica):

```
        self.motor = MotorMatching(self.df, col_matching, sufixos)
```

**Substituir por:**

```
        # O v2 recebe a coluna ja como lista de strings — ele nao conhece pandas.
        self.motor = MotorMatching(
            coluna_como_texto(self.df, col_matching),
            sufixos,
            PesosScore(),
        )
```

**Ancora 9b** (bloco contiguo, logo abaixo):

```
            pasta_raiz, self.motor, threshold, col_novo_nome, col_pasta_destino
        )
```

**Substituir por:**

```
            pasta_raiz, self.motor, self.df, sufixos, threshold,
            col_novo_nome, col_pasta_destino
        )
```

> `sufixos` e a variavel local definida algumas linhas acima (`sufixos = self.cfg.get("sufixos", CONFIG_PADRAO["sufixos"])`). Confirme que existe no escopo. Se tiver outro nome, **PARE**.

---

## Fora de escopo

- **Exibir a transparencia na tabela.** `componentes`, `codigo_casado` e `ambiguo` passam a ser CARREGADOS, mas **nao aparecem na UI**. Colunas novas e a aba de `código_ausente` sao a WO 0006, e dependem de decisao de UX que o dono ainda nao tomou. O `[código não cadastrado]` no texto da lista de sem-match e o minimo para nao perder o motivo — nao e a UX final.
- **Dois thresholds** (exibicao × selecao) e **`PesosScore` editavel**. Seguem no backlog.
- **`meta/CONTEXT.md`** — a armadilha do `dtype` e a nova estrutura de import entram no fecho, pelo chat, depois da validacao.
- **Transformar `UTILITÁRIOS/` em pacote** (`core/` + `__init__.py`). Mais limpo que o `sys.path.insert`, mas renomear pasta e decisao do dono e arrasta quatro documentos.
- **Rebuild do `.exe`.** Nao rode o PyInstaller aqui. Quando rodar, o `--onefile` vai precisar enxergar `UTILITÁRIOS/` — risco conhecido, nao um passo desta WO.

## Armadilhas desta WO

- **A ordem importa.** A edicao 1 poe o import; as 2, 3 e 4 removem o que ele substitui. Invertendo, o arquivo fica quebrado no meio e um `git diff` interrompido nao mostra isso.
- **As edicoes 3 e 4 sao remocoes por BORDA, nao por texto inteiro.** Confira que a borda final e a que esta na WO, e nao um trecho parecido mais adiante — as duas bordas foram verificadas como unicas no sandbox.
- **A edicao 6 e a maior.** Aplique-a inteira de uma vez; aplicar metade deixa `res` e `match` convivendo.
- **`grep -c` conta LINHA.** `self.df` aparece muitas vezes; as conferencias abaixo usam simbolos exclusivos.
- **Nao rode o teste com cano.** `python ... | tail` devolve o codigo de saida do `tail`, nao do Python. Esse erro ja aconteceu uma vez nesta serie de WOs.

---

## Depois de aplicar — conferencia antes do commit

- [ ] `git diff --stat` mostra **exatamente** `main.py` e a propria WO. Nada alem — em especial, `UTILITÁRIOS/` e `test/` **nao podem aparecer**.
- [ ] `python -m pyflakes main.py` -> **nenhuma linha com `undefined name`**. Se `pyflakes` nao estiver instalado, use `python -c "import ast; ast.parse(open('main.py',encoding='utf-8').read())"` e diga no relatorio que a checagem de nome indefinido **nao** foi feita — ela e a que pega o defeito que motivou esta WO.
- [ ] Cinco contagens, **uma por simbolo**, todas esperando **0**: `grep -c "class MotorMatching" main.py` · `grep -c "self.motor.df" main.py` · `grep -c "token_set_ratio" main.py` · `grep -c "REGEX_CODIGO" main.py` · `grep -c 'match\["' main.py`.
- [ ] `grep -c "^from matching_engine import" main.py` -> **1**.
- [ ] `grep -c "def limpar_valor_planilha" main.py` -> **0**; idem `normalizar_texto`, `extrair_codigos`, `separar_sufixos`, `reescrever_sufixo`. **Cinco checagens separadas.**
- [ ] `wc -l main.py` -> **1298** *(era 1458)*. Numero diferente nao e reprovacao automatica, mas **explique a diferenca no relatorio** antes de commitar.
- [ ] **Validacao do projeto:** `python UTILITÁRIOS/test_matching.py` (sem argumentos, **sem cano**) -> **24/24**, codigo de saida **0**. Diferente: **PARE, nao commite, feche com menu numerado.**
      *Chega no ramo?* **Nao chega.** O harness roda o motor direto e nao importa `main.py`. Ele so prova que nada em `UTILITÁRIOS/` foi danificado por acidente. Quem valida esta WO e o teste manual abaixo.
- [ ] **Teste manual da GUI — obrigatorio, e a unica rede real desta WO.**
      - **Quem roda:** quem aplica (`python main.py`). Execucao local reversivel.
      - **Preparo:** crie `..\wo0005-imgs\` (**pasta-pai, FORA do repo**) e ponha la 3 arquivos vazios com estes nomes exatos:
        ```
        ALMEIDA - 00611 - PISO ACET RETIF 32HDA60 32X62 CX 1,95MT².jpg
        ALMEIDA - 00611 - PISO ACET RETIF 32HDA60 32X62 CX 1,95MT² (A).jpg
        ALMEIDA - 00611 - PISO ACET RETIF 32HDA60 32X62 CX 1,95MT² (A)v2.jpg
        ```
      - **O que fazer:** abrir a GUI, carregar `test\planilha_referencia.csv`, escolher `Nome Imagem` como coluna de matching **e** como coluna de novo nome, apontar `..\wo0005-imgs\`, escanear. **Nao execute renomeacao** — so olhe o preview.
      - **Esperado, os tres em «Novo nome»:**
        ```
        ALMEIDA - 29102 - 00611 - PISO ACET RETIF 32HDA60 32X62 CX 1,95MT².jpg
        ALMEIDA - 29102 - 00611 - PISO ACET RETIF 32HDA60 32X62 CX 1,95MT² (Ambiente).jpg
        ALMEIDA - 29102 - 00611 - PISO ACET RETIF 32HDA60 32X62 CX 1,95MT² (Ambiente) _v2.jpg
        ```
        A terceira linha e o teste de verdade: se sair `(A) v2` em vez de `(Ambiente) _v2`, a edicao 3 nao removeu o `reescrever_sufixo` antigo. Coluna «Método» deve mostrar `código` nas tres.
      - **Prova de vida:** antes de aceitar «rodou sem erro», confirme que a tabela veio com **3 linhas**. Tabela vazia tambem «roda sem erro», e foi assim que o `NameError` desta WO passou batido.
      - **Segundo caso, negativo:** ponha tambem um arquivo `EMBRAMACO - P63005 - PISO POL RETIF MONT BLANC LUX 63X122 CX 2,30MT².jpg`. Ele deve cair em **«Sem correspondência»**, anotado com `[código não cadastrado]` — nunca casar com nada.
      - **Esta e qual pergunta?** «presta?». Ela **nao** responde nada sobre as colunas de transparencia: elas nao existem na tabela ainda, de proposito.
      - **Limpeza:** apague `..\wo0005-imgs\` ao terminar. Se sobrar, declare o caminho no relatorio.
- [ ] **Nada criado fora do repositorio ficou aberto.** Sem processo, porta ou pasta temporaria pendurada.

## Relatorio de aplicacao *(quem aplica preenche ao terminar)*

O que foi feito · o que fugiu do texto literal · `wc -l` final · o resultado do `pyflakes` · as cinco contagens · o golden set com o codigo de saida · **as quatro linhas do preview da GUI, copiadas como apareceram** · o commit e o push.

## Commit

```
git add main.py meta/workorders/260904-wo0003-integra-motor-v2-na-gui.md meta/workorders/260905-wo0005-motor-v2-na-gui.md
```

```
git commit -m "refactor: GUI passa a usar o motor de matching v2" -m "Conserta o NameError deixado pelo corte Parte A / Parte B da WO 0003: o main.py chamava carregar_planilha sem importar, e a GUI quebrava ao carregar planilha. Remove o MotorMatching embutido, a REGEX_CODIGO duplicada e os cinco utilitarios atrasados, e importa de UTILITARIOS/. ThreadVarredura passa a receber o DataFrame e a config de sufixos por fora, porque o motor v2 e puro Python e nao carrega pandas (DEC-002). O resultado leva componentes, codigo casado e flag de ambiguidade, ainda nao exibidos na tabela. Sem match por codigo ausente passa a ser anotado na lista. main.py de 1458 para 1298 linhas."
```

```
git push
```

*Formato do Kit de Contexto Universal v1.122.0.*
