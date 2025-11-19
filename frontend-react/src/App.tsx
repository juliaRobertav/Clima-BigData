import React, { useMemo, useRef, useState } from 'react'
import axios from 'axios'
import Plot from 'react-plotly.js'

type ApiData = {
  monthly: { month: string[]; avg_temp: number[] }
  trend_line: number[]
  insights: string[]
}

export default function App() {
  const now = useMemo(() => new Date(), [])
  const [source, setSource] = useState<'csv' | 'simulado' | 'openmeteo'>('openmeteo')
  const [file, setFile] = useState<File | null>(null)
  const [start, setStart] = useState(`${now.getFullYear()-5}-${String(now.getMonth()+1).padStart(2,'0')}`)
  const [end, setEnd] = useState(`${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}`)
  const [city, setCity] = useState('São Paulo')
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<ApiData | null>(null)
  const [showBars, setShowBars] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const csvRef = useRef<HTMLInputElement | null>(null)

  async function run() {
    setLoading(true)
    setError(null)
    try {
      if (source === 'csv') {
        if (!file) throw new Error('Selecione um CSV')
        const form = new FormData()
        form.append('file', file)
        const res = await axios.post('/api/upload_csv', form)
        setData(res.data)
      } else if (source === 'simulado') {
        const res = await axios.post('/api/simulate', { start: `${start}-01`, end: `${end}-01`, city })
        setData(res.data)
      } else {
        const res = await axios.post('/api/openmeteo', { start: `${start}-01`, end: `${end}-01`, city })
        setData(res.data)
      }
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || String(e))
    } finally {
      setLoading(false)
    }
  }

  function quickRun(type: 'openmeteo' | 'simulado') {
    setSource(type)
    run()
  }

  return (
    <div>
      <div className="nav">
        <div className="nav-inner container">
          <div className="brand"><span className="brand-dot"></span> Clima — Temperatura Mensal</div>
          <div className="nav-links">
            <a href="#explorar">Explorar</a>
            <a href="#graficos">Gráficos</a>
            <a href="#sobre">Sobre</a>
          </div>
        </div>
      </div>

      <section className="hero">
        <div className="container">
          <h1>Análise de temperatura mensal e tendência</h1>
          <p>Explore dados reais de temperatura média diária agregados por mês, visualize tendências e gere arquivos CSV. Integração com Open‑Meteo e suporte a dados simulados ou seu próprio CSV.</p>
          <div className="cta">
            <button className="btn btn-primary" onClick={() => quickRun('openmeteo')} disabled={loading}>Explorar dados reais</button>
            <button className="btn" onClick={() => quickRun('simulado')} disabled={loading}>Usar simulado</button>
            <button className="btn btn-ghost" onClick={() => { setSource('csv'); setTimeout(() => csvRef.current?.click(), 50) }} disabled={loading}>Enviar CSV</button>
          </div>
          <div className="grid">
            <div className="card"><h3>Médias mensais</h3><p>Calcula médias por mês a partir de diárias, com série temporal organizada.</p></div>
            <div className="card"><h3>Tendência</h3><p>Estima tendência com regressão linear e informa aquecimento ou resfriamento.</p></div>
            <div className="card"><h3>Exportação</h3><p>Salve o agregado em CSV e integre com seus relatórios.</p></div>
          </div>
        </div>
      </section>

      <section id="explorar" className="container section">
        <h2>Parâmetros e fonte</h2>
        <p className="muted">Defina a fonte e o período. CSV deve conter colunas de data e temperatura.</p>
        <div className="card">
          <div className="controls">
            <div>
              <label>Fonte de dados</label>
              <select value={source} onChange={e => setSource(e.target.value as any)}>
                <option value="csv">CSV do usuário</option>
                <option value="simulado">Simulado</option>
                <option value="openmeteo">API Open‑Meteo</option>
              </select>
            </div>
            {source === 'csv' && (
              <div>
                <label>Arquivo CSV</label>
                <input id="csvInput" ref={csvRef} type="file" accept=".csv" onChange={e => { const f = e.target.files?.[0] || null; setFile(f); if (f) { run() } }} />
              </div>
            )}
            <div>
              <label>Cidade</label>
              <input value={city} onChange={e => setCity(e.target.value)} />
            </div>
            <div className="row">
              <div>
                <label>Início</label>
                <input type="month" value={start} onChange={e => setStart(e.target.value)} />
              </div>
              <div>
                <label>Fim</label>
                <input type="month" value={end} onChange={e => setEnd(e.target.value)} />
              </div>
            </div>
            <div className="row">
              <button className="btn btn-primary" onClick={run} disabled={loading}>{loading ? 'Processando...' : 'Executar'}</button>
              <a className="btn" href="/api/csv" target="_blank" rel="noreferrer">Baixar CSV</a>
              <label className="row">
                <input type="checkbox" checked={showBars} onChange={e => setShowBars(e.target.checked)} /> Mostrar barras
              </label>
            </div>
            {error && <p className="muted" style={{ color: '#ffb4b4' }}>{error}</p>}
          </div>
        </div>
      </section>

      <section id="graficos" className="container section">
        <h2>Gráficos</h2>
        <div className="card charts">
          {data ? (
            <>
              {('meta' in (data as any)) && (
                <p className="muted">Origem: {(data as any).meta?.city} [{(data as any).meta?.lat}, {(data as any).meta?.lon}]</p>
              )}
              <Plot
                data={[
                  { x: data.monthly.month, y: data.monthly.avg_temp, type: 'scatter', mode: 'lines+markers', name: 'Média mensal (°C)' },
                  { x: data.monthly.month, y: data.trend_line, type: 'scatter', mode: 'lines', name: 'Tendência', line: { dash: 'dot', color: '#d33' } }
                ]}
                layout={{ paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: '#0f152d', margin: { t: 32, r: 12, b: 40, l: 48 }, yaxis: { title: '°C', gridcolor: 'rgba(255,255,255,0.1)' }, xaxis: { title: 'Mês', gridcolor: 'rgba(255,255,255,0.05)' }, height: 520 }}
                config={{ displayModeBar: true }}
                style={{ width: '100%' }}
              />
              {showBars && (
                <Plot
                  data={[{ x: data.monthly.month, y: data.monthly.avg_temp, type: 'bar', name: 'Média mensal (°C)' }]}
                  layout={{ paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: '#0f152d', margin: { t: 32, r: 12, b: 40, l: 48 }, yaxis: { title: '°C', gridcolor: 'rgba(255,255,255,0.1)' }, xaxis: { title: 'Mês', gridcolor: 'rgba(255,255,255,0.05)' }, height: 360 }}
                  config={{ displayModeBar: true }}
                  style={{ width: '100%' }}
                />
              )}
              <ul className="insights">
                {data.insights.map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </>
          ) : (
            <p className="muted">Carregue um CSV, use simulado ou API Open‑Meteo e clique em Executar.</p>
          )}
        </div>
      </section>

      <section id="sobre" className="container section">
        <h2>Sobre clima e importância</h2>
        <div className="grid">
          <div className="card"><h3>Contexto</h3><p>Temperatura média indica estado térmico do ambiente e responde à sazonalidade, variabilidade natural e mudanças de longo prazo.</p></div>
          <div className="card"><h3>Impactos</h3><p>Tendências afetam agricultura, energia e saúde. Identificar aquecimento ou resfriamento ajuda planejamento e mitigação.</p></div>
          <div className="card"><h3>Metodologia</h3><p>Agrega diárias em médias mensais e estima tendência linear. CSV exportado facilita replicação e auditoria.</p></div>
        </div>
      </section>

      <div className="footer">Construído com React, Plotly, FastAPI, pandas e numpy</div>
    </div>
  )
}
