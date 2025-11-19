import os
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
from .analysis import load_csv_bytes, simulate_monthly, compute_monthly_average, analyze_monthly, save_monthly_csv

APP_TITLE = 'Clima — Temperatura Mensal'
OUTPUT_CSV = os.path.join('data', 'output', 'monthly_temps.csv')

app = FastAPI(title=APP_TITLE)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.post('/api/upload_csv')
async def upload_csv(file: UploadFile = File(...)):
    try:
        content = await file.read()
        df = load_csv_bytes(content)
        monthly = compute_monthly_average(df)
        analysis = analyze_monthly(monthly)
        save_monthly_csv(monthly, OUTPUT_CSV)
        payload = {
            'monthly': {
                'month': monthly['month'].dt.strftime('%Y-%m').tolist(),
                'avg_temp': monthly['avg_temp'].round(3).tolist()
            },
            'trend_line': analysis['trend_line'],
            'insights': analysis['insights']
        }
        return JSONResponse(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/api/simulate')
async def simulate(params: dict):
    try:
        start = params.get('start', '2018-01-01')
        end = params.get('end', '2025-12-01')
        city = params.get('city', 'Cidade')
        df = simulate_monthly(start, end, city)
        monthly = compute_monthly_average(df)
        analysis = analyze_monthly(monthly)
        save_monthly_csv(monthly, OUTPUT_CSV)
        payload = {
            'monthly': {
                'month': monthly['month'].dt.strftime('%Y-%m').tolist(),
                'avg_temp': monthly['avg_temp'].round(3).tolist()
            },
            'trend_line': analysis['trend_line'],
            'insights': analysis['insights']
        }
        return JSONResponse(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get('/api/csv')
async def get_csv():
    if not os.path.exists(OUTPUT_CSV):
        raise HTTPException(status_code=404, detail='CSV não encontrado')
    return FileResponse(OUTPUT_CSV, media_type='text/csv', filename='monthly_temps.csv')

static_dir = 'frontend-react/dist' if os.path.exists('frontend-react/dist') else 'frontend'

@app.get('/')
async def index_page():
    index_path = os.path.join(static_dir, 'index.html')
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail='index.html não encontrado')
    return FileResponse(index_path)

assets_dir = os.path.join(static_dir, 'assets')
if os.path.exists(assets_dir):
    app.mount('/assets', StaticFiles(directory=assets_dir), name='assets')

def _geocode_city(name: str):
    r = requests.get(
        'https://geocoding-api.open-meteo.com/v1/search',
        params={'name': name, 'count': 1, 'language': 'pt', 'format': 'json'}, timeout=20
    )
    r.raise_for_status()
    js = r.json()
    if not js.get('results'):
        raise HTTPException(status_code=404, detail='Cidade não encontrada')
    res = js['results'][0]
    return {
        'latitude': res['latitude'],
        'longitude': res['longitude'],
        'name': res.get('name'),
        'country': res.get('country')
    }

@app.post('/api/openmeteo')
async def open_meteo(params: dict):
    try:
        city = params.get('city')
        lat = params.get('lat')
        lon = params.get('lon')
        start = params.get('start', '2018-01-01')
        end = params.get('end', '2025-12-01')

        if city and (not lat or not lon):
            g = _geocode_city(city)
            lat, lon = g['latitude'], g['longitude']
            city = f"{g.get('name')} ({g.get('country')})"

        if lat is None or lon is None:
            raise HTTPException(status_code=400, detail='Informe city ou lat/lon')

        r = requests.get(
            'https://archive-api.open-meteo.com/v1/era5',
            params={
                'latitude': lat,
                'longitude': lon,
                'start_date': start,
                'end_date': end,
                'daily': 'temperature_2m_mean',
                'timezone': 'auto'
            }, timeout=30
        )
        r.raise_for_status()
        js = r.json()
        if 'daily' not in js or not js['daily'].get('time'):
            raise HTTPException(status_code=404, detail='Sem dados diários na API')

        dates = js['daily']['time']
        temps = js['daily']['temperature_2m_mean']
        df = pd.DataFrame({'date': pd.to_datetime(dates), 'temperature': temps})
        monthly = compute_monthly_average(df)
        analysis = analyze_monthly(monthly)
        save_monthly_csv(monthly, OUTPUT_CSV)
        payload = {
            'meta': {'city': city, 'lat': lat, 'lon': lon},
            'monthly': {
                'month': monthly['month'].dt.strftime('%Y-%m').tolist(),
                'avg_temp': monthly['avg_temp'].round(3).tolist()
            },
            'trend_line': analysis['trend_line'],
            'insights': analysis['insights']
        }
        return JSONResponse(payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
