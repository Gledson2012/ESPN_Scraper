import type { Match, OddsEvent, Player, Team } from '../types/api'

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

const demoPhotoUrls: Record<number, string> = {
  1001: 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Alan_Patrick_2018.jpg/330px-Alan_Patrick_2018.jpg',
  1002: 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Sergio_Rochet_%282022%29.jpg/330px-Sergio_Rochet_%282022%29.jpg',
  1003: 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/RAFAEL_BORRE_%28cropped2%29.jpg/330px-RAFAEL_BORRE_%28cropped2%29.jpg',
  1005: 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Martin_Braithwaite_Web_Summit_2021.jpg/330px-Martin_Braithwaite_Web_Summit_2021.jpg',
  1006: 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Partido_Galicia_-_Panam%C3%A1_en_Bala%C3%ADdos_182_%28cropped%29.jpg/330px-Partido_Galicia_-_Panam%C3%A1_en_Bala%C3%ADdos_182_%28cropped%29.jpg',
  1007: 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Ante_Budimir_Croatia_v_Portugal_2_July_2026-034.jpg/330px-Ante_Budimir_Croatia_v_Portugal_2_July_2026-034.jpg',
  1008: 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/2019147183134_2019-05-27_Fussball_1.FC_Kaiserslautern_vs_FC_Bayern_M%C3%BCnchen_-_Sven_-_1D_X_MK_II_-_0228_-_B70I8527_%28cropped%29.jpg/330px-2019147183134_2019-05-27_Fussball_1.FC_Kaiserslautern_vs_FC_Bayern_M%C3%BCnchen_-_Sven_-_1D_X_MK_II_-_0228_-_B70I8527_%28cropped%29.jpg',
  1009: 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Pedri_France_v_Spain_7.24.26-245.jpg/330px-Pedri_France_v_Spain_7.24.26-245.jpg',
  1010: 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Raphinha_Brazil_V_Morocco_13_June_2026-133_%28cropped%29.jpg/330px-Raphinha_Brazil_V_Morocco_13_June_2026-133_%28cropped%29.jpg',
  1011: 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Inaki_Williams_England_v_Ghana_23_June_2026-154.jpg/330px-Inaki_Williams_England_v_Ghana_23_June_2026-154.jpg',
  1012: 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Nico_Williams_Argentina_v_Spain_19_July_2026-196_%28cropped%29.jpg/330px-Nico_Williams_Argentina_v_Spain_19_July_2026-196_%28cropped%29.jpg',
  1013: 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Cole_Palmer_2025_FIFA_Club_World_Cup_Final.jpg/330px-Cole_Palmer_2025_FIFA_Club_World_Cup_Final.jpg',
  1014: 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Enzo_Fernandez_Argentina_v_Spain_19_July_2026-050_%28cropped%29.jpg/330px-Enzo_Fernandez_Argentina_v_Spain_19_July_2026-050_%28cropped%29.jpg',
  1015: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Nicolas_Jackson_France_v_Senegal_16_June_2026-369_%28cropped%29.jpg/330px-Nicolas_Jackson_France_v_Senegal_16_June_2026-369_%28cropped%29.jpg',
  1016: 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/Carlton_Morris.png/330px-Carlton_Morris.png',
  1017: 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Joaopalhinha.jpg/330px-Joaopalhinha.jpg',
  1018: 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Jake_Reeves_15022025_%281%29.jpg/330px-Jake_Reeves_15022025_%281%29.jpg',
}

