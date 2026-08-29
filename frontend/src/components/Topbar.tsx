import { FormEvent, useState } from 'react'
import { Bell, Menu, Search } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { api } from '../lib/api'

export function Topbar({ onMenu }: { onMenu: () => void }) {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [searching, setSearching] = useState(false)

  async function handleSearch(event: FormEvent) {
    event.preventDefault()
    const value = query.trim()
    if (!value || searching) return

    setSearching(true)
    try {
      const response = await api.search(value, undefined, 1)
      navigate(response.results[0]?.path || `/partidas?search=${encodeURIComponent(value)}`)
    } catch {
      navigate(`/partidas?search=${encodeURIComponent(value)}`)
    } finally {
      setSearching(false)
    }
  }

  return (
    <header className="topbar">
      <button className="mobile-menu" aria-label="Abrir menu" onClick={onMenu}><Menu size={20} /></button>
      <div className="topbar-context"><span>SCOUTLY</span><strong>Centro de inteligência</strong></div>
      <form className="topbar-search" role="search" onSubmit={handleSearch}>
        <Search size={17} />
        <input aria-label="Buscar partidas, times ou jogadores" aria-busy={searching} value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar partidas, times ou jogadores" />
        <kbd>⌘ K</kbd>
      </form>
      <div className="topbar-actions">
        <span className="icon-button" aria-label="Notificações indisponíveis" title="Notificações indisponíveis"><Bell size={18} /></span>
        <div className="profile">
          <div className="avatar">GC</div>
          <div className="profile-copy"><strong>Gledson</strong><span>Analista</span></div>
        </div>
      </div>
    </header>
  )
}
