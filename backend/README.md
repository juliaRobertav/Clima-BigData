# Clima — Backend (FastAPI)

Backend em FastAPI para processar dados de temperatura mensal, com endpoints para upload de CSV, simulação de séries e integração com a API Open‑Meteo. Também serve os arquivos estáticos do frontend quando construído.

## Requisitos
- `Python 3.10+` (testado com 3.12)
- `pip`

## Instalação
Recomendado usar ambiente virtual:

1. Crie e ative o venv (Windows):
   - `python -m venv .venv`
   - `\.venv\Scripts\activate`
2. Instale dependências:
   - `pip install fastapi uvicorn pandas numpy requests python-multipart`

> Observação: Execute os comandos a partir da raiz do projeto (`Clima-BigData`) para que os caminhos relativos funcionem (pasta `data/` e `frontend-react/dist`).

## Executar em desenvolvimento
Comandos a partir da raiz do projeto:

- `python -m uvicorn backend.app:app --reload --port 8000`

Isso inicia a API em `http://127.0.0.1:8000/`. Em desenvolvimento, o frontend (Vite) usa proxy para `/api` apontando para essa URL.

## Endpoints principais
- `POST /api/upload_csv` — envia um `file` (CSV). Retorna agregação mensal, linha de tendência e insights. Salva `data/output/monthly_temps.csv`.
- `POST /api/simulate` — corpo JSON `{ start: 'YYYY-MM-01', end: 'YYYY-MM-01', city?: string }`. Gera dados simulados, agrega e analisa.
- `POST /api/openmeteo` — corpo JSON `{ city?: string, lat?: number, lon?: number, start?: 'YYYY-MM-01', end?: 'YYYY-MM-01' }`. Busca diárias na Open‑Meteo, agrega e analisa. Se só informar `city`, o backend geocodifica lat/lon.
- `GET /api/csv` — baixa o CSV gerado (`monthly_temps.csv`).

## Servir frontend construído
Após construir o frontend (`frontend-react/dist`), o backend serve:
- `GET /` — retorna `frontend-react/dist/index.html`
- `GET /assets/*` — arquivos estáticos do build

Para isso, primeiro construa o frontend (veja o README do frontend) e depois execute o backend a partir da raiz do projeto.

## Fluxo típico
1. Inicie o backend: `python -m uvicorn backend.app:app --reload`
2. Inicie o frontend em dev: `npm run dev` na pasta `frontend-react`
3. Use a UI para:
   - Enviar um CSV com colunas de data (`date` ou `dt`) e temperatura (`temperature`, `temp`, `t` ou `avg_temp`)
   - Rodar simulado
   - Consultar Open‑Meteo por cidade
4. Baixe o CSV agregado via botão “Baixar CSV” ou `GET /api/csv`.

## Notas
- O arquivo de saída é gravado em `data/output/monthly_temps.csv`.
- Em produção, execute sem `--reload` e considere um servidor ASGI (ex.: `uvicorn`/`gunicorn` com `--workers`).
- Latência de Open‑Meteo pode variar; o backend usa `timeout` e retorna erros amigáveis.