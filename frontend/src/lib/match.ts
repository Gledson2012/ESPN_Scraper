import type { Match } from '../types/api'

export function isFinishedMatch(match: Match) {
  return match.home_score !== null && match.away_score !== null
}

export function matchTimestamp(match: Match) {
  if (!match.match_date) return Number.NaN
  return Date.parse(match.match_date)
}

export function isUpcomingMatch(match: Match, now = Date.now()) {
  const timestamp = matchTimestamp(match)
  return !isFinishedMatch(match) && Number.isFinite(timestamp) && timestamp >= now
}

export function isPendingMatch(match: Match, now = Date.now()) {
  const timestamp = matchTimestamp(match)
  return !isFinishedMatch(match) && Number.isFinite(timestamp) && timestamp < now
}
