import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    watch: {
      // Ignore heavy directories to reduce file watching overhead
      ignored: [
        '**/node_modules/**',
        '**/.venv/**',
        '**/backend/chroma_db/**',
        '**/generated/**',
        '**/__pycache__/**',
        '**/*.pyc',
      ],
    },
  },
})
