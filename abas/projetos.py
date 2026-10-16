from __future__ import annotations

from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import componentes as cp
import config as cfg
import metricas as mt

AJUDA = {
    "andamento": "Projetos com status 'em andamento' no fim do último mês selecionado (exclui concluídos, cancelados e não iniciados).",
    "concluidos": "Projetos com status 'concluído' e data de conclusão no período.",
    "csat": f"Média das notas de CSAT dos projetos concluídos com pesquisa respondida, ponderada pelas respostas. Escala de {cfg.ESCALA_CSAT[0]} a {cfg.ESCALA_CSAT[1]}.",
    "nps": f"Respostas de {cfg.ESCALA_NPS_RESPOSTA[0]} a {cfg.ESCALA_NPS_RESPOSTA[1]}. NPS = % promotores ({cfg.NPS_PROMOTOR_MIN}–10) − % detratores ({cfg.ESCALA_NPS_RESPOSTA[0]}–{cfg.NPS_DETRATOR_MAX}), recalculado sobre todas as respostas do período; varia de −100 a 100.",
    "alocados": "Pessoas com alocação ativa em projetos em andamento no último mês selecionado.",
    "alocacoes": "Vínculos pessoa–projeto iniciados no período. A mesma pessoa pode contar mais de uma vez.",
    "cancelados": "Projetos interrompidos antes da conclusão, com data de cancelamento no período.",
    "rescisoes": "Rescisões de contrato formalizadas no período. Distinção em relação a 'cancelados' pendente de validação com a Direx.",
    "iniciados": "Projetos com data de início efetivo no período, independentemente do status atual.",
}


def _barras(df, coluna, titulo, cor=cfg.COR_PRINCIPAL, altura=260):
    fig = go.Figure(go.Bar(x=[cfg.MESES_ABREV[i - 1] for i in df["mes_num"]], y=df[coluna],
                           marker=dict(color=cor, line=dict(color=cfg.COR_PRINCIPAL_BRILHO, width=1)),
                           text=df[coluna], textposition="outside", textfont=dict(color=cfg.COR_TEXTO),
                           hovertemplate="%{x}: %{y}<extra></extra>"))
    fig.update_yaxes(rangemode="tozero")
    return cp.layout_grafico(fig, titulo, altura=altura)


