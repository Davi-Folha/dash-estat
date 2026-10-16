from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

import componentes as cp
import config as cfg
import metricas as mt
from dados import calcular_indice_ocupacao_diaria


def renderizar_aba_gestao(df, df_completo, meses, m) -> None:
    delta = lambda nome: mt.comparar_mes_anterior(df_completo, meses, nome)  # noqa: E731
    cp.secao("Clima e diversidade")
    l1 = st.columns(4)
    with l1[0]:
        cp.renderizar_card_metrica("Nota de clima", mt.formatar_nota(m["nota_clima"]), "Média do período",
                                   ajuda="Nota média da pesquisa de clima (0–10)")
    with l1[1]:
        cp.renderizar_card_metrica("Membros nos grupos de diversidade", mt.formatar_inteiro(m["membros_diversidade"]), "Último mês",
                                   delta("membros_diversidade"), ajuda="Contagem agregada; nenhum dado individual é exibido.")
    with l1[2]:
        falta = "Meta batida ✦" if m["falta_diversidade"] == 0 else mt.formatar_inteiro(m["falta_diversidade"])
        cp.renderizar_card_metrica(f"Falta para a meta ({mt.formatar_inteiro(m['meta_diversidade'])})", falta, "Último mês")
    with l1[3]:
        cp.renderizar_card_metrica("Atingimento da meta de diversidade", mt.formatar_pct(m["pct_diversidade"]), "Último mês")

    st.write("")
    c1, c2 = st.columns(2)
    x = [cfg.MESES_ABREV[i - 1] for i in df["mes_num"]]
    with c1:
        fig = go.Figure()
        cp.linha_neon(fig, x, df["nota_clima"], "Clima", hover="%{y:.2f}", preencher=True)
        fig.add_scatter(x=x, y=df["nota_clima"] + 0.25, mode="text", text=[mt.formatar_nota(v) for v in df["nota_clima"]],
                        textfont=dict(size=10, color=cfg.COR_TEXTO), hoverinfo="skip", showlegend=False)
        fig.update_yaxes(range=[5, 10.2])
        cp.mostrar_grafico(cp.layout_grafico(fig, "Evolução da nota de clima", altura=280))
    with c2:
        fig = go.Figure()
        fig.add_bar(x=x, y=df["membros_diversidade"], name="Membros", marker=dict(color="rgba(0,128,145,.75)", line=dict(color="#5FD3E0", width=1)),
                    hovertemplate="%{x}: %{y}<extra>Membros</extra>")
        fig.add_scatter(x=x, y=df["meta_diversidade"], name="Meta", mode="lines", line=dict(color=cfg.COR_PRINCIPAL_BRILHO, dash="dash", width=2))
        cp.mostrar_grafico(cp.layout_grafico(fig, "Diversidade: membros × meta", altura=280))

    cp.secao("Mapa de calor da ocupação diária")
    meses_num = [cfg.MESES.index(mes) + 1 for mes in meses]
    cp.mostrar_grafico(cp.heatmap_ocupacao(calcular_indice_ocupacao_diaria(), meses_num))
    cp.legenda_farol()
    cp.nota("Índice diário <b>simulado</b> (placeholder em <code>calcular_indice_ocupacao_diaria()</code>). "
            "Meses fora do filtro ficam apagados. A fórmula real ainda será definida.")

    cp.secao("Sugerir novo indicador")
    cp.renderizar_formulario_sugestoes("Gestão", "gestao")

    cp.secao("Indicadores sugeridos")
    cp.indicadores_sugeridos([
        ("Participação em eventos internos", "presentes ÷ membros convocados"),
        ("Absenteísmo em reuniões gerais", "ausências ÷ convocações"),
        ("Rotatividade de membros", "desligamentos ÷ média de membros no período"),
        ("Distribuição da carga de trabalho", "dispersão de projetos por membro"),
        ("% de membros sem alocação", "complemento do % de membros alocados"),
        ("Horas de capacitação por membro", "horas de treinamento ÷ membros"),
        ("Participação em processos seletivos", "membros envolvidos no PS ÷ total"),
        ("Evolução da percepção de clima", "variação da nota de clima entre ciclos"),
    ])
