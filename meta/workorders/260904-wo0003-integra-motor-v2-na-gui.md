# WO 0003 — Integra o motor v2 na GUI e corrige o FIX-005 na carga da planilha

> **Tipo:** WO de CODIGO (uma edicao de doc no `CLAUDE.md`, o resto e codigo).
> **Config sugerida:** modelo mais capaz, esforco alto. E refatoracao multi-ponto em arquivo grande (`main.py`, 1486 linhas) com contrato de retorno mudando; nao e mecanica.
> **Pre-requisito:**
> 1. Commit `efcdf3d` na `main`, arvore LIMPA, sincronizada com `origin/main`.
> 2. **O dono ja salvou o `.claude/settings.json` novo** (entregue pelo chat nesta rodada) — sem ele o executor **nao consegue rodar `python`** e esta WO nao tem como ser validada. Confira antes de comecar: o `allow` precisa conter `Bash(python:*)`. Se nao contiver, **PARE e reporte** — nao tente contornar, e config do executor e o classificador barra.
> 3. **O arquivo `UTILITÁRIOS/spreadsheet_loader.py` ja esta no disco** (entregue inteiro pelo chat nesta rodada). Se nao estiver, **PARE e reporte** — esta WO nao o cria.
> **Base:** FIX-005 (`meta/DECISIONS.md`), item 1 do backlog do `meta/STATUS.md`, ideia «Loader unico de planilha» (`meta/IDEAS.md`, 2026-09-04).
> **Depende de:** WO 0002 (aplicada, `50b369e`; fechada em `efcdf3d`).
> **Ancora semantica:** se um trecho-ancora nao bater EXATAMENTE, **PARE e reporte**.
> **Idempotencia:** antes de cada edicao, procure a frase-chave do texto NOVO. Se ja existir, PULE e diga no relatorio.
> **Ancoras lidas em:** 2026-09-04, pelo mount achatado (`_MANIFEST_OAI.md` gerado em 2026-09-04 14:43, commit `efcdf3d`, arvore limpa). Trechos literais lidos NESTE turno:
> - `main.py` linha 19: `from rapidfuzz import fuzz, process`
> - `main.py` linhas 114-195: as cinco funcoes duplicadas (`limpar_valor_planilha`, `normalizar_texto`, `extrair_codigos`, `separar_sufixos`, `reescrever_sufixo`)
> - `main.py` linha 225: `class MotorMatching:` ate a linha 326 (`        }`), imediatamente antes do divisor `# THREAD DE VARREDURA`
> - `main.py` linhas 341-348: assinatura de `ThreadVarredura.__init__`
> - `main.py` linhas 367-408: corpo de `ThreadVarredura.run()` que consome o dict
> - `main.py` linha 1381: `        self.motor = MotorMatching(self.df, col_matching, sufixos)`
> - `main.py` linhas 1293-1305: bloco de leitura da planilha em `_carregar_planilha`
> - `UTILITÁRIOS/test_matching.py` linhas 28-31: funcao `carregar_csv`
> - `CLAUDE.md` linhas 11-12: as duas linhas PLACEHOLDER de build/validacao
> **Fim de linha:** `main.py` e `test_matching.py` conferidos como LF puro; todas as ancoras abaixo cabem no criterio de bloco contiguo literal.
> **Proximo comando:** `/wrap`

> **Canal dos meta neste ciclo = CHAT.** Esta WO toca codigo e o `CLAUDE.md` da raiz — **nao faca append em `meta/`**. O chat entrega STATUS/DECISIONS/CHANGELOG depois de ver o resultado da validacao.

---

## 1. Por que

A GUI ainda roda o `MotorMatching` **antigo, embutido no proprio `main.py`** — o que usa `token_set_ratio`, nao exclui medidas da extracao de codigo, nao tem guarda de codigo ausente e detecta um sufixo so. Ou seja: a interface roda com o motor que **sabemos estar errado**, enquanto o motor certo (`matching_engine.py`, 24/24 no golden set) so e exercitado pelo harness.

