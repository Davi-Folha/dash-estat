"""Componentes visuais reutilizáveis — tema escuro com identidade ESTAT."""
from __future__ import annotations

import math
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import config as cfg
import metricas as mt

ASSETS = Path(__file__).parent / "assets"
LOGO_ESCURO = ASSETS / "logo_estat_escuro.png"  # versão com letras claras para fundo preto
LOGO = ASSETS / "logo_estat.png"


def aplicar_css() -> None:
    c = cfg
    css = (
        f"""
        <link href="https://fonts.googleapis.com/css2?family=Bungee&family=Montserrat:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
        :root {{
            --vermelho: {c.COR_PRINCIPAL}; --brilho: {c.COR_PRINCIPAL_BRILHO};
            --painel: {c.COR_PAINEL}; --borda: {c.COR_BORDA};
            --texto: {c.COR_TEXTO}; --suave: {c.COR_TEXTO_SUAVE};
        }}
        html, body, [class*="css"], .stMarkdown, button, input, textarea, select, label {{
            font-family: 'Montserrat', 'Segoe UI', sans-serif !important;
        }}
        .stApp {{
            background-color: {c.COR_FUNDO};
            background-image:
                radial-gradient(1200px 520px at 8% -8%, rgba(161,29,33,.34), transparent 60%),
                radial-gradient(900px 500px at 100% 0%, rgba(0,128,145,.10), transparent 60%),
                linear-gradient(rgba(255,255,255,.025) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,.025) 1px, transparent 1px);
            background-size: auto, auto, 44px 44px, 44px 44px;
            background-attachment: fixed;
        }}
        header[data-testid="stHeader"] {{ background: transparent; }}
        [data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer {{ visibility: hidden; height: 0; }}
        .block-container {{ padding-top: 1.6rem; max-width: 1420px; }}
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #0E0E13 0%, #09090C 100%);
            border-right: 1px solid rgba(161,29,33,.35);
        }}
        section[data-testid="stSidebar"] h3 {{ font-family: 'Bungee', sans-serif !important; font-size: .95rem; letter-spacing: .04em; color: var(--texto); }}
        .marca {{ font-family: 'Bungee', sans-serif; color: var(--texto); font-size: 2.2rem; line-height: 1; }}
        .marca span {{ color: var(--brilho); }}
        .marca-sub {{ font-size: .72rem; color: var(--suave); letter-spacing: .14em; text-transform: uppercase; margin-top: 6px; }}
        .chip-sim {{ display:inline-flex; align-items:center; gap:8px; border:1px solid rgba(242,194,0,.45); color:#F2C200;
                     background: rgba(242,194,0,.08); border-radius: 999px; padding: 3px 12px; font-size: .72rem; font-weight: 700; letter-spacing: .08em; }}
        .chip-sim::before {{ content:''; width:7px; height:7px; border-radius:50%; background:#F2C200; box-shadow: 0 0 10px #F2C200; animation: pulsar 1.8s infinite; }}
        @keyframes pulsar {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: .25; }} }}
        .hero {{ display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:14px; margin-bottom: 10px; }}
        .hero .sobre {{ font-size: .72rem; letter-spacing: .32em; color: var(--suave); text-transform: uppercase; font-weight: 600; }}
        .hero h1 {{ font-family: 'Bungee', sans-serif !important; font-size: clamp(2rem, 4.2vw, 3.3rem); line-height: 1.02; margin: 4px 0 0; padding: 0;
                   background: linear-gradient(92deg, #FFFFFF 0%, #FFFFFF 38%, var(--brilho) 75%, var(--vermelho) 100%);
                   -webkit-background-clip: text; background-clip: text; color: transparent; }}
        .periodo {{ display:inline-flex; gap:10px; align-items:center; border:1px solid rgba(161,29,33,.55); background: rgba(161,29,33,.12);
                    border-radius: 999px; padding: 7px 16px; font-weight: 600; font-size: .85rem; color: var(--texto);
                    box-shadow: 0 0 22px rgba(161,29,33,.25) inset; }}
        .periodo b {{ color: var(--brilho); font-weight: 800; letter-spacing: .05em; }}
        .linha-neon {{ height:2px; margin: 10px 0 6px; background: linear-gradient(90deg, var(--vermelho), rgba(161,29,33,0) 70%); box-shadow: 0 0 12px var(--vermelho); }}
        div[data-testid="stTabs"] [role="tablist"] {{ gap: 22px; border-bottom: 1px solid var(--borda); }}
        div[data-testid="stTabs"] button[role="tab"] {{ background: transparent; border-radius: 10px 10px 0 0; padding: 8px 18px; }}
        div[data-testid="stTabs"] button[role="tab"] p {{ font-family: 'Bungee', sans-serif !important; font-size: .82rem; letter-spacing: .05em; color: var(--suave); }}
        div[data-testid="stTabs"] button[aria-selected="true"] {{ background: linear-gradient(180deg, rgba(161,29,33,.30), rgba(161,29,33,0)); }}
        div[data-testid="stTabs"] button[aria-selected="true"] p {{ color: #FFFFFF; }}
        .secao {{ font-family: 'Bungee', sans-serif; font-size: .95rem; letter-spacing: .06em; color: var(--texto);
                  margin: 26px 0 12px; display:flex; align-items:center; gap:10px; flex-wrap: wrap; }}
        .secao::before {{ content:''; width: 10px; height: 18px; background: var(--vermelho); border-radius: 2px; box-shadow: 0 0 12px var(--vermelho); }}
        .secao::after {{ content:''; flex: 1; min-width: 40px; height: 1px; background: linear-gradient(90deg, var(--borda), transparent); }}
        .tag-nova {{ font-family: 'Montserrat', sans-serif; font-size: .65rem; letter-spacing: .08em; text-transform: uppercase; font-weight: 700;
                     color: #5FD3E0; border: 1px solid rgba(0,128,145,.6); background: rgba(0,128,145,.12); border-radius: 999px; padding: 2px 10px; }}
        .card {{
            position: relative; overflow: hidden; height: 100%; min-height: 128px;
            background: linear-gradient(160deg, rgba(28,28,36,.92), rgba(14,14,19,.92));
            border: 1px solid var(--borda); border-radius: 16px; padding: 16px 18px 14px;
            box-shadow: 0 10px 30px rgba(0,0,0,.35);
            transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
        }}
        .card::before {{ content:''; position:absolute; inset:0 0 auto 0; height:2px;
                         background: linear-gradient(90deg, transparent, var(--brilho), transparent); opacity:.9; }}
        .card::after {{ content:''; position:absolute; width:140px; height:140px; right:-50px; top:-70px; border-radius:50%;
                        background: radial-gradient(circle, rgba(161,29,33,.30), transparent 70%); }}
        .card:hover {{ transform: translateY(-3px); border-color: rgba(224,53,59,.55); box-shadow: 0 0 0 1px rgba(224,53,59,.25), 0 14px 38px rgba(161,29,33,.30); }}
        .card .rotulo {{ font-size: .68rem; color: var(--suave); font-weight: 700; text-transform: uppercase; letter-spacing: .14em; }}
        .card .valor {{ font-size: 1.85rem; font-weight: 800; color: var(--texto); margin: 8px 0 6px; line-height: 1.1;
                        font-variant-numeric: tabular-nums; letter-spacing: -.01em; }}
        .card .valor small {{ font-size: .9rem; color: var(--suave); font-weight: 600; }}
        .card .rodape {{ display:flex; gap:8px; align-items:center; flex-wrap:wrap; font-size: .74rem; color: var(--suave); }}
        .card .detalhe {{ font-size: .74rem; color: var(--suave); margin-top: 6px; }}
        .selo {{ border: 1px solid rgba(224,53,59,.45); color: #FF8A8E; border-radius: 999px; padding: 1px 9px; font-weight: 700;
                 font-size: .62rem; letter-spacing: .08em; text-transform: uppercase; }}
        .delta-pos {{ color: {c.COR_SUCESSO}; font-weight: 700; }}
        .delta-neg {{ color: {c.COR_PERIGO}; font-weight: 700; }}
        .resumo-dir {{ background: linear-gradient(160deg, rgba(28,28,36,.9), rgba(14,14,19,.9)); border: 1px solid var(--borda);
                       border-left: 3px solid var(--vermelho); border-radius: 14px; padding: 14px 18px; height: 100%; color: var(--texto); line-height: 1.7; }}
        .resumo-dir .t {{ font-family: 'Bungee', sans-serif; color: var(--brilho); letter-spacing: .05em; font-size: .9rem; }}
        .resumo-dir b {{ color: #FFFFFF; }}
        [data-testid="stPlotlyChart"] {{ background: linear-gradient(160deg, rgba(24,24,31,.85), rgba(12,12,16,.85));
            border: 1px solid var(--borda); border-radius: 16px; padding: 8px 8px 4px; box-shadow: 0 10px 30px rgba(0,0,0,.30); }}
        [data-testid="stForm"] {{ background: rgba(17,17,23,.85); border: 1px solid var(--borda); border-radius: 16px; }}
        [data-testid="stExpander"] details {{ background: rgba(17,17,23,.85); border: 1px solid var(--borda); border-radius: 12px; }}
        .stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {{
            border-radius: 10px; font-weight: 700; letter-spacing: .03em; }}
        [data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"], .stButton > button[kind="primary"] {{
            background: linear-gradient(90deg, var(--vermelho), var(--brilho)); border: 0; box-shadow: 0 0 18px rgba(224,53,59,.4); }}
        [data-testid="stProgress"] > div > div > div > div {{ background: linear-gradient(90deg, var(--vermelho), var(--brilho)); box-shadow: 0 0 14px var(--brilho); }}
        .legenda-farol span {{ border-radius: 6px; padding: 3px 9px; margin: 3px 4px 3px 0; display: inline-block; font-size: .7rem; font-weight: 700; letter-spacing: .03em; }}
        .nota {{ font-size: .74rem; color: var(--suave); margin-top: 4px; }}
        .nota code {{ color: #FF8A8E; background: rgba(161,29,33,.15); }}
        </style>
        """
    )
    # Linhas em branco ou indentadas fazem o Markdown encerrar o bloco HTML e imprimir o CSS como texto.
    st.markdown("\n".join(linha.strip() for linha in css.splitlines() if linha.strip()), unsafe_allow_html=True)


