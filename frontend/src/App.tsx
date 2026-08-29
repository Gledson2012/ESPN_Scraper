import { Route, Routes } from 'react-router-dom'
import { AppShell } from './components/AppShell'
import { DashboardPage } from './pages/DashboardPage'
import { MatchesPage } from './pages/MatchesPage'
import { TeamsPage } from './pages/TeamsPage'
import { PlayersPage } from './pages/PlayersPage'
import { PredictionsPage } from './pages/PredictionsPage'
import { OddsPage } from './pages/OddsPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { TeamDetailPage } from './pages/TeamDetailPage'
import { MatchDetailPage } from './pages/MatchDetailPage'

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/partidas" element={<MatchesPage />} />
        <Route path="/partidas/:matchId" element={<MatchDetailPage />} />
        <Route path="/times" element={<TeamsPage />} />
        <Route path="/times/:teamId" element={<TeamDetailPage />} />
        <Route path="/jogadores" element={<PlayersPage />} />
        <Route path="/previsoes" element={<PredictionsPage />} />
        <Route path="/odds" element={<OddsPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}
