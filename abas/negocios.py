from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

import componentes as cp
import config as cfg
import metricas as mt


def renderizar_aba_negocios(df, df_completo, meses, m) -> None:
    cp.secao("Indicadores comerciais")
    den = "diagnóstico" if cfg.DENOMINADOR_CONVERSAO == "reunioes_diagnostico" else "proposta"
    l1 = st.columns(3)
    with l1[0]:
        cp.renderizar_card_metrica("Taxa de conversão", mt.formatar_pct(m["taxa_conversao"]), "Período",
                                   ajuda=f"Contratos fechados ÷ reuniões de {den} × 100")
    with l1[1]:
        cp.renderizar_card_metrica("Reuniões de diagnóstico", mt.formatar_inteiro(m["reunioes_diagnostico"]), "Acumulado")
    with l1[2]:
        cp.renderizar_card_metrica("Reuniões de proposta", mt.formatar_inteiro(m["reunioes_proposta"]), "Acumulado")
    st.write("")
    l2 = st.columns(4)
    with l2[0]:
        cp.renderizar_card_metrica("Faturamento", mt.formatar_moeda_brasileira(m["faturamento"]), "Acumulado")
    with l2[1]:
        cp.renderizar_card_metrica("Meta de faturamento", mt.formatar_moeda_brasileira(m["meta_faturamento"]), "Acumulado")
    with l2[2]:
        falta = "Meta batida ✦" if m["falta_meta"] == 0 else mt.formatar_moeda_brasileira(m["falta_meta"])
        cp.renderizar_card_metrica("Falta para a meta", falta, "Acumulado")
    with l2[3]:
        cp.renderizar_card_metrica("Atingimento da meta", mt.formatar_pct(m["pct_meta"]), "Acumulado")

    pct = m["pct_meta"]
    if pct == pct:  # não é NaN
        st.progress(min(pct / 100, 1.0), text=f"Progresso da meta: {mt.formatar_pct(pct)}")
        if pct >= 100:
            st.success(f"✦ Meta superada em {mt.formatar_moeda_brasileira(m['faturamento'] - m['meta_faturamento'])}!")
    else:
        st.info("Meta igual a zero ou ausente no período: não é possível calcular o atingimento.")

    c1, c2 = st.columns([1, 1.4])
    with c1:
        etapas = ["Reuniões de diagnóstico", "Reuniões de proposta", "Contratos fechados"]
        valores = [m["reunioes_diagnostico"], m["reunioes_proposta"], m["contratos_fechados"]]
        fig = go.Figure(go.Funnel(y=etapas, x=valores, textinfo="value+percent initial",
                                  marker=dict(color=["rgba(224,53,59,.25)", "rgba(224,53,59,.55)", cfg.COR_PRINCIPAL_BRILHO],
                                              line=dict(color=cfg.COR_PRINCIPAL_BRILHO, width=1)),
                                  connector=dict(fillcolor="rgba(161,29,33,.12)", line=dict(width=0)),
                                  textfont=dict(color="#FFFFFF", size=13)))
        cp.mostrar_grafico(cp.layout_grafico(fig, "Funil comercial", altura=300))
        d2p = mt.dividir(valores[1], valores[0]) * 100
        p2c = mt.dividir(valores[2], valores[1]) * 100
        cp.nota(f"Diagnóstico → proposta: {mt.formatar_pct(d2p)} · Proposta → contrato: {mt.formatar_pct(p2c)}")
    with c2:
        x = [cfg.MESES_ABREV[i - 1] for i in df["mes_num"]]
        fig = go.Figure()
        fig.add_bar(x=x, y=df["reunioes_diagnostico"], name="Diagnóstico", marker_color="#008091")
        fig.add_bar(x=x, y=df["reunioes_proposta"], name="Proposta", marker_color="#CC9900")
        fig.add_bar(x=x, y=df["contratos_fechados"], name="Contratos", marker_color=cfg.COR_PRINCIPAL)
        fig.update_layout(barmode="group")
        cp.mostrar_grafico(cp.layout_grafico(fig, "Reuniões e contratos por mês", altura=300))

    c3, c4 = st.columns(2)
    with c3:
        conv = [mt.calcular_taxa_conversao(df.iloc[[i]]) for i in range(len(df))]
        fig = go.Figure()
        cp.linha_neon(fig, x, conv, "Conversão", hover="%{y:.1f}%", preencher=True)
        fig.update_yaxes(range=[0, 100], ticksuffix="%")
        cp.mostrar_grafico(cp.layout_grafico(fig, "Taxa de conversão mensal", altura=280))
    with c4:
        acum_fat, acum_meta = df["faturamento"].cumsum(), df["meta_faturamento"].cumsum()
        fig = go.Figure()
        cp.linha_neon(fig, x, acum_fat, "Realizado acumulado", hover="R$ %{y:,.2f}", preencher=True)
        cp.linha_neon(fig, x, acum_meta, "Meta acumulada", cor="#CC9900", hover="R$ %{y:,.2f}", tracejada=True)
        cp.mostrar_grafico(cp.layout_grafico(fig, "Faturamento realizado × meta (acumulado)", altura=280, eixo_y="R$"))

    cp.secao("Sugerir novo indicador")
    cp.renderizar_formulario_sugestoes("Negócios", "negocios")

    cp.secao("Indicadores sugeridos")
    cp.indicadores_sugeridos([
        ("Ticket médio", "faturamento ÷ contratos fechados"),
        ("Tempo médio diagnóstico → fechamento", "dias entre a 1ª reunião e a assinatura"),
        ("Taxa diagnóstico → proposta", "propostas ÷ diagnósticos"),
        ("Taxa proposta → contrato", "contratos ÷ propostas"),
        ("Valor do pipeline", "soma do valor das propostas em aberto"),
        ("Faturamento por projeto", "faturamento ÷ projetos executados"),
        ("Previsibilidade do faturamento", "erro entre faturamento previsto e realizado"),
        ("Oportunidades em aberto", "leads ainda sem desfecho"),
    ])
