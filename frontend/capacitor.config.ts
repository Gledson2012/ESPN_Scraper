import type { CapacitorConfig } from '@capacitor/cli'

const config: CapacitorConfig = {
  appId: 'com.scoutly.app',
  appName: 'Scoutly',
  webDir: 'dist',
  server: {
    androidScheme: 'https',
  },
}

export default config