def renderizar_aba_projetos(df, df_completo, meses, m) -> None:
    delta = lambda nome: mt.comparar_mes_anterior(df_completo, meses, nome)  # noqa: E731

    cp.secao("Indicadores da especificação (v1)")
    l1 = st.columns(4)
    with l1[0]:
        cp.renderizar_card_metrica("Projetos em andamento", mt.formatar_inteiro(m["projetos_andamento"]), "Último mês",
                                   delta("projetos_andamento"), ajuda=AJUDA["andamento"])
    with l1[1]:
        cp.renderizar_card_metrica("Projetos concluídos", mt.formatar_inteiro(m["projetos_concluidos"]), "Acumulado", ajuda=AJUDA["concluidos"])
    with l1[2]:
        cp.renderizar_card_metrica("Projetos iniciados", mt.formatar_inteiro(m["projetos_iniciados"]), "Acumulado", ajuda=AJUDA["iniciados"])
    with l1[3]:
        cp.renderizar_card_metrica("Cancelados · Rescisões", f"{mt.formatar_inteiro(m['projetos_cancelados'])} · {mt.formatar_inteiro(m['rescisoes'])}",
                                   "Acumulado", ajuda=AJUDA["cancelados"] + " " + AJUDA["rescisoes"])
    st.write("")
    l2 = st.columns(4)
    with l2[0]:
        cp.renderizar_card_metrica("CSAT médio", f"{mt.formatar_nota(m['csat'])} <small>/ {cfg.ESCALA_CSAT[1]}</small>", "Média do período", ajuda=AJUDA["csat"])
    with l2[1]:
        rotulo, cor = mt.faixa_nps(m["nps"])
        cp.renderizar_card_metrica("NPS", f"{mt.formatar_inteiro(m['nps'])} <span style='font-size:.8rem;color:{cor}'>● {rotulo}</span>",
                                   "Período", ajuda=AJUDA["nps"], detalhe=f"Nota média das respostas: {mt.formatar_nota(m['nps_nota_media'])} / {cfg.ESCALA_NPS_RESPOSTA[1]}")
    with l2[2]:
        cp.renderizar_card_metrica(
            "Alocados no momento", mt.formatar_inteiro(m["alocados_total"]), "Último mês",
            ajuda=AJUDA["alocados"], detalhe=f"Gerentes {mt.formatar_inteiro(m['alocados_gerentes'])} · Executores {mt.formatar_inteiro(m['alocados_executores'])}")
    with l2[3]:
        cp.renderizar_card_metrica("Alocações no período", mt.formatar_inteiro(m["alocacoes_total"]), "Acumulado", ajuda=AJUDA["alocacoes"],
                                   detalhe=f"Gerentes {mt.formatar_inteiro(m['alocacoes_gerentes'])} · Executores {mt.formatar_inteiro(m['alocacoes_executores'])}")

    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        x = [cfg.MESES_ABREV[i - 1] for i in df["mes_num"]]
        fig = go.Figure()
        fig.add_bar(x=x, y=df["projetos_iniciados"], name="Iniciados", marker_color="#008091")
        fig.add_bar(x=x, y=df["projetos_concluidos"], name="Concluídos", marker_color=cfg.COR_PRINCIPAL)
        fig.add_bar(x=x, y=df["projetos_cancelados"], name="Cancelados", marker_color="#CC9900")
        fig.update_layout(barmode="group")
        cp.mostrar_grafico(cp.layout_grafico(fig, "Projetos iniciados, concluídos e cancelados por mês", altura=300))
    with c2:
        cp.mostrar_grafico(_barras(df, "projetos_andamento", "Projetos em andamento (fim de cada mês)", cfg.COR_PRINCIPAL, altura=300))

    c3, c4 = st.columns(2)
    with c3:
        csat, nps = mt.serie_mensal(df, "csat"), mt.serie_mensal(df, "nps")
        x = [cfg.MESES_ABREV[i - 1] for i in csat.index]
        fig = go.Figure()
        cp.linha_neon(fig, x, csat.values, f"CSAT ({cfg.ESCALA_CSAT[0]}–{cfg.ESCALA_CSAT[1]})", hover="%{y:.2f}")
        cp.linha_neon(fig, x, nps.values, "NPS (−100 a 100)", cor="#008091", hover="%{y:.0f}", yaxis="y2", tracejada=True)
        fig.update_layout(yaxis=dict(range=[cfg.ESCALA_CSAT[0], cfg.ESCALA_CSAT[1] + 0.1], title="CSAT"),
                          yaxis2=dict(range=[-100, 100], overlaying="y", side="right", title="NPS", showgrid=False, dtick=50,
                                      tickfont=dict(color=cfg.COR_TEXTO_SUAVE)))
        cp.mostrar_grafico(cp.layout_grafico(fig, "Evolução mensal de CSAT e NPS", altura=300))
        cp.nota("Meses sem projeto concluído com pesquisa respondida ficam sem ponto.")
    with c4:
        x = [cfg.MESES_ABREV[i - 1] for i in df["mes_num"]]
        acum = df[["alocacoes_gerentes", "alocacoes_executores"]].cumsum()
        fig = go.Figure()
        fig.add_bar(x=x, y=acum["alocacoes_gerentes"], name="Gerentes", marker_color=cfg.COR_PRINCIPAL)
        fig.add_bar(x=x, y=acum["alocacoes_executores"], name="Executores", marker_color="#008091")
        fig.update_layout(barmode="stack")
        cp.mostrar_grafico(cp.layout_grafico(fig, "Alocações acumuladas no período selecionado", altura=300))

    # --------------------------------------------------------------- novas
    cp.secao("Ocupação e qualidade da gestão de projetos", nova=True)
    l3 = st.columns(4)
    with l3[0]:
        cp.renderizar_card_metrica("Gerentes ocupados", mt.formatar_pct(m["pct_gerentes_ocupados"]), "Média do período",
                                   ajuda="Gerentes gerenciando ≥ 1 projeto ÷ total de gerentes × 100")
    with l3[1]:
        cp.renderizar_card_metrica("Empresa alocada em projetos", mt.formatar_pct(m["pct_membros_alocados"]), "Média do período",
                                   ajuda="Membros executando ≥ 1 projeto ÷ total de membros × 100")
    with l3[2]:
        cp.renderizar_card_metrica("Nota de contextualização", mt.formatar_nota(m["nota_contextualizacao"]), "Média do período",
                                   ajuda="Nota média dada aos gerentes quanto à contextualização do projeto (0–10)")
    with l3[3]:
        cp.renderizar_card_metrica("Nota de comunicação", mt.formatar_nota(m["nota_comunicacao"]), "Média do período",
                                   ajuda="Nota média dada aos gerentes quanto à comunicação (0–10)")

    c5, c6, c7 = st.columns([1.3, 1.3, 1])
    with c5:
        x = [cfg.MESES_ABREV[i - 1] for i in df["mes_num"]]
        fig = go.Figure()
        cp.linha_neon(fig, x, mt.serie_mensal(df, "pct_gerentes_ocupados").values, "Gerentes ocupados", hover="%{y:.1f}%")
        cp.linha_neon(fig, x, mt.serie_mensal(df, "pct_membros_alocados").values, "Membros alocados", cor="#008091", hover="%{y:.1f}%")
        fig.update_yaxes(range=[0, 105], ticksuffix="%")
        cp.mostrar_grafico(cp.layout_grafico(fig, "Ocupação de gerentes e membros", altura=290))
    with c6:
        x = [cfg.MESES_ABREV[i - 1] for i in df["mes_num"]]
        fig = go.Figure()
        fig.add_bar(x=x, y=df["nota_contextualizacao"], name="Contextualização", marker_color=cfg.COR_PRINCIPAL)
        fig.add_bar(x=x, y=df["nota_comunicacao"], name="Comunicação", marker_color="#CC9900")
        fig.update_layout(barmode="group")
        fig.update_yaxes(range=[0, 10])
        cp.mostrar_grafico(cp.layout_grafico(fig, "Contextualização × comunicação dos gerentes", altura=290))
    with c7:
        cp.mostrar_grafico(cp.gauge(m["pct_csat_coletados"], "Cobertura da coleta de CSAT", altura=270))
        cp.nota(f"{mt.formatar_inteiro(df['csat_coletados'].sum())} CSATs coletados de "
                   f"{mt.formatar_inteiro(df['projetos_elegiveis_csat'].sum())} projetos finalizados elegíveis."
                   if df["projetos_elegiveis_csat"].sum() else "Nenhum projeto elegível no período.")

    with st.expander("📌 Premissas e pendências da Direx"):
        st.markdown(
            "- **Fonte de dados centralizada:** ainda não existe. O protótipo usa dados simulados; o schema esperado está em `dados_modelo/`.\n"
            "- **Cancelados × rescisões:** premissa de que a rescisão é um subconjunto dos cancelados com contrato formalmente rescindido. *Validar com quem administra os contratos.*\n"
            "- **Alocados no momento × alocações no período:** o primeiro é uma foto do último mês; o segundo soma vínculos iniciados e pode contar a mesma pessoa mais de uma vez.\n"
            "- **Periodicidade de atualização:** premissa mensal (dados fechados no fim de cada mês).\n"
            f"- **Escalas:** CSAT de {cfg.ESCALA_CSAT[0]} a {cfg.ESCALA_CSAT[1]}; respostas de NPS de {cfg.ESCALA_NPS_RESPOSTA[0]} a {cfg.ESCALA_NPS_RESPOSTA[1]}."
        )

    renderizar_demandas()