Junto vai o FIX-005: a planilha e lida sem `dtype=str` em dois lugares independentes, o pandas infere `int64` numa coluna de codigo e `00611` vira `611`. Isso come o zero no nome final **e** mata o match por codigo. As duas correcoes andam juntas porque a segunda so tem uma forma decente — um ponto de carga unico — e esse ponto e justamente o que a primeira precisa para nao herdar a duplicacao.

## 2. O que uma troca ingenua quebraria *(leia antes de comecar)*

Trocar so a classe `MotorMatching` por um `import` **nao funciona**. Foram encontrados tres pontos, e todos os tres estao tratados nas edicoes abaixo:

1. **Contrato de retorno diferente.** O motor antigo devolve um `dict` (`indice_df`, `nome_planilha`, `base_arquivo`, `score`, `metodo`, `sufixo_original`) ou `None`. O v2 devolve sempre um `Resultado` (dataclass) com `indice` podendo ser `None`, e **nao devolve `nome_planilha`** — ele vive em `motor.nomes_planilha[idx]`.
2. **O motor v2 nao carrega o DataFrame.** Por design (DEC-002) ele e puro Python e recebe uma lista de strings. Mas `ThreadVarredura.run()` faz `self.motor.df.iloc[idx]` e `self.motor.df.columns` — isso **deixa de existir**. A thread precisa receber o `df` diretamente.
3. **`reescrever_sufixo` duplicado e incompativel.** O `separar_sufixos` do v2 detecta sufixos COMPOSTOS e devolve `"(A) v2"` (juntos por espaco); o `reescrever_sufixo` que ainda vive no `main.py` compara a string inteira contra um sufixo so, nao acha, e devolve `"(A) v2"` cru. O nome final sairia com `(A) v2` literal em vez de `(Ambiente) _v2`. **Este e o mais traicoeiro**: nao levanta excecao, so produz nome errado em silencio. Por isso as cinco funcoes duplicadas saem do `main.py` e passam a vir do motor.

## Inventario — de onde saiu a lista de edicoes

A pergunta feita ao codigo foi *"que pontos do `main.py` dependem do motor embutido ou da leitura de planilha?"*, grepando os simbolos e nao a prosa (`grep -n "limpar_valor_planilha(\|normalizar_texto(\|extrair_codigos(\|separar_sufixos(\|reescrever_sufixo(\|REGEX_CODIGO"`, `grep -n "fuzz\.\|process\.\|rapidfuzz"`, `grep -n "MotorMatching("`, `grep -n "read_csv\|read_excel\|detectar_encoding"`).

**Sao 9 pontos em `main.py`, 1 em `test_matching.py` e 2 no `CLAUDE.md`** — 12 no total, todos cobertos pelas edicoes abaixo:

| # | Ponto | Onde | Edicao |
|---|---|---|---|
| 1 | `from rapidfuzz import fuzz, process` (fica orfao) | `main.py` ~19 | B1 |
| 2 | `REGEX_CODIGO` duplicado | `main.py` ~68 | B2 |
| 3 | `detectar_encoding` (fica orfao apos A2) | `main.py` ~99 | A3 |
| 4 | 5 utilitarios duplicados | `main.py` ~114-195 | B2 |
| 5 | classe `MotorMatching` embutida | `main.py` ~225-326 | B3 |
| 6 | `ThreadVarredura.__init__` | `main.py` ~341 | B4 |
| 7 | `ThreadVarredura.run()` (consumo do dict) | `main.py` ~367-408 | B5 |
| 8 | bloco de leitura da planilha | `main.py` ~1293-1305 | A2 |
| 9 | `MotorMatching(self.df, ...)` + `ThreadVarredura(...)` | `main.py` ~1381-1389 | B6 |
| 10 | `carregar_csv` do harness | `test_matching.py` ~28-31 | A4 |
| 11 | linha de build PLACEHOLDER | `CLAUDE.md` 11 | C1 |
| 12 | linha de validacao PLACEHOLDER | `CLAUDE.md` 12 | C1 |

**Confira esta contagem antes de editar.** Achou um 13º ponto: **PARE e reporte** — a divergencia e o achado.

