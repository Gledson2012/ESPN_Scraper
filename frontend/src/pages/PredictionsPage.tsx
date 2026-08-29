import { ArrowRight, CheckCircle2, Info, Sparkles, Target } from 'lucide-react'
import { FormEvent, useEffect, useMemo, useState } from 'react'
import { DemoNotice } from '../components/DemoNotice'
import { LoadingState } from '../components/LoadingState'
import { PageHeader } from '../components/PageHeader'
import { TeamBadge } from '../components/TeamBadge'
import { api } from '../lib/api'
import { mockTeams } from '../data/mockData'
import { percent } from '../lib/format'
import { getCurrentSeason, getSeasonOptions } from '../lib/season'
import type { Prediction, Team } from '../types/api'

function demoPrediction(homeId: number, awayId: number): Prediction {
  return { home_team_id: homeId, away_team_id: awayId, home_win_probability: 0.46, draw_probability: 0.27, away_win_probability: 0.27, predicted_home_score: 1.5, predicted_away_score: 1.1, over_2_5_probability: 0.54, btts_probability: 0.59, confidence: 0.78, model_version: 'demo-1.0' }
}

export function PredictionsPage() {
  const [teams, setTeams] = useState<Team[]>([])
  const [homeId, setHomeId] = useState('')
  const [awayId, setAwayId] = useState('')
  const [competition, setCompetition] = useState('Serie-A')
  const [season, setSeason] = useState(getCurrentSeason('Serie-A'))
  const [prediction, setPrediction] = useState<Prediction | null>(null)
  const [loading, setLoading] = useState(false)
  const [loadingTeams, setLoadingTeams] = useState(true)
  const [demo, setDemo] = useState(false)

  useEffect(() => {
    api.getTeams().then((teamData) => {
      setTeams(teamData.length ? teamData : mockTeams)
      setDemo(!teamData.length)
    }).catch(() => {
      setTeams(mockTeams)
      setHomeId(String(mockTeams[0].id))
      setAwayId(String(mockTeams[1].id))
      setDemo(true)
    }).finally(() => setLoadingTeams(false))
  }, [])

  useEffect(() => {
    if (teams.length && !homeId) setHomeId(String(teams[0].id))
    if (teams.length > 1 && !awayId) setAwayId(String(teams[1].id))
  }, [awayId, homeId, teams])

  const home = useMemo(() => teams.find((team) => team.id === Number(homeId)), [homeId, teams])
  const away = useMemo(() => teams.find((team) => team.id === Number(awayId)), [awayId, teams])

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (!homeId || !awayId || homeId === awayId) return
    setLoading(true)
    setPrediction(null)
    try {
      setPrediction(await api.predict({
        home_team_id: Number(homeId),
        away_team_id: Number(awayId),
        competition,
        season,
      }))
    } catch {
      setDemo(true)
      setPrediction(demoPrediction(Number(homeId), Number(awayId)))
    } finally {
      setLoading(false)
    }
  }

  if (loadingTeams) return <LoadingState label="Carregando times para análise..." />
  if (!teams.length) return <div className="empty-card">Cadastre times na API para gerar uma previsão.</div>

  return (
    <>
      {demo && <DemoNotice />}
      <PageHeader eyebrow="MODELO POISSON + XG" title="Previsões" description="Transforme o histórico das equipes em uma leitura objetiva do próximo jogo." />
      <section className="prediction-layout">
        <form className="prediction-form" onSubmit={handleSubmit}>
          <div className="form-title"><span className="form-icon"><Sparkles size={18} /></span><div><h2>Nova análise</h2><p>Selecione os dois times para calcular as probabilidades.</p></div></div>
          <label>Time da casa<select value={homeId} onChange={(event) => setHomeId(event.target.value)}>{teams.map((team) => <option value={team.id} key={team.id}>{team.name}</option>)}</select></label>
          <div className="versus-divider"><span>VS</span></div>
          <label>Time visitante<select value={awayId} onChange={(event) => setAwayId(event.target.value)}>{teams.map((team) => <option value={team.id} key={team.id}>{team.name}</option>)}</select></label>
          <div className="form-select-row"><label>Competição<select value={competition} onChange={(event) => { const nextCompetition = event.target.value; setCompetition(nextCompetition); setSeason(getCurrentSeason(nextCompetition)) }}><option value="Serie-A">Brasileirão Série A</option><option value="Premier-League">Premier League</option><option value="La-Liga">La Liga</option></select></label><label>Temporada<select value={season} onChange={(event) => setSeason(event.target.value)}>{getSeasonOptions(competition).map((option) => <option key={option}>{option}</option>)}</select></label></div>
          <button className="button primary full-width" disabled={loading || homeId === awayId}>{loading ? 'Calculando...' : <><Target size={16} /> Gerar previsão <ArrowRight size={15} /></>}</button>
          <div className="form-footnote"><Info size={14} /> A previsão usa estatísticas históricas disponíveis na API.</div>
        </form>

        <section className="prediction-result">
          {!prediction && !loading && <div className="prediction-placeholder"><div className="placeholder-icon"><Sparkles size={25} /></div><h2>Sua análise aparecerá aqui</h2><p>Escolha os times e gere uma previsão baseada em dados históricos, xG e mando de campo.</p></div>}
          {loading && <LoadingState label="Analisando histórico..." />}
          {prediction && home && away && <>
            <div className="result-header"><div><span className="eyebrow">PREVISÃO GERADA</span><h2>{home.name} <span>vs</span> {away.name}</h2></div><span className="confidence-badge"><CheckCircle2 size={14} /> {percent(prediction.confidence)} confiança</span></div>
            <div className="result-score"><div><TeamBadge name={home.name} shortName={home.short_name} /><strong>{prediction.predicted_home_score.toFixed(1)}</strong><span>{home.name}</span></div><span className="score-separator">—</span><div><TeamBadge name={away.name} shortName={away.short_name} color="#315fca" /><strong>{prediction.predicted_away_score.toFixed(1)}</strong><span>{away.name}</span></div></div>
            <div className="probability-block"><div className="probability-title"><span>Probabilidade de resultado</span><small>Modelo {prediction.model_version}</small></div><div className="probability-bar"><i style={{ width: `${prediction.home_win_probability * 100}%` }} /><i style={{ width: `${prediction.draw_probability * 100}%` }} /><i style={{ width: `${prediction.away_win_probability * 100}%` }} /></div><div className="probability-legend"><span><b className="green-dot" /> Casa <strong>{percent(prediction.home_win_probability)}</strong></span><span><b className="yellow-dot" /> Empate <strong>{percent(prediction.draw_probability)}</strong></span><span><b className="blue-dot" /> Fora <strong>{percent(prediction.away_win_probability)}</strong></span></div></div>
            <div className="result-metrics"><div><span>Mais de 2.5 gols</span><strong>{percent(prediction.over_2_5_probability)}</strong></div><div><span>Ambos marcam</span><strong>{percent(prediction.btts_probability)}</strong></div><div><span>Placar provável</span><strong>{prediction.predicted_home_score.toFixed(0)} — {prediction.predicted_away_score.toFixed(0)}</strong></div></div>
          </>}
        </section>
      </section>
    </>
  )
}
