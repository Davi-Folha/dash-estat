import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config as cfg  # noqa: E402
import metricas as mt  # noqa: E402
from dados import derivar_mensal, simular_projetos  # noqa: E402


def dados():
    rng = np.random.default_rng(cfg.SEMENTE)
    return derivar_mensal(simular_projetos(rng), rng)


def test_doze_meses_ordem():
    df = dados()
    assert list(df["mes_num"]) == list(range(1, 13))


def test_ordem_cronologica():
    assert mt.ordenar_meses(["Dezembro", "Abril", "Janeiro"]) == ["Janeiro", "Abril", "Dezembro"]


def test_soma_ultimo_media():
    df = mt.filtrar_dados_por_mes(dados(), ["Março", "Abril", "Maio"])
    assert mt.agregar(df, "faturamento") == df["faturamento"].sum()
    assert mt.agregar(df, "projetos_andamento") == df.iloc[-1]["projetos_andamento"]
    assert math.isclose(mt.agregar(df, "nota_clima"), df["nota_clima"].mean())


def test_nps_recalculado_nao_media():
    df = pd.DataFrame({"mes_num": [1, 2], "nps_promotores": [9, 1], "nps_neutros": [0, 0], "nps_detratores": [1, 0]})
    assert math.isclose(mt.agregar(df, "nps"), (10 - 1) / 11 * 100)  # e não média de (80, 100) = 90


def test_csat_ponderado():
    df = pd.DataFrame({"mes_num": [1, 2], "csat_soma_notas": [90.0, 6.0], "csat_coletados": [10, 1]})
    assert math.isclose(mt.agregar(df, "csat"), 96 / 11)


def test_modos_percentual():
    df = pd.DataFrame({"mes_num": [1, 2], "membros_alocados": [1, 50], "membros_total": [2, 100]})
    assert math.isclose(mt.agregar(df, "pct_membros_alocados", "razao_agregada"), 51 / 102 * 100)
    assert math.isclose(mt.agregar(df, "pct_membros_alocados", "media_simples"), 50.0)


def test_divisao_por_zero_e_vazio():
    assert math.isnan(mt.dividir(1, 0))
    assert math.isnan(mt.agregar(pd.DataFrame(), "faturamento"))
    assert mt.filtrar_dados_por_mes(dados(), []).empty
    assert math.isnan(mt.calcular_nps(0, 0, 0))


def test_percentuais_validos():
    m = mt.calcular_metricas_gerais(dados())
    for k in ["pct_membros_alocados", "pct_gerentes_ocupados", "pct_csat_coletados", "taxa_conversao"]:
        assert 0 <= m[k] <= 100


def test_coerencia_projetos():
    df = dados()
    assert (df["projetos_concluidos"] >= 0).all()
    assert (df["csat_coletados"] <= df["projetos_elegiveis_csat"]).all()
    assert (df["contratos_fechados"] <= df["reunioes_proposta"]).all()
    assert (df["reunioes_proposta"] <= df["reunioes_diagnostico"]).all()


def test_farol_ordem():
    assert [mt.obter_faixa_alocacao(v)[0] for v in [10, 50, 70, 80, 95, 100]] == [
        "Baixa", "Moderada", "Alta", "Muito alta", "Crítica", "Crítica"]


def test_formatacao():
    assert mt.formatar_moeda_brasileira(12345.678) == "R$ 12.345,68"
    assert mt.formatar_moeda_brasileira(None) == "—"
    assert mt.formatar_pct(72.44) == "72,4%"
    assert mt.formatar_nota(8.567) == "8,57"


def test_escalas_csat_nps():
    df = dados()
    csat_medio = mt.agregar(df, "csat")
    assert cfg.ESCALA_CSAT[0] <= csat_medio <= cfg.ESCALA_CSAT[1]
    assert cfg.ESCALA_NPS_RESPOSTA[0] <= mt.agregar(df, "nps_nota_media") <= cfg.ESCALA_NPS_RESPOSTA[1]
    assert -100 <= mt.agregar(df, "nps") <= 100
