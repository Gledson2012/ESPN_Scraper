import { mockMatches, mockOdds, mockTeams } from '../data/mockData'
import type { Catalog, LiveMatch, Match, MatchStats, OddsEvent, Overview, Player, Prediction, PredictionRequest, SearchResponse, SoccerOddsResponse, SyncStatus, Team, TeamSummary } from '../types/api'

const browserHost = typeof window !== 'undefined' ? window.location.hostname : 'localhost'

const API_URL_STORAGE_KEY = 'espn_api_url'

function normalizeApiUrl(value?: string): string {
  if (!value) return ''

  const normalized = value.replace(/\/+$/, '')
  return normalized.endsWith('/api/v1') ? normalized : `${normalized}/api/v1`
}

function getStoredApiUrl(): string {
  if (typeof window === 'undefined') return ''
  try {
    return normalizeApiUrl(window.localStorage.getItem(API_URL_STORAGE_KEY) ?? '')
  } catch {
    return ''
  }
}

const defaultApiUrl = normalizeApiUrl(
  (import.meta.env.VITE_API_URL as string | undefined)?.trim()
    || (!import.meta.env.PROD ? `http://${browserHost}:8000/api/v1` : ''),
)

/** URL base atual (configuração em runtime tem prioridade sobre o build). */
export function getApiUrl(): string {
  return getStoredApiUrl() || defaultApiUrl
}

/** Configura (ou limpa) a URL base da API em runtime, sem recompilar. */
export function setApiUrl(value?: string): string {
  const url = normalizeApiUrl(value ?? '')
  if (typeof window !== 'undefined') {
    try {
      if (url) window.localStorage.setItem(API_URL_STORAGE_KEY, url)
      else window.localStorage.removeItem(API_URL_STORAGE_KEY)
    } catch {
      // Ignora falhas de armazenamento (ex.: modo privado).
    }
  }
  return url
}

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
  if (!getApiUrl()) {
    throw new ApiError('A URL pública da API não foi configurada; o painel está em modo demonstração.')
  }

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

  try {
    const response = await fetch(`${getApiUrl()}${path}`, {
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
  baseUrl: getApiUrl(),

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

  async getOverview(competition?: string, season?: string): Promise<Overview> {
    const params = new URLSearchParams()
    if (competition) params.set('competition', competition)
    if (season) params.set('season', season)
    const query = params.toString()
    return expectObject<Overview>(await request<unknown>(`/overview${query ? `?${query}` : ''}`), 'resumo do painel')
  },

  async getSyncStatus(): Promise<SyncStatus> {
    return expectObject<SyncStatus>(await request<unknown>('/sync/status'), 'status da sincronização')
  },

  async getCatalog(): Promise<Catalog> {
    return expectObject<Catalog>(await request<unknown>('/catalog'), 'catálogo de filtros')
  },

  async search(query: string, types?: Array<'team' | 'player' | 'match'>, limit = 10): Promise<SearchResponse> {
    const params = new URLSearchParams({ q: query, limit: String(limit) })
    if (types?.length) params.set('types', types.join(','))
    return expectObject<SearchResponse>(await request<unknown>(`/search?${params.toString()}`), 'busca')
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
  overview: Overview | null
  demo: boolean
}

export async function loadDashboardData(): Promise<DashboardData> {
  const [teamsResult, matchesResult, oddsResult, overviewResult] = await Promise.allSettled([
    api.getTeams(),
    api.getMatches(),
    api.getOdds(),
    api.getOverview(),
  ])

  const realTeams = teamsResult.status === 'fulfilled' ? teamsResult.value : []
  const realMatches = matchesResult.status === 'fulfilled' ? matchesResult.value : []
  const realOdds = oddsResult.status === 'fulfilled' ? oddsResult.value.events : []
  const useTeamSnapshot = !realTeams.length
  const useMatchSnapshot = !realMatches.length
  const teams = useTeamSnapshot ? mockTeams : realTeams
  const matches = useMatchSnapshot ? mockMatches : realMatches
  const odds = realOdds.length ? realOdds : mockOdds
  const overview = overviewResult.status === 'fulfilled' ? overviewResult.value : null
  const emptyResponse = useTeamSnapshot || useMatchSnapshot || !realOdds.length

  return {
    teams,
    matches,
    odds,
    overview,
    demo: [teamsResult, matchesResult, oddsResult].some((result) => result.status === 'rejected') || emptyResponse,
  }
}
