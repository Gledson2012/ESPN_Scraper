import { ArrowLeft, CalendarDays, Globe, MapPin, Shield, Users } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { EmptyState } from '../components/EmptyState'
import { LoadingState } from '../components/LoadingState'
import { MatchCard } from '../components/MatchCard'
import { PageHeader } from '../components/PageHeader'
import { TeamBadge } from '../components/TeamBadge'
import { api } from '../lib/api'
import { formatDate } from '../lib/format'
import type { Match, Player, Team, TeamSummary } from '../types/api'

export function TeamDetailPage() {
  const { teamId } = useParams()
  const id = Number(teamId)
  const [team, setTeam] = useState<Team | null>(null)
  const [teams, setTeams] = useState<Team[]>([])
  const [players, setPlayers] = useState<Player[]>([])
  const [matches, setMatches] = useState<Match[]>([])
  const [summary, setSummary] = useState<TeamSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!Number.isInteger(id) || id <= 0) {
      setError('Time inválido.')
      setLoading(false)
      return
    }

    Promise.all([
      api.getTeam(id),
      api.getTeams(),
      api.getTeamPlayers(id),
      api.getTeamMatches(id),
      api.getTeamSummary(id),
    ]).then(([teamData, teamDataList, playerData, matchData, summaryData]) => {
      setTeam(teamData)
      setTeams(teamDataList)
      setPlayers(playerData)
      setMatches(matchData)
      setSummary(summaryData)
    }).catch(() => setError('Não foi possível carregar os dados deste time.'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <LoadingState label="Carregando detalhes do time..." />
  if (error || !team || !summary) return <EmptyState message={error || 'Time não encontrado.'} />

  return (
    <>
      <PageHeader eyebrow="DETALHE DO TIME" title={team.name} description={`${team.league || 'Competição não informada'} · ${team.country || 'País não informado'}`} action={<Link className="button secondary" to="/times"><ArrowLeft size={16} /> Voltar aos times</Link>} />

      <section className="detail-hero">
        <TeamBadge name={team.name} shortName={team.short_name} logo={team.logo_url} />
        <div><span className="eyebrow">PERFIL DO CLUBE</span><h2>{team.short_name || team.name}</h2><p>{team.stadium || 'Estádio não informado'}</p></div>
        <div className="detail-hero-meta"><span><MapPin size={14} /> {team.stadium || 'Local não informado'}</span>{team.website && <a href={team.website} target="_blank" rel="noreferrer"><Globe size={14} /> Site oficial</a>}</div>
      </section>

      <section className="detail-summary-grid">
        <div><strong>{summary.matches}</strong><span>partidas cadastradas</span></div>
        <div><strong>{summary.completed_matches}</strong><span>partidas concluídas</span></div>
        <div><strong>{summary.points}</strong><span>pontos</span></div>
        <div><strong>{summary.stats_available}</strong><span>com estatísticas</span></div>
      </section>

      <section className="detail-columns">
        <div className="detail-panel"><div className="detail-panel-heading"><div><span className="eyebrow">CAMPANHA</span><h2>Desempenho registrado</h2></div><Shield size={18} /></div><div className="record-grid"><div><strong>{summary.wins}</strong><span>Vitórias</span></div><div><strong>{summary.draws}</strong><span>Empates</span></div><div><strong>{summary.losses}</strong><span>Derrotas</span></div><div><strong>{summary.goals_for}</strong><span>Gols marcados</span></div><div><strong>{summary.goals_against}</strong><span>Gols sofridos</span></div><div><strong>{summary.goal_difference > 0 ? `+${summary.goal_difference}` : summary.goal_difference}</strong><span>Saldo de gols</span></div></div></div>

        <div className="detail-panel"><div className="detail-panel-heading"><div><span className="eyebrow">HISTÓRICO</span><h2>Últimas partidas</h2></div><CalendarDays size={18} /></div>{matches.length ? <div className="detail-match-list">{matches.slice(0, 5).map((match) => <Link className="match-card-link" to={`/partidas/${match.id}`} key={match.id}><MatchCard match={match} teams={teams} compact /></Link>)}</div> : <p className="detail-muted">Nenhuma partida cadastrada para este time.</p>}</div>

        <div className="detail-panel"><div className="detail-panel-heading"><div><span className="eyebrow">ELENCO</span><h2>Jogadores</h2></div><Users size={18} /></div>{players.length ? <ul className="detail-player-list">{players.slice(0, 12).map((player) => <li key={player.id}><span className="mini-avatar">{player.name.slice(0, 1)}</span><span><strong>{player.name}</strong><small>{player.position || 'Posição não informada'}{player.shirt_number != null ? ` · camisa ${player.shirt_number}` : ''}</small></span></li>)}</ul> : <p className="detail-muted">Nenhum jogador cadastrado para este time.</p>}<Link className="text-link" to="/jogadores">Ver todos os jogadores</Link></div>

        <div className="detail-panel detail-info-panel"><div className="detail-panel-heading"><div><span className="eyebrow">INFORMAÇÕES</span><h2>Dados do clube</h2></div></div><dl><div><dt>País</dt><dd>{team.country || 'Não informado'}</dd></div><div><dt>Competição</dt><dd>{team.league || 'Não informada'}</dd></div><div><dt>Fundação</dt><dd>{team.founded || 'Não informada'}</dd></div><div><dt>Atualizado em</dt><dd>{team.updated_at ? formatDate(team.updated_at) : 'Não informado'}</dd></div></dl></div>
      </section>
    </>
  )
}