export const mockPlayers: Player[] = [
  { id: 1001, name: 'Alan Patrick', full_name: null, birth_date: null, nationality: 'Brasil', position: 'MF', foot: null, height_cm: null, weight_kg: null, shirt_number: 10, team_id: 1, espn_id: null, photo_url: demoPhotoUrls[1001] },
  { id: 1002, name: 'Sergio Rochet', full_name: null, birth_date: null, nationality: 'Uruguai', position: 'GK', foot: null, height_cm: null, weight_kg: null, shirt_number: 1, team_id: 1, espn_id: null, photo_url: demoPhotoUrls[1002] },
  { id: 1003, name: 'Rafael Borré', full_name: null, birth_date: null, nationality: 'Colômbia', position: 'FW', foot: null, height_cm: null, weight_kg: null, shirt_number: 9, team_id: 1, espn_id: null, photo_url: demoPhotoUrls[1003] },
  { id: 1004, name: 'Franco Cristaldo', full_name: null, birth_date: null, nationality: 'Argentina', position: 'MF', foot: null, height_cm: null, weight_kg: null, shirt_number: 10, team_id: 2, espn_id: null, photo_url: null },
  { id: 1005, name: 'Martin Braithwaite', full_name: null, birth_date: null, nationality: 'Dinamarca', position: 'FW', foot: null, height_cm: null, weight_kg: null, shirt_number: 22, team_id: 2, espn_id: null, photo_url: demoPhotoUrls[1005] },
  { id: 1006, name: 'Iago Aspas', full_name: null, birth_date: null, nationality: 'Espanha', position: 'FW', foot: null, height_cm: null, weight_kg: null, shirt_number: 10, team_id: 3, espn_id: null, photo_url: demoPhotoUrls[1006] },
  { id: 1007, name: 'Ante Budimir', full_name: null, birth_date: null, nationality: 'Croácia', position: 'FW', foot: null, height_cm: null, weight_kg: null, shirt_number: 17, team_id: 4, espn_id: null, photo_url: demoPhotoUrls[1007] },
  { id: 1008, name: 'Robert Lewandowski', full_name: null, birth_date: null, nationality: 'Polônia', position: 'FW', foot: null, height_cm: null, weight_kg: null, shirt_number: 9, team_id: 5, espn_id: null, photo_url: demoPhotoUrls[1008] },
  { id: 1009, name: 'Pedri', full_name: null, birth_date: null, nationality: 'Espanha', position: 'MF', foot: null, height_cm: null, weight_kg: null, shirt_number: 8, team_id: 5, espn_id: null, photo_url: demoPhotoUrls[1009] },
  { id: 1010, name: 'Raphinha', full_name: null, birth_date: null, nationality: 'Brasil', position: 'FW', foot: null, height_cm: null, weight_kg: null, shirt_number: 11, team_id: 5, espn_id: null, photo_url: demoPhotoUrls[1010] },
  { id: 1011, name: 'Iñaki Williams', full_name: null, birth_date: null, nationality: 'Gana', position: 'FW', foot: null, height_cm: null, weight_kg: null, shirt_number: 9, team_id: 6, espn_id: null, photo_url: demoPhotoUrls[1011] },
  { id: 1012, name: 'Nico Williams', full_name: null, birth_date: null, nationality: 'Espanha', position: 'FW', foot: null, height_cm: null, weight_kg: null, shirt_number: 10, team_id: 6, espn_id: null, photo_url: demoPhotoUrls[1012] },
  { id: 1013, name: 'Cole Palmer', full_name: null, birth_date: null, nationality: 'Inglaterra', position: 'MF', foot: null, height_cm: null, weight_kg: null, shirt_number: 20, team_id: 7, espn_id: null, photo_url: demoPhotoUrls[1013] },
  { id: 1014, name: 'Enzo Fernández', full_name: null, birth_date: null, nationality: 'Argentina', position: 'MF', foot: null, height_cm: null, weight_kg: null, shirt_number: 8, team_id: 7, espn_id: null, photo_url: demoPhotoUrls[1014] },
  { id: 1015, name: 'Nicolas Jackson', full_name: null, birth_date: null, nationality: 'Senegal', position: 'FW', foot: null, height_cm: null, weight_kg: null, shirt_number: 15, team_id: 7, espn_id: null, photo_url: demoPhotoUrls[1015] },
  { id: 1016, name: 'Carlton Morris', full_name: null, birth_date: null, nationality: 'Inglaterra', position: 'FW', foot: null, height_cm: null, weight_kg: null, shirt_number: 9, team_id: 8, espn_id: null, photo_url: demoPhotoUrls[1016] },
  { id: 1017, name: 'João Palhinha', full_name: null, birth_date: null, nationality: 'Portugal', position: 'MF', foot: null, height_cm: null, weight_kg: null, shirt_number: 26, team_id: 9, espn_id: null, photo_url: demoPhotoUrls[1017] },
  { id: 1018, name: 'Jake Reeves', full_name: null, birth_date: null, nationality: 'Inglaterra', position: 'MF', foot: null, height_cm: null, weight_kg: null, shirt_number: 4, team_id: 10, espn_id: null, photo_url: demoPhotoUrls[1018] },
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
