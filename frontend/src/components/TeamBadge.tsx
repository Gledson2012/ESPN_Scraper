import type { CSSProperties } from 'react'

interface TeamBadgeProps {
  name: string
  shortName?: string | null
  color?: string
}

export function TeamBadge({ name, shortName, color }: TeamBadgeProps) {
  const initials = (shortName || name)
    .split(/\s+/)
    .map((part) => part[0])
    .join('')
    .slice(0, 3)
    .toUpperCase()

  return (
    <div className="team-badge" title={name} style={color ? { '--badge-color': color } as CSSProperties : undefined}>
      {initials}
    </div>
  )
}
