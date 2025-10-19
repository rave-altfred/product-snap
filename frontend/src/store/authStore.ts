import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import posthog from 'posthog-js'

interface User {
  id: string
  email: string
  full_name?: string
  avatar_url?: string
  is_admin: boolean
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  _hasHydrated: boolean
  setUser: (user: User | null) => void
  login: (accessToken: string, refreshToken: string, user: User) => void
  logout: () => void
  setHasHydrated: (state: boolean) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      _hasHydrated: false,
      
      setUser: (user) => 
        set({ user, isAuthenticated: !!user }),
      
      login: (accessToken, refreshToken, user) => {
        localStorage.setItem('access_token', accessToken)
        localStorage.setItem('refresh_token', refreshToken)
        set({ user, isAuthenticated: true })
        
        // Identify user in PostHog
        if (import.meta.env.VITE_POSTHOG_API_KEY) {
          posthog.identify(user.id, {
            email: user.email,
            name: user.full_name,
            is_admin: user.is_admin,
          })
        }
      },
      
      logout: () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        set({ user: null, isAuthenticated: false })
        
        // Reset PostHog user
        if (import.meta.env.VITE_POSTHOG_API_KEY) {
          posthog.reset()
        }
      },
      
      setHasHydrated: (state) => {
        set({ _hasHydrated: state })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true)
      },
    }
  )
)
