"""
test_matching.py — Harness do golden set. Reporta % de acerto e lista erros.

Uso:
    python test_matching.py <planilha.csv> <golden_set.csv> [threshold]

Compara o motor v2 (matching_engine) contra os pares esperados do golden set.
indice_esperado == -1 significa "deve ficar SEM match".
"""

import sys
import chardet
import pandas as pd

from matching_engine import MotorMatching, PesosScore

SUFIXOS_PADRAO = [
    {"detectar": "(A)v2", "reescrever": "(Ambiente)_v2"},
    {"detectar": "(A)",   "reescrever": "(Ambiente)"},
    {"detectar": "(a)",   "reescrever": "(Ambiente)"},
    {"detectar": "v2",    "reescrever": "_v2"},
    {"detectar": "v3",    "reescrever": "_v3"},
    {"detectar": "face 2","reescrever": "_face2"},
    {"detectar": "face 3","reescrever": "_face3"},
]


def carregar_csv(caminho: str) -> pd.DataFrame:
    with open(caminho, "rb") as f:
        enc = chardet.detect(f.read())["encoding"] or "utf-8-sig"
    return pd.read_csv(caminho, encoding=enc, sep=None, engine="python")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    caminho_planilha = sys.argv[1]
    caminho_golden = sys.argv[2]
    threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 70.0

    df = carregar_csv(caminho_planilha)
    col = "Atual: 14/04/2026 - Anterior: 14/04/2026"
    if col not in df.columns:
        # fallback: última coluna que contém ' - ' nos valores
        col = next(c for c in df.columns
                   if df[c].astype(str).str.contains(" - ").any())
    nomes_planilha = df[col].fillna("").astype(str).tolist()

    golden = pd.read_csv(caminho_golden, encoding="utf-8", sep=",")
    motor = MotorMatching(nomes_planilha, SUFIXOS_PADRAO, PesosScore())

    acertos = 0
    total = len(golden)
    erros = []

    for _, linha in golden.iterrows():
        arquivo = str(linha["arquivo"])
        esperado = int(linha["indice_esperado"])
        obs = str(linha.get("observacao", ""))

        res = motor.buscar(arquivo, threshold)
        obtido = res.indice if res.indice is not None else -1

        ok = (obtido == esperado)
        if ok:
            acertos += 1
        else:
            erros.append((arquivo, esperado, obtido, res, obs))

    pct = 100.0 * acertos / total if total else 0.0
    print(f"\n{'='*70}")
    print(f"GOLDEN SET: {acertos}/{total} acertos ({pct:.1f}%)  ·  threshold={threshold}")
    print(f"{'='*70}\n")

    if erros:
        print("ERROS:\n")
        for arquivo, esperado, obtido, res, obs in erros:
            esp_txt = nomes_planilha[esperado] if esperado >= 0 else "(SEM MATCH)"
            obt_txt = nomes_planilha[obtido] if obtido >= 0 else "(SEM MATCH)"
            print(f"  ✗ {arquivo[:65]}")
            print(f"      esperado [{esperado}]: {esp_txt[:60]}")
            print(f"      obtido   [{obtido}] score={res.score} via {res.metodo}: {obt_txt[:55]}")
            if res.componentes:
                print(f"      componentes: {res.componentes}")
            print(f"      nota: {obs}")
            print()
    else:
        print("✔ Nenhum erro — todos os casos do golden set passaram.\n")


if __name__ == "__main__":
    main()
