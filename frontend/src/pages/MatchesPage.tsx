import { CalendarDays, Filter, Radio, Search, SlidersHorizontal } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { DemoNotice } from '../components/DemoNotice'
import { LiveMatchCard } from '../components/LiveMatchCard'
import { LoadingState } from '../components/LoadingState'
import { MatchCard } from '../components/MatchCard'
import { PageHeader } from '../components/PageHeader'
import { api } from '../lib/api'
import { mockMatches, mockTeams } from '../data/mockData'
import type { LiveMatch, Match, Team } from '../types/api'

export function MatchesPage() {
  const [searchParams] = useSearchParams()
  const [matches, setMatches] = useState<Match[]>([])
  const [liveMatches, setLiveMatches] = useState<LiveMatch[]>([])
  const [teams, setTeams] = useState<Team[]>([])
  const [search, setSearch] = useState(searchParams.get('search') || '')
  const [filter, setFilter] = useState<'all' | 'live' | 'upcoming' | 'finished'>('all')
  const [demo, setDemo] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.getMatches(), api.getTeams()]).then(([matchData, teamData]) => {
      const useSnapshot = !matchData.length || !teamData.length
      setMatches(useSnapshot ? mockMatches : matchData)
      setTeams(useSnapshot ? mockTeams : teamData)
      setDemo(!matchData.length || !teamData.length)
    }).catch(() => {
      setMatches(mockMatches)
      setTeams(mockTeams)
      setDemo(true)
    }).finally(() => setLoading(false))

    // Jogos ao vivo vêm da ESPN em tempo real; uma falha não afeta a página.
    api.getLiveMatches().then(setLiveMatches).catch(() => setLiveMatches([]))
  }, [])

  const filteredMatches = useMemo(() => matches.filter((match) => {
    const home = teams.find((team) => team.id === match.home_team_id)?.name || ''
    const away = teams.find((team) => team.id === match.away_team_id)?.name || ''
    const queryMatches = `${home} ${away} ${match.competition || ''}`.toLowerCase().includes(search.toLowerCase())
    const isFinished = match.home_score !== null && match.away_score !== null
    const statusMatches = filter === 'all' || (filter === 'finished' && isFinished) || (filter === 'upcoming' && !isFinished)
    return queryMatches && statusMatches
  }), [filter, matches, search, teams])

  if (loading) return <LoadingState />

  return (
    <>
      {demo && <DemoNotice />}
      <PageHeader eyebrow="CENTRAL DE JOGOS" title="Partidas" description="Resultados, próximos confrontos e dados históricos em um só lugar." action={<button className="button secondary"><CalendarDays size={16} /> Temporada atual</button>} />
      <section className="page-toolbar">
        <div className="search-field"><Search size={17} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar por time ou competição" /></div>
        <div className="filter-tabs" role="tablist"><button className={filter === 'all' ? 'selected' : ''} onClick={() => setFilter('all')}>Todas <span>{matches.length}</span></button><button className={filter === 'live' ? 'selected' : ''} onClick={() => setFilter('live')}>Ao vivo <span>{liveMatches.length}</span></button><button className={filter === 'upcoming' ? 'selected' : ''} onClick={() => setFilter('upcoming')}>Próximas <span>{matches.filter((match) => match.home_score === null || match.away_score === null).length}</span></button><button className={filter === 'finished' ? 'selected' : ''} onClick={() => setFilter('finished')}>Encerradas <span>{matches.filter((match) => match.home_score !== null && match.away_score !== null).length}</span></button></div>
        <button className="icon-button outline" aria-label="Mais filtros"><SlidersHorizontal size={17} /><span className="desktop-only">Filtros</span></button>
      </section>
      <div className="content-caption"><span><Filter size={14} /> {filter === 'live' ? liveMatches.length : filteredMatches.length} partidas encontradas</span><span>Ordenado por data mais recente</span></div>
      {filter === 'live' ? (
        <>
          <section className="matches-grid">{liveMatches.map((match) => <LiveMatchCard key={match.espn_event_id} match={match} />)}</section>
          {!liveMatches.length && <div className="empty-card"><Radio size={15} /> Nenhum jogo ao vivo neste momento.</div>}
        </>
      ) : (
        <>
          <section className="matches-grid">{filteredMatches.map((match) => <MatchCard key={match.id} match={match} teams={teams} />)}</section>
          {!filteredMatches.length && <div className="empty-card">Nenhuma partida corresponde aos filtros.</div>}
        </>
      )}
    </>
  )
}