def renderizar_marca() -> None:
    for caminho in (LOGO_ESCURO, LOGO):
        if caminho.exists():
            try:
                st.image(str(caminho), width=160)
                st.markdown("<div class='marca-sub'>Consultoria Estatística · UnB</div>", unsafe_allow_html=True)
                return
            except Exception:
                continue
    st.markdown("<div class='marca'><span>›</span>ESTAT</div><div class='marca-sub'>Consultoria Estatística<br>Universidade de Brasília</div>",
                unsafe_allow_html=True)


def renderizar_cabecalho(periodo: str) -> None:
    st.markdown(
        f"<div class='hero'><div><div class='sobre'>ESTAT · Consultoria Estatística · {cfg.ANO_REFERENCIA}</div>"
        f"<h1>Painel de Indicadores</h1></div>"
        f"<div class='periodo'>PERÍODO <b>{periodo.upper()}</b></div></div><div class='linha-neon'></div>",
        unsafe_allow_html=True,
    )


def renderizar_card_metrica(rotulo: str, valor: str, tipo: str = "", delta: float | None = None,
                            fmt_delta=None, ajuda: str = "", inverter_delta: bool = False, detalhe: str = "") -> None:
    selo = f"<span class='selo'>{tipo}</span>" if tipo else ""
    delta_html = ""
    if delta is not None and not pd.isna(delta):
        positivo = (delta >= 0) != inverter_delta
        seta = "▲" if delta >= 0 else "▼"
        txt = fmt_delta(abs(delta)) if fmt_delta else mt.formatar_inteiro(abs(delta))
        delta_html = f"<span class='{'delta-pos' if positivo else 'delta-neg'}'>{seta} {txt} vs mês anterior</span>"
    titulo = f" title=\"{ajuda}\"" if ajuda else ""
    icone = " ⓘ" if ajuda else ""
    det = f"<div class='detalhe'>{detalhe}</div>" if detalhe else ""
    st.markdown(
        f"<div class='card'{titulo}><div class='rotulo'>{rotulo}{icone}</div><div class='valor'>{valor}</div>"
        f"<div class='rodape'>{selo}{delta_html}</div>{det}</div>",
        unsafe_allow_html=True,
    )


