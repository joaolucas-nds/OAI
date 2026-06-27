"""
matching_engine.py — Motor de correspondência arquivo↔planilha (puro Python, testável).

Separado da GUI (DEC-002 / ROADMAP F2). Não importa PySide6: pode ser testado
isoladamente com um golden set.

Hierarquia de decisão (DEC-001):
  P1. Código de referência (âncora) — bidirecional, confiança 100.
  P2. Score fuzzy PONDERADO (DEC-002) — substitui o token_set_ratio puro que
      inflava nota para subconjuntos.

O score ponderado combina:
  - token_sort_ratio  : base sensível a conteúdo extra (não infla com subconjunto)
  - WRatio            : reforço que escolhe estratégia conforme razão de comprimento
  - penalização de cobertura : quantos tokens da planilha ficaram "sem par"
                               (mata o efeito subconjunto do token_set_ratio)
  - bônus de medida   : quando dimensões (70X70, 32X62) coincidem nos dois lados
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from rapidfuzz import fuzz


# ─────────────────────────────────────────────────────────────────────────────
# REGEX E CONSTANTES
# ─────────────────────────────────────────────────────────────────────────────

# Código: sequência alfanumérica com 4+ chars contendo ao menos 1 dígito.
# Captura 1660730013300, PR12147, 00611, 32HDA60, R70181.
REGEX_CODIGO = re.compile(r'\b([A-Za-z]{0,4}\d[\dA-Za-z]{3,})\b')

# Medida/dimensão: 70X70, 32X62, 57,3X57,3, 61X120 etc.
REGEX_MEDIDA = re.compile(r'\b(\d{1,3}(?:,\d+)?X\d{1,3}(?:,\d+)?)\b', re.IGNORECASE)

# Tokens comuns demais para discriminar (peso reduzido na cobertura).
# Aparecem em quase toda linha do catálogo de pisos.
STOPWORDS_CATALOGO = {
    "PISO", "CX", "MT", "MT²", "MT2", "RETIF", "BOLD", "HD",
    "POL", "ACET", "BRIL", "SEMIG", "ABS", "GRANIL", "PORC", "IN", "OUT",
}

GUARDA_COMPRIMENTO_CODIGO = 4  # comprimento mínimo p/ considerar continência


# ─────────────────────────────────────────────────────────────────────────────
# NORMALIZAÇÃO
# ─────────────────────────────────────────────────────────────────────────────

def limpar_valor_planilha(texto: str) -> str:
    """Remove marcadores internos `* # + !` do FINAL do valor da planilha."""
    if not isinstance(texto, str):
        texto = str(texto)
    return re.sub(r'[\s*#+!]+$', '', texto).strip()


def normalizar_texto(texto: str) -> str:
    """Maiúsculas, remove especiais, troca hífen/underscore por espaço, colapsa espaços."""
    if not isinstance(texto, str):
        texto = str(texto)
    texto = texto.upper()
    texto = re.sub(r'[*#+!()\[\]{}²³°]', ' ', texto)
    texto = re.sub(r'[-_/\\]', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()


def extrair_codigos(texto: str) -> list[str]:
    """
    Extrai códigos alfanuméricos (lista em maiúsculas), EXCLUINDO dimensões.

    Dimensões (70X70, 33X57) e fragmentos de medida (50MT de '2,50MT²') NÃO são
    códigos de referência e não podem ancorar o match — senão linhas de mesma
    medida casariam entre si (bug detectado no golden set: 61838→39182 via 33X57).
    """
    brutos = [m.upper() for m in REGEX_CODIGO.findall(texto)]
    medidas = extrair_medidas(texto)
    resultado = []
    for c in brutos:
        if c in medidas:
            continue
        # Fragmento de medida tipo '50MT', '95MT', '30MT' (vem de '2,50MT²')
        if re.fullmatch(r'\d{2}MT\d*', c):
            continue
        # Dimensão isolada tipo '50X50' que escapou da regex de medida
        if re.fullmatch(r'\d{1,3}X\d{1,3}', c):
            continue
        resultado.append(c)
    return resultado


def extrair_medidas(texto: str) -> set[str]:
    """Extrai dimensões normalizadas (ex: {'70X70'})."""
    return {m.upper().replace(" ", "") for m in REGEX_MEDIDA.findall(texto)}


def tokens_significativos(texto_norm: str) -> set[str]:
    """Tokens do texto normalizado, sem stopwords de catálogo e sem puramente numéricos curtos."""
    brutos = set(texto_norm.split())
    return {t for t in brutos if t not in STOPWORDS_CATALOGO and len(t) > 1}


# ─────────────────────────────────────────────────────────────────────────────
# SUFIXOS DE VARIAÇÃO
# ─────────────────────────────────────────────────────────────────────────────

def separar_sufixos(nome: str, sufixos_cfg: list[dict]) -> tuple[str, str]:
    """
    Separa a base dos sufixos de variação configurados.
    Suporta sufixos COMPOSTOS (ex: '(A)v2' detecta o mais longo primeiro).
    Retorna (base, sufixo_original_concatenado).
    """
    nome = nome.strip()
    sufixos_acumulados = []

    # Ordena do maior para o menor (detecta '(A)v2' antes de 'v2')
    ordenados = sorted(sufixos_cfg, key=lambda s: len(s["detectar"]), reverse=True)

    # Tenta destacar múltiplos sufixos encadeados no fim do nome
    mudou = True
    while mudou:
        mudou = False
        for entrada in ordenados:
            det = entrada["detectar"].strip()
            if not det:
                continue
            padrao = re.compile(re.escape(det) + r'\s*$', re.IGNORECASE)
            m = padrao.search(nome)
            if m:
                sufixos_acumulados.insert(0, det)
                nome = nome[:m.start()].strip()
                mudou = True
                break

    return nome, " ".join(sufixos_acumulados)


def reescrever_sufixo(sufixo_original: str, sufixos_cfg: list[dict]) -> str:
    """Converte cada sufixo detectado para o formato configurado, preservando ordem."""
    if not sufixo_original:
        return ""
    partes_reescritas = []
    for parte in sufixo_original.split():
        reescrito = parte
        for entrada in sufixos_cfg:
            if entrada["detectar"].strip().lower() == parte.strip().lower():
                reescrito = entrada["reescrever"].strip()
                break
        if reescrito:
            partes_reescritas.append(reescrito)
    return " ".join(partes_reescritas).strip()


# ─────────────────────────────────────────────────────────────────────────────
# SCORE PONDERADO (DEC-002)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PesosScore:
    """Pesos do score ponderado. Ajustáveis e persistíveis (config futura)."""
    token_sort: float = 0.45
    wratio: float = 0.25
    cobertura: float = 0.30      # quanto da planilha foi coberto pela base do arquivo
    bonus_medida: float = 6.0    # pontos somados quando a medida coincide
    penalidade_medida: float = 25.0  # pontos SUBTRAÍDOS quando a medida diverge
    teto: float = 100.0


def score_ponderado(base_norm: str, planilha_norm: str, pesos: PesosScore) -> tuple[float, dict]:
    """
    Calcula score 0–100 entre a base do arquivo e a entrada da planilha.

    Decomposição por campos com poder discriminante (Fellegi-Sunter / record linkage):
    - similaridade textual (token_sort + WRatio) — base
    - cobertura de tokens significativos — mata o efeito subconjunto
    - MEDIDA como campo discriminante: 27 medidas distintas nos dados reais;
      medida coincidente reforça (bônus), medida DIVERGENTE penaliza forte —
      é o que separa produtos de descrição parecida mas formato diferente.

    Retorna (score, componentes) — componentes serve para transparência na UI.
    """
    if not base_norm or not planilha_norm:
        return 0.0, {}

    s_sort = fuzz.token_sort_ratio(base_norm, planilha_norm)
    s_wratio = fuzz.WRatio(base_norm, planilha_norm)

    # Cobertura: fração dos tokens significativos da planilha presentes na base.
    tok_base = tokens_significativos(base_norm)
    tok_plan = tokens_significativos(planilha_norm)
    if tok_plan:
        cobertos = len(tok_base & tok_plan)
        cobertura = 100.0 * cobertos / len(tok_plan)
    else:
        cobertura = s_sort

    # MEDIDA como campo discriminante (DEC-005): bônus se coincide, penalidade se diverge.
    med_base = extrair_medidas(base_norm)
    med_plan = extrair_medidas(planilha_norm)
    ajuste_medida = 0.0
    estado_medida = "ausente"
    if med_base and med_plan:
        if med_base & med_plan:
            ajuste_medida = pesos.bonus_medida
            estado_medida = "coincide"
        else:
            ajuste_medida = -pesos.penalidade_medida
            estado_medida = "diverge"

    bruto = (
        pesos.token_sort * s_sort +
        pesos.wratio * s_wratio +
        pesos.cobertura * cobertura +
        ajuste_medida
    )
    score = max(0.0, min(pesos.teto, bruto))

    componentes = {
        "token_sort": round(s_sort, 1),
        "wratio": round(s_wratio, 1),
        "cobertura": round(cobertura, 1),
        "medida": estado_medida,
        "ajuste_medida": ajuste_medida,
    }
    return round(score, 1), componentes


# ─────────────────────────────────────────────────────────────────────────────
# RESULTADO
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Resultado:
    indice: int | None          # índice da linha na planilha, ou None
    score: float
    metodo: str                 # "código" | "fuzzy" | "nenhum"
    base: str
    sufixo_original: str
    componentes: dict = field(default_factory=dict)
    ambiguo: bool = False       # True se houve 2º candidato com score próximo
    codigo_casado: str = ""     # qual código bateu (transparência)


# ─────────────────────────────────────────────────────────────────────────────
# MOTOR
# ─────────────────────────────────────────────────────────────────────────────

class MotorMatching:
    """
    Motor hierárquico código→fuzzy ponderado. Recebe listas simples (sem pandas),
    o que o torna trivial de testar.
    """

    def __init__(
        self,
        nomes_planilha: list[str],
        sufixos_cfg: list[dict],
        pesos: PesosScore | None = None,
        margem_ambiguidade: float = 5.0,
    ):
        self.sufixos_cfg = sufixos_cfg
        self.pesos = pesos or PesosScore()
        self.margem_ambiguidade = margem_ambiguidade

        # Pré-computa: limpa marcadores, normaliza, extrai códigos.
        self.nomes_planilha = [limpar_valor_planilha(n) for n in nomes_planilha]
        self.nomes_norm = [normalizar_texto(n) for n in self.nomes_planilha]
        self.codigos_planilha = [extrair_codigos(n) for n in self.nomes_planilha]

    # ── Match por código (bidirecional, FIX-001) ──────────────────────────
    def _match_codigo(self, codigos_arquivo: list[str]) -> tuple[int | None, str]:
        melhor_idx = None
        melhor_comp = 0
        melhor_cod = ""
        for cod_arq in codigos_arquivo:
            for idx, cods_plan in enumerate(self.codigos_planilha):
                for cod_plan in cods_plan:
                    exato = (cod_arq == cod_plan)
                    plan_em_arq = (len(cod_plan) >= GUARDA_COMPRIMENTO_CODIGO and cod_plan in cod_arq)
                    arq_em_plan = (len(cod_arq) >= GUARDA_COMPRIMENTO_CODIGO and cod_arq in cod_plan)
                    if exato or plan_em_arq or arq_em_plan:
                        comp = max(len(cod_arq), len(cod_plan))
                        # match exato tem prioridade sobre continência de mesmo comprimento
                        peso = comp + (1 if exato else 0)
                        if peso > melhor_comp:
                            melhor_comp = peso
                            melhor_idx = idx
                            melhor_cod = cod_plan if exato else f"{cod_arq}~{cod_plan}"
        return melhor_idx, melhor_cod

    # ── Busca principal ────────────────────────────────────────────────────
    def buscar(self, nome_arquivo: str, threshold: float) -> Resultado:
        base, sufixo = separar_sufixos(Path(nome_arquivo).stem, self.sufixos_cfg)
        codigos_arquivo = extrair_codigos(base)

        # P1 — código
        if codigos_arquivo:
            idx, cod = self._match_codigo(codigos_arquivo)
            if idx is not None:
                return Resultado(
                    indice=idx, score=100.0, metodo="código",
                    base=base, sufixo_original=sufixo, codigo_casado=cod,
                )

        # GUARDA DE CÓDIGO AUSENTE (DEC-006, decisão do usuário):
        # Se o arquivo TEM um código de referência claro (não-medida) mas ele não
        # casa com NENHUMA linha, o produto provavelmente não está cadastrado.
        # Bloqueia o fuzzy de "resgatar" com um produto diferente de nome parecido
        # (ex: 39184 casando com 39182). Mas só bloqueia se o código existe nos
        # códigos DA PLANILHA em algum lugar — se nenhuma linha tem código algum,
        # o catálogo é descrição-pura e o fuzzy deve rodar.
        planilha_tem_codigos = any(self.codigos_planilha)
        if codigos_arquivo and planilha_tem_codigos:
            return Resultado(
                indice=None, score=0.0, metodo="código_ausente",
                base=base, sufixo_original=sufixo,
                componentes={"motivo": "código do arquivo não existe na planilha"},
            )

        # P2 — fuzzy ponderado
        base_norm = normalizar_texto(base)
        if not base_norm:
            return Resultado(None, 0.0, "nenhum", base, sufixo)

        melhor_score = -1.0
        melhor_idx = None
        melhor_comp = {}
        segundo_score = -1.0
        for idx, plan_norm in enumerate(self.nomes_norm):
            sc, comp = score_ponderado(base_norm, plan_norm, self.pesos)
            if sc > melhor_score:
                segundo_score = melhor_score
                melhor_score, melhor_idx, melhor_comp = sc, idx, comp
            elif sc > segundo_score:
                segundo_score = sc

        if melhor_idx is None or melhor_score < threshold:
            return Resultado(None, melhor_score if melhor_idx is not None else 0.0,
                             "nenhum", base, sufixo, melhor_comp)

        ambiguo = (segundo_score >= 0 and (melhor_score - segundo_score) <= self.margem_ambiguidade)
        return Resultado(
            indice=melhor_idx, score=melhor_score, metodo="fuzzy",
            base=base, sufixo_original=sufixo, componentes=melhor_comp, ambiguo=ambiguo,
        )
