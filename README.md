# Dashboard ESTAT — protótipo (dados simulados)

Protótipo em Streamlit com quatro abas: Visão Geral, Projetos, Gestão e Negócios.

## Rodar no Windows

```bat
cd "2026-10-15-dashboard-estat"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Para os testes, rode `python -m pytest tests`.

## Arquivos

| Arquivo | Papel |
|---|---|
| `app.py` | Entrada do app: barra lateral, filtro de meses e abas |
| `config.py` | Cores, faixas do farol, escalas, regras de agregação e `FONTE_DADOS` |
| `dados.py` | `carregar_dados_2026()`, a simulação e `calcular_indice_ocupacao_diaria()` (placeholder) |
| `metricas.py` | Cálculos puros: agregação, NPS, conversão, formatação BR |
| `componentes.py` | CSS, cards, farol, heatmap e formulários |
| `abas/*.py` | Uma função `renderizar_aba_*` por aba |
| `dados_modelo/` | CSVs vazios com o schema dos dados reais |
| `.streamlit/config.toml` | Tema escuro com o vermelho institucional |
| `assets/logo_estat_escuro.png` | Logo com letras claras para o fundo preto |

## Trocar os dados simulados pelos reais

1. Preencha `dados_modelo/mensal.csv`, com uma linha por mês e as colunas do cabeçalho. `projetos.csv` é o schema por projeto, para quando houver a base desagregada.
2. Em `config.py`, troque `FONTE_DADOS = "simulado"` por `"csv"`.
3. Se o CSV estiver inválido, o app avisa e volta para os dados simulados, sem quebrar.
4. Para ler de Google Sheets ou de um banco, edite apenas `carregar_dados_2026()` em `dados.py`. A função deve devolver um DataFrame com as mesmas colunas.

### Dicionário da tabela mensal (`mensal.csv`)

- **Identificação:** `mes_num` (1–12) e `mes` (nome do mês).
- **Comercial:** `faturamento`, `meta_faturamento`, `reunioes_diagnostico`, `reunioes_proposta` e `contratos_fechados`, todos volumes do mês.
- **Projetos (volume):** `projetos_iniciados`, `projetos_concluidos`, `projetos_cancelados`, `rescisoes`, `alocacoes_gerentes` e `alocacoes_executores`.
- **Projetos (posição no fim do mês):** `projetos_andamento`, `alocados_gerentes` e `alocados_executores`.
- **Ocupação:** `gerentes_ocupados`/`gerentes_total` e `membros_alocados`/`membros_total`.
- **Satisfação:** `csat_coletados`, `projetos_elegiveis_csat` e `csat_soma_notas` (soma das notas de 1 a 5, para a média ponderada), além de `nps_promotores`, `nps_neutros`, `nps_detratores` e `nps_soma_notas` (soma das respostas de 1 a 10).
- **Notas (0–10):** `nota_contextualizacao`, `nota_comunicacao` e `nota_clima`.
- **Diversidade:** `membros_diversidade` e `meta_diversidade`, apenas contagens agregadas.
