# Premissas adotadas e pendências da Direx

## Agregação (`config.py`)

- **Volumes:** são somados no período.
- **Posições:** projetos em andamento, alocados no momento e membros de diversidade usam o valor do último mês selecionado.
- **Percentuais:** o padrão é `razao_agregada` (soma dos numeradores ÷ soma dos denominadores). `media_simples` está disponível.
- **CSAT:** média ponderada pelo número de respostas.
- **NPS:** recalculado com todas as respostas do período, nunca como média de NPS mensais.

## Premissas provisórias (validar)

1. **Escalas (definidas pela diretoria):** o CSAT vai de 1 a 5. As respostas de NPS vão de 1 a 10, com promotores em 9–10, neutros em 7–8 e detratores em 1–6. O NPS final vai de −100 a 100, e o painel também mostra a nota média das respostas (1–10).
2. **Faixas do farol:** verde < 40%, amarelo < 60%, laranja < 75%, vermelho < 90%, preto ≥ 90%.
3. **Faixas do NPS:** < 0 crítica, 0–49 neutra, ≥ 50 excelência.
4. **Taxa de conversão:** contratos ÷ reuniões de diagnóstico. O denominador é configurável.
5. **Rescisão:** tratada como subconjunto dos cancelados com contrato formalmente rescindido.
6. **Contrato fechado:** conta como projeto iniciado no mesmo mês, mas só nos dados simulados.
7. **Faturamento simulado:** 50% na assinatura e 50% na conclusão do projeto.
8. **Periodicidade:** mensal, com dados fechados no fim de cada mês.
9. **Ocupação diária:** o índice é simulado (`calcular_indice_ocupacao_diaria()`). A fórmula real ainda será definida.
10. **Demandas e sugestões:** ficam só na sessão. Há botão para baixar em CSV.

## Pendências da Direx (documento de pré-requisitos de 16/09)

- Definir a fonte de dados centralizada e quem a mantém atualizada.
- Validar a diferença entre cancelados e rescisões.
- Validar a diferença entre alocados no momento e alocações no período.
- Decidir a periodicidade de atualização.
- Confirmar as métricas novas (% de gerentes ocupados, notas dos gerentes, % de CSAT coletados), que estão fora da especificação v1.
