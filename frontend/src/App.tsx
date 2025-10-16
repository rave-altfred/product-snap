import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'
import VerifyEmail from './pages/VerifyEmail'
import OAuthCallback from './pages/OAuthCallback'
import Dashboard from './pages/Dashboard'
import NewShoot from './pages/NewShoot'
import Library from './pages/Library'
import Billing from './pages/Billing'
import Account from './pages/Account'
import Terms from './pages/Terms'
import Privacy from './pages/Privacy'
import Branding from './pages/Branding'
import Contact from './pages/Contact'
import Layout from './components/Layout'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, logout, _hasHydrated } = useAuthStore()
  
  console.log('[ProtectedRoute] isAuthenticated:', isAuthenticated, ', hasHydrated:', _hasHydrated)
  
  // Check if we actually have valid tokens
  const hasTokens = localStorage.getItem('access_token') && localStorage.getItem('refresh_token')
  console.log('[ProtectedRoute] hasTokens:', !!hasTokens)
  
  // If store hasn't hydrated yet, show loading or wait
  if (!_hasHydrated) {
    console.log('[ProtectedRoute] Waiting for store to hydrate...')
    // Check tokens directly while waiting for hydration
    return hasTokens ? <>{children}</> : <Navigate to="/login" replace />
  }
  
  // If state says authenticated but no tokens, clear the state
  if (isAuthenticated && !hasTokens) {
    console.log('[ProtectedRoute] Clearing stale auth state')
    logout()
    return <Navigate to="/login" replace />
  }
  
  const shouldRender = isAuthenticated && hasTokens
  console.log('[ProtectedRoute] shouldRender:', shouldRender)
  
  return shouldRender ? <>{children}</> : <Navigate to="/login" replace />
}

function App() {
  console.log('[App] Rendering App component')
  
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route path="/verify-email" element={<VerifyEmail />} />
      <Route path="/auth/callback" element={<OAuthCallback />} />
      <Route path="/terms" element={<Terms />} />
      <Route path="/privacy" element={<Privacy />} />
      <Route path="/branding" element={<Branding />} />
      
      <Route element={<Layout />}>
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/new-shoot"
          element={
            <ProtectedRoute>
              <NewShoot />
            </ProtectedRoute>
          }
        />
        <Route
          path="/library"
          element={
            <ProtectedRoute>
              <Library />
            </ProtectedRoute>
          }
        />
        <Route
          path="/billing"
          element={
            <ProtectedRoute>
              <Billing />
            </ProtectedRoute>
          }
        />
        <Route
          path="/account"
          element={
            <ProtectedRoute>
              <Account />
            </ProtectedRoute>
          }
        />
        <Route
          path="/contact"
          element={
            <ProtectedRoute>
              <Contact />
            </ProtectedRoute>
          }
        />
      </Route>
    </Routes>
  )
}

export default App
