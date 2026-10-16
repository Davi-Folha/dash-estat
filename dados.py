"""Camada de dados do Dashboard ESTAT.

DADOS SIMULADOS. A simulação é feita no nível desagregado (uma linha por
projeto, com gerente, executores, datas e pesquisa de satisfação) e a tabela
mensal é derivada dela — assim os números ficam coerentes entre si e o schema
já é o que os dados reais devem seguir.

Para usar dados reais: preencha dados_modelo/mensal.csv (mesmas colunas da
tabela mensal) e mude FONTE_DADOS para "csv" em config.py.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

import config as cfg

PASTA_MODELO = Path(__file__).parent / "dados_modelo"

COLUNAS_MENSAIS = [
    "mes_num", "mes", "faturamento", "meta_faturamento",
    "reunioes_diagnostico", "reunioes_proposta", "contratos_fechados",
    "projetos_iniciados", "projetos_concluidos", "projetos_cancelados", "projetos_andamento", "rescisoes",
    "alocacoes_gerentes", "alocacoes_executores", "alocados_gerentes", "alocados_executores",
    "gerentes_ocupados", "gerentes_total", "membros_alocados", "membros_total",
    "csat_coletados", "projetos_elegiveis_csat", "csat_soma_notas",
    "nps_promotores", "nps_neutros", "nps_detratores", "nps_soma_notas",
    "nota_contextualizacao", "nota_comunicacao", "nota_clima",
    "membros_diversidade", "meta_diversidade",
]

# Peso de atividade por mês (calendário da UnB: férias em jan/fev e julho)
SAZONALIDADE = np.array([0.45, 0.6, 1.1, 1.2, 1.2, 1.0, 0.55, 1.05, 1.2, 1.25, 1.15, 0.8])


def _fim_mes(m: int) -> pd.Timestamp:
    return pd.Timestamp(cfg.ANO_REFERENCIA, m, 1) + pd.offsets.MonthEnd(0)


def _inicio_mes(m: int) -> pd.Timestamp:
    return pd.Timestamp(cfg.ANO_REFERENCIA, m, 1)


def simular_projetos(rng: np.random.Generator) -> pd.DataFrame:
    """Uma linha por projeto (inclui 6 projetos herdados de 2025)."""
    ano = cfg.ANO_REFERENCIA
    linhas = []
    pid = 1
    # herdados de 2025, ainda em andamento em janeiro
    for _ in range(6):
        inicio = pd.Timestamp(ano - 1, 12, 1) - pd.Timedelta(days=int(rng.integers(0, 75)))
        linhas.append({"id": pid, "inicio": inicio, "herdado": True})
        pid += 1
    for m in range(1, 13):
        n = rng.poisson(4.2 * SAZONALIDADE[m - 1])
        for _ in range(n):
            dia = int(rng.integers(1, _fim_mes(m).day + 1))
            linhas.append({"id": pid, "inicio": pd.Timestamp(ano, m, dia), "herdado": False})
            pid += 1
    df = pd.DataFrame(linhas)

    gerentes = [f"G{i:02d}" for i in range(1, 13)]
    membros = [f"M{i:02d}" for i in range(1, 49)]
    fim_ano = pd.Timestamp(ano, 12, 31)
    status, fins, ger, execs, valor = [], [], [], [], []
    for _, p in df.iterrows():
        duracao = int(rng.integers(35, 120))
        fim_previsto = p["inicio"] + pd.Timedelta(days=duracao)
        sorteio = rng.random()
        if sorteio < 0.06:
            st_ = "cancelado"
            fim = p["inicio"] + pd.Timedelta(days=int(rng.integers(10, duracao)))
        elif fim_previsto <= fim_ano:
            st_, fim = "concluido", fim_previsto
        else:
            st_, fim = "em_andamento", pd.NaT
        if st_ == "cancelado" and fim > fim_ano:
            st_, fim = "em_andamento", pd.NaT
        status.append(st_)
        fins.append(fim)
        ger.append(gerentes[int(rng.integers(0, len(gerentes)))])
        execs.append(",".join(rng.choice(membros, size=int(rng.integers(2, 5)), replace=False)))
        valor.append(round(float(rng.uniform(2500, 9000)), 2))
    df["status"] = status
    df["fim"] = fins
    df["gerente"] = ger
    df["executores"] = execs
    df["valor_contrato"] = valor

    # pesquisa de satisfação: ~80% dos concluídos respondem
    concl = df["status"] == "concluido"
    respondeu = concl & (rng.random(len(df)) < 0.8)
    df["respondeu_pesquisa"] = respondeu
    df["csat"] = np.where(respondeu, np.clip(np.round(rng.normal(4.3, 0.6, len(df))), cfg.ESCALA_CSAT[0], cfg.ESCALA_CSAT[1]), np.nan)
    nps_bruto = np.clip(np.round(rng.normal(8.6, 1.3, len(df))), cfg.ESCALA_NPS_RESPOSTA[0], cfg.ESCALA_NPS_RESPOSTA[1])
    df["nps_nota"] = np.where(respondeu, nps_bruto, np.nan)
    # rescisão: PREMISSA — subconjunto dos cancelados com contrato formalmente rescindido
    df["rescisao"] = (df["status"] == "cancelado") & (rng.random(len(df)) < 0.6)
    return df


def derivar_mensal(proj: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    linhas = []
    gerentes_total = 12
    for m in range(1, 13):
        ini, fim = _inicio_mes(m), _fim_mes(m)
        no_ano = ~proj["herdado"]
        iniciados = proj[no_ano & (proj["inicio"] >= ini) & (proj["inicio"] <= fim)]
        ativos = proj[(proj["inicio"] <= fim) & (proj["fim"].isna() | (proj["fim"] >= ini))]
        andamento = proj[(proj["inicio"] <= fim) & (proj["fim"].isna() | (proj["fim"] > fim))]
        concluidos = proj[(proj["status"] == "concluido") & (proj["fim"] >= ini) & (proj["fim"] <= fim)]
        cancelados = proj[(proj["status"] == "cancelado") & (proj["fim"] >= ini) & (proj["fim"] <= fim)]
        executores_ativos = set(",".join(ativos["executores"]).split(",")) - {""}
        executores_andamento = set(",".join(andamento["executores"]).split(",")) - {""}
        respostas = concluidos[concluidos["respondeu_pesquisa"]]
        membros_total = 40 if m < 3 else (48 if m < 8 else 46)  # processos seletivos em mar e ago

        contratos = len(iniciados)  # PREMISSA: contrato fechado = projeto iniciado no mês
        propostas = contratos + int(rng.poisson(2 * SAZONALIDADE[m - 1]))
        diagnosticos = propostas + int(rng.poisson(3 * SAZONALIDADE[m - 1]))

        linhas.append({
            "mes_num": m, "mes": cfg.MESES[m - 1],
            # PREMISSA: 50% faturado na assinatura e 50% na conclusão do projeto
            "faturamento": round(float(0.5 * iniciados["valor_contrato"].sum() + 0.5 * concluidos["valor_contrato"].sum()), 2),
            "meta_faturamento": round(23000 * SAZONALIDADE[m - 1], -2),
            "reunioes_diagnostico": diagnosticos, "reunioes_proposta": propostas, "contratos_fechados": contratos,
            "projetos_iniciados": len(iniciados), "projetos_concluidos": len(concluidos),
            "projetos_cancelados": len(cancelados), "projetos_andamento": len(andamento),
            "rescisoes": int(cancelados["rescisao"].sum()),
            "alocacoes_gerentes": len(iniciados),
            "alocacoes_executores": int(iniciados["executores"].str.count(",").sum() + len(iniciados)),
            "alocados_gerentes": andamento["gerente"].nunique(),
            "alocados_executores": len(executores_andamento),
            "gerentes_ocupados": ativos["gerente"].nunique(), "gerentes_total": gerentes_total,
            "membros_alocados": min(len(executores_ativos), membros_total), "membros_total": membros_total,
            "csat_coletados": len(respostas), "projetos_elegiveis_csat": len(concluidos),
            "csat_soma_notas": round(float(respostas["csat"].sum()), 1),
            "nps_promotores": int((respostas["nps_nota"] >= cfg.NPS_PROMOTOR_MIN).sum()),
            "nps_neutros": int(respostas["nps_nota"].between(cfg.NPS_DETRATOR_MAX + 1, cfg.NPS_PROMOTOR_MIN - 1).sum()),
            "nps_detratores": int((respostas["nps_nota"] <= cfg.NPS_DETRATOR_MAX).sum()),
            "nps_soma_notas": float(respostas["nps_nota"].sum()),
            "nota_contextualizacao": round(float(np.clip(rng.normal(8.3, 0.45), 0, 10)), 2),
            "nota_comunicacao": round(float(np.clip(rng.normal(8.0, 0.55), 0, 10)), 2),
            "nota_clima": round(float(np.clip(rng.normal(7.9, 0.4) + 0.05 * m / 2, 0, 10)), 2),
            "membros_diversidade": int(11 + (m >= 3) * 2 + (m >= 8) * 2 + rng.integers(0, 2)),
            "meta_diversidade": 18,
        })
    return pd.DataFrame(linhas, columns=COLUNAS_MENSAIS)


@st.cache_data(show_spinner=False)
def carregar_dados_2026() -> pd.DataFrame:
    """Retorna a tabela mensal de 2026 (12 linhas, ordem cronológica)."""
    if cfg.FONTE_DADOS == "csv":
        caminho = PASTA_MODELO / "mensal.csv"
        try:
            df = pd.read_csv(caminho)
            faltando = [c for c in COLUNAS_MENSAIS if c not in df.columns]
            if faltando or df.empty:
                raise ValueError(f"colunas ausentes ou arquivo vazio: {faltando}")
            return df.sort_values("mes_num").reset_index(drop=True)
        except Exception as erro:  # cai para o simulado em vez de quebrar
            st.warning(f"Não foi possível ler {caminho.name} ({erro}). Usando dados simulados.")
    rng = np.random.default_rng(cfg.SEMENTE)
    proj = simular_projetos(rng)
    return derivar_mensal(proj, rng)


def calcular_indice_ocupacao_diaria(seed: int = cfg.SEMENTE) -> pd.DataFrame:
    """PLACEHOLDER: índice diário de ocupação (0–100) simulado.

    Deve ser substituído pela regra real (ex.: horas alocadas ÷ horas disponíveis
    por dia). Simulação: dias úteis mais altos, fins de semana mais baixos,
    queda nas férias da UnB e picos em semanas de entrega.
    """
    rng = np.random.default_rng(seed + 1)
    dias = pd.date_range(f"{cfg.ANO_REFERENCIA}-01-01", f"{cfg.ANO_REFERENCIA}-12-31", freq="D")
    base = SAZONALIDADE[dias.month - 1] / SAZONALIDADE.max() * 72
    util = np.where(dias.dayofweek < 5, 1.0, 0.35)
    picos = np.where(dias.isocalendar().week.to_numpy() % 6 == 0, 18, 0)
    indice = np.clip(base * util + picos + rng.normal(0, 7, len(dias)), 0, 100).round(1)
    return pd.DataFrame({"data": dias, "indice": indice})


def exportar_modelos() -> None:
    """Cria os CSVs vazios com o schema esperado para os dados reais."""
    PASTA_MODELO.mkdir(exist_ok=True)
    pd.DataFrame(columns=COLUNAS_MENSAIS).to_csv(PASTA_MODELO / "mensal.csv", index=False)
    pd.DataFrame(columns=[
        "id", "inicio", "fim", "status", "gerente", "executores", "valor_contrato",
        "respondeu_pesquisa", "csat", "nps_nota", "rescisao",
    ]).to_csv(PASTA_MODELO / "projetos.csv", index=False)


if __name__ == "__main__":
    exportar_modelos()
    print("Modelos criados em", PASTA_MODELO)