def secao(titulo: str, nova: bool = False) -> None:
    tag = "<span class='tag-nova'>nova · fora da especificação v1</span>" if nova else ""
    st.markdown(f"<div class='secao'>{titulo.upper()}{tag}</div>", unsafe_allow_html=True)


def nota(texto: str) -> None:
    st.markdown(f"<div class='nota'>{texto}</div>", unsafe_allow_html=True)


def layout_grafico(fig: go.Figure, titulo: str = "", altura: int = 320, eixo_y: str = "") -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        title=dict(text=titulo.upper(), font=dict(size=13, color=cfg.COR_TEXTO, family="Montserrat, sans-serif"), x=0.01, xanchor="left"),
        height=altura, margin=dict(l=12, r=12, t=48 if titulo else 18, b=12),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", separators=",.",
        font=dict(family="Montserrat, Segoe UI, sans-serif", color=cfg.COR_TEXTO_SUAVE, size=12),
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5, title=None, font=dict(color=cfg.COR_TEXTO)),
        hoverlabel=dict(bgcolor="#16161D", bordercolor=cfg.COR_PRINCIPAL_BRILHO, font=dict(color="#FFFFFF", size=12, family="Montserrat")),
        colorway=cfg.SERIES, bargap=0.28,
    )
    fig.update_xaxes(showgrid=False, linecolor=cfg.COR_GRADE, tickfont=dict(color=cfg.COR_TEXTO_SUAVE), title=None)
    fig.update_yaxes(gridcolor=cfg.COR_GRADE, zeroline=False, linecolor="rgba(0,0,0,0)", tickfont=dict(color=cfg.COR_TEXTO_SUAVE), title=eixo_y or None)
    return fig


