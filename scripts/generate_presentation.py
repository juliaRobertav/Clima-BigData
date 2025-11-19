import os
import sys
from datetime import datetime
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

sys.path.append(os.path.join(os.getcwd()))
try:
    from backend.analysis import simulate_monthly, compute_monthly_average
except Exception:
    simulate_monthly = None
    compute_monthly_average = None

OUT_DIR = os.path.join('assets')
OUT_PATH = os.path.join(OUT_DIR, 'presentation.pdf')

TITLE = 'Clima — Temperatura Mensal'
SUBTITLE = 'Análise de médias mensais, tendência e insights rápidos'

SECTIONS = [
    ('Problema',
     'Mudanças de temperatura impactam saúde, agricultura e energia. \n'
     'Entender a tendência e a sazonalidade mensal ajuda decisões e políticas públicas.'),
    ('Objetivo',
     'Calcular a média mensal de temperatura, estimar tendência (aquecimento/resfriamento) \n'
     'e destacar picos e volatilidade para comunicação clara.'),
    ('Dados e Fontes',
     'Três fontes: API Open‑Meteo (ERA5), CSV do usuário e dados simulados. \n'
     'Período configurável e cidade por nome com geocodificação automática.'),
    ('Metodologia',
     'Agrega temperaturas diárias em médias mensais com pandas. \n'
     'Ajusta regressão linear para estimar tendência e compõe uma linha de tendência junto ao gráfico.'),
    ('Arquitetura',
     'Backend em FastAPI serve endpoints de upload/simulação/real. \n'
     'Frontend React (Vite) com Plotly para visualização interativa e exportação de CSV.'),
    ('Insights',
     '• Tendência anual: aquecimento/resfriamento e magnitude (°C/ano). \n'
     '• Mês mais quente e mais frio com valores médios. \n'
     '• Volatilidade mensal (desvio‑padrão da variação %).'),
    ('Demonstração',
     'Ajuste Cidade e Período, escolha fonte, clique em Executar e Baixar CSV. \n'
     'Frontend moderno com tema escuro e navegação por seções.'),
    ('Conclusões e Próximos Passos',
     'Entregável simples e útil para relatórios. \n'
     'Próximos passos: comparação entre cidades, sazonalidade por ano, exportar PNG/PDF, automação com Actions.'),
]

TOOLS = (
    'Backend: FastAPI, Uvicorn, pandas, numpy, requests\n'
    'Frontend: React (Vite), react-plotly.js, plotly.js-dist-min, axios, TypeScript\n'
    'Dados: Open‑Meteo (ERA5 histórico), CSV do usuário, simulado'
)

def draw_header(c: canvas.Canvas, title: str, subtitle: str):
    w, h = c._pagesize
    c.setFillColor(colors.HexColor('#0b1020'))
    c.rect(0, 0, w, h, stroke=0, fill=1)
    c.setFillColor(colors.HexColor('#16213e'))
    c.rect(0, h-2.8*cm, w, 2.8*cm, stroke=0, fill=1)
    c.setFillColor(colors.HexColor('#e6edf7'))
    c.setFont('Helvetica-Bold', 24)
    c.drawString(2*cm, h-2*cm, title)
    c.setFont('Helvetica', 12)
    c.setFillColor(colors.HexColor('#b7c1d6'))
    c.drawString(2*cm, h-2.6*cm, subtitle)

def paragraph(c: canvas.Canvas, text: str, x: float, y: float, max_width: float, size: int = 13):
    style = ParagraphStyle('p', fontName='Helvetica', fontSize=size, leading=size+2, textColor=colors.HexColor('#e6edf7'))
    p = Paragraph(text.replace('\n', '<br/>'), style)
    w, h = p.wrap(max_width, 1000)
    p.drawOn(c, x, y - h)
    return h

def draw_section(c: canvas.Canvas, title: str, text: str):
    draw_header(c, TITLE, SUBTITLE)
    c.setFillColor(colors.HexColor('#e6edf7'))
    c.setFont('Helvetica-Bold', 18)
    c.drawString(2*cm, 17*cm, title)
    h = paragraph(c, text, 2*cm, 16*cm, 24*cm)
    c.showPage()

