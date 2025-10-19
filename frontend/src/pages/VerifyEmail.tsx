import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { api } from '../lib/api'
import { useAuthStore } from '../store/authStore'

export default function VerifyEmail() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { isAuthenticated } = useAuthStore()
  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying')
  const [message, setMessage] = useState('')

  useEffect(() => {
    const token = searchParams.get('token')
    
    if (!token) {
      setStatus('error')
      setMessage('Invalid verification link. No token provided.')
      return
    }

    const verifyEmail = async () => {
      try {
        await api.get(`/api/auth/verify-email?token=${token}`)
        setStatus('success')
        
        // Redirect based on authentication status
        if (isAuthenticated) {
          setMessage('Email verified successfully! Redirecting to dashboard...')
          setTimeout(() => {
            navigate('/dashboard')
          }, 2000)
        } else {
          setMessage('Email verified successfully! Redirecting to login...')
          setTimeout(() => {
            navigate('/login')
          }, 2000)
        }
      } catch (error: any) {
        setStatus('error')
        setMessage(
          error.response?.data?.detail || 
          'Failed to verify email. The link may be expired or invalid.'
        )
      }
    }

    verifyEmail()
  }, [searchParams, navigate])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-100 via-blue-50/80 to-cyan-50/60 dark:from-gray-900 dark:via-primary-950/30 dark:to-gray-800 px-4">
      <div className="card max-w-md w-full text-center">
        {status === 'verifying' && (
          <>
            <div className="w-16 h-16 mx-auto mb-6">
              <div className="animate-spin rounded-full h-16 w-16 border-4 border-primary-200 border-t-primary-600"></div>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Verifying Your Email
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Please wait while we verify your email address...
            </p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="w-16 h-16 mx-auto mb-6 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center">
              <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Email Verified! ✓
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              {message}
            </p>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="w-16 h-16 mx-auto mb-6 bg-gradient-to-br from-red-400 to-red-600 rounded-full flex items-center justify-center">
              <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Verification Failed
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              {message}
            </p>
            <button
              onClick={() => navigate('/login')}
              className="btn btn-primary"
            >
              Go to Login
            </button>
          </>
        )}
      </div>
    </div>
  )
}
