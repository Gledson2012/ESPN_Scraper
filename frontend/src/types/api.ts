export type Nullable<T> = T | null

export interface Team {
  id: number
  name: string
  short_name: Nullable<string>
  country: Nullable<string>
  league: Nullable<string>
  stadium: Nullable<string>
  logo_url?: Nullable<string>
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
  fbref_id: Nullable<string>
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
