const calendarYearCompetitions = new Set([
  'Serie-A',
  'Brasileirao-Serie-A',
  'MLS',
  'Libertadores',
])

export function getCurrentSeason(competition?: string, now = new Date()): string {
  const year = now.getFullYear()
  if (competition && calendarYearCompetitions.has(competition)) return String(year)

  const startYear = now.getMonth() >= 6 ? year : year - 1
  return `${startYear}-${startYear + 1}`
}

export function getSeasonOptions(competition?: string, now = new Date()): string[] {
  const current = getCurrentSeason(competition, now)
  if (calendarYearCompetitions.has(competition || '')) {
    return [current, String(now.getFullYear() - 1)]
  }

  const [startYear] = current.split('-').map(Number)
  return [current, `${startYear - 1}-${startYear}`]
}
