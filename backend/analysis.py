import os
from io import BytesIO
import pandas as pd
import numpy as np

def _ensure_datetime_series(df):
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    elif 'dt' in df.columns:
        df['date'] = pd.to_datetime(df['dt'])
    else:
        raise ValueError('CSV precisa conter coluna "date" ou "dt"')
    return df

def _ensure_temperature_series(df):
    candidates = ['temperature', 'temp', 't', 'avg_temp']
    found = None
    for c in candidates:
        if c in df.columns:
            found = c
            break
    if found is None:
        raise ValueError('CSV precisa conter coluna de temperatura: temperature/temp/t/avg_temp')
    df['temperature'] = pd.to_numeric(df[found], errors='coerce')
    return df[['date', 'temperature']]

def load_csv_bytes(file_bytes):
    bio = BytesIO(file_bytes)
    df = pd.read_csv(bio)
    df = _ensure_datetime_series(df)
    df = _ensure_temperature_series(df)
    return df

def load_csv_path(path):
    df = pd.read_csv(path)
    df = _ensure_datetime_series(df)
    df = _ensure_temperature_series(df)
    return df

def simulate_monthly(start_date: str, end_date: str, city: str | None = None, seed: int | None = 42):
    rng = np.random.default_rng(seed)
    idx = pd.date_range(start=start_date, end=end_date, freq='MS')
    m = np.arange(len(idx))
    seasonal = 8 * np.sin(2 * np.pi * (m % 12) / 12)
    trend = 0.02 * m
    noise = rng.normal(0, 1.2, size=len(idx))
    base = 18.0
    temps = base + seasonal + trend + noise
    df = pd.DataFrame({'date': idx, 'temperature': temps})
    if city:
        df['city'] = city
    return df

def compute_monthly_average(df: pd.DataFrame):
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M').dt.to_timestamp()
    g = df.groupby('month', as_index=False)['temperature'].mean()
    g.rename(columns={'temperature': 'avg_temp'}, inplace=True)
    return g

def analyze_monthly(monthly_df: pd.DataFrame):
    x = np.arange(len(monthly_df))
    y = monthly_df['avg_temp'].to_numpy()
    coeffs = np.polyfit(x, y, 1)
    slope = float(coeffs[0])
    intercept = float(coeffs[1])
    hottest_idx = int(np.argmax(y))
    coldest_idx = int(np.argmin(y))
    hottest_month = str(pd.to_datetime(monthly_df.loc[hottest_idx, 'month']).date())
    coldest_month = str(pd.to_datetime(monthly_df.loc[coldest_idx, 'month']).date())
    hottest_val = float(y[hottest_idx])
    coldest_val = float(y[coldest_idx])
    changes = pd.Series(y).pct_change().dropna()
    volatility = float(changes.std())
    direction = 'aquecimento' if slope > 0 else 'resfriamento' if slope < 0 else 'estável'
    per_year = slope * 12
    insights = [
        f'Tendência: {direction} de {per_year:.2f} °C/ano.',
        f'Mês mais quente: {hottest_month} com {hottest_val:.2f} °C; mais frio: {coldest_month} com {coldest_val:.2f} °C.',
        f'Volatilidade mensal (variação %): {volatility:.3f}.'
    ]
    trend_line = intercept + slope * x
    return {
        'slope_per_month': slope,
        'slope_per_year': per_year,
        'insights': insights,
        'trend_line': trend_line.tolist()
    }

def save_monthly_csv(monthly_df: pd.DataFrame, out_path: str):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    out = monthly_df.copy()
    out['month'] = pd.to_datetime(out['month']).dt.strftime('%Y-%m')
    out.to_csv(out_path, index=False)
    return out_path

