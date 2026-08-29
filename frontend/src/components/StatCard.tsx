import type { LucideIcon } from 'lucide-react'

interface StatCardProps {
  label: string
  value: string | number
  note: string
  icon: LucideIcon
  tone?: 'green' | 'blue' | 'orange' | 'purple'
}

export function StatCard({ label, value, note, icon: Icon, tone = 'green' }: StatCardProps) {
  return (
    <article className="stat-card">
      <div className={`stat-icon ${tone}`}><Icon size={19} /></div>
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
      <div className="stat-note">{note}</div>
    </article>
  )
}
