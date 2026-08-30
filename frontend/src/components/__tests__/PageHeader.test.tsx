import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { PageHeader } from '../PageHeader'

describe('PageHeader', () => {
  it('renders title', () => {
    render(<PageHeader title="Times" />)
    expect(screen.getByRole('heading', { name: 'Times' })).toBeInTheDocument()
  })

  it('renders eyebrow when provided', () => {
    render(<PageHeader eyebrow="Geral" title="Times" />)
    expect(screen.getByText('Geral')).toBeInTheDocument()
  })

  it('renders description when provided', () => {
    render(<PageHeader title="Times" description="Lista de todos os times" />)
    expect(screen.getByText('Lista de todos os times')).toBeInTheDocument()
  })

  it('does not render eyebrow when not provided', () => {
    render(<PageHeader title="Times" />)
    expect(screen.queryByText('Geral')).not.toBeInTheDocument()
  })

  it('renders action when provided', () => {
    render(<PageHeader title="Times" action={<button>Adicionar</button>} />)
    expect(screen.getByRole('button', { name: 'Adicionar' })).toBeInTheDocument()
  })
})
