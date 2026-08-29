export function LoadingState({ label = 'Carregando dados...' }: { label?: string }) {
  return <div className="loading-state"><span className="spinner" />{label}</div>
}
