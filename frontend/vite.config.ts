import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '')

  return {
    // GitHub Pages publica o app em subcaminho; o CI define VITE_BASE.
    base: env.VITE_BASE || '/',
    plugins: [react()],
    server: {
      port: 5173,
      host: '0.0.0.0',
    },
  }
})
