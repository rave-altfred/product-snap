import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import posthog from 'posthog-js'
import App from './App'
import './index.css'
import { useThemeStore, applyTheme } from './store/themeStore'

console.log('[main.tsx] Starting app initialization')

// Initialize PostHog
if (import.meta.env.VITE_POSTHOG_API_KEY) {
  posthog.init(import.meta.env.VITE_POSTHOG_API_KEY, {
    api_host: import.meta.env.VITE_POSTHOG_HOST || 'https://eu.i.posthog.com',
    person_profiles: 'identified_only', // Only track identified users
    capture_pageview: true,
    capture_pageleave: true,
  })
  console.log('[main.tsx] PostHog initialized')
}

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
