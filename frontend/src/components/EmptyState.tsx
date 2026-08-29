import { AlertCircle, ArrowLeft } from 'lucide-react'
import { Link } from 'react-router-dom'

export function EmptyState({ message }: { message: string }) {
  return <div className="empty-state"><AlertCircle size={22} /><p>{message}</p><Link className="button secondary" to="/"><ArrowLeft size={15} /> Voltar ao início</Link></div>
}
