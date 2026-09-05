"""
test_matching.py — Harness do golden set do motor de matching.

Uso:
    python UTILITÁRIOS/test_matching.py [planilha.csv] [golden_set.csv] [threshold]

Sem argumentos roda contra a REFERÊNCIA CONGELADA em `test/` — e esse é o modo
normal. O harness não deve depender de alguém achar um export solto no disco:
foi exatamente isso que custou um ciclo inteiro em 2026-09-04 (ver DEC-008).

Chave de verdade: a coluna `Interno` (código interno da loja), não o índice da
linha. Índice absoluto muda a cada reexport e não é propriedade do produto.

Código de saída: 0 se todos os casos passam, 1 se algum falha, 2 se o insumo
está errado (coluna ausente, arquivo faltando). Instrumento que não reprova
ninguém não roda.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from matching_engine import MotorMatching, PesosScore  # noqa: E402
from spreadsheet_loader import carregar_planilha  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
PLANILHA_PADRAO = RAIZ / "test" / "planilha_referencia.csv"
GOLDEN_PADRAO = RAIZ / "test" / "golden_set.csv"

# Colunas EXPLÍCITAS. Não há fallback por adivinhação: um harness que escolhe
# sozinho a coluna e não diz qual escolheu troca em silêncio o que está medindo.
COL_MATCHING = "Nome Imagem"
COL_IDENTIDADE = "Interno"

SEM_MATCH = "SEM_MATCH"

SUFIXOS_PADRAO = [
    {"detectar": "(A)v2", "reescrever": "(Ambiente)_v2"},
    {"detectar": "(A)",   "reescrever": "(Ambiente)"},
    {"detectar": "(a)",   "reescrever": "(Ambiente)"},
    {"detectar": "v2",    "reescrever": "_v2"},
    {"detectar": "v3",    "reescrever": "_v3"},
    {"detectar": "face 2", "reescrever": "_face2"},
    {"detectar": "face 3", "reescrever": "_face3"},
]


def morrer(mensagem: str) -> None:
    """Aborta com código 2: o problema é do insumo, não do motor."""
    print(f"\n[INSUMO INVÁLIDO] {mensagem}\n", file=sys.stderr)
    sys.exit(2)


def exigir_colunas(df: pd.DataFrame, caminho: Path) -> None:
    """Falha alto se a planilha não tem as colunas nomeadas."""
    faltando = [c for c in (COL_MATCHING, COL_IDENTIDADE) if c not in df.columns]
    if faltando:
        morrer(
            f"{caminho} não tem a(s) coluna(s) {faltando}.\n"
            f"Colunas encontradas: {list(df.columns)}\n"
            f"O harness NÃO escolhe coluna sozinho — corrija o arquivo ou as "
            f"constantes COL_MATCHING/COL_IDENTIDADE."
        )
    if df[COL_IDENTIDADE].astype(str).str.strip().eq("").any():
        morrer(f"{caminho}: a coluna '{COL_IDENTIDADE}' tem valor vazio; "
               f"ela é a chave de identidade e precisa estar completa.")


def main() -> int:
    planilha = Path(sys.argv[1]) if len(sys.argv) > 1 else PLANILHA_PADRAO
    golden_csv = Path(sys.argv[2]) if len(sys.argv) > 2 else GOLDEN_PADRAO
    threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 70.0

    for caminho in (planilha, golden_csv):
        if not caminho.exists():
            morrer(f"arquivo não encontrado: {caminho}")

    df = carregar_planilha(planilha)
    exigir_colunas(df, planilha)

    nomes = df[COL_MATCHING].fillna("").astype(str).tolist()
    identidades = df[COL_IDENTIDADE].astype(str).str.strip().tolist()

    golden = pd.read_csv(golden_csv, encoding="utf-8", sep=",", dtype=str,
                         keep_default_na=False)
    if "interno_esperado" not in golden.columns:
        morrer(f"{golden_csv} não tem a coluna 'interno_esperado'. "
               f"Golden set no formato antigo (indice_esperado)? Ver DEC-008.")

    motor = MotorMatching(nomes, SUFIXOS_PADRAO, PesosScore())

    acertos, erros = 0, []
    for _, linha in golden.iterrows():
        arquivo = str(linha["arquivo"])
        esperado = str(linha["interno_esperado"]).strip()
        obs = str(linha.get("observacao", ""))

        res = motor.buscar(arquivo, threshold)
        obtido = identidades[res.indice] if res.indice is not None else SEM_MATCH

        if obtido == esperado:
            acertos += 1
        else:
            erros.append((arquivo, esperado, obtido, res, obs))

    total = len(golden)
    pct = 100.0 * acertos / total if total else 0.0
    print()
    print("=" * 74)
    print(f"GOLDEN SET: {acertos}/{total} acertos ({pct:.1f}%)  ·  threshold={threshold}")
    print(f"  planilha : {planilha}  ({len(df)} linhas)")
    print(f"  colunas  : matching='{COL_MATCHING}'  identidade='{COL_IDENTIDADE}'")
    print("=" * 74)
    print()

    if erros:
        print("ERROS:\n")
        for arquivo, esperado, obtido, res, obs in erros:
            print(f"  x {arquivo[:68]}")
            print(f"      esperado : {esperado}")
            print(f"      obtido   : {obtido}  (score={res.score} via {res.metodo})")
            if res.indice is not None:
                print(f"      linha    : {nomes[res.indice][:60]}")
            if res.componentes:
                print(f"      componentes: {res.componentes}")
            print(f"      nota     : {obs}\n")
        return 1

    print("OK — todos os casos do golden set passaram.")
    print("Isso NAO quer dizer que o motor esta certo: quer dizer que ele nao")
    print("regrediu nos 24 casos medidos. O que o harness nunca olha esta em")
    print("meta/STATUS.md (auto-match amplo, GUI, pastas reais).\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
