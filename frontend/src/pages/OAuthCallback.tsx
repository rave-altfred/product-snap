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
      console.log('[OAuthCallback] Starting callback handler')
      const accessToken = searchParams.get('access_token')
      const refreshToken = searchParams.get('refresh_token')
      const error = searchParams.get('error')
      
      console.log('[OAuthCallback] Query params:', { 
        hasAccessToken: !!accessToken, 
        hasRefreshToken: !!refreshToken, 
        error 
      })

      // Check if we're in a popup window
      const isPopup = window.opener && window.opener !== window
      console.log('[OAuthCallback] isPopup:', isPopup)

      if (error) {
        console.error('OAuth error:', error)
        if (isPopup && window.opener) {
          // Send error to parent window
          window.opener.postMessage(
            { type: 'OAUTH_ERROR', error },
            window.location.origin
          )
          window.close()
        } else {
          navigate('/login?error=' + error)
        }
        return
      }

      if (!accessToken || !refreshToken) {
        if (isPopup && window.opener) {
          window.opener.postMessage(
            { type: 'OAUTH_ERROR', error: 'Missing tokens' },
            window.location.origin
          )
          window.close()
        } else {
          navigate('/login?error=missing_tokens')
        }
        return
      }

      if (isPopup && window.opener) {
        // Send tokens to parent window via postMessage
        window.opener.postMessage(
          {
            type: 'OAUTH_SUCCESS',
            access_token: accessToken,
            refresh_token: refreshToken,
          },
          window.location.origin
        )
        // Close the popup
        window.close()
      } else {
        // Fallback: traditional redirect flow (if not in popup)
        console.log('[OAuthCallback] Using fallback redirect flow')
        try {
          // Store tokens first so userApi.getMe() can use them
          console.log('[OAuthCallback] Storing tokens in localStorage')
          localStorage.setItem('access_token', accessToken)
          localStorage.setItem('refresh_token', refreshToken)

          // Get user data
          console.log('[OAuthCallback] Fetching user data')
          const { data: userData } = await userApi.getMe()
          console.log('[OAuthCallback] Got user data:', { email: userData.email })

          // Update auth store
          console.log('[OAuthCallback] Updating auth store')
          login(accessToken, refreshToken, userData)

          // Redirect to dashboard
          console.log('[OAuthCallback] Navigating to /dashboard')
          navigate('/dashboard')
        } catch (err) {
          console.error('[OAuthCallback] Failed to complete OAuth login:', err)
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          navigate('/login?error=auth_failed')
        }
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
