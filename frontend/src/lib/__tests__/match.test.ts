import { describe, it, expect } from 'vitest'
import { isFinishedMatch, matchTimestamp, isUpcomingMatch, isPendingMatch } from '../match'
import type { Match } from '../../types/api'

const baseMatch: Match = {
  id: 1,
  home_team_id: 1,
  away_team_id: 2,
  competition: 'Serie-A',
  season: '2026',
  home_score: null,
  away_score: null,
  match_date: '2026-09-01T15:00:00',
  venue: 'Maracanã',
  fbref_id: 'match-1',
}

describe('isFinishedMatch', () => {
  it('returns true when both scores are set', () => {
    const match = { ...baseMatch, home_score: 2, away_score: 1 }
    expect(isFinishedMatch(match)).toBe(true)
  })

  it('returns false when scores are null', () => {
    expect(isFinishedMatch(baseMatch)).toBe(false)
  })

  it('returns false when only home score is set', () => {
    const match = { ...baseMatch, home_score: 2 }
    expect(isFinishedMatch(match)).toBe(false)
  })

  it('returns false when scores are 0', () => {
    const match = { ...baseMatch, home_score: 0, away_score: 0 }
    expect(isFinishedMatch(match)).toBe(true)
  })
})

describe('matchTimestamp', () => {
  it('parses a valid date', () => {
    const ts = matchTimestamp(baseMatch)
    expect(ts).toBeGreaterThan(0)
    expect(Number.isFinite(ts)).toBe(true)
  })

  it('returns NaN for null match_date', () => {
    const match = { ...baseMatch, match_date: null }
    expect(matchTimestamp(match)).toBeNaN()
  })

  it('returns NaN for invalid date', () => {
    const match = { ...baseMatch, match_date: 'invalid-date' }
    expect(matchTimestamp(match)).toBeNaN()
  })
})

describe('isUpcomingMatch', () => {
  it('returns true for future matches', () => {
    const match = { ...baseMatch, match_date: '2099-01-01T12:00:00' }
    expect(isUpcomingMatch(match, Date.parse('2026-01-01'))).toBe(true)
  })

  it('returns false for past matches', () => {
    const match = { ...baseMatch, match_date: '2020-01-01T12:00:00' }
    expect(isUpcomingMatch(match, Date.parse('2026-01-01'))).toBe(false)
  })

  it('returns false for finished matches', () => {
    const match = { ...baseMatch, home_score: 1, away_score: 0, match_date: '2099-01-01T12:00:00' }
    expect(isUpcomingMatch(match)).toBe(false)
  })
})

describe('isPendingMatch', () => {
  it('returns true for past unfinished matches', () => {
    const match = { ...baseMatch, match_date: '2020-01-01T12:00:00' }
    expect(isPendingMatch(match, Date.parse('2026-01-01'))).toBe(true)
  })

  it('returns false for future matches', () => {
    const match = { ...baseMatch, match_date: '2099-01-01T12:00:00' }
    expect(isPendingMatch(match, Date.parse('2026-01-01'))).toBe(false)
  })

  it('returns false for finished matches', () => {
    const match = { ...baseMatch, home_score: 1, away_score: 0, match_date: '2020-01-01T12:00:00' }
    expect(isPendingMatch(match)).toBe(false)
  })
})