def _rgba(hex_cor: str, alfa: float) -> str:
    h = hex_cor.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alfa})"


def linha_neon(fig: go.Figure, x, y, nome: str, cor: str = cfg.COR_PRINCIPAL_BRILHO, hover: str = "%{y}",
               preencher: bool = False, yaxis: str = "y", tracejada: bool = False) -> None:
    """Linha com efeito 'neon': traço largo e translúcido por baixo do traço principal."""
    fig.add_scatter(x=x, y=y, mode="lines", line=dict(color=cor, width=10, shape="spline", smoothing=0.6), opacity=0.16,
                    hoverinfo="skip", showlegend=False, connectgaps=True, yaxis=yaxis)
    fig.add_scatter(x=x, y=y, name=nome, mode="lines+markers", connectgaps=True, yaxis=yaxis,
                    line=dict(color=cor, width=3, shape="spline", smoothing=0.6, dash="dot" if tracejada else "solid"),
                    marker=dict(size=7, color=cfg.COR_FUNDO, line=dict(color=cor, width=2)),
                    fill="tozeroy" if preencher else None,
                    fillcolor=_rgba(cor, 0.10) if preencher else None,
                    hovertemplate=f"%{{x}}: {hover}<extra>{nome}</extra>")


def mostrar_grafico(fig: go.Figure) -> None:
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "locale": "pt-BR"})


