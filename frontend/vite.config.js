// frontend/vite.config.js
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  // Load the correct .env file (dev / prod)
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react()],

    // Development server options
    server: {
      port: 3000,               // React dev server
      proxy: {
        // Forward any /api requests to Django on port 8001
        '/api': {
          target: 'http://localhost:8001',
          changeOrigin: true,
          secure: false,
        },
      },
    },

    // Optional: expose env variables to your React code
    define: {
      __API_URL__: JSON.stringify(env.VITE_API_URL || 'http://localhost:8001/api'),
    },
  }
})