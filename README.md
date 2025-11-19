# Clima — Temperatura Mensal (Projeto 04 Lite)

Projeto que analisa a temperatura média mensal e suas tendências usando pandas, numpy e plotly. Inclui carregamento de dados reais (API Open‑Meteo) ou simulados, importação de CSV do usuário, geração de gráficos simples, salvamento em CSV e insights sobre variações e padrões climáticos.

## Principais Recursos
- Fontes de dados: API Open‑Meteo, CSV do usuário, dados simulados
- Agregação: cálculo da média mensal a partir de séries de datas/temperaturas
- Tendência: regressão linear sobre médias mensais (aquecimento/resfriamento)
- Visualização: 1–2 gráficos (linha + tendência; opcional gráfico de barras)
- Exportação: salvamento do agregado em `data/output/monthly_temps.csv`
- Insights: picos (mês mais quente/frio), tendência anual e volatilidade mensal

## Tecnologia
- Backend: Python, FastAPI, Uvicorn, pandas, numpy, requests
- Frontend: React (Vite), Plotly (`react-plotly.js`), axios

## Estrutura
- `backend/analysis.py`: carga/normalização, agregação mensal, regressão e insights, salvamento de CSV
- `backend/app.py`: endpoints FastAPI, CORS, estáticos do frontend, Open‑Meteo
- `frontend-react/`: aplicação React (Vite) com UI, gráficos, chamadas de API
- `data/output/monthly_temps.csv`: saída do agregado mensal

## Instalação
1. Dependências Python:
   - `python -m pip install fastapi uvicorn pandas numpy python-multipart requests`
2. Dependências Frontend:
   - `cd frontend-react && npm install && npm run build`

## Execução
- Iniciar servidor: `python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000`
- Abrir o app: `http://127.0.0.1:8000/`
- O backend serve automaticamente `frontend-react/dist` (após `npm run build`)

## Formato do CSV (Entrada)
- Necessário conter uma coluna de data e uma de temperatura
- Colunas suportadas:
  - Data: `date` ou `dt` (qualquer formato parseável pelo pandas)
  - Temperatura: `temperature`, `temp`, `t` ou `avg_temp`

Exemplo mínimo (UTF‑8, separador vírgula):
```
date,temperature
2023-01-01,22.5
2023-01-02,23.1
...
```

## Endpoints (API)
- `POST /api/upload_csv` (multipart):
  - Campo: `file` (CSV)
  - Retorno: `{ monthly: { month[], avg_temp[] }, trend_line[], insights[] }`
- `POST /api/simulate` (JSON):
  - Corpo: `{ start: 'YYYY-MM-DD', end: 'YYYY-MM-DD', city: 'Cidade' }`
  - Retorno: igual ao acima
- `POST /api/openmeteo` (JSON):
  - Corpo: `{ city: 'Cidade', start: 'YYYY-MM-DD', end: 'YYYY-MM-DD' }` ou `{ lat, lon, start, end }`
  - Usa geocodificação (Open‑Meteo) se apenas `city` for informada
  - Retorno: `{ meta: { city, lat, lon }, monthly, trend_line, insights }`
- `GET /api/csv`:
  - Baixa o CSV agregado atual (`monthly_temps.csv`)

## Frontend (Guia Rápido)
- Fonte de dados: escolha entre `API Open‑Meteo`, `Simulado` ou `CSV do usuário`
- Parâmetros: cidade, início/fim (mês/ano)
- Ações:
  - `Explorar dados reais`: consulta Open‑Meteo no intervalo
  - `Usar simulado`: gera série mensal sintética
  - `Enviar CSV`: seleciona arquivo e executa automaticamente
  - `Executar`: processa a fonte atual
  - `Baixar CSV`: salva o agregado mensal
  - `Mostrar barras`: alterna o gráfico extra em barras
- Gráficos: média mensal (linha) + tendência (linha pontilhada) e, opcionalmente, barras
- Mensagens de erro: exibidas no painel de parâmetros (ex.: rede ou CSV inválido)

## Backend (Detalhes)
- `load_csv_bytes/load_csv_path`: lê CSV, normaliza colunas de data e temperatura
- `simulate_monthly(start, end, city, seed)`: cria série mensal com sazonalidade, tendência e ruído
- `compute_monthly_average(df)`: agrega por mês (
  `month` como período `YYYY-MM`, `avg_temp` média)
- `analyze_monthly(monthly_df)`: regressão linear (inclui `trend_line`, `insights`, `slope_per_year`)
- `save_monthly_csv(monthly_df, path)`: salva CSV formatado (`month` em `YYYY-MM`)

## Metodologia e Insights
- Tendência: coeficiente linear aplicado às médias mensais; convertido para °C/ano
- Picos: meses de maior e menor média
- Volatilidade: desvio‑padrão da variação percentual mensal

## Exemplos de Uso (Python requests)
```py
import requests
# Simulado
requests.post('http://127.0.0.1:8000/api/simulate', json={
  'start': '2023-01-01', 'end': '2023-12-01', 'city': 'São Paulo'
}).json()
# Open‑Meteo
requests.post('http://127.0.0.1:8000/api/openmeteo', json={
  'city': 'São Paulo', 'start': '2023-01-01', 'end': '2023-12-31'
}).json()
```

## Observações
- Open‑Meteo (arquivo histórico ERA5) não requer chave de API
- O timezone é automático; resultados podem variar conforme a localidade
- Em ambientes sem acesso externo, utilize `Simulado` ou `CSV do usuário`
- Em Windows, paths são resolvidos automaticamente; o CSV de saída é gerado em `data/output/`

