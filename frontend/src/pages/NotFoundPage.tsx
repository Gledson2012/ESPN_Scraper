import { ArrowLeft } from 'lucide-react'
import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return <div className="not-found"><span className="not-found-code">404</span><h1>Página não encontrada</h1><p>O caminho que você acessou não existe neste painel.</p><Link className="button primary" to="/"><ArrowLeft size={16} /> Voltar ao início</Link></div>
}
