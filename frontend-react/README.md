# Clima — Frontend (React + Vite)

Interface em React para explorar temperaturas mensais, visualizar gráficos (Plotly) e interagir com a API de backend.

## Requisitos
- `Node.js 18+` e `npm`

## Instalação
Na pasta `frontend-react`:

- `npm install`

## Desenvolvimento
Na pasta `frontend-react`:

- `npm run dev`

Abrirá em `http://localhost:5173`. O proxy de desenvolvimento está configurado em `vite.config.ts` para encaminhar chamadas a `/api` para `http://127.0.0.1:8000`. Garanta que o backend esteja rodando (veja o README do backend).

## Build de produção
Na pasta `frontend-react`:

- `npm run build`

Gera `dist/`. Quando o backend estiver ativo a partir da raiz do projeto, ele serve automaticamente `dist/index.html` e `dist/assets/*` em `GET /` e `GET /assets/*`.

## Preview do build
Para testar o build localmente, sem o backend:

- `npm run preview -- --port 5173`

Abra `http://localhost:5173`. Para funcionalidades da API, rode o backend junto.

## Funcionalidades
- Upload de CSV com colunas de data (`date` ou `dt`) e temperatura (`temperature`, `temp`, `t` ou `avg_temp`).
- Simulação de série mensal com período e cidade.
- Consulta à Open‑Meteo por cidade (geocodificação automática) ou por lat/lon.
- Gráficos de linha (com tendência) e barras; exportação de imagens (PNG).
- Download do CSV agregado diretamente via botão “Baixar CSV”.

## Dicas
- Se a API não responder em dev, verifique se o backend está rodando em `http://127.0.0.1:8000`.
- Em ambientes corporativos com proxy, ajuste `vite.config.ts` conforme necessário.