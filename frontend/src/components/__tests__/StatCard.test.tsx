import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Shield } from 'lucide-react'
import { StatCard } from '../StatCard'

describe('StatCard', () => {
  it('renders label, value, and note', () => {
    render(<StatCard label="Times" value={10} note="cadastrados" icon={Shield} />)
    expect(screen.getByText('Times')).toBeInTheDocument()
    expect(screen.getByText('10')).toBeInTheDocument()
    expect(screen.getByText('cadastrados')).toBeInTheDocument()
  })

  it('renders string values', () => {
    render(<StatCard label="Status" value="Ativo" note="sistema" icon={Shield} />)
    expect(screen.getByText('Ativo')).toBeInTheDocument()
  })

  it('applies default green tone', () => {
    const { container } = render(
      <StatCard label="Test" value={1} note="note" icon={Shield} />
    )
    const icon = container.querySelector('.stat-icon')
    expect(icon).toHaveClass('green')
  })

  it('applies custom tone', () => {
    const { container } = render(
      <StatCard label="Test" value={1} note="note" icon={Shield} tone="blue" />
    )
    const icon = container.querySelector('.stat-icon')
    expect(icon).toHaveClass('blue')
  })
})
