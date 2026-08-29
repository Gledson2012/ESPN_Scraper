import { MapPin } from 'lucide-react'
import type { LiveMatch } from '../types/api'
import { TeamBadge } from './TeamBadge'

interface TeamSideProps {
  name: string
  logo?: string | null
  color?: string
}

function TeamSide({ name, logo, color }: TeamSideProps) {
  return (
    <div className="live-team">
      {logo ? <img className="live-team-logo" src={logo} alt={name} loading="lazy" /> : <TeamBadge name={name} color={color} />}
      <span>{name}</span>
    </div>
  )
}

export function LiveMatchCard({ match }: { match: LiveMatch }) {
  return (
    <article className="match-card live-card">
      <div className="match-meta">
        <span className="competition-pill">{match.league}</span>
        <span className="match-status live"><span className="live-dot" /> AO VIVO {match.clock || ''}</span>
      </div>
      <div className="match-teams">
        <TeamSide name={match.home_team} logo={match.home_team_logo} />
        <div className="match-score">
          <strong>{match.home_score ?? 0} <span>—</span> {match.away_score ?? 0}</strong>
          {!match.venue ? null : <small><MapPin size={11} /> {match.venue}</small>}
        </div>
        <TeamSide name={match.away_team} logo={match.away_team_logo} color="#315fca" />
      </div>
    </article>
  )
}