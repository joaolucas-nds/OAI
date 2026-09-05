"""
spreadsheet_loader.py — Carga da planilha (CSV/XLSX) como TEXTO.

Ponto ÚNICO de leitura, usado pela GUI (`main.py`) e pelo harness
(`test_matching.py`). Existe por causa do FIX-005: a leitura estava escrita
duas vezes, e as duas cópias comiam o zero à esquerda da mesma forma.

Não importa PySide6 nem nada da GUI — pode ser testado isoladamente.
"""

from __future__ import annotations

from pathlib import Path

import chardet
import pandas as pd

# Separadores candidatos, na ordem em que são contados na primeira linha.
SEPARADORES = (";", ",")


def detectar_encoding(caminho: str | Path) -> str:
    """
    Detecta o encoding do arquivo com chardet; cai em `utf-8-sig` se falhar.

    O fallback é `utf-8-sig` e não `utf-8` porque a origem real dos dados é
    export do Google Sheets, que grava BOM. Sem o BOM tratado, a primeira
    coluna vira `ï»¿Código Referência` (armadilha 7 do CONTEXT).
    """
    try:
        with open(caminho, "rb") as f:
            bruto = f.read(32768)
        enc = chardet.detect(bruto).get("encoding") or "utf-8-sig"
        if enc.lower() in ("utf-8-sig", "utf-8-bom"):
            return "utf-8-sig"
        return enc
    except Exception:
        return "utf-8-sig"


def detectar_separador(caminho: str | Path, encoding: str) -> str:
    """
    Escolhe o separador contando ocorrências na PRIMEIRA linha do arquivo.

    Heurística deliberada, em vez do sniffer do pandas (`sep=None`): é
    determinística e falha de forma previsível. O sniffer acerta mais em
    arquivos estranhos, mas erra em silêncio — e aqui um separador errado
    produz uma planilha de uma coluna só, que o resto do programa aceita
    sem reclamar.
    """
    try:
        with open(caminho, encoding=encoding, errors="replace") as f:
            primeira = f.readline()
    except Exception:
        return ","
    return max(SEPARADORES, key=primeira.count)


def carregar_planilha(caminho: str | Path) -> pd.DataFrame:
    """
    Lê CSV ou XLSX SEMPRE como texto e devolve o DataFrame com colunas limpas.

    Os dois argumentos que importam (FIX-005):

    - `dtype=str` impede o pandas de inferir `int64` numa coluna cujos valores
      são todos numéricos. Sem ele, `00611` vira `611` ANTES de qualquer
      `str()` do nosso código — o que come o zero no nome do arquivo E mata o
      match por código (`611` tem 3 caracteres e nem casa com a REGEX_CODIGO,
      então a linha fica sem código nenhum e o produto é ignorado).
    - `keep_default_na=False` faz célula vazia virar `""` em vez de `NaN`.
      Sem ele, `str(NaN)` põe o literal `nan` dentro do nome do arquivo.

    Planilha é texto. Qualquer coluna aqui pode ser um identificador, e
    identificador com inferência de tipo é dano silencioso.
    """
    caminho = str(caminho)

    if caminho.lower().endswith(".csv"):
        enc = detectar_encoding(caminho)
        df = pd.read_csv(
            caminho,
            encoding=enc,
            sep=detectar_separador(caminho, enc),
            dtype=str,
            keep_default_na=False,
            on_bad_lines="skip",
            low_memory=False,
        )
    else:
        df = pd.read_excel(
            caminho,
            engine="openpyxl",
            dtype=str,
            keep_default_na=False,
        )

    # Nome de coluna com espaço nas pontas quebra a seleção nos combos da GUI.
    df.columns = [str(c).strip() for c in df.columns]
    return df


def coluna_como_texto(df: pd.DataFrame, coluna: str) -> list[str]:
    """
    Devolve a coluna como lista de strings, pronta para o motor de matching.

    O `fillna("")` continua aqui como cinto de segurança: `keep_default_na`
    cobre a carga, mas um DataFrame montado por outro caminho (teste, futura
    origem de dados) pode chegar com NaN.
    """
    return df[coluna].fillna("").astype(str).tolist()
