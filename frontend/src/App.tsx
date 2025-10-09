import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import OAuthCallback from './pages/OAuthCallback'
import Dashboard from './pages/Dashboard'
import NewShoot from './pages/NewShoot'
import Library from './pages/Library'
import Billing from './pages/Billing'
import Account from './pages/Account'
import Layout from './components/Layout'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, logout } = useAuthStore()
  
  console.log('[ProtectedRoute] isAuthenticated:', isAuthenticated)
  
  // Check if we actually have valid tokens
  const hasTokens = localStorage.getItem('access_token') && localStorage.getItem('refresh_token')
  console.log('[ProtectedRoute] hasTokens:', !!hasTokens)
  
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
      <Route path="/auth/callback" element={<OAuthCallback />} />
      
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
      </Route>
    </Routes>
  )
}

export default App
