import { mockMatches, mockOdds, mockTeams } from '../data/mockData'
import type { LiveMatch, Match, MatchStats, OddsEvent, Player, Prediction, PredictionRequest, SoccerOddsResponse, Team, TeamSummary } from '../types/api'

const browserHost = typeof window !== 'undefined' ? window.location.hostname : 'localhost'
const configuredApiUrl = import.meta.env.VITE_API_URL?.trim()
const API_URL = (configuredApiUrl || (!import.meta.env.PROD ? `http://${browserHost}:8000/api/v1` : '')).replace(/\/$/, '')
const REQUEST_TIMEOUT_MS = 15_000

export class ApiError extends Error {
  status: number

  constructor(message: string, status = 500) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  if (!API_URL) {
    throw new ApiError('A URL pública da API não foi configurada; o painel está em modo demonstração.')
  }

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

  try {
    const response = await fetch(`${API_URL}${path}`, {
      ...options,
      signal: options?.signal ?? controller.signal,
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
  } finally {
    clearTimeout(timeoutId)
  }
}

function expectArray<T>(value: unknown, resource: string): T[] {
  if (!Array.isArray(value)) throw new ApiError(`A API retornou um formato inválido para ${resource}.`)
  return value as T[]
}

function expectObject<T>(value: unknown, resource: string): T {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new ApiError(`A API retornou um formato inválido para ${resource}.`)
  return value as T
}

export const api = {
  baseUrl: API_URL,

  async getTeams(): Promise<Team[]> {
    return expectArray<Team>(await request<unknown>('/teams/?limit=100'), 'times')
  },

  async getTeam(teamId: number): Promise<Team> {
    return expectObject<Team>(await request<unknown>(`/teams/${teamId}`), 'time')
  },

  async getTeamPlayers(teamId: number): Promise<Player[]> {
    return expectArray<Player>(await request<unknown>(`/teams/${teamId}/players?limit=1000`), 'jogadores')
  },

  async getTeamMatches(teamId: number): Promise<Match[]> {
    return expectArray<Match>(await request<unknown>(`/teams/${teamId}/matches?limit=100`), 'partidas do time')
  },

  async getTeamSummary(teamId: number): Promise<TeamSummary> {
    return expectObject<TeamSummary>(await request<unknown>(`/teams/${teamId}/summary`), 'resumo do time')
  },

  async getPlayers(teamId?: number): Promise<Player[]> {
    const params = new URLSearchParams({ limit: '1000' })
    if (teamId) params.set('team_id', String(teamId))
    return expectArray<Player>(await request<unknown>(`/players/?${params.toString()}`), 'jogadores')
  },

  async getMatches(): Promise<Match[]> {
    return expectArray<Match>(await request<unknown>('/matches/?limit=100'), 'partidas')
  },

  async getMatch(matchId: number): Promise<Match> {
    return expectObject<Match>(await request<unknown>(`/matches/${matchId}`), 'partida')
  },

  async getMatchStats(matchId: number): Promise<MatchStats[]> {
    return expectArray<MatchStats>(await request<unknown>(`/matches/${matchId}/stats`), 'estatísticas')
  },

  async getLiveMatches(): Promise<LiveMatch[]> {
    return expectArray<LiveMatch>(await request<unknown>('/matches/live'), 'partidas ao vivo')
  },

  async getOdds(): Promise<SoccerOddsResponse> {
    const response = expectObject<Partial<SoccerOddsResponse>>(await request<unknown>('/odds/soccer'), 'odds')
    const events = expectArray<OddsEvent>(response.events, 'eventos de odds')
    return { events, total: typeof response.total === 'number' ? response.total : events.length }
  },

  async getEventMarkets(eventId: string | number): Promise<Record<string, unknown>> {
    return request<Record<string, unknown>>(`/odds/event/${encodeURIComponent(String(eventId))}/markets`)
  },

  async predict(payload: PredictionRequest): Promise<Prediction> {
    return expectObject<Prediction>(await request<unknown>('/predictions/', {
      method: 'POST',
      body: JSON.stringify(payload),
    }), 'previsão')
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
  const useTeamSnapshot = !realTeams.length
  const useMatchSnapshot = !realMatches.length
  const teams = useTeamSnapshot ? mockTeams : realTeams
  const matches = useMatchSnapshot ? mockMatches : realMatches
  const odds = realOdds.length ? realOdds : mockOdds
  const emptyResponse = useTeamSnapshot || useMatchSnapshot || !realOdds.length

  return {
    teams,
    matches,
    odds,
    demo: [teamsResult, matchesResult, oddsResult].some((result) => result.status === 'rejected') || emptyResponse,
  }
}
