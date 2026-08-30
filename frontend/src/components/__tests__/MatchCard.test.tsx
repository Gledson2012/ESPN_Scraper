import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { MatchCard } from '../MatchCard'
import type { Match, Team } from '../../types/api'

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <MemoryRouter>{children}</MemoryRouter>
)

const teams: Team[] = [
  { id: 1, name: 'Flamengo', short_name: 'FLA', country: 'Brasil', league: 'Serie-A', stadium: 'Maracanã' },
  { id: 2, name: 'Palmeiras', short_name: 'PAL', country: 'Brasil', league: 'Serie-A', stadium: 'Allianz Parque' },
]

describe('MatchCard', () => {
  it('renders team names', () => {
    const match: Match = {
      id: 1,
      home_team_id: 1,
      away_team_id: 2,
      competition: 'Serie-A',
      season: '2026',
      match_date: '2026-09-01T15:00:00',
      home_score: null,
      away_score: null,
    }
    render(<MatchCard match={match} teams={teams} />, { wrapper })
    expect(screen.getByText('Flamengo')).toBeInTheDocument()
    expect(screen.getByText('Palmeiras')).toBeInTheDocument()
  })

  it('shows VS for pending matches', () => {
    const match: Match = {
      id: 1,
      home_team_id: 1,
      away_team_id: 2,
      competition: 'Serie-A',
      season: '2026',
      match_date: '2099-01-01T12:00:00',
      home_score: null,
      away_score: null,
    }
    render(<MatchCard match={match} teams={teams} />, { wrapper })
    expect(screen.getByText('VS')).toBeInTheDocument()
  })

  it('shows score for finished matches', () => {
    const match: Match = {
      id: 1,
      home_team_id: 1,
      away_team_id: 2,
      competition: 'Serie-A',
      season: '2026',
      match_date: '2026-01-01T15:00:00',
      home_score: 2,
      away_score: 1,
    }
    const { container } = render(<MatchCard match={match} teams={teams} />, { wrapper })
    const scoreEl = container.querySelector('.match-score strong')
    expect(scoreEl).toHaveTextContent('2')
    expect(scoreEl).toHaveTextContent('1')
    expect(scoreEl).not.toHaveTextContent('VS')
  })

  it('shows competition pill', () => {
    const match: Match = {
      id: 1,
      home_team_id: 1,
      away_team_id: 2,
      competition: 'Serie-A',
      season: '2026',
      match_date: '2099-01-01T12:00:00',
      home_score: null,
      away_score: null,
    }
    render(<MatchCard match={match} teams={teams} />, { wrapper })
    expect(screen.getByText('Serie-A')).toBeInTheDocument()
  })

  it('hides location in compact mode', () => {
    const match: Match = {
      id: 1,
      home_team_id: 1,
      away_team_id: 2,
      competition: 'Serie-A',
      season: '2026',
      match_date: '2099-01-01T12:00:00',
      venue: 'Maracanã',
      home_score: null,
      away_score: null,
    }
    render(<MatchCard match={match} teams={teams} compact />, { wrapper })
    expect(screen.queryByText('Maracanã')).not.toBeInTheDocument()
  })
})