def renderizar_demandas() -> None:
    cp.secao("Demandas pontuais da Diretoria de Projetos")
    st.session_state.setdefault("demandas", [])
    with st.form("form_demanda", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        nome = c1.text_input("Nome da demanda *")
        responsavel = c2.text_input("Responsável")
        prazo = c3.date_input("Prazo", value=date.today(), format="DD/MM/YYYY")
        descricao = st.text_area("Descrição", height=70)
        c4, c5, c6 = st.columns([1, 1, 2])
        status = c4.selectbox("Status", ["Não iniciada", "Em andamento", "Concluída", "Pausada"])
        prioridade = c5.selectbox("Prioridade", ["Baixa", "Média", "Alta"], index=1)
        obs = c6.text_input("Observações")
        if st.form_submit_button("Adicionar demanda", type="primary"):
            if not nome.strip():
                st.error("Informe o nome da demanda.")
            else:
                st.session_state["demandas"].append({
                    "Demanda": nome.strip(), "Descrição": descricao, "Responsável": responsavel,
                    "Prazo": prazo.strftime("%d/%m/%Y"), "Status": status, "Prioridade": prioridade, "Observações": obs,
                })
                st.success("Demanda cadastrada.")
    cp.nota("⚠ Dados temporários: as demandas somem quando a sessão é encerrada. Baixe o CSV para guardar.")
    demandas = st.session_state["demandas"]
    if not demandas:
        st.info("Nenhuma demanda cadastrada nesta sessão.")
        return
    tabela = pd.DataFrame(demandas)
    tabela.insert(0, "Remover", False)
    editada = st.data_editor(
        tabela, hide_index=True, use_container_width=True, key="editor_demandas",
        column_config={
            "Remover": st.column_config.CheckboxColumn("Remover", width="small"),
            "Status": st.column_config.SelectboxColumn("Status", options=["Não iniciada", "Em andamento", "Concluída", "Pausada"]),
            "Prioridade": st.column_config.SelectboxColumn("Prioridade", options=["Baixa", "Média", "Alta"]),
        },
        disabled=["Demanda", "Descrição", "Responsável", "Prazo", "Observações"],
    )
    c1, c2 = st.columns([1, 4])
    if c1.button("Salvar alterações"):
        st.session_state["demandas"] = editada[~editada["Remover"]].drop(columns="Remover").to_dict("records")
        st.success("Alterações aplicadas.")
        st.rerun()
    with c2:
        cp._baixar_csv(demandas, f"{date.today():%Y-%m-%d}-demandas-projetos.csv", "dl_demandas")
