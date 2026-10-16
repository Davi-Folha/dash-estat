from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

import componentes as cp
import config as cfg
import metricas as mt


def renderizar_aba_geral(df, df_completo, meses, m) -> None:
    x = [cfg.MESES_ABREV[i - 1] for i in df["mes_num"]]
    cp.secao("Indicadores estratégicos")
    linha1 = st.columns(4)
    with linha1[0]:
        cp.renderizar_card_metrica("Faturamento", mt.formatar_moeda_brasileira(m["faturamento"]), "Acumulado")
    with linha1[1]:
        cp.renderizar_card_metrica("Meta de faturamento", mt.formatar_moeda_brasileira(m["meta_faturamento"]), "Acumulado")
    with linha1[2]:
        falta = "Meta batida ✦" if m["falta_meta"] == 0 else mt.formatar_moeda_brasileira(m["falta_meta"])
        cp.renderizar_card_metrica("Falta para a meta", falta, "Acumulado")
    with linha1[3]:
        cp.renderizar_card_metrica("Atingimento da meta", mt.formatar_pct(m["pct_meta"]), "Acumulado",
                                   ajuda="Faturamento acumulado ÷ meta acumulada × 100")
    st.write("")
    linha2 = st.columns(3)
    with linha2[0]:
        cp.renderizar_card_metrica("CSAT", f"{mt.formatar_nota(m['csat'])} <small>/ {cfg.ESCALA_CSAT[1]}</small>", "Média do período",
                                   ajuda=f"Média das notas de CSAT ({cfg.ESCALA_CSAT[0]} a {cfg.ESCALA_CSAT[1]}) ponderada pelo número de respostas")
    with linha2[1]:
        cp.renderizar_card_metrica("Gerentes ocupados", mt.formatar_pct(m["pct_gerentes_ocupados"]), "Média do período",
                                   ajuda="Gerentes com ≥ 1 projeto ÷ total de gerentes × 100")
    with linha2[2]:
        cp.renderizar_card_metrica("Membros alocados", mt.formatar_pct(m["pct_membros_alocados"]), "Média do período",
                                   ajuda="Membros executando ≥ 1 projeto ÷ total de membros × 100")

    st.write("")
    c1, c2 = st.columns([1, 1.6])
    with c1:
        cp.mostrar_grafico(cp.gauge_alocacao(m["pct_membros_alocados"]))
        cp.legenda_farol()
    with c2:
        fig = go.Figure()
        fig.add_bar(x=x, y=df["faturamento"], name="Faturamento", marker=dict(color=cfg.COR_PRINCIPAL, line=dict(color=cfg.COR_PRINCIPAL_BRILHO, width=1)),
                    hovertemplate="%{x}: R$ %{y:,.2f}<extra>Faturamento</extra>")
        cp.linha_neon(fig, x, df["meta_faturamento"], "Meta", cor="#CC9900", hover="R$ %{y:,.2f}", tracejada=True)
        cp.mostrar_grafico(cp.layout_grafico(fig, "Faturamento mensal × meta", altura=360))

    c3, c4 = st.columns(2)
    with c3:
        csat = mt.serie_mensal(df, "csat")
        fig = go.Figure()
        cp.linha_neon(fig, [cfg.MESES_ABREV[i - 1] for i in csat.index], csat.values, "CSAT", hover="%{y:.2f}", preencher=True)
        fig.update_yaxes(range=[cfg.ESCALA_CSAT[0], cfg.ESCALA_CSAT[1] + 0.1])
        cp.mostrar_grafico(cp.layout_grafico(fig, f"CSAT mensal ({cfg.ESCALA_CSAT[0]} a {cfg.ESCALA_CSAT[1]})", altura=290))
    with c4:
        aloc = mt.serie_mensal(df, "pct_membros_alocados")
        cores = [mt.obter_cor_alocacao(v) for v in aloc.values]
        fig = go.Figure(go.Bar(x=[cfg.MESES_ABREV[i - 1] for i in aloc.index], y=aloc.values,
                               marker=dict(color=cores, line=dict(color="rgba(255,255,255,.35)", width=1)),
                               text=[mt.formatar_pct(v) for v in aloc.values], textposition="outside", textfont=dict(size=10, color=cfg.COR_TEXTO_SUAVE),
                               hovertemplate="%{x}: %{y:.1f}%<extra>Membros alocados</extra>"))
        fig.update_yaxes(range=[0, 110], ticksuffix="%")
        cp.mostrar_grafico(cp.layout_grafico(fig, "Membros alocados por mês · cor do farol", altura=290))

    cp.secao("Resumo das diretorias")
    r1, r2, r3 = st.columns(3)
    r1.markdown(
        f"<div class='resumo-dir'><div class='t'>Projetos</div><b>{mt.formatar_inteiro(m['projetos_concluidos'])}</b> concluídos · "
        f"<b>{mt.formatar_inteiro(m['projetos_andamento'])}</b> em andamento<br>NPS <b>{mt.formatar_inteiro(m['nps'])}</b> · "
        f"CSAT <b>{mt.formatar_nota(m['csat'])}</b>/{cfg.ESCALA_CSAT[1]}</div>", unsafe_allow_html=True)
    r2.markdown(
        f"<div class='resumo-dir'><div class='t'>Negócios</div><b>{mt.formatar_inteiro(m['contratos_fechados'])}</b> contratos de "
        f"<b>{mt.formatar_inteiro(m['reunioes_diagnostico'])}</b> diagnósticos<br>Conversão <b>{mt.formatar_pct(m['taxa_conversao'])}</b> · "
        f"meta <b>{mt.formatar_pct(m['pct_meta'])}</b></div>", unsafe_allow_html=True)
    r3.markdown(
        f"<div class='resumo-dir'><div class='t'>Gestão</div>Clima <b>{mt.formatar_nota(m['nota_clima'])}</b><br>Diversidade "
        f"<b>{mt.formatar_inteiro(m['membros_diversidade'])}</b>/{mt.formatar_inteiro(m['meta_diversidade'])} "
        f"(<b>{mt.formatar_pct(m['pct_diversidade'])}</b> da meta)</div>", unsafe_allow_html=True)
