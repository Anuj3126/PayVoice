import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig(({ mode }) => {
  // Load env file from parent directory (where consolidated .env is)
  const env = loadEnv(mode, path.resolve(__dirname, '..'), 'VITE_')
  
  return {
    plugins: [react()],
    server: {
      port: 3000,
      host: true
    },
    // Environment variables with VITE_ prefix will be available
    define: {
      // Make sure VITE_ prefixed vars are available
    }
  }
})