def gauge(valor: float, titulo: str, faixas: list[tuple] | None = None, cor_barra: str = cfg.COR_PRINCIPAL_BRILHO,
          rotulo_inferior: str = "", altura: int = 290) -> go.Figure:
    v = 0 if valor is None or pd.isna(valor) else mt.limitar_pct(valor)
    if faixas:
        steps = [dict(range=[ini, min(fim, 100)], color=cor,
                      line=dict(color="rgba(255,255,255,.45)" if cor == "#000000" else cor, width=1.5))
                 for ini, fim, _, cor, *_ in faixas]
    else:
        steps = [dict(range=[0, 100], color="rgba(255,255,255,.05)")]
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=v,
        number=dict(suffix="%", valueformat=".1f", font=dict(size=42, color="#FFFFFF", family="Montserrat, Segoe UI, Arial, sans-serif")),
        gauge=dict(
            shape="angular",
            axis=dict(range=[0, 100], ticksuffix="%", tickcolor=cfg.COR_TEXTO_SUAVE, tickfont=dict(size=10, color=cfg.COR_TEXTO_SUAVE)),
            bar=dict(color="rgba(0,0,0,0)" if faixas else cor_barra, thickness=0.0 if faixas else 0.32),
            bgcolor="rgba(255,255,255,.03)", borderwidth=0, steps=steps,
            threshold=dict(line=dict(color="#FFFFFF", width=5), thickness=0.95, value=v),
        ),
    ))
    layout_grafico(fig, titulo, altura=altura)
    fig.update_layout(margin=dict(l=34, r=34))
    if rotulo_inferior:
        fig.update_layout(margin=dict(b=36))
        fig.add_annotation(text=rotulo_inferior, x=0.5, y=-0.1, showarrow=False, xref="paper", yref="paper",
                           font=dict(size=13, color=cfg.COR_TEXTO))
    return fig


def gauge_alocacao(pct: float, titulo: str = "Farol de alocação dos membros") -> go.Figure:
    rotulo = mt.obter_faixa_alocacao(pct)[0]
    return gauge(pct, titulo, faixas=cfg.FAIXAS_FAROL, rotulo_inferior=f"Faixa: <b>{rotulo}</b>")


def legenda_farol() -> None:
    partes = []
    for ini, fim, rotulo, cor, cor_txt in cfg.FAIXAS_FAROL:
        borda = "border:1px solid rgba(255,255,255,.45);" if cor == "#000000" else ""
        partes.append(f"<span style='background:{cor};color:{cor_txt};{borda}'>{rotulo} {ini:.0f}–{min(fim, 100):.0f}%</span>")
    st.markdown(
        "<div class='legenda-farol'>" + "".join(partes) + "</div><div class='nota'>Verde = menor ocupação · preto = maior ocupação. "
        "Faixas provisórias, configuráveis em <code>config.py</code>.</div>",
        unsafe_allow_html=True,
    )


