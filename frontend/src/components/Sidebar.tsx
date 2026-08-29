import { BarChart3, CircleDollarSign, LayoutDashboard, Shield, Sparkles, Trophy, Users } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const navigation = [
  { label: 'Visão geral', to: '/', icon: LayoutDashboard, end: true },
  { label: 'Partidas', to: '/partidas', icon: Trophy },
  { label: 'Times', to: '/times', icon: Shield },
  { label: 'Jogadores', to: '/jogadores', icon: Users },
  { label: 'Previsões', to: '/previsoes', icon: Sparkles },
  { label: 'Odds', to: '/odds', icon: CircleDollarSign },
]

interface SidebarProps {
  mobileOpen: boolean
  onClose: () => void
}

export function Sidebar({ mobileOpen, onClose }: SidebarProps) {
  return (
    <aside className={`sidebar${mobileOpen ? ' mobile-open' : ''}`}>
      <div className="brand">
        <div className="brand-mark"><BarChart3 size={22} strokeWidth={2.5} /></div>
        <div>
          <strong>Scoutly</strong>
          <span>Football intelligence</span>
        </div>
      </div>

      <div className="sidebar-section-label">Navegação</div>
      <nav className="main-nav" aria-label="Navegação principal">
        {navigation.map(({ label, to, icon: Icon, end }) => (
          <NavLink
            className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
            end={end}
            key={to}
            to={to}
            onClick={onClose}
          >
            <Icon size={18} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="data-status">
          <span className="status-dot" />
          <div>
            <strong>Snapshot real ativo</strong>
            <span>5 jogos · 27 ago 2026</span>
          </div>
        </div>
        <span className="sidebar-version">Scoutly v0.1.0</span>
      </div>
    </aside>
  )
}
