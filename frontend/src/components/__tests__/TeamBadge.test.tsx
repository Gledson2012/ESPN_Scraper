import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { TeamBadge } from '../TeamBadge'

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <MemoryRouter>{children}</MemoryRouter>
)

describe('TeamBadge', () => {
  it('renders first letter from shortName', () => {
    const { container } = render(<TeamBadge name="Flamengo" shortName="FLA" />, { wrapper })
    const badge = container.querySelector('.team-badge')
    expect(badge).toHaveTextContent('F')
  })

  it('falls back to name initials when shortName is not provided', () => {
    const { container } = render(<TeamBadge name="Palmeiras" />, { wrapper })
    const badge = container.querySelector('.team-badge')
    expect(badge).toHaveTextContent('P')
  })

  it('renders logo when provided', () => {
    const { container } = render(<TeamBadge name="Flamengo" shortName="FLA" logo="https://example.com/logo.png" />, { wrapper })
    const img = container.querySelector('img')
    expect(img).toHaveAttribute('src', 'https://example.com/logo.png')
  })

  it('does not render img when logo is not provided', () => {
    render(<TeamBadge name="Flamengo" shortName="FLA" />, { wrapper })
    expect(screen.queryByRole('img')).not.toBeInTheDocument()
  })

  it('applies custom color as CSS variable', () => {
    const { container } = render(
      <TeamBadge name="Flamengo" shortName="FLA" color="#ff0000" />,
      { wrapper }
    )
    const badge = container.querySelector('.team-badge')
    expect(badge).toHaveStyle({ '--badge-color': '#ff0000' })
  })

  it('has title attribute with full name', () => {
    render(<TeamBadge name="Flamengo" shortName="FLA" />, { wrapper })
    expect(screen.getByTitle('Flamengo')).toBeInTheDocument()
  })
})
