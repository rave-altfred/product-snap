import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { userApi } from '../lib/api'
import { useAuthStore } from '../store/authStore'

export default function AuthCallback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { login } = useAuthStore()

  useEffect(() => {
    const handleOAuthCallback = async () => {
      try {
        // Get tokens from URL parameters
        const accessToken = searchParams.get('access_token')
        const refreshToken = searchParams.get('refresh_token')
        const error = searchParams.get('error')

        if (error) {
          // Handle OAuth error
          console.error('OAuth error:', error)
          
          // Get the return URL from sessionStorage to redirect back
          const returnUrl = sessionStorage.getItem('oauth_return_url') || '/login'
          sessionStorage.removeItem('oauth_return_url')
          
          // Redirect back to login/register with error
          let errorMessage = 'Authentication failed'
          if (error === 'invalid_state') {
            errorMessage = 'Security check failed. Please try again.'
          } else if (error === 'oauth_failed') {
            errorMessage = 'Google authentication failed. Please try again.'
          }
          
          navigate(`${returnUrl}?error=${encodeURIComponent(errorMessage)}`)
          return
        }

        if (!accessToken || !refreshToken) {
          console.error('Missing tokens in OAuth callback')
          const returnUrl = sessionStorage.getItem('oauth_return_url') || '/login'
          sessionStorage.removeItem('oauth_return_url')
          navigate(`${returnUrl}?error=${encodeURIComponent('Authentication failed. Missing tokens.')}`)
          return
        }

        // Store tokens and get user data
        localStorage.setItem('access_token', accessToken)
        localStorage.setItem('refresh_token', refreshToken)
        
        const { data: userData } = await userApi.getMe()
        
        // Complete login
        login(accessToken, refreshToken, userData)
        
        // Clean up sessionStorage
        sessionStorage.removeItem('oauth_return_url')
        
        // Navigate to dashboard
        navigate('/dashboard')

      } catch (err: any) {
        console.error('OAuth callback error:', err)
        
        // Clean up tokens on error
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        
        const returnUrl = sessionStorage.getItem('oauth_return_url') || '/login'
        sessionStorage.removeItem('oauth_return_url')
        
        navigate(`${returnUrl}?error=${encodeURIComponent('Failed to complete authentication')}`)
      }
    }

    handleOAuthCallback()
  }, [searchParams, navigate, login])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="card text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-500 mx-auto mb-4"></div>
        <h2 className="text-xl font-semibold mb-2">Completing sign in...</h2>
        <p className="text-gray-600 dark:text-gray-400">Please wait while we complete your authentication.</p>
      </div>
    </div>
  )
}