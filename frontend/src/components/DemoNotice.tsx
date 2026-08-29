import { ExternalLink, Radio } from 'lucide-react'
import { DEMO_DATA_AS_OF, DEMO_DATA_SOURCE_URL } from '../data/mockData'

export function DemoNotice() {
  return <div className="demo-notice">
    <span className="demo-notice-icon"><Radio size={16} /></span>
    <span className="demo-notice-copy"><strong>Agenda real em modo snapshot</strong><span>Partidas consultadas em {DEMO_DATA_AS_OF}. Sincronize a API para receber atualizações automáticas.</span></span>
    <a className="demo-source" href={DEMO_DATA_SOURCE_URL} target="_blank" rel="noreferrer">Abrir fonte <ExternalLink size={13} /></a>
  </div>
}
