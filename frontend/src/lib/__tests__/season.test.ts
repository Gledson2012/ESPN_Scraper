import { describe, it, expect } from 'vitest'
import { getCurrentSeason, getSeasonOptions } from '../season'

describe('getCurrentSeason', () => {
  it('returns calendar year for Serie-A', () => {
    const result = getCurrentSeason('Serie-A', new Date(2026, 7, 1))
    expect(result).toBe('2026')
  })

  it('returns calendar year for MLS', () => {
    const result = getCurrentSeason('MLS', new Date(2026, 7, 1))
    expect(result).toBe('2026')
  })

  it('returns calendar year for Libertadores', () => {
    const result = getCurrentSeason('Libertadores', new Date(2026, 7, 1))
    expect(result).toBe('2026')
  })

  it('returns cross-year format for Premier League (after June)', () => {
    const result = getCurrentSeason('Premier-League', new Date(2026, 7, 1))
    expect(result).toBe('2026-2027')
  })

  it('returns cross-year format for La Liga (before June)', () => {
    const result = getCurrentSeason('La-Liga', new Date(2026, 3, 1))
    expect(result).toBe('2025-2026')
  })

  it('defaults to cross-year format for unknown competition', () => {
    const result = getCurrentSeason('Unknown', new Date(2026, 7, 1))
    expect(result).toMatch(/^\d{4}-\d{4}$/)
  })
})

describe('getSeasonOptions', () => {
  it('returns two calendar years for Serie-A', () => {
    const options = getSeasonOptions('Serie-A', new Date(2026, 7, 1))
    expect(options).toHaveLength(2)
    expect(options[0]).toBe('2026')
    expect(options[1]).toBe('2025')
  })

  it('returns two cross-year seasons for Premier League', () => {
    const options = getSeasonOptions('Premier-League', new Date(2026, 7, 1))
    expect(options).toHaveLength(2)
    expect(options[0]).toBe('2026-2027')
    expect(options[1]).toBe('2025-2026')
  })

  it('returns two seasons for unknown competition', () => {
    const options = getSeasonOptions('Unknown', new Date(2026, 7, 1))
    expect(options).toHaveLength(2)
  })
})
