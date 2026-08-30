export type Nullable<T> = T | null

export interface Team {
  id: number
  name: string
  short_name: Nullable<string>
  country: Nullable<string>
  league: Nullable<string>
  stadium: Nullable<string>
  founded?: Nullable<number>
  website?: Nullable<string>
  espn_id?: Nullable<string>
  logo_url?: Nullable<string>
  created_at?: string
  updated_at?: string
}

export interface Player {
  id: number
  name: string
  full_name: Nullable<string>
  birth_date: Nullable<string>
  nationality: Nullable<string>
  position: Nullable<string>
  foot: Nullable<string>
  height_cm: Nullable<number>
  weight_kg: Nullable<number>
  shirt_number: Nullable<number>
  team_id: Nullable<number>
  espn_id: Nullable<string>
  photo_url: Nullable<string>
}

export interface Match {
  id: number
  home_team_id: number
  away_team_id: number
  competition: Nullable<string>
  season: Nullable<string>
  match_date: Nullable<string>
  venue?: Nullable<string>
  home_score: Nullable<number>
  away_score: Nullable<number>
  home_xg?: Nullable<number>
  away_xg?: Nullable<number>
  attendance?: Nullable<number>
  referee?: Nullable<string>
  espn_id?: Nullable<string>
  created_at?: string
  updated_at?: string
  stats?: MatchStats[]
}

export interface MatchStats {
  id: number
  match_id: number
  team_id: number
  is_home: boolean
  possession: Nullable<number>
  shots: Nullable<number>
  shots_on_target: Nullable<number>
  xg: Nullable<number>
  xg_against: Nullable<number>
  corners?: Nullable<number>
  fouls?: Nullable<number>
  yellow_cards?: Nullable<number>
  red_cards?: Nullable<number>
  offsides?: Nullable<number>
  passes?: Nullable<number>
  pass_accuracy?: Nullable<number>
  tackles?: Nullable<number>
  interceptions?: Nullable<number>
  saves?: Nullable<number>
}

export interface TeamSummary {
  team_id: number
  team_name: string
  matches: number
  completed_matches: number
  wins: number
  draws: number
  losses: number
  goals_for: number
  goals_against: number
  goal_difference: number
  points: number
  stats_available: number
}

export interface CatalogOption {
  code: string
  name: string
}

export interface Catalog {
  competitions: CatalogOption[]
  seasons: string[]
  positions: string[]
  nationalities: string[]
  countries: string[]
}

export interface SyncResourceStatus {
  resource: 'teams' | 'players' | 'matches' | 'stats'
  count: number
  last_updated_at: string | null
  source: string
}

export interface SyncStatus {
  generated_at: string
  resources: SyncResourceStatus[]
}

export interface OverviewMatch {
  id: number
  home_team_id: number
  away_team_id: number
  home_team: string
  away_team: string
  competition: string | null
  season: string | null
  match_date: string | null
  home_score: number | null
  away_score: number | null
}

export interface Overview {
  generated_at: string
  competition: string | null
  season: string | null
  totals: {
    teams: number
    players: number
    matches: number
    completed_matches: number
    upcoming_matches: number
    stats: number
  }
  next_matches: OverviewMatch[]
  recent_matches: OverviewMatch[]
}

export interface SearchResult {
  type: 'team' | 'player' | 'match'
  id: number
  title: string
  subtitle: string | null
  path: string
}

export interface SearchResponse {
  query: string
  results: SearchResult[]
  total: number
}

export interface PredictionRequest {
  home_team_id: number
  away_team_id: number
  competition?: string
  season?: string
}

export interface Prediction {
  home_team_id: number
  away_team_id: number
  home_win_probability: number
  draw_probability: number
  away_win_probability: number
  predicted_home_score: number
  predicted_away_score: number
  over_2_5_probability: number
  btts_probability: number
  confidence: number
  model_version: string
}

export interface OddsEvent {
  event_id: string | number
  event_name: string
  home_team?: Nullable<string>
  away_team?: Nullable<string>
  start_time?: Nullable<string>
  competition?: Nullable<{ name?: string; key?: string }>
  markets?: Record<string, unknown>
  status?: Nullable<string>
}

export interface SoccerOddsResponse {
  events: OddsEvent[]
  total: number
}

export interface LiveMatch {
  league: string
  espn_event_id: string
  status: string
  clock?: Nullable<string>
  match_date?: Nullable<string>
  venue?: Nullable<string>
  home_team: string
  away_team: string
  home_score?: Nullable<number>
  away_score?: Nullable<number>
  home_team_logo?: Nullable<string>
  away_team_logo?: Nullable<string>
}
