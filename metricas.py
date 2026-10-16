"""Cálculos puros (sem Streamlit) — testados em tests/test_metricas.py."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

import config as cfg


def ordenar_meses(selecionados: list[str]) -> list[str]:
    """Mantém a ordem cronológica, nunca alfabética."""
    return [m for m in cfg.MESES if m in set(selecionados)]


def filtrar_dados_por_mes(df: pd.DataFrame, meses: list[str]) -> pd.DataFrame:
    if df is None or df.empty or not meses:
        return pd.DataFrame(columns=[] if df is None else df.columns)
    return df[df["mes"].isin(meses)].sort_values("mes_num").reset_index(drop=True)


def dividir(num: float, den: float) -> float:
    """Divisão segura: retorna NaN quando o denominador é 0 ou ausente."""
    try:
        if den is None or pd.isna(den) or den == 0 or pd.isna(num):
            return math.nan
        return num / den
    except Exception:
        return math.nan


def limitar_pct(valor: float) -> float:
    return valor if pd.isna(valor) else float(min(max(valor, 0.0), 100.0))


def calcular_nps(promotores: float, neutros: float, detratores: float) -> float:
    total = promotores + neutros + detratores
    if total == 0:
        return math.nan
    return (promotores - detratores) / total * 100


def calcular_taxa_conversao(df: pd.DataFrame, denominador: str = cfg.DENOMINADOR_CONVERSAO) -> float:
    """Contratos fechados ÷ reuniões (diagnóstico por padrão) × 100.

    O denominador é configurável em config.DENOMINADOR_CONVERSAO caso a ESTAT
    defina outra etapa do funil.
    """
    if df.empty:
        return math.nan
    return limitar_pct(dividir(df["contratos_fechados"].sum(), df[denominador].sum()) * 100)


def agregar(df: pd.DataFrame, nome: str, modo_pct: str = cfg.MODO_AGREGACAO_PERCENTUAIS) -> float:
    """Agrega uma métrica no período segundo config.METRICAS."""
    if df is None or df.empty:
        return math.nan
    regra = cfg.METRICAS[nome]
    tipo = regra["tipo"]
    if tipo == "soma":
        return float(df[nome].sum())
    if tipo == "ultimo":
        return float(df.sort_values("mes_num")[nome].iloc[-1])
    if tipo == "media":
        return float(df[nome].mean()) if df[nome].notna().any() else math.nan
    if tipo == "razao":
        num, den = df[regra["num"]], df[regra["den"]]
        if modo_pct == "media_simples":
            mensais = [dividir(n, d) * 100 for n, d in zip(num, den)]
            mensais = [v for v in mensais if not pd.isna(v)]
            return limitar_pct(float(np.mean(mensais))) if mensais else math.nan
        return limitar_pct(dividir(num.sum(), den.sum()) * 100)
    if tipo == "csat":  # média ponderada pelas respostas
        return dividir(df["csat_soma_notas"].sum(), df["csat_coletados"].sum())
    if tipo == "nps":  # recalculado, nunca média de NPS mensais
        return calcular_nps(df["nps_promotores"].sum(), df["nps_neutros"].sum(), df["nps_detratores"].sum())
    if tipo == "nps_media":
        respostas = df["nps_promotores"].sum() + df["nps_neutros"].sum() + df["nps_detratores"].sum()
        return dividir(df["nps_soma_notas"].sum(), respostas)
    raise ValueError(f"tipo de agregação desconhecido: {tipo}")


def serie_mensal(df: pd.DataFrame, nome: str) -> pd.Series:
    """Valor mensal (um mês por vez) de qualquer métrica, inclusive as especiais."""
    return pd.Series([agregar(df.iloc[[i]], nome) for i in range(len(df))], index=df["mes_num"].values)


def comparar_mes_anterior(df_completo: pd.DataFrame, meses: list[str], nome: str) -> float | None:
    """Variação do último mês selecionado contra o mês imediatamente anterior.

    Retorna None quando não há mês anterior nos dados (não inventa comparação).
    """
    if not meses:
        return None
    ultimo = cfg.MESES.index(meses[-1]) + 1
    if ultimo == 1:
        return None
    atual = df_completo[df_completo["mes_num"] == ultimo]
    anterior = df_completo[df_completo["mes_num"] == ultimo - 1]
    if atual.empty or anterior.empty:
        return None
    a, b = agregar(atual, nome), agregar(anterior, nome)
    if pd.isna(a) or pd.isna(b):
        return None
    return a - b


def calcular_metricas_gerais(df: pd.DataFrame) -> dict[str, float]:
    m = {nome: agregar(df, nome) for nome in cfg.METRICAS}
    m["falta_meta"] = max(m["meta_faturamento"] - m["faturamento"], 0) if not pd.isna(m["meta_faturamento"]) else math.nan
    m["pct_meta"] = dividir(m["faturamento"], m["meta_faturamento"]) * 100
    m["taxa_conversao"] = calcular_taxa_conversao(df) if not df.empty else math.nan
    m["alocados_total"] = m["alocados_gerentes"] + m["alocados_executores"]
    m["alocacoes_total"] = m["alocacoes_gerentes"] + m["alocacoes_executores"]
    m["falta_diversidade"] = max(m["meta_diversidade"] - m["membros_diversidade"], 0) if not pd.isna(m["meta_diversidade"]) else math.nan
    m["pct_diversidade"] = dividir(m["membros_diversidade"], m["meta_diversidade"]) * 100
    return m


def obter_faixa_alocacao(pct: float) -> tuple[str, str, str]:
    """(rótulo, cor, cor_do_texto) da faixa do farol para um percentual."""
    if pd.isna(pct):
        return ("Sem dado", "#BDBDBD", "#1F1F1F")
    pct = limitar_pct(pct)
    for ini, fim, rotulo, cor, cor_txt in cfg.FAIXAS_FAROL:
        if ini <= pct < fim:
            return (rotulo, cor, cor_txt)
    return cfg.FAIXAS_FAROL[-1][2:5]


def obter_cor_alocacao(pct: float) -> str:
    return obter_faixa_alocacao(pct)[1]


def faixa_nps(nps: float) -> tuple[str, str]:
    if pd.isna(nps):
        return ("Sem dado", "#BDBDBD")
    for ini, fim, rotulo, cor in cfg.FAIXAS_NPS:
        if ini <= nps < fim:
            return (rotulo, cor)
    return cfg.FAIXAS_NPS[-1][2:4]


# ------------------------------------------------------------- formatação
def formatar_moeda_brasileira(valor: float) -> str:
    try:
        if valor is None or pd.isna(valor):
            return "—"
        txt = f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {txt}"
    except Exception:
        return "—"


def formatar_pct(valor: float, casas: int = 1) -> str:
    if valor is None or pd.isna(valor):
        return "—"
    return f"{valor:.{casas}f}%".replace(".", ",")


def formatar_nota(valor: float) -> str:
    if valor is None or pd.isna(valor):
        return "—"
    return f"{valor:.2f}".replace(".", ",")


def formatar_inteiro(valor: float) -> str:
    if valor is None or pd.isna(valor):
        return "—"
    return f"{int(round(valor)):,}".replace(",", ".")


def descrever_periodo(meses: list[str]) -> str:
    if not meses:
        return "Nenhum mês selecionado"
    if len(meses) == 12:
        return f"Ano completo de {cfg.ANO_REFERENCIA}"
    idx = [cfg.MESES.index(m) for m in meses]
    if len(meses) == 1:
        return f"{meses[0]} de {cfg.ANO_REFERENCIA}"
    if idx == list(range(idx[0], idx[-1] + 1)):
        return f"{meses[0]} a {meses[-1]} de {cfg.ANO_REFERENCIA}"
    return ", ".join(cfg.MESES_ABREV[i] for i in idx) + f" de {cfg.ANO_REFERENCIA}"