def draw_cover(c: canvas.Canvas):
    draw_header(c, TITLE, SUBTITLE)
    c.setFillColor(colors.HexColor('#4cc9f0'))
    c.circle(26*cm, 3*cm, 0.35*cm, stroke=0, fill=1)
    c.setFillColor(colors.HexColor('#b5179e'))
    c.circle(25*cm, 2.6*cm, 0.25*cm, stroke=0, fill=1)
    c.setFont('Helvetica-Bold', 28)
    c.setFillColor(colors.HexColor('#e6edf7'))
    c.drawString(2*cm, 12*cm, 'Apresentação do Projeto')
    c.setFont('Helvetica', 12)
    c.setFillColor(colors.HexColor('#b7c1d6'))
    c.drawString(2*cm, 11.2*cm, f'Gerado em {datetime.now().strftime("%d/%m/%Y %H:%M")}')
    paragraph(c, TOOLS, 2*cm, 10*cm, 24*cm, size=12)
    c.showPage()

def draw_chart(c: canvas.Canvas):
    draw_header(c, TITLE, 'Gráfico de média mensal e tendência (ilustrativo)')
    # area
    x0, y0, w, h = 3*cm, 6*cm, 23*cm, 9*cm
    c.setFillColor(colors.HexColor('#0f152d'))
    c.roundRect(x0, y0, w, h, 10, stroke=0, fill=1)
    c.setStrokeColor(colors.HexColor('#2a335a'))
    c.setLineWidth(1)
    for i in range(6):
        yy = y0 + (i+1) * h/7
        c.line(x0+1*cm, yy, x0+w-1*cm, yy)

    # data
    months = [f'2023-{str(i).zfill(2)}' for i in range(1,13)]
    values = []
    try:
        if os.path.exists(os.path.join('data','output','monthly_temps.csv')):
            import pandas as pd
            df = pd.read_csv(os.path.join('data','output','monthly_temps.csv'))
            if 'month' in df.columns and 'avg_temp' in df.columns:
                months = df['month'].tolist()
                values = df['avg_temp'].tolist()
        elif simulate_monthly and compute_monthly_average:
            df = compute_monthly_average(simulate_monthly('2023-01-01','2023-12-01','São Paulo'))
            months = df['month'].dt.strftime('%Y-%m').tolist()
            values = df['avg_temp'].tolist()
    except Exception:
        values = []

    if not values:
        values = [18.5,19.8,22.6,24.1,23.0,21.2,19.0,20.2,21.0,18.9,17.5,18.3]

    # scale values
    vmin, vmax = min(values), max(values)
    def map_val(v):
        return y0 + 1*cm + (v - vmin) / (vmax - vmin + 1e-6) * (h - 2*cm)

    # line
    c.setStrokeColor(colors.HexColor('#4cc9f0'))
    c.setLineWidth(2)
    for i in range(len(values)-1):
        x1 = x0 + 1*cm + i * (w - 2*cm) / (len(values)-1)
        x2 = x0 + 1*cm + (i+1) * (w - 2*cm) / (len(values)-1)
        y1 = map_val(values[i])
        y2 = map_val(values[i+1])
        c.line(x1, y1, x2, y2)

    # points
    c.setFillColor(colors.HexColor('#4cc9f0'))
    for i in range(len(values)):
        x = x0 + 1*cm + i * (w - 2*cm) / (len(values)-1)
        y = map_val(values[i])
        c.circle(x, y, 2.2, stroke=0, fill=1)

    c.setFillColor(colors.HexColor('#b7c1d6'))
    c.setFont('Helvetica', 10)
    c.drawString(x0, y0-0.6*cm, 'Mês')
    c.rotate(90)
    c.drawString(y0, -x0+0.6*cm, '°C')
    c.rotate(-90)
    c.showPage()

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    c = canvas.Canvas(OUT_PATH, pagesize=landscape(A4))
    draw_cover(c)
    for t, txt in SECTIONS:
        draw_section(c, t, txt)
    draw_chart(c)
    c.save()
    print(OUT_PATH)

if __name__ == '__main__':
    main()