---

## Passo 0 — Medicao previa (nao e edicao, nao commita nada)

Esta WO precisa de um numero que a raia de planejamento nao consegue ler: **o caminho do export da planilha-mestre em disco**. Ele nao e versionado (nao esta no `.gitignore` porque nunca esteve no repo) e sem ele o golden set nao roda.

O que contar/achar, e o comando sugerido (Git Bash interno):

```
ls -la ../*.csv ../*.xlsx 2>/dev/null; ls -la *.csv *.xlsx 2>/dev/null; ls -la test/
```

Devolva o **caminho cru e o comando que o produziu**, sem interpretacao. Se houver mais de um candidato, liste todos com data de modificacao e **nao escolha** — reporte e pare. Se nao houver nenhum, **PARE e reporte**: sem planilha nao ha validacao, e uma WO de codigo sem validacao nao pode ser commitada.

---

## PARTE A — Carga unica da planilha (FIX-005)

> Pare ao fim da Parte A e rode a verificacao A antes de comecar a Parte B. Se a Parte A quebrar o golden set, o suspeito nº 1 **nao** e o `dtype`: e a deteccao de separador, que o harness fazia com o sniffer do pandas (`sep=None`) e agora faz pela contagem na primeira linha. Reporte o numero antes de mexer.

### Edicao A1 — arquivo novo `UTILITÁRIOS/spreadsheet_loader.py`

**Nao crie este arquivo.** Ele foi entregue inteiro pelo chat nesta rodada. Confirme que esta no disco e **PARE se nao estiver**. Ele entra no `git add` do commit A.

### Edicao A2 — `main.py` · troca o bloco de leitura pelo loader

**Ancora** (dentro de `def _carregar_planilha`, bloco contiguo):

```
        try:
            if caminho.lower().endswith(".csv"):
                enc = detectar_encoding(caminho)
                # Tenta detectar separador
                with open(caminho, encoding=enc, errors="replace") as f:
                    primeira_linha = f.readline()
                sep = ";" if primeira_linha.count(";") > primeira_linha.count(",") else ","
                self.df = pd.read_csv(
                    caminho, encoding=enc, sep=sep,
                    on_bad_lines="skip", low_memory=False
                )
            else:
                self.df = pd.read_excel(caminho, engine="openpyxl")

            self.df.columns = [str(c).strip() for c in self.df.columns]
```

**Substituir por:**

```
        try:
            # Carga SEMPRE como texto — ver FIX-005. A limpeza dos nomes de
            # coluna acontece dentro de carregar_planilha().
            self.df = carregar_planilha(caminho)
```

### Edicao A3 — `main.py` · remove o `detectar_encoding` orfao

Apos a edicao A2, `detectar_encoding` nao tem mais nenhuma chamada no `main.py` (era usada so na linha removida) e existe duplicada, ja corrigida, dentro do loader.

**Ancora** (bloco contiguo, funcao inteira):

```
def detectar_encoding(caminho: str) -> str:
    """Usa chardet para detectar encoding do arquivo; fallback utf-8-sig."""
    try:
        with open(caminho, "rb") as f:
            raw = f.read(32768)
        resultado = chardet.detect(raw)
        enc = resultado.get("encoding") or "utf-8-sig"
        # Normalizar variantes do UTF-8 com BOM
        if enc.lower() in ("utf-8-sig", "utf-8-bom"):
            return "utf-8-sig"
        return enc
    except Exception:
        return "utf-8-sig"


```

**Remover o bloco inteiro** (inclusive as duas linhas em branco finais, para nao sobrar um vao triplo).

> `import chardet` (linha 11) fica **orfao no `main.py` depois disto**. Remova-o tambem: ancora `import chardet` na linha de import (ocorre 1 vez) — remover a linha inteira. Se o `grep` acusar mais de uma ocorrencia, **PARE**.

### Edicao A4 — `UTILITÁRIOS/test_matching.py` · usa o mesmo loader

**Ancora** (bloco contiguo, funcao inteira):

```
def carregar_csv(caminho: str) -> pd.DataFrame:
    with open(caminho, "rb") as f:
        enc = chardet.detect(f.read())["encoding"] or "utf-8-sig"
    return pd.read_csv(caminho, encoding=enc, sep=None, engine="python")
```

**Substituir por:**

```
def carregar_csv(caminho: str) -> pd.DataFrame:
    """
    Carrega a planilha pelo MESMO caminho que a GUI usa.

    O harness precisa ler exatamente como o programa le — senao ele valida
    uma configuracao que o usuario nunca executa. Foi assim que o FIX-005
    passou despercebido por 24/24.
    """
    return carregar_planilha(caminho)
```

E, no topo de `test_matching.py`, **ancora**:

```
from matching_engine import MotorMatching, PesosScore
```

**Substituir por:**

```
from matching_engine import MotorMatching, PesosScore
from spreadsheet_loader import carregar_planilha
```

> `import chardet` no topo do `test_matching.py` tambem fica orfao. Remova a linha `import chardet` (ocorre 1 vez).

### Verificacao A — rode ANTES de comecar a Parte B

- **Quem roda:** quem aplica. E leitura + execucao local reversivel; nao toca rede de terceiro nem destroi nada.
- **Comando:** `python UTILITÁRIOS/test_matching.py <planilha-medida-no-passo-0> test/golden_set.csv 70`
- **Esperado:** **24/24 (100%)**. A Parte A nao muda regra de matching nenhuma — muda so COMO a planilha entra. Qualquer numero diferente de 24 e regressao: **PARE, reporte o numero e nao commite.**
- **Chega no ramo?** `test_matching.py:main()` -> `carregar_csv()` -> `spreadsheet_loader.carregar_planilha()` — o caminho passa pelo codigo que A4 e A1 mudaram.
- **Esta e qual pergunta?** «presta?», parcialmente: prova que a carga nova nao regrediu o que ja funcionava. **NAO prova que o FIX-005 foi corrigido** — o golden set casa contra a coluna descritiva, que nunca teve o defeito. Quem responde isso e a Verificacao FIX-005, abaixo.
- **Prova de vida:** antes de comemorar o 24/24, confirme que o harness realmente rodou com o arquivo novo — `python -c "import sys; sys.path.insert(0,'UTILITÁRIOS'); import spreadsheet_loader; print(spreadsheet_loader.__file__)"` deve imprimir o caminho do loader. Sem isso, um `carregar_csv` antigo em cache daria o mesmo 24/24 sem nada ter mudado.

### Verificacao FIX-005 — o par negativo (obrigatoria)

O golden set nao alcanca este defeito. Force o sinal com um arquivo descartavel:

- **Quem roda:** quem aplica.
- **Como:** crie `../fix005-check.csv` (**pasta-pai, FORA do repo**) com duas linhas — cabecalho `Codigo Referencia,Descricao` e a linha `00611,PISO ACET RETIF`. Rode:

```
python -c "import sys; sys.path.insert(0,'UTILITÁRIOS'); from spreadsheet_loader import carregar_planilha; print(repr(carregar_planilha('../fix005-check.csv')['Codigo Referencia'][0]))"
```

- **Esperado:** imprime `'00611'`. Se imprimir `'611'`, a correcao **nao pegou** — PARE e reporte.
- **Par negativo:** rode a mesma linha trocando `carregar_planilha(...)` por `__import__('pandas').read_csv('../fix005-check.csv')` e confirme que ELA imprime `611`. So depois de ver o `611` do jeito antigo o `00611` do jeito novo significa alguma coisa.
- **Limpeza:** **apague `../fix005-check.csv` ao terminar.** Quem abre, fecha. Se por algum motivo nao der para apagar, declare o caminho no relatorio.

### Commit A

```
git add UTILITÁRIOS/spreadsheet_loader.py main.py UTILITÁRIOS/test_matching.py
```

```
git commit -m "fix: le a planilha sempre como texto (FIX-005)" -m "Carga passa por um loader unico com dtype=str e keep_default_na=False, usado pela GUI e pelo harness. Sem isso o pandas inferia int64 numa coluna de codigo e 00611 virava 611, o que comia o zero no nome final e matava o match por codigo. Ver meta/DECISIONS.md FIX-005."
```

```
git push
```

---

## PARTE B — Motor v2 no lugar do embutido

### Edicao B1 — `main.py` · imports

**Ancora:**

```
from rapidfuzz import fuzz, process
```

**Substituir por:**

```
# O motor de matching v2 e o loader vivem em UTILITÁRIOS/. A pasta entra no
# sys.path em vez de virar pacote: nao renomeia nada e nao depende de o nome
# da pasta ser um identificador Python valido. Ver IDEAS (2026-09-04).
sys.path.insert(0, str(Path(__file__).parent / "UTILITÁRIOS"))

from matching_engine import (  # noqa: E402  (import depende do sys.path acima)
    MotorMatching,
    PesosScore,
    limpar_valor_planilha,
    normalizar_texto,
    extrair_codigos,
    separar_sufixos,
    reescrever_sufixo,
)
from spreadsheet_loader import carregar_planilha  # noqa: E402
```

> **Armadilha:** `sys` e `Path` sao importados nas linhas 6 e 12, ANTES desta — confira que continuam la antes de aplicar. Se algum tiver saido, **PARE**.

### Edicao B2 — `main.py` · remove os utilitarios duplicados

**Ancora** (bloco contiguo — comeca no comentario da regex e termina na ultima linha de `reescrever_sufixo`):

```
# Regex para extração de código:
# Captura sequências alfanuméricas com 4+ chars que contenham ao menos 1 dígito
# Ex: 1660730013300, 00491, PR12147, 32HDA60
REGEX_CODIGO = re.compile(r'\b([A-Za-z]{0,4}\d[\dA-Za-z]{3,})\b')
```

**Remover o bloco inteiro.**

Depois, **ancora** (bloco contiguo das cinco funcoes, de `def limpar_valor_planilha` ate o `return sufixo_original` de `reescrever_sufixo`) — remova as **cinco funcoes inteiras**: `limpar_valor_planilha`, `normalizar_texto`, `extrair_codigos`, `separar_sufixos`, `reescrever_sufixo`. Elas passam a vir do `matching_engine`.

**Nao remova** `carregar_config`, `salvar_config`, `sanitizar_nome_arquivo` nem `nome_sem_colisao` — essas sao da GUI e nao existem no motor.

> **Por que sair, e nao ficar:** as versoes do `main.py` estao ATRASADAS, nao apenas repetidas. `extrair_codigos` nao exclui medidas (FIX-004 nunca chegou aqui) e `separar_sufixos`/`reescrever_sufixo` tratam um sufixo so. Deixar as duas versoes convivendo e garantir que a errada ganhe em algum ponto.

### Edicao B3 — `main.py` · remove a classe `MotorMatching` embutida

**Ancora inicial** (linha unica, ocorre 1 vez):

```
class MotorMatching:
```

**Remover** dessa linha ate — inclusive — a linha `        }` que fecha o `return` do bloco fuzzy, imediatamente antes do divisor:

```
# ─────────────────────────────────────────────────────────────────────────────
# THREAD DE VARREDURA
```

Mantenha o divisor e o cabecalho `# MOTOR DE MATCHING` que vem antes da classe **so se** voce puser algo no lugar; caso contrario **remova tambem o divisor `# MOTOR DE MATCHING`**, para nao deixar uma secao vazia com titulo.

> **Confira:** apos esta edicao, `grep -c "class MotorMatching" main.py` deve dar **0** (a classe agora vem do import).

### Edicao B4 — `main.py` · `ThreadVarredura` passa a receber o `df`

**Ancora** (bloco contiguo):

```
    def __init__(self, pasta_raiz: str, motor: MotorMatching,
                 threshold: int, col_novo_nome: str, col_pasta_destino: str):
        super().__init__()
        self.pasta_raiz = Path(pasta_raiz)
        self.motor = motor
        self.threshold = threshold
        self.col_novo_nome = col_novo_nome
        self.col_pasta_destino = col_pasta_destino
```

