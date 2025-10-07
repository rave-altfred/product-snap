import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { userApi } from '../lib/api'
import { useAuthStore } from '../store/authStore'

export default function OAuthCallback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { login } = useAuthStore()

  useEffect(() => {
    const handleCallback = async () => {
      const accessToken = searchParams.get('access_token')
      const refreshToken = searchParams.get('refresh_token')
      const error = searchParams.get('error')

      if (error) {
        console.error('OAuth error:', error)
        navigate('/login?error=' + error)
        return
      }

      if (!accessToken || !refreshToken) {
        navigate('/login?error=missing_tokens')
        return
      }

      try {
        // Store tokens first so userApi.getMe() can use them
        localStorage.setItem('access_token', accessToken)
        localStorage.setItem('refresh_token', refreshToken)

        // Get user data
        const { data: userData } = await userApi.getMe()

        // Update auth store
        login(accessToken, refreshToken, userData)

        // Redirect to dashboard
        navigate('/dashboard')
      } catch (err) {
        console.error('Failed to complete OAuth login:', err)
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        navigate('/login?error=auth_failed')
      }
    }

    handleCallback()
  }, [searchParams, navigate, login])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
        <p className="text-gray-600 dark:text-gray-400">Completing sign in...</p>
      </div>
    </div>
  )
}
