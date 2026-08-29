export function formatDate(value: string | null | undefined, options?: Intl.DateTimeFormatOptions) {
  if (!value) return 'A definir'
  return new Intl.DateTimeFormat('pt-BR', options ?? { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(value))
}

export function formatMatchDate(value: string | null | undefined) {
  if (!value) return 'Data a confirmar'
  return new Intl.DateTimeFormat('pt-BR', { weekday: 'short', day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }).format(new Date(value))
}

export function formatToday() {
  const value = new Intl.DateTimeFormat('pt-BR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(new Date())
  return value.charAt(0).toUpperCase() + value.slice(1)
}

export function percent(value: number) {
  return `${Math.round(value * 100)}%`
}

export function initials(name: string) {
  return name.split(/\s+/).map((part) => part[0]).join('').slice(0, 2).toUpperCase()
}
