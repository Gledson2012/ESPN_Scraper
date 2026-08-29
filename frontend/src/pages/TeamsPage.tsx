import { Search, Shield, Users } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { DemoNotice } from '../components/DemoNotice'
import { LoadingState } from '../components/LoadingState'
import { PageHeader } from '../components/PageHeader'
import { TeamBadge } from '../components/TeamBadge'
import { api } from '../lib/api'
import { mockTeams } from '../data/mockData'
import type { Team } from '../types/api'

const teamColors = ['#178f64', '#315fca', '#d97736', '#7b61b8']

export function TeamsPage() {
  const [teams, setTeams] = useState<Team[]>([])
  const [search, setSearch] = useState('')
  const [demo, setDemo] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getTeams().then((teamData) => {
      setTeams(teamData.length ? teamData : mockTeams)
      setDemo(!teamData.length)
    }).catch(() => {
      setTeams(mockTeams)
      setDemo(true)
    }).finally(() => setLoading(false))
  }, [])

  const filteredTeams = useMemo(() => teams.filter((team) => `${team.name} ${team.short_name || ''} ${team.league || ''}`.toLowerCase().includes(search.toLowerCase())), [search, teams])

  if (loading) return <LoadingState />

  return (
    <>
      {demo && <DemoNotice />}
      <PageHeader eyebrow="BASE DE DADOS" title="Times monitorados" description="Explore os clubes disponíveis e acompanhe seus dados de performance." action={<button className="button primary"><Shield size={16} /> Adicionar time</button>} />
      <section className="teams-summary"><div><span className="summary-icon green"><Shield size={18} /></span><span><strong>{teams.length}</strong><small>clubes cadastrados</small></span></div><div><span className="summary-icon blue"><Users size={18} /></span><span><strong>{new Set(teams.map((team) => team.league)).size}</strong><small>competições</small></span></div><div><span className="summary-icon orange"><Search size={18} /></span><span><strong>{teams.filter((team) => team.country === 'Brasil').length || teams.length}</strong><small>times brasileiros</small></span></div></section>
      <section className="page-toolbar simple"><div className="search-field"><Search size={17} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar clube ou competição" /></div><span className="toolbar-result">{filteredTeams.length} resultados</span></section>
      <section className="teams-grid">
        {filteredTeams.map((team, index) => <article className="team-card" key={team.id}>
          <div className="team-card-head"><TeamBadge name={team.name} shortName={team.short_name} color={teamColors[index % teamColors.length]} /><button className="more-button" aria-label={`Mais opções para ${team.name}`}>•••</button></div>
          <h3>{team.name}</h3><span className="team-short-name">{team.short_name || 'Sem abreviação'}</span>
          <div className="team-card-meta"><span>{team.league || 'Competição não informada'}</span><span>{team.country || 'País não informado'}</span></div>
          <div className="team-card-footer"><span><span className="mini-avatar">{team.name.slice(0, 1)}</span> Dados disponíveis</span><button className="text-link-button">Ver detalhes →</button></div>
        </article>)}
      </section>
      {!filteredTeams.length && <div className="empty-card">Nenhum time corresponde à sua busca.</div>}
    </>
  )
}