**Substituir por:**

```
    def __init__(self, pasta_raiz: str, motor: MotorMatching, df,
                 sufixos_cfg: list[dict], threshold: int,
                 col_novo_nome: str, col_pasta_destino: str):
        super().__init__()
        self.pasta_raiz = Path(pasta_raiz)
        self.motor = motor
        # O motor v2 e puro Python e NAO carrega o DataFrame (DEC-002), entao
        # o df e a config de sufixos vem por fora — antes vinham por dentro do
        # motor antigo (`motor.df`, `motor.sufixos_cfg`).
        self.df = df
        self.sufixos_cfg = sufixos_cfg
        self.threshold = threshold
        self.col_novo_nome = col_novo_nome
        self.col_pasta_destino = col_pasta_destino
```

### Edicao B5 — `main.py` · `run()` consome o `Resultado` do v2

**Ancora** (bloco contiguo, do `match = ...` ate o fecho do dict de correspondencia):

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
                if sufixo_reescrito:
                    novo_nome_base = f"{novo_nome_base} {sufixo_reescrito}"

                novo_nome = sanitizar_nome_arquivo(novo_nome_base) + arq.suffix

                # Pasta destino
                pasta_destino_val = ""
                if self.col_pasta_destino and self.col_pasta_destino in self.motor.df.columns:
                    pasta_destino_val = str(linha[self.col_pasta_destino]).strip()

                correspondencias.append({
                    "selecionado": True,
                    "caminho_original": str(arq),
                    "nome_original": arq.name,
                    "base_detectada": match["base_arquivo"],
                    "sufixo_detectado": match["sufixo_original"],
                    "sufixo_reescrito": sufixo_reescrito,
                    "nome_planilha": match["nome_planilha"],
                    "score": match["score"],
                    "metodo": match["metodo"],
                    "novo_nome": novo_nome,
                    "pasta_destino": pasta_destino_val,
                    "indice_df": idx,
                })
```

**Substituir por:**

```
                res = self.motor.buscar(arq.name, self.threshold)

                # O v2 sempre devolve um Resultado; "sem match" e indice None.
                # `metodo` pode ser "código_ausente" (DEC-006): o arquivo tem
                # codigo claro que nao existe na planilha. Por enquanto ele cai
                # em "Sem correspondência" como qualquer outro, mas levando o
                # motivo junto — a aba/filtro proprio ainda nao foi decidido.
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
                # separadamente e preserva a ordem.
                sufixo_reescrito = reescrever_sufixo(
                    res.sufixo_original, self.sufixos_cfg
                )
                if sufixo_reescrito:
                    novo_nome_base = f"{novo_nome_base} {sufixo_reescrito}"

                novo_nome = sanitizar_nome_arquivo(novo_nome_base) + arq.suffix

                # Pasta destino
                pasta_destino_val = ""
                if self.col_pasta_destino and self.col_pasta_destino in self.df.columns:
                    pasta_destino_val = str(linha[self.col_pasta_destino]).strip()

                correspondencias.append({
                    "selecionado": True,
                    "caminho_original": str(arq),
                    "nome_original": arq.name,
                    "base_detectada": res.base,
                    "sufixo_detectado": res.sufixo_original,
                    "sufixo_reescrito": sufixo_reescrito,
                    "nome_planilha": self.motor.nomes_planilha[idx],
                    "score": res.score,
                    "metodo": res.metodo,
                    "novo_nome": novo_nome,
                    "pasta_destino": pasta_destino_val,
                    "indice_df": idx,
                    # Transparencia do match — ainda NAO exibida na tabela.
                    # Guardada agora para a WO seguinte nao ter de mexer aqui.
                    "componentes": res.componentes,
                    "codigo_casado": res.codigo_casado,
                    "ambiguo": res.ambiguo,
                })
```

### Edicao B6 — `main.py` · instanciacao do motor e da thread

**Ancora** (bloco contiguo):

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

E, logo abaixo, **ancora**:

```
        self.thread_varredura = ThreadVarredura(
            pasta_raiz, self.motor, threshold, col_novo_nome, col_pasta_destino
        )
