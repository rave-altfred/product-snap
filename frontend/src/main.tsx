import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'
import './index.css'
import { useThemeStore, applyTheme } from './store/themeStore'

console.log('[main.tsx] Starting app initialization')

// Initialize theme from store
const storedTheme = localStorage.getItem('theme-storage')
let theme: 'auto' | 'light' | 'dark' = 'auto'

if (storedTheme) {
  try {
    const parsed = JSON.parse(storedTheme)
    theme = parsed.state?.theme || 'auto'
  } catch (e) {
    console.error('[main.tsx] Failed to parse theme from storage', e)
  }
}

// Apply initial theme
applyTheme(theme)

// Listen for system theme changes (only when in auto mode)
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
  const currentTheme = useThemeStore.getState().theme
  if (currentTheme === 'auto') {
    applyTheme('auto')
  }
})

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

console.log('[main.tsx] QueryClient created, mounting React app')

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
