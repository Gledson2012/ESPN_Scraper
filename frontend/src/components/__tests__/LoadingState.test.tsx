import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { LoadingState } from '../LoadingState'
import { EmptyState } from '../EmptyState'

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <MemoryRouter>{children}</MemoryRouter>
)

describe('LoadingState', () => {
  it('renders default label', () => {
    render(<LoadingState />)
    expect(screen.getByText('Carregando dados...')).toBeInTheDocument()
  })

  it('renders custom label', () => {
    render(<LoadingState label="Carregando times..." />)
    expect(screen.getByText('Carregando times...')).toBeInTheDocument()
  })
})

describe('EmptyState', () => {
  it('renders message', () => {
    render(<EmptyState message="Nenhum time encontrado" />, { wrapper })
    expect(screen.getByText('Nenhum time encontrado')).toBeInTheDocument()
  })

  it('renders link to home', () => {
    render(<EmptyState message="Sem dados" />, { wrapper })
    expect(screen.getByText('Voltar ao início')).toBeInTheDocument()
  })
})
