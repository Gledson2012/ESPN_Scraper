import { ArrowLeft, CalendarDays, MapPin, Trophy } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { EmptyState } from '../components/EmptyState'
import { LoadingState } from '../components/LoadingState'
import { PageHeader } from '../components/PageHeader'
import { TeamBadge } from '../components/TeamBadge'
import { api } from '../lib/api'
import { formatMatchDate } from '../lib/format'
import { isFinishedMatch, isPendingMatch } from '../lib/match'
import type { Match, MatchStats, Team } from '../types/api'

function statValue(value: number | null | undefined, suffix = '') {
  return value == null ? '—' : `${value}${suffix}`
}

export function MatchDetailPage() {
  const { matchId } = useParams()
  const id = Number(matchId)
  const [match, setMatch] = useState<Match | null>(null)
  const [stats, setStats] = useState<MatchStats[]>([])
  const [teams, setTeams] = useState<Team[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!Number.isInteger(id) || id <= 0) {
      setError('Partida inválida.')
      setLoading(false)
      return
    }
    Promise.all([api.getMatch(id), api.getMatchStats(id), api.getTeams()])
      .then(([matchData, statsData, teamData]) => { setMatch(matchData); setStats(statsData); setTeams(teamData) })
      .catch(() => setError('Não foi possível carregar os detalhes da partida.'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <LoadingState label="Carregando detalhes da partida..." />
  if (error || !match) return <EmptyState message={error || 'Partida não encontrada.'} />

  const home = teams.find((team) => team.id === match.home_team_id)
  const away = teams.find((team) => team.id === match.away_team_id)
  const homeStats = stats.find((stat) => stat.is_home)
  const awayStats = stats.find((stat) => !stat.is_home)
  const finished = isFinishedMatch(match)
  const pending = isPendingMatch(match)
  const status = finished ? 'Encerrada' : pending ? 'Resultado pendente' : 'Próxima'

  return (
    <>
      <PageHeader eyebrow="DETALHE DA PARTIDA" title={match.competition || 'Partida de futebol'} description={match.season || 'Temporada não informada'} action={<Link className="button secondary" to="/partidas"><ArrowLeft size={16} /> Voltar às partidas</Link>} />
      <section className="match-detail-hero"><div className="match-detail-meta"><span className="competition-pill">{match.competition || 'Futebol'}</span><span className="match-detail-status">{status}</span></div><div className="match-detail-date"><CalendarDays size={15} /> {formatMatchDate(match.match_date)}</div><div className="match-detail-teams"><div><TeamBadge name={home?.name || `Time ${match.home_team_id}`} shortName={home?.short_name} logo={home?.logo_url} /><strong>{home?.name || `Time ${match.home_team_id}`}</strong><small>Mandante</small></div><div className="match-detail-score">{finished ? <strong>{match.home_score} <span>—</span> {match.away_score}</strong> : <strong className="versus">VS</strong>}<small>{match.venue || 'Local não informado'}</small></div><div><TeamBadge name={away?.name || `Time ${match.away_team_id}`} shortName={away?.short_name} logo={away?.logo_url} color="#315fca" /><strong>{away?.name || `Time ${match.away_team_id}`}</strong><small>Visitante</small></div></div></section>

      <section className="detail-columns match-detail-columns"><div className="detail-panel"><div className="detail-panel-heading"><div><span className="eyebrow">ESTATÍSTICAS</span><h2>Comparativo da partida</h2></div><Trophy size={18} /></div>{stats.length ? <div className="stats-table"><div className="stats-table-head"><strong>{home?.short_name || home?.name || 'Casa'}</strong><span>Métrica</span><strong>{away?.short_name || away?.name || 'Fora'}</strong></div>{[['Posse', statValue(homeStats?.possession, '%'), statValue(awayStats?.possession, '%')], ['Finalizações', statValue(homeStats?.shots), statValue(awayStats?.shots)], ['No alvo', statValue(homeStats?.shots_on_target), statValue(awayStats?.shots_on_target)], ['xG', statValue(homeStats?.xg), statValue(awayStats?.xg)], ['Escanteios', statValue(homeStats?.corners), statValue(awayStats?.corners)], ['Passes', statValue(homeStats?.passes), statValue(awayStats?.passes)]].map(([label, homeValue, awayValue]) => <div className="stats-table-row" key={label}><strong>{homeValue}</strong><span>{label}</span><strong>{awayValue}</strong></div>)}</div> : <p className="detail-muted">As estatísticas desta partida ainda não foram coletadas.</p>}</div><div className="detail-panel detail-info-panel"><div className="detail-panel-heading"><div><span className="eyebrow">CONTEXTO</span><h2>Informações</h2></div><MapPin size={18} /></div><dl><div><dt>Local</dt><dd>{match.venue || 'Não informado'}</dd></div><div><dt>Árbitro</dt><dd>{match.referee || 'Não informado'}</dd></div><div><dt>Público</dt><dd>{match.attendance != null ? match.attendance.toLocaleString('pt-BR') : 'Não informado'}</dd></div><div><dt>xG da casa</dt><dd>{statValue(match.home_xg)}</dd></div><div><dt>xG visitante</dt><dd>{statValue(match.away_xg)}</dd></div></dl></div></section>
    </>
  )
}
