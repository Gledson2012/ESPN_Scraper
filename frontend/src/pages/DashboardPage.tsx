import { Activity, ArrowRight, BarChart3, CalendarDays, CircleDollarSign, Database, Shield, Sparkles, Trophy, Users } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { DemoNotice } from '../components/DemoNotice'
import { LoadingState } from '../components/LoadingState'
import { MatchCard } from '../components/MatchCard'
import { PageHeader } from '../components/PageHeader'
import { SectionHeading } from '../components/SectionHeading'
import { StatCard } from '../components/StatCard'
import { TeamBadge } from '../components/TeamBadge'
import { loadDashboardData } from '../lib/api'
import { formatMatchDate, formatToday, getGreeting } from '../lib/format'
import { isFinishedMatch, isUpcomingMatch, matchTimestamp } from '../lib/match'
import type { DashboardData } from '../lib/api'

export function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null)

  useEffect(() => {
    loadDashboardData().then(setData)
  }, [])

  const teamById = useMemo(() => new Map(data?.teams.map((team) => [team.id, team]) ?? []), [data?.teams])
  const upcoming = [...(data?.matches.filter((match) => isUpcomingMatch(match)) ?? [])]
    .sort((left, right) => matchTimestamp(left) - matchTimestamp(right))
  const finished = [...(data?.matches.filter(isFinishedMatch) ?? [])]
    .sort((left, right) => matchTimestamp(right) - matchTimestamp(left))
  const matchesWithMetadata = data?.matches.filter((match) => Boolean(match.match_date && match.competition)).length ?? 0
  const nextMatch = upcoming[0]

  if (!data) return <LoadingState label="Preparando seu painel..." />

  const totals = data.overview?.totals

  return (
    <>
      {data.demo && <DemoNotice />}
      <PageHeader
        eyebrow={formatToday()}
        title={`${getGreeting()}, Gledson`}
        description="Acompanhe o que está acontecendo no futebol e encontre os próximos insights."
        action={<Link className="button primary" to="/previsoes"><Sparkles size={16} /> Nova previsão</Link>}
      />

      <section className="stats-grid">
        <StatCard label={data.demo ? 'Jogos na agenda' : 'Partidas analisadas'} value={totals?.matches ?? data.matches.length} note={data.demo ? 'Snapshot real do dia' : 'Base disponível'} icon={Trophy} tone="green" />
        <StatCard label={data.demo ? 'Clubes na agenda' : 'Times monitorados'} value={totals?.teams ?? data.teams.length} note={data.demo ? 'Nos próximos confrontos' : 'Em todas as competições'} icon={Shield} tone="blue" />
        <StatCard label="Jogos encerrados" value={totals?.completed_matches ?? finished.length} note="Com resultado registrado" icon={Activity} tone="orange" />
        <StatCard label="Eventos de odds" value={data.odds.length} note={data.demo ? 'Cotações aguardando conexão' : 'Eventos com odds'} icon={CircleDollarSign} tone="purple" />
      </section>

      <section className="dashboard-grid main-grid">
        <div className="dashboard-column">
          <SectionHeading title="Próxima partida" description="O próximo confronto na sua base de dados" to="/partidas" />
          {nextMatch ? (
            <div className="featured-match">
              <div className="featured-match-top"><span className="eyebrow">EM DESTAQUE</span><span className="live-label"><span className="status-dot" /> {data.demo ? 'Agenda real' : 'Dados atualizados'}</span></div>
              <div className="featured-date"><CalendarDays size={15} /> {formatMatchDate(nextMatch.match_date)}</div>
              <div className="featured-teams">
                <div className="featured-team"><TeamBadge name={teamById.get(nextMatch.home_team_id)?.name || 'Casa'} logo={teamById.get(nextMatch.home_team_id)?.logo_url} /><strong>{teamById.get(nextMatch.home_team_id)?.name || `Time ${nextMatch.home_team_id}`}</strong><span>Mandante</span></div>
                <div className="featured-vs"><span>VS</span><small>{nextMatch.competition || 'Partida'}</small></div>
                <div className="featured-team"><TeamBadge name={teamById.get(nextMatch.away_team_id)?.name || 'Fora'} logo={teamById.get(nextMatch.away_team_id)?.logo_url} color="#315fca" /><strong>{teamById.get(nextMatch.away_team_id)?.name || `Time ${nextMatch.away_team_id}`}</strong><span>Visitante</span></div>
              </div>
              <div className="featured-footer"><span><span className="tiny-icon"><Users size={13} /></span> {nextMatch.venue || 'Local não informado'}</span><Link to="/previsoes">Ver previsão <ArrowRight size={14} /></Link></div>
            </div>
          ) : <div className="empty-card">Nenhuma partida futura encontrada.</div>}

          <SectionHeading title="Últimas partidas" description="Resultados mais recentes" to="/partidas" />
          <div className="match-list">
            {finished.slice(0, 3).map((match) => <Link className="match-card-link" key={match.id} to={`/partidas/${match.id}`}><MatchCard match={match} teams={data.teams} compact /></Link>)}
            {!finished.length && <div className="empty-card">Ainda não há resultados registrados.</div>}
          </div>
        </div>

        <aside className="dashboard-column side-column">
          <SectionHeading title="Resumo de performance" />
          <div className="performance-card">
            <div className="performance-card-header"><div><span className="eyebrow">STATUS DA FONTE</span><h3>{data.demo ? 'Dados de demonstração' : 'Agenda atualizada'}</h3></div><div className="source-badge"><span className="status-dot" /> {data.demo ? 'Fallback' : 'Ativa'}</div></div>
            <div className="source-summary"><Database size={17} /><div><strong>{data.demo ? 'Snapshot real disponível' : 'Banco sincronizado'}</strong><span>{data.demo ? 'Dados prontos para exploração' : 'Dados atualizados pela API'}</span></div></div>
            <div className="progress-row"><span>Partidas com data e competição</span><strong>{data.matches.length ? `${Math.round((matchesWithMetadata / data.matches.length) * 100)}%` : '0%'}</strong><div className="progress-track"><i style={{ width: data.matches.length ? `${(matchesWithMetadata / data.matches.length) * 100}%` : '0%' }} /></div></div>
            <div className="progress-row"><span>Resultados já registrados</span><strong>{data.matches.length ? `${Math.round((finished.length / data.matches.length) * 100)}%` : '0%'}</strong><div className="progress-track blue"><i style={{ width: data.matches.length ? `${(finished.length / data.matches.length) * 100}%` : '0%' }} /></div></div>
            <div className="performance-divider" />
            <div className="performance-insight"><div className="insight-icon"><BarChart3 size={16} /></div><p><strong>Pronto para explorar</strong><br />Abra uma partida para consultar detalhes e gerar uma previsão.</p></div>
          </div>

          <SectionHeading title="Times em alta" to="/times" />
          <div className="trending-list">
            {data.teams.slice(0, 4).map((team, index) => <Link className="trending-team" to={`/times/${team.id}`} key={team.id}><TeamBadge name={team.name} shortName={team.short_name} logo={team.logo_url} color={index % 2 ? '#315fca' : undefined} /><span><strong>{team.name}</strong><small>{team.league || 'Liga não informada'}</small></span><span className="trend-label">Na agenda</span></Link>)}
          </div>
        </aside>
      </section>

      <section className="quick-actions">
        <Link to="/partidas"><Trophy size={17} /><span><strong>Explorar partidas</strong><small>Filtre por temporada e competição</small></span><ArrowRight size={16} /></Link>
        <Link to="/times"><Shield size={17} /><span><strong>Consultar times</strong><small>Veja elencos e desempenho</small></span><ArrowRight size={16} /></Link>
        <Link to="/odds"><CircleDollarSign size={17} /><span><strong>Ver odds</strong><small>Acompanhe os mercados disponíveis</small></span><ArrowRight size={16} /></Link>
      </section>
    </>
  )
}
