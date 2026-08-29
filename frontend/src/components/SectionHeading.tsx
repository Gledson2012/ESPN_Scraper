import { ArrowUpRight } from 'lucide-react'
import { Link } from 'react-router-dom'

interface SectionHeadingProps {
  title: string
  description?: string
  to?: string
  actionLabel?: string
}

export function SectionHeading({ title, description, to, actionLabel = 'Ver tudo' }: SectionHeadingProps) {
  return (
    <div className="section-heading">
      <div><h2>{title}</h2>{description && <p>{description}</p>}</div>
      {to && <Link className="text-link" to={to}>{actionLabel}<ArrowUpRight size={15} /></Link>}
    </div>
  )
}
