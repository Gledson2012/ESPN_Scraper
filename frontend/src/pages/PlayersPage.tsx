import { Search, Shield, Users } from 'lucide-react'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { LoadingState } from '../components/LoadingState'
import { PageHeader } from '../components/PageHeader'
import { api } from '../lib/api'
import { mockPlayers, mockTeams } from '../data/mockData'
import type { Player, Team } from '../types/api'

const positionLabels: Record<string, string> = {
  GK: 'Goleiro',
  DF: 'Defensor',
  MF: 'Meio-campista',
  FW: 'Atacante',
}

function initials(name: string) {
  return name
    .split(/\s+/)
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
}

function PlayerPhoto({ player }: { player: Player }) {
  const [failed, setFailed] = useState(false)
  const showPhoto = Boolean(player.photo_url) && !failed

  return (
    <div className="player-photo">
      {showPhoto ? (
        <img src={player.photo_url || undefined} alt={`Foto de ${player.name}`} onError={() => setFailed(true)} />
      ) : (
        <span>{initials(player.name)}</span>
      )}
      {player.shirt_number != null && <b>{player.shirt_number}</b>}
    </div>
  )
}

export function PlayersPage() {
  const [searchParams] = useSearchParams()
  const [players, setPlayers] = useState<Player[]>([])
  const [teams, setTeams] = useState<Team[]>([])
  const [search, setSearch] = useState(searchParams.get('search') || '')
  const [selectedTeamId, setSelectedTeamId] = useState('all')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [demo, setDemo] = useState(false)

  const loadPlayers = useCallback(() => {
    setLoading(true)
    setError('')
    Promise.allSettled([api.getPlayers(), api.getTeams()])
      .then(([playersResult, teamsResult]) => {
        const playerData = playersResult.status === 'fulfilled' && playersResult.value.length ? playersResult.value : mockPlayers
        const teamData = teamsResult.status === 'fulfilled' && teamsResult.value.length ? teamsResult.value : mockTeams
        setPlayers(playerData)
        setTeams(teamData)
        setDemo(playersResult.status === 'rejected' || teamsResult.status === 'rejected' || playerData === mockPlayers || teamData === mockTeams)
      })
      .catch(() => setError('Não foi possível carregar os jogadores.'))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => { loadPlayers() }, [loadPlayers])

  useEffect(() => {
    setSearch(searchParams.get('search') || '')
  }, [searchParams])

  const teamNames = useMemo(() => new Map(teams.map((team) => [team.id, team.name])), [teams])
  const filteredPlayers = useMemo(() => {
    const query = search.trim().toLowerCase()
    return players
      .filter((player) => selectedTeamId === 'all' || String(player.team_id) === selectedTeamId)
      .filter((player) => `${player.name} ${player.full_name || ''} ${player.nationality || ''} ${teamNames.get(player.team_id ?? -1) || ''}`.toLowerCase().includes(query))
      .sort((first, second) => first.name.localeCompare(second.name, 'pt-BR'))
  }, [players, search, selectedTeamId, teamNames])

  if (loading) return <LoadingState label="Carregando jogadores e fotos..." />

  return (
    <>
      <PageHeader
        eyebrow="ELENCOS ATUAIS"
        title="Jogadores"
        description="Consulte os atletas sincronizados pela ESPN com foto, posição, nacionalidade e clube atual."
        action={<span className="source-badge"><span className="status-dot" /> {demo ? 'Dados de demonstração' : 'Dados da ESPN'}</span>}
      />

      {error && <div className="error-card" role="alert"><span>{error}</span><button className="button secondary" onClick={loadPlayers}>Tentar novamente</button></div>}

      <section className="players-summary">
        <div><span className="summary-icon green"><Users size={18} /></span><span><strong>{players.length}</strong><small>jogadores cadastrados</small></span></div>
        <div><span className="summary-icon blue"><Shield size={18} /></span><span><strong>{new Set(players.map((player) => player.team_id).filter((teamId): teamId is number => teamId !== null)).size}</strong><small>clubes com elenco</small></span></div>
        <div><span className="summary-icon orange"><Users size={18} /></span><span><strong>{players.filter((player) => player.photo_url).length}</strong><small>fotos disponíveis</small></span></div>
      </section>

      <section className="page-toolbar simple">
        <div className="search-field"><Search size={17} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar jogador, clube ou nacionalidade" /></div>
        <select className="player-team-filter" value={selectedTeamId} onChange={(event) => setSelectedTeamId(event.target.value)} aria-label="Filtrar por clube">
          <option value="all">Todos os clubes</option>
          {teams.slice().sort((first, second) => first.name.localeCompare(second.name, 'pt-BR')).map((team) => <option key={team.id} value={team.id}>{team.name}</option>)}
        </select>
        <span className="toolbar-result">{filteredPlayers.length} jogadores</span>
      </section>

      <section className="players-grid">
        {filteredPlayers.map((player) => (
          <article className="player-card" key={player.id}>
            <PlayerPhoto player={player} />
            <div className="player-card-copy">
              <span className="player-position">{positionLabels[player.position || ''] || 'Posição não informada'}</span>
              <h3>{player.name}</h3>
              <p>{teamNames.get(player.team_id ?? -1) || 'Clube não informado'}</p>
              <div className="player-card-meta"><span>{player.nationality || 'Nacionalidade não informada'}</span><span>{player.position || '—'}</span></div>
            </div>
          </article>
        ))}
      </section>
      {!filteredPlayers.length && <div className="empty-card">Nenhum jogador corresponde aos filtros.</div>}
    </>
  )
}
