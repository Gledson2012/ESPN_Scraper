import { describe, it, expect } from 'vitest'
import { formatDate, formatMatchDate, getGreeting, percent, initials } from '../format'

describe('formatDate', () => {
  it('returns "A definir" for null', () => {
    expect(formatDate(null)).toBe('A definir')
  })

  it('returns "A definir" for undefined', () => {
    expect(formatDate(undefined)).toBe('A definir')
  })

  it('returns "A definir" for invalid date', () => {
    expect(formatDate('not-a-date')).toBe('A definir')
  })

  it('formats a valid date', () => {
    const result = formatDate('2026-03-15T12:00:00')
    expect(result).toContain('15')
    expect(result).toContain('2026')
  })
})

describe('formatMatchDate', () => {
  it('returns "Data a confirmar" for null', () => {
    expect(formatMatchDate(null)).toBe('Data a confirmar')
  })

  it('returns "Data a confirmar" for invalid date', () => {
    expect(formatMatchDate('invalid')).toBe('Data a confirmar')
  })

  it('formats a valid date with time', () => {
    const result = formatMatchDate('2026-03-15T14:30:00')
    expect(result).toContain('15')
  })
})

describe('getGreeting', () => {
  it('returns "Bom dia" for morning', () => {
    expect(getGreeting(new Date(2026, 0, 1, 9, 0))).toBe('Bom dia')
  })

  it('returns "Boa tarde" for afternoon', () => {
    expect(getGreeting(new Date(2026, 0, 1, 15, 0))).toBe('Boa tarde')
  })

  it('returns "Boa noite" for evening', () => {
    expect(getGreeting(new Date(2026, 0, 1, 20, 0))).toBe('Boa noite')
  })

  it('returns "Bom dia" at exactly midnight', () => {
    expect(getGreeting(new Date(2026, 0, 1, 0, 0))).toBe('Bom dia')
  })

  it('returns "Bom dia" at 11:59', () => {
    expect(getGreeting(new Date(2026, 0, 1, 11, 59))).toBe('Bom dia')
  })
})

describe('percent', () => {
  it('formats 0.5 as 50%', () => {
    expect(percent(0.5)).toBe('50%')
  })

  it('formats 0 as 0%', () => {
    expect(percent(0)).toBe('0%')
  })

  it('formats 1 as 100%', () => {
    expect(percent(1)).toBe('100%')
  })

  it('rounds decimals', () => {
    expect(percent(0.333)).toBe('33%')
  })
})

describe('initials', () => {
  it('extracts first letter of each word', () => {
    expect(initials('Flamengo')).toBe('F')
  })

  it('handles multi-word names', () => {
    expect(initials('São Paulo')).toBe('SP')
  })

  it('returns uppercase', () => {
    expect(initials('palmeiras')).toBe('P')
  })
})
