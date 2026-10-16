"""Dashboard ESTAT — protótipo (dados simulados).

Executar (qualquer uma das opções):
  - botão ▷ "Run Python File" do VS Code, ou  python app.py
  - dois cliques em rodar.bat
  - streamlit run app.py   (de dentro desta pasta)
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import streamlit as st
from streamlit import runtime

PASTA = Path(__file__).resolve().parent

if __name__ == "__main__" and not runtime.exists():
    # Rodado como script comum (ex.: botão ▷ do VS Code): relança via Streamlit,
    # a partir desta pasta, para que .streamlit/config.toml (tema escuro) seja lido.
    sys.exit(subprocess.call([sys.executable, "-m", "streamlit", "run", str(PASTA / "app.py")], cwd=PASTA))

_ICONE = PASTA / "assets" / "logo_estat.png"
st.set_page_config(page_title="Painel ESTAT", page_icon=str(_ICONE) if _ICONE.exists() else "📊", layout="wide", initial_sidebar_state="expanded")

import componentes as cp  # noqa: E402
import config as cfg  # noqa: E402
import metricas as mt  # noqa: E402
from abas.geral import renderizar_aba_geral  # noqa: E402
from abas.gestao import renderizar_aba_gestao  # noqa: E402
from abas.negocios import renderizar_aba_negocios  # noqa: E402
from abas.projetos import renderizar_aba_projetos  # noqa: E402
from dados import carregar_dados_2026  # noqa: E402


def barra_lateral() -> list[str]:
    with st.sidebar:
        cp.renderizar_marca()
        st.markdown("### Painel institucional")
        if cfg.FONTE_DADOS == "simulado":
            st.markdown("<span class='chip-sim'>DADOS SIMULADOS</span>", unsafe_allow_html=True)
        st.write("")
        st.session_state.setdefault("filtro_meses", list(cfg.MESES))
        if st.button("Selecionar todos os meses", use_container_width=True):
            st.session_state["filtro_meses"] = list(cfg.MESES)
        selecionados = st.multiselect(f"Meses de {cfg.ANO_REFERENCIA}", cfg.MESES, key="filtro_meses",
                                      placeholder="Escolha um ou mais meses")
        with st.expander("Como os números são agregados"):
            modo = "soma dos numeradores ÷ soma dos denominadores" if cfg.MODO_AGREGACAO_PERCENTUAIS == "razao_agregada" else "média simples dos meses"
            st.markdown(
                "- **Acumulado:** volumes somados (faturamento, reuniões, projetos concluídos…).\n"
                "- **Último mês:** posições/estoques (projetos em andamento, alocados no momento).\n"
                "- **Média do período:** notas pela média; percentuais pela " + modo + ".\n"
                "- **CSAT:** média ponderada pelas respostas.\n"
                f"- **NPS:** respostas de {cfg.ESCALA_NPS_RESPOSTA[0]} a {cfg.ESCALA_NPS_RESPOSTA[1]}; recalculado com todas as respostas do período (não é média de NPS mensais)."
            )
        st.markdown(f"[estat.com.br ↗]({cfg.SITE_ESTAT})")
    return mt.ordenar_meses(selecionados)


def main() -> None:
    cp.aplicar_css()
    meses = barra_lateral()
    cp.renderizar_cabecalho(mt.descrever_periodo(meses))

    if not meses:
        st.info("Selecione ao menos um mês na barra lateral para ver os indicadores.")
        return
    try:
        df_completo = carregar_dados_2026()
    except Exception as erro:
        st.error(f"Não foi possível carregar os dados: {erro}")
        return
    df = mt.filtrar_dados_por_mes(df_completo, meses)
    if df.empty:
        st.warning("Não há dados para os meses selecionados.")
        return
    m = mt.calcular_metricas_gerais(df)

    abas = st.tabs(["Visão Geral", "Projetos", "Gestão", "Negócios"])
    renderizadores = [renderizar_aba_geral, renderizar_aba_projetos, renderizar_aba_gestao, renderizar_aba_negocios]
    for aba, renderizar in zip(abas, renderizadores):
        with aba:
            try:
                renderizar(df, df_completo, meses, m)
            except Exception as erro:  # uma aba com erro não derruba as demais
                st.error(f"Erro ao montar esta aba: {erro}")


main()