```

**Substituir por:**

```
        self.thread_varredura = ThreadVarredura(
            pasta_raiz, self.motor, self.df, sufixos, threshold,
            col_novo_nome, col_pasta_destino
        )
```

> A edicao B6 usa `coluna_como_texto`, que vive no loader. Acrescente-a ao import da edicao B1: `from spreadsheet_loader import carregar_planilha, coluna_como_texto`.

---

## PARTE C — Preencher o comando de validacao do projeto

### Edicao C1 — `CLAUDE.md` · troca os dois PLACEHOLDER

**Ancora** (bloco contiguo, duas linhas):

```
- Build: `<seu comando de build, ex.: npm run build>`  (PLACEHOLDER — troque pelo do seu projeto)
- Testes/validação: `<seu comando de teste>` — rode antes de commitar mudança de código.
```

**Substituir por:**

```
- Build: `pyinstaller --onefile --windowed main.py` — gera `dist/OrganizadorArquivos.exe`. **Só quando o dono pedir um executável**; não faz parte da validação de rotina.
- Testes/validação: `python UTILITÁRIOS/test_matching.py <planilha.csv> test/golden_set.csv 70` — alvo **24/24** no golden set. Troque `<planilha.csv>` pelo export mais recente da planilha-mestre em disco (ele **não é versionado**); se não achar nenhum, PARE e reporte em vez de pular o teste. Rode antes de commitar qualquer mudança em `main.py`, `UTILITÁRIOS/matching_engine.py` ou `UTILITÁRIOS/spreadsheet_loader.py`.
```

---

## Fora de escopo

- **Exibir a transparencia do match na tabela.** `componentes`, `codigo_casado` e `ambiguo` passam a ser CARREGADOS (edicao B5) mas **nao aparecem na UI**. As colunas e a aba de `código_ausente` sao a WO seguinte, e dependem de decisao de UX que o dono ainda nao tomou.
- **Dois thresholds** (exibicao × selecao) e **`PesosScore` editavel** na aba Configuracoes. Seguem no backlog.
- **Ampliar o golden set** com caso de zero a esquerda contra coluna de codigo pura. Depende da planilha real; a Verificacao FIX-005 acima e o substituto provisorio, e ela nao e versionada.
- **Transformar `UTILITÁRIOS/` em pacote Python** (renomear para `core/` + `__init__.py`). E mais limpo que o `sys.path.insert` da edicao B1, mas renomear pasta e decisao do dono e arrasta `CLAUDE.md`, `CONTEXT.md`, `STATUS.md` e a caixa de instrucoes. Vira ideia, nao esta WO.
- **Rebuild do `.exe`.** Nao rode o PyInstaller nesta WO. Quando rodar, lembre que o `--onefile` precisa passar a enxergar `UTILITÁRIOS/` — e um risco conhecido, nao um passo daqui.

## Armadilhas desta WO

- **A ordem importa.** A3 depende de A2 ja ter removido a unica chamada de `detectar_encoding`. B2 depende de B1 ja ter posto o import — se remover as funcoes antes de importar, o arquivo fica quebrado no meio e um `git diff` interrompido nao mostra isso.
- **`sufixos` na edicao B6** e a variavel local definida algumas linhas acima (`sufixos = self.cfg.get("sufixos", CONFIG_PADRAO["sufixos"])`). Confirme que ela existe no escopo antes de aplicar; se tiver outro nome, **PARE**.
- **O `# noqa: E402`** nas linhas de import da B1 e proposital: o import depende do `sys.path` alterado logo acima, entao ele nao pode subir para o topo. Nao "arrume" isso.
- **`grep -c` e por LINHA.** A frase `dtype=str` aparece varias vezes no loader e nesta WO; nao a use como contagem de verificacao. As verificacoes abaixo usam simbolos exclusivos.
- **Nao commite Parte A e Parte B juntas.** Se a B quebrar, o commit A ja empurrado e o ponto de retorno — e ele sozinho ja entrega a correcao do FIX-005 ao dono.

