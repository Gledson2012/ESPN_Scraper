import { mockMatches, mockOdds, mockTeams } from '../data/mockData'
import type { Match, OddsEvent, Player, Prediction, PredictionRequest, SoccerOddsResponse, Team } from '../types/api'

const browserHost = typeof window !== 'undefined' ? window.location.hostname : 'localhost'
const API_URL = (import.meta.env.VITE_API_URL || `http://${browserHost}:8000/api/v1`).replace(/\/$/, '')

export class ApiError extends Error {
  status: number

  constructor(message: string, status = 500) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options?.headers },
  })

  if (!response.ok) {
    let detail = `A API respondeu com o status ${response.status}.`
    try {
      const body = await response.json()
      if (typeof body.detail === 'string') detail = body.detail
    } catch {
      // Mantém uma mensagem útil mesmo quando o backend não retorna JSON.
    }
    throw new ApiError(detail, response.status)
  }

  return response.json() as Promise<T>
}

export const api = {
  baseUrl: API_URL,

  async getTeams(): Promise<Team[]> {
    return request<Team[]>('/teams/?limit=100')
  },

  async getPlayers(teamId?: number): Promise<Player[]> {
    const params = new URLSearchParams({ limit: '1000' })
    if (teamId) params.set('team_id', String(teamId))
    return request<Player[]>(`/players/?${params.toString()}`)
  },

  async getMatches(): Promise<Match[]> {
    return request<Match[]>('/matches/?limit=100')
  },

  async getOdds(): Promise<SoccerOddsResponse> {
    return request<SoccerOddsResponse>('/odds/soccer')
  },

  async predict(payload: PredictionRequest): Promise<Prediction> {
    return request<Prediction>('/predictions/', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
}

export interface DashboardData {
  teams: Team[]
  matches: Match[]
  odds: OddsEvent[]
  demo: boolean
}

export async function loadDashboardData(): Promise<DashboardData> {
  const [teamsResult, matchesResult, oddsResult] = await Promise.allSettled([
    api.getTeams(),
    api.getMatches(),
    api.getOdds(),
  ])

  const realTeams = teamsResult.status === 'fulfilled' ? teamsResult.value : []
  const realMatches = matchesResult.status === 'fulfilled' ? matchesResult.value : []
  const realOdds = oddsResult.status === 'fulfilled' ? oddsResult.value.events : []
  const useMatchSnapshot = !realTeams.length || !realMatches.length
  const teams = useMatchSnapshot ? mockTeams : realTeams
  const matches = useMatchSnapshot ? mockMatches : realMatches
  const odds = realOdds.length ? realOdds : mockOdds
  const emptyResponse = useMatchSnapshot || !realOdds.length

  return {
    teams,
    matches,
    odds,
    demo: [teamsResult, matchesResult, oddsResult].some((result) => result.status === 'rejected') || emptyResponse,
  }
}