def heatmap_ocupacao(diario: pd.DataFrame, meses_num: list[int]) -> go.Figure:
    """Calendário estilo 'contribuições' (semanas × dias da semana)."""
    d = diario.copy()
    d["mes"] = d["data"].dt.month
    d.loc[~d["mes"].isin(meses_num), "indice"] = math.nan  # meses fora do filtro ficam apagados
    inicio = d["data"].min()
    d["semana"] = ((d["data"] - (inicio - pd.Timedelta(days=inicio.dayofweek))).dt.days // 7).astype(int)
    d["dow"] = d["data"].dt.dayofweek
    n_sem = d["semana"].max() + 1
    z = [[math.nan] * n_sem for _ in range(7)]
    fundo = [[math.nan] * n_sem for _ in range(7)]
    texto = [[""] * n_sem for _ in range(7)]
    for _, r in d.iterrows():
        fundo[r["dow"]][r["semana"]] = 1
        z[r["dow"]][r["semana"]] = r["indice"]
        if not pd.isna(r["indice"]):
            faixa = mt.obter_faixa_alocacao(r["indice"])[0]
            texto[r["dow"]][r["semana"]] = (
                f"<b>{r['data']:%d/%m/%Y}</b> · {cfg.DIAS_SEMANA[r['dow']]}<br>Ocupação: {mt.formatar_pct(r['indice'])}<br>Faixa: {faixa}")
    escala = []
    for ini, fim, _, cor, _ in cfg.FAIXAS_FAROL:
        escala += [(ini / 100, cor), (min(fim, 100) / 100, cor)]
    fig = go.Figure()
    # camada de fundo: todos os dias do ano (dias fora do filtro ficam visíveis, porém apagados)
    fig.add_heatmap(z=fundo, colorscale=[(0, "#1C1C25"), (1, "#1C1C25")], showscale=False, hoverinfo="skip", xgap=3, ygap=3)
    fig.add_heatmap(z=z, text=texto, hovertemplate="%{text}<extra></extra>", colorscale=escala, zmin=0, zmax=100, xgap=3, ygap=3,
                    colorbar=dict(title=dict(text="Índice", font=dict(color=cfg.COR_TEXTO_SUAVE)), ticksuffix="%", thickness=10, len=0.9,
                                  outlinewidth=0, tickfont=dict(color=cfg.COR_TEXTO_SUAVE)))
    marcas = d.groupby("mes")["semana"].min()
    fig.update_xaxes(tickvals=marcas.values, ticktext=[cfg.MESES_ABREV[m - 1] for m in marcas.index], side="top")
    fig.update_yaxes(tickvals=list(range(7)), ticktext=[s[:3] for s in cfg.DIAS_SEMANA], autorange="reversed")
    layout_grafico(fig, "", altura=270)
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
    return fig


def _baixar_csv(registros: list[dict], nome: str, chave: str) -> None:
    if registros:
        csv = pd.DataFrame(registros).to_csv(index=False, sep=";").encode("utf-8-sig")
        st.download_button("⬇ Baixar em CSV", csv, file_name=nome, mime="text/csv", key=chave)


def renderizar_formulario_sugestoes(diretoria_padrao: str, chave: str) -> None:
    """Formulário de sugestões de novos indicadores (dados só da sessão)."""
    estado = f"sugestoes_{chave}"
    st.session_state.setdefault(estado, [])
    diretorias = ["Geral", "Projetos", "Negócios", "Gestão"]
    with st.form(f"form_sug_{chave}", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Seu nome (opcional)")
        diretoria = c2.selectbox("Diretoria", diretorias, index=diretorias.index(diretoria_padrao))
        indicador = st.text_input("Nome do indicador sugerido *")
        descricao = st.text_area("Descrição", height=70)
        justificativa = st.text_area("Justificativa", height=70)
        c3, c4, c5 = st.columns(3)
        fonte = c3.text_input("Fonte de dados imaginada")
        periodicidade = c4.selectbox("Periodicidade", ["Semanal", "Mensal", "Semestral", "Anual"], index=1)
        prioridade = c5.selectbox("Prioridade", ["Baixa", "Média", "Alta"], index=1)
        if st.form_submit_button("Enviar sugestão", type="primary"):
            if not indicador.strip():
                st.error("Informe o nome do indicador.")
            else:
                st.session_state[estado].append({
                    "Nome": nome or "Anônimo", "Diretoria": diretoria, "Indicador": indicador.strip(),
                    "Descrição": descricao, "Justificativa": justificativa, "Fonte de dados": fonte,
                    "Periodicidade": periodicidade, "Prioridade": prioridade,
                })
                st.success("Sugestão registrada nesta sessão.")
    sugestoes = st.session_state[estado]
    nota("⚠ As sugestões ficam só nesta sessão e somem ao fechar o navegador. Baixe o CSV para guardar.")
    if sugestoes:
        st.dataframe(pd.DataFrame(sugestoes), use_container_width=True, hide_index=True)
        c1, c2 = st.columns([3, 1])
        opcoes = {f"{i + 1}. {s['Indicador']}": i for i, s in enumerate(sugestoes)}
        remover = c1.selectbox("Remover sugestão", list(opcoes), key=f"rm_sel_{chave}", label_visibility="collapsed")
        if c2.button("Remover", key=f"rm_btn_{chave}"):
            sugestoes.pop(opcoes[remover])
            st.rerun()
        _baixar_csv(sugestoes, f"{date.today():%Y-%m-%d}-sugestoes-{chave}.csv", f"dl_{chave}")


def indicadores_sugeridos(itens: list[tuple[str, str]]) -> None:
    nota("Sugestões para avaliação futura: <b>não são indicadores oficiais</b> e não estão sendo calculados.")
    for inicio in range(0, len(itens), 4):
        cols = st.columns(4)
        for col, (nome, desc) in zip(cols, itens[inicio:inicio + 4]):
            col.markdown(
                f"<div class='card' style='min-height:100px;margin-bottom:12px'><div class='rotulo'>Sugestão</div>"
                f"<div style='font-weight:700;color:{cfg.COR_TEXTO};margin:6px 0 4px'>{nome}</div><div class='detalhe'>{desc}</div></div>",
                unsafe_allow_html=True)
