"""Configurações centrais do Dashboard ESTAT.

Tudo o que for regra de negócio provisória (faixas, metas, escalas, modo de
agregação) mora aqui, para ser alterado sem mexer no restante do código.
"""
from __future__ import annotations

ANO_REFERENCIA = 2026

# Fonte dos dados: "simulado" (gera dados fictícios) ou "csv" (lê dados_modelo/*.csv)
FONTE_DADOS = "simulado"
SEMENTE = 2026

MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]
MESES_ABREV = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
DIAS_SEMANA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

# ---------------------------------------------------------------- identidade
# Tema escuro "futurista" com as cores oficiais da ESTAT.
COR_PRINCIPAL = "#A11D21"          # vermelho institucional
COR_PRINCIPAL_BRILHO = "#E0353B"   # tom derivado, mais luminoso, para linhas e destaques no fundo escuro
COR_PRINCIPAL_CLARA = "rgba(161,29,33,0.18)"
CORES_ESTAT = [  # vetor cores_estat da Padronização ESTAT (packages.R)
    "#A11D21", "#003366", "#CC9900", "#663333", "#FF6600",
    "#CC9966", "#999966", "#006606", "#008091", "#041835", "#666666",
]
# Subconjunto das cores ESTAT legível sobre fundo preto (azuis-marinho ficam de fora)
SERIES = ["#E0353B", "#CC9900", "#008091", "#CC9966", "#FF6600", "#999966"]
COR_FUNDO = "#07070A"
COR_PAINEL = "#111117"
COR_BORDA = "rgba(255,255,255,0.07)"
COR_TEXTO = "#F2F2F5"
COR_TEXTO_SUAVE = "#9A9AA8"
COR_GRADE = "rgba(255,255,255,0.06)"
COR_SUCESSO = "#3DDC84"
COR_ALERTA = "#F2C200"
COR_PERIGO = "#FF4D52"
SITE_ESTAT = "https://estat.com.br/"

# ------------------------------------------------- farol de alocação (provisório)
# (limite_inferior_inclusivo, limite_superior_exclusivo, rótulo, cor, cor_do_texto)
FAIXAS_FAROL = [
    (0, 40, "Baixa", "#2E7D32", "#FFFFFF"),
    (40, 60, "Moderada", "#F2C200", "#1F1F1F"),
    (60, 75, "Alta", "#EF7D00", "#1F1F1F"),
    (75, 90, "Muito alta", "#C62828", "#FFFFFF"),
    (90, 100.0001, "Crítica", "#000000", "#FFFFFF")  # preto: recebe contorno claro no tema escuro,
]

# ------------------------------------------------------- escalas e faixas
ESCALA_CSAT = (1, 5)          # CSAT de 1 a 5 (definido pela diretoria)
ESCALA_NPS_RESPOSTA = (1, 10)  # respostas da pergunta de NPS: 1 a 10
NPS_PROMOTOR_MIN = 9           # promotores: 9–10
NPS_DETRATOR_MAX = 6           # detratores: 1–6 (neutros: 7–8)
ESCALA_NOTAS = (0, 10)  # notas de contextualização, comunicação e clima
FAIXAS_NPS = [(-100, 0, "Crítica", COR_PERIGO), (0, 50, "Neutra", COR_ALERTA), (50, 100.0001, "Excelência", COR_SUCESSO)]

# Taxa de conversão: denominador configurável ("reunioes_diagnostico" ou "reunioes_proposta")
DENOMINADOR_CONVERSAO = "reunioes_diagnostico"

# ------------------------------------------------- regras de agregação
# "razao_agregada": soma(numerador) / soma(denominador) no período (padrão — dá peso
#                   proporcional ao tamanho de cada mês).
# "media_simples":  média aritmética dos percentuais mensais (peso igual por mês).
MODO_AGREGACAO_PERCENTUAIS = "razao_agregada"

# tipo: soma | ultimo | media | razao | csat | nps
METRICAS: dict[str, dict] = {
    # volumes (somam)
    "faturamento": {"tipo": "soma"},
    "meta_faturamento": {"tipo": "soma"},
    "reunioes_diagnostico": {"tipo": "soma"},
    "reunioes_proposta": {"tipo": "soma"},
    "contratos_fechados": {"tipo": "soma"},
    "projetos_iniciados": {"tipo": "soma"},
    "projetos_concluidos": {"tipo": "soma"},
    "projetos_cancelados": {"tipo": "soma"},
    "rescisoes": {"tipo": "soma"},
    "alocacoes_gerentes": {"tipo": "soma"},
    "alocacoes_executores": {"tipo": "soma"},
    # posição no último mês selecionado
    "projetos_andamento": {"tipo": "ultimo"},
    "alocados_gerentes": {"tipo": "ultimo"},
    "alocados_executores": {"tipo": "ultimo"},
    "membros_diversidade": {"tipo": "ultimo"},
    "meta_diversidade": {"tipo": "ultimo"},
    # notas (média simples dos meses com dado)
    "nota_contextualizacao": {"tipo": "media"},
    "nota_comunicacao": {"tipo": "media"},
    "nota_clima": {"tipo": "media"},
    # percentuais com numerador/denominador
    "pct_gerentes_ocupados": {"tipo": "razao", "num": "gerentes_ocupados", "den": "gerentes_total"},
    "pct_membros_alocados": {"tipo": "razao", "num": "membros_alocados", "den": "membros_total"},
    "pct_csat_coletados": {"tipo": "razao", "num": "csat_coletados", "den": "projetos_elegiveis_csat"},
    # especiais
    "csat": {"tipo": "csat"},  # média ponderada pelas respostas
    "nps": {"tipo": "nps"},    # recalculado a partir de promotores/detratores
    "nps_nota_media": {"tipo": "nps_media"},  # média das respostas (1–10), ponderada
}

ROTULO_TIPO = {
    "soma": "Acumulado",
    "ultimo": "Último mês",
    "media": "Média do período",
    "razao": "Média do período",
    "csat": "Média do período",
    "nps": "Período",
    "nps_media": "Média do período",
}
