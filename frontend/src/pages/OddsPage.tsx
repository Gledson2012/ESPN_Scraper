import { CircleDollarSign, ExternalLink, Info, RefreshCw, TrendingUp } from 'lucide-react'
import { useEffect, useState } from 'react'
import { DemoNotice } from '../components/DemoNotice'
import { LoadingState } from '../components/LoadingState'
import { PageHeader } from '../components/PageHeader'
import { TeamBadge } from '../components/TeamBadge'
import { api } from '../lib/api'
import { mockOdds } from '../data/mockData'
import { formatMatchDate } from '../lib/format'
import type { OddsEvent } from '../types/api'

function getOneXTwo(event: OddsEvent) {
  const markets = event.markets ?? {}
  const marketEntry = Object.entries(markets).find(([key]) => key.toLowerCase().includes('1x2') || key.toLowerCase().includes('match_odds'))
  const market = marketEntry?.[1] as { home?: number; draw?: number; away?: number; selections?: Array<{ name?: string; price?: number }> } | undefined
  if (!market) return { home: undefined, draw: undefined, away: undefined }
  if (market.selections) {
    return market.selections.reduce((prices, selection) => {
      const name = (selection.name || '').toLowerCase()
      if (name.includes('draw') || name.includes('empate')) prices.draw = selection.price
      else if (name.includes('away') || name.includes('fora')) prices.away = selection.price
      else if (prices.home === undefined) prices.home = selection.price
      return prices
    }, { home: undefined as number | undefined, draw: undefined as number | undefined, away: undefined as number | undefined })
  }
  return market
}

export function OddsPage() {
  const [odds, setOdds] = useState<OddsEvent[]>([])
  const [demo, setDemo] = useState(false)
  const [loading, setLoading] = useState(true)

  const loadOdds = () => {
    setLoading(true)
    return api.getOdds().then((response) => {
      setOdds(response.events.length ? response.events : mockOdds)
      setDemo(!response.events.length)
    }).catch(() => {
      setOdds(mockOdds)
      setDemo(true)
    }).finally(() => setLoading(false))
  }

  useEffect(() => { loadOdds() }, [])

  if (loading) return <LoadingState label="Buscando mercados..." />

  return (
    <>
      {demo && <DemoNotice />}
      <PageHeader eyebrow="MERCADOS EM TEMPO REAL" title="Odds de futebol" description="Compare os mercados disponíveis para os próximos confrontos." action={<button className="button secondary" onClick={loadOdds}><RefreshCw size={15} /> Atualizar</button>} />
      <div className="odds-overview"><div className="odds-overview-main"><span className="odds-icon"><CircleDollarSign size={19} /></span><div><strong>{odds.length}</strong><span>eventos disponíveis</span></div></div><div><span className="overview-label">Fonte</span><strong>Cloudbet</strong></div><div><span className="overview-label">Última atualização</span><strong>Agora</strong></div><div><span className="market-live"><span className="status-dot" /> Ao vivo</span></div></div>
      <section className="odds-list">
        {odds.map((event) => { const prices = getOneXTwo(event); const hasPrices = [prices.home, prices.draw, prices.away].some((price) => price !== undefined); return <article className="odds-card" key={event.event_id}>
          <div className="odds-card-top"><span className="competition-pill">{event.competition?.name || 'Futebol'}</span><span className="odds-time">{formatMatchDate(event.start_time)}</span></div>
          <div className="odds-match"><div><TeamBadge name={event.home_team || 'Casa'} /><strong>{event.home_team || 'Time da casa'}</strong></div><span>vs</span><div><TeamBadge name={event.away_team || 'Fora'} color="#315fca" /><strong>{event.away_team || 'Time visitante'}</strong></div></div>
          <div className="market-label"><span><TrendingUp size={14} /> Resultado 1X2</span><small>{event.status === 'TRADING' ? 'Mercado aberto' : event.status || 'Status não informado'}</small></div>
          {hasPrices ? <div className="odds-prices"><div><span>Casa</span><strong>{prices.home?.toFixed(2) || '—'}</strong></div><div><span>Empate</span><strong>{prices.draw?.toFixed(2) || '—'}</strong></div><div><span>Fora</span><strong>{prices.away?.toFixed(2) || '—'}</strong></div></div> : <div className="odds-empty-market"><Info size={15} /><span><strong>Cotações ainda não disponíveis</strong><small>O evento foi encontrado, mas a fonte não retornou preços.</small></span></div>}
          <button className="odds-link">Ver todos os mercados <ExternalLink size={14} /></button>
        </article> })}
      </section>
    </>
  )
}
