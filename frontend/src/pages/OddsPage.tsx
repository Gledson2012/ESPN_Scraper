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

interface OneXTwoPrices {
  home?: number
  draw?: number
  away?: number
}

function normalizeName(value: string) {
  return value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim()
}

function getOneXTwo(event: OddsEvent): OneXTwoPrices {
  const markets = event.markets ?? {}
  const marketEntry = Object.entries(markets).find(([key]) => key.toLowerCase().includes('1x2') || key.toLowerCase().includes('match_odds'))
  const market = marketEntry?.[1] as { home?: number; draw?: number; away?: number; selections?: Array<{ name?: string; price?: number }> } | undefined
  if (!market) return {}
  if (market.selections) {
    const homeName = normalizeName(event.home_team || '')
    const awayName = normalizeName(event.away_team || '')
    const prices: OneXTwoPrices = {}
    const unresolved: number[] = []

    for (const selection of market.selections) {
      if (typeof selection.price !== 'number' || !Number.isFinite(selection.price)) continue
      const name = normalizeName(selection.name || '')
      const isDraw = name === 'x' || name.includes('draw') || name.includes('empate')
      const isHome = name === '1' || name === 'home' || name.includes('home') || Boolean(homeName && (name === homeName || name.includes(homeName) || homeName.includes(name)))
      const isAway = name === '2' || name === 'away' || name.includes('away') || name.includes('fora') || Boolean(awayName && (name === awayName || name.includes(awayName) || awayName.includes(name)))

      if (isDraw) prices.draw = selection.price
      else if (isHome) prices.home = selection.price
      else if (isAway) prices.away = selection.price
      else unresolved.push(selection.price)
    }

    if (prices.home === undefined) prices.home = unresolved.shift()
    if (prices.away === undefined) prices.away = unresolved.shift()
    return prices
  }
  return market
}

export function OddsPage() {
  const [odds, setOdds] = useState<OddsEvent[]>([])
  const [demo, setDemo] = useState(false)
  const [loading, setLoading] = useState(true)
  const [expandedEventId, setExpandedEventId] = useState<string | null>(null)
  const [marketDetails, setMarketDetails] = useState<Record<string, Record<string, unknown>>>({})
  const [marketsLoading, setMarketsLoading] = useState<string | null>(null)
  const [marketsError, setMarketsError] = useState('')

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

  const toggleMarkets = async (eventId: string | number) => {
    const key = String(eventId)
    if (expandedEventId === key) {
      setExpandedEventId(null)
      return
    }
    setExpandedEventId(key)
    setMarketsError('')
    if (marketDetails[key]) return
    setMarketsLoading(key)
    try {
      const details = await api.getEventMarkets(eventId)
      setMarketDetails((current) => ({ ...current, [key]: details }))
    } catch {
      setMarketsError('Não foi possível carregar os mercados deste evento.')
    } finally {
      setMarketsLoading(null)
    }
  }

  if (loading) return <LoadingState label="Buscando mercados..." />

  return (
    <>
      {demo && <DemoNotice />}
      <PageHeader eyebrow="MERCADOS EM TEMPO REAL" title="Odds de futebol" description="Compare os mercados disponíveis para os próximos confrontos." action={<button className="button secondary" onClick={loadOdds}><RefreshCw size={15} /> Atualizar</button>} />
      <div className="odds-overview"><div className="odds-overview-main"><span className="odds-icon"><CircleDollarSign size={19} /></span><div><strong>{odds.length}</strong><span>eventos disponíveis</span></div></div><div><span className="overview-label">Fonte</span><strong>Cloudbet</strong></div><div><span className="overview-label">Última atualização</span><strong>Agora</strong></div><div><span className="market-live"><span className="status-dot" /> Ao vivo</span></div></div>
      <section className="odds-list">
        {odds.map((event) => { const prices = getOneXTwo(event); const hasPrices = [prices.home, prices.draw, prices.away].some((price) => price !== undefined); const eventKey = String(event.event_id); return <article className="odds-card" key={event.event_id}>
          <div className="odds-card-top"><span className="competition-pill">{event.competition?.name || 'Futebol'}</span><span className="odds-time">{formatMatchDate(event.start_time)}</span></div>
          <div className="odds-match"><div><TeamBadge name={event.home_team || 'Casa'} /><strong>{event.home_team || 'Time da casa'}</strong></div><span>vs</span><div><TeamBadge name={event.away_team || 'Fora'} color="#315fca" /><strong>{event.away_team || 'Time visitante'}</strong></div></div>
          <div className="market-label"><span><TrendingUp size={14} /> Resultado 1X2</span><small>{event.status === 'TRADING' ? 'Mercado aberto' : event.status || 'Status não informado'}</small></div>
          {hasPrices ? <div className="odds-prices"><div><span>Casa</span><strong>{prices.home?.toFixed(2) || '—'}</strong></div><div><span>Empate</span><strong>{prices.draw?.toFixed(2) || '—'}</strong></div><div><span>Fora</span><strong>{prices.away?.toFixed(2) || '—'}</strong></div></div> : <div className="odds-empty-market"><Info size={15} /><span><strong>Cotações ainda não disponíveis</strong><small>O evento foi encontrado, mas a fonte não retornou preços.</small></span></div>}
          <button className="odds-link" onClick={() => toggleMarkets(event.event_id)} aria-expanded={expandedEventId === eventKey}>{expandedEventId === eventKey ? 'Ocultar mercados' : 'Ver todos os mercados'} <ExternalLink size={14} /></button>
          {expandedEventId === eventKey && <div className="market-details">{marketsLoading === eventKey ? <small>Carregando mercados...</small> : marketsError ? <small className="market-error">{marketsError}</small> : Object.entries(marketDetails[eventKey] || {}).map(([marketName, market]) => {
            const selections = typeof market === 'object' && market !== null && 'selections' in market && Array.isArray(market.selections) ? market.selections as Array<{ name?: string; price?: number }> : []
            return <div key={marketName}><strong>{marketName}</strong>{selections.length ? <ul>{selections.map((selection, index) => <li key={`${selection.name || 'selection'}-${index}`}>{selection.name || 'Seleção'} <b>{typeof selection.price === 'number' ? selection.price.toFixed(2) : '—'}</b></li>)}</ul> : <small>Sem seleções disponíveis.</small>}</div>
          })}</div>}
        </article> })}
      </section>
    </>
  )
}
