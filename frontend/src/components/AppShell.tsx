import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Topbar } from './Topbar'

export function AppShell() {
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <div className="app-shell">
      <Sidebar mobileOpen={mobileOpen} onClose={() => setMobileOpen(false)} />
      {mobileOpen && <button className="sidebar-overlay" aria-label="Fechar menu" onClick={() => setMobileOpen(false)} />}
      <main className="main-content">
        <Topbar onMenu={() => setMobileOpen(true)} />
        <div className="page-content">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
