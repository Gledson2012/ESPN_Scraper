import type { Match, OddsEvent, Team } from '../types/api'

export const DEMO_DATA_AS_OF = '27/08/2026'
export const DEMO_DATA_SOURCE_URL = 'https://jc.uol.com.br/blog-do-torcedor/onde-assistir/2026/08/27/jogos-de-hoje-27-08-confira-a-programacao-do-futebol-horarios-e-onde-assistir.html'

export const mockTeams: Team[] = [
  { id: 1, name: 'Internacional', short_name: 'INT', country: 'Brasil', league: 'Copa do Brasil', stadium: 'Beira-Rio' },
  { id: 2, name: 'Grêmio', short_name: 'GRE', country: 'Brasil', league: 'Copa do Brasil', stadium: 'Arena do Grêmio' },
  { id: 3, name: 'Celta', short_name: 'CEL', country: 'Espanha', league: 'La Liga', stadium: 'Abanca-Balaídos' },
  { id: 4, name: 'Osasuna', short_name: 'OSA', country: 'Espanha', league: 'La Liga', stadium: 'El Sadar' },
  { id: 5, name: 'Barcelona', short_name: 'BAR', country: 'Espanha', league: 'La Liga', stadium: 'Spotify Camp Nou' },
  { id: 6, name: 'Athletic Bilbao', short_name: 'ATH', country: 'Espanha', league: 'La Liga', stadium: 'San Mamés' },
  { id: 7, name: 'Chelsea', short_name: 'CHE', country: 'Inglaterra', league: 'Copa da Liga Inglesa', stadium: 'Stamford Bridge' },
  { id: 8, name: 'Luton Town', short_name: 'LUT', country: 'Inglaterra', league: 'Copa da Liga Inglesa', stadium: 'Kenilworth Road' },
  { id: 9, name: 'Fulham', short_name: 'FUL', country: 'Inglaterra', league: 'Copa da Liga Inglesa', stadium: 'Craven Cottage' },
  { id: 10, name: 'AFC Wimbledon', short_name: 'WIM', country: 'Inglaterra', league: 'Copa da Liga Inglesa', stadium: 'Plough Lane' },
]

export const mockMatches: Match[] = [
  // Agenda real consultada em 27/08/2026; a API do FBref substitui este
  // snapshot assim que houver dados sincronizados no banco.
  { id: 101, home_team_id: 1, away_team_id: 2, competition: 'Copa do Brasil', season: '2026', match_date: '2026-08-27T20:00:00-03:00', venue: 'Beira-Rio', home_score: null, away_score: null },
  { id: 102, home_team_id: 3, away_team_id: 4, competition: 'La Liga', season: '2026-2027', match_date: '2026-08-27T15:30:00-03:00', venue: 'Abanca-Balaídos', home_score: null, away_score: null },
  { id: 103, home_team_id: 5, away_team_id: 6, competition: 'La Liga', season: '2026-2027', match_date: '2026-08-27T16:00:00-03:00', venue: 'Spotify Camp Nou', home_score: null, away_score: null },
  { id: 104, home_team_id: 7, away_team_id: 8, competition: 'Copa da Liga Inglesa', season: '2026-2027', match_date: '2026-08-27T15:30:00-03:00', venue: 'Stamford Bridge', home_score: null, away_score: null },
  { id: 105, home_team_id: 9, away_team_id: 10, competition: 'Copa da Liga Inglesa', season: '2026-2027', match_date: '2026-08-27T16:00:00-03:00', venue: 'Craven Cottage', home_score: null, away_score: null },
]

export const mockOdds: OddsEvent[] = [
  { event_id: 'real-2026-inter-gremio', event_name: 'Internacional vs Grêmio', home_team: 'Internacional', away_team: 'Grêmio', start_time: '2026-08-27T20:00:00-03:00', competition: { name: 'Copa do Brasil' }, status: 'TRADING', markets: {} },
  { event_id: 'real-2026-barcelona-athletic', event_name: 'Barcelona vs Athletic Bilbao', home_team: 'Barcelona', away_team: 'Athletic Bilbao', start_time: '2026-08-27T16:00:00-03:00', competition: { name: 'La Liga' }, status: 'TRADING', markets: {} },
]
