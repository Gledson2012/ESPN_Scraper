import { CalendarDays, MapPin } from 'lucide-react'
import type { Match, Team } from '../types/api'
import { TeamBadge } from './TeamBadge'

interface MatchCardProps {
  match: Match
  teams: Team[]
  compact?: boolean
}

const formatDate = (value: string | null) => {
  if (!value) return 'Data a confirmar'
  return new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }).format(new Date(value))
}

export function MatchCard({ match, teams, compact = false }: MatchCardProps) {
  const home = teams.find((team) => team.id === match.home_team_id)
  const away = teams.find((team) => team.id === match.away_team_id)
  const isFinished = match.home_score !== null && match.away_score !== null

  return (
    <article className={`match-card${compact ? ' compact' : ''}`}>
      <div className="match-meta">
        <span className="competition-pill">{match.competition || 'Competição'}</span>
        <span className={`match-status ${isFinished ? 'finished' : 'scheduled'}`}>{isFinished ? 'Encerrada' : 'Próxima'}</span>
      </div>
      <div className="match-teams">
        <div className="match-team home-team">
          <TeamBadge name={home?.name || `Time ${match.home_team_id}`} shortName={home?.short_name} />
          <span>{home?.name || `Time ${match.home_team_id}`}</span>
        </div>
        <div className="match-score">
          {isFinished ? <strong>{match.home_score} <span>—</span> {match.away_score}</strong> : <strong className="versus">VS</strong>}
          {!compact && <small>{formatDate(match.match_date)}</small>}
        </div>
        <div className="match-team away-team">
          <TeamBadge name={away?.name || `Time ${match.away_team_id}`} shortName={away?.short_name} color="#315fca" />
          <span>{away?.name || `Time ${match.away_team_id}`}</span>
        </div>
      </div>
      {!compact && <div className="match-location"><MapPin size={13} /> {match.venue || 'Local não informado'} <CalendarDays size={13} /> {match.season || 'Temporada atual'}</div>}
    </article>
  )
}
