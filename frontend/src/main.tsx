import React from 'react'
import ReactDOM from 'react-dom/client'
import { HashRouter } from 'react-router-dom'
import App from './App'
import './styles/index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {/* HashRouter é mais robusto no app Android (Capacitor): as rotas ficam em
        uma única URL com '#', evitando 404/deep-links ao recarregar na WebView. */}
    <HashRouter>
      <App />
    </HashRouter>
  </React.StrictMode>,
)