---

## Depois de aplicar — conferencia antes do commit B

- [ ] `git diff` mostra **exatamente** `main.py`, `UTILITÁRIOS/test_matching.py`, `CLAUDE.md` e a propria WO, e nada alem.
- [ ] `grep -c "class MotorMatching" main.py` -> **0**.
- [ ] `grep -c "^from matching_engine import" main.py` -> **1**.
- [ ] `grep -c "self.motor.df" main.py` -> **0** (o motor v2 nao tem `.df`; qualquer sobra e crash em runtime).
- [ ] `grep -c "token_set_ratio" main.py` -> **0**.
- [ ] `grep -c "def limpar_valor_planilha" main.py` -> **0**; idem `normalizar_texto`, `extrair_codigos`, `separar_sufixos`, `reescrever_sufixo`. **Sao cinco checagens, uma por funcao** — nao agrupe.
- [ ] `python -c "import ast,sys; ast.parse(open('main.py',encoding='utf-8').read())"` roda sem erro (o arquivo continua sintaticamente valido depois das remocoes).
- [ ] **Validacao do projeto:** `python UTILITÁRIOS/test_matching.py <planilha-do-passo-0> test/golden_set.csv 70` -> **24/24**. Diferente disso: **PARE, nao commite, e feche com menu numerado.**
- [ ] **Teste manual que a validacao NAO cobre** — a validacao roda o motor, nunca a GUI. Este passo e o unico que exercita a integracao de verdade:
      - **Quem roda:** quem aplica (`python main.py`; e execucao local reversivel, nao e do dono).
      - **O que fazer:** carregar a planilha medida no passo 0, escolher a coluna de matching, apontar a pasta de imagens do dono se houver — **ou uma pasta com 3 arquivos de nome copiado do golden set, criada em `../` e apagada depois** — e escanear.
      - **Esperado:** a varredura termina sem excecao; a coluna «Método» mostra `código` / `fuzzy` / `nenhum`; um arquivo com sufixo composto `(A)v2` produz novo nome terminando em `(Ambiente) _v2` e **nao** em `(A) v2`.
      - **Chega no ramo?** `JanelaPrincipal._escanear()` -> `MotorMatching(...)` (B6) -> `ThreadVarredura.run()` (B4/B5) -> `reescrever_sufixo` importado do motor (B1/B2). O teste do `(A)v2` e justamente o que prova que a funcao certa venceu.
      - **Esta e qual pergunta?** «presta?». Ela NAO responde «esta la?» para as colunas de transparencia — elas nao existem na tabela ainda, de proposito.
      - **Prova de vida:** antes de aceitar «rodou sem erro», confirme que a tabela veio com pelo menos uma linha. Tabela vazia tambem «roda sem erro».
- [ ] **O que foi criado FORA do repositorio ja foi fechado?** `../fix005-check.csv` e qualquer pasta de teste. O que sobrar entra no relatorio **com o caminho**.

## Relatorio de aplicacao *(quem aplica preenche ao terminar)*

O que foi feito · o que fugiu do texto literal da WO · arquivos tocados · **o numero do golden set antes e depois** · o resultado do teste manual da GUI · os dois commits e os dois pushes. Escreva depois de resolver o segundo push.

## Commit B

```
git add main.py UTILITÁRIOS/test_matching.py CLAUDE.md meta/workorders/260904-wo0003-integra-motor-v2-na-gui.md
```

```
git commit -m "refactor: GUI passa a usar o motor de matching v2" -m "Remove o MotorMatching embutido e os cinco utilitarios duplicados do main.py e importa de UTILITARIOS/matching_engine.py. ThreadVarredura passa a receber o DataFrame e a config de sufixos por fora, porque o motor v2 e puro Python e nao carrega pandas (DEC-002). Resultado do motor carrega componentes, codigo casado e flag de ambiguidade, ainda nao exibidos na tabela. Preenche o comando de validacao no CLAUDE.md."
```

```
git push
```

*Formato do Kit de Contexto Universal v1.122.0.*
