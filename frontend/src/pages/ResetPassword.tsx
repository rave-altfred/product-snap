import { useState, useEffect } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { authApi } from '../lib/api'
import Footer from '../components/Footer'
import logo from '../assets/lightclick-logo-noborder.png'

export default function ResetPassword() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [token, setToken] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const tokenParam = searchParams.get('token')
    if (!tokenParam) {
      setError('Invalid or missing reset token')
    } else {
      setToken(tokenParam)
    }
  }, [searchParams])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess(false)

    // Validate passwords match
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    // Validate password length
    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters long')
      return
    }

    if (!token) {
      setError('Invalid or missing reset token')
      return
    }

    setLoading(true)

    try {
      await authApi.resetPassword(token, newPassword)
      setSuccess(true)
      // Redirect to login after 2 seconds
      setTimeout(() => {
        navigate('/login')
      }, 2000)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to reset password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="max-w-md w-full card">
          <div className="flex justify-center mb-6">
            <img 
              src={logo} 
              alt="LightClick Logo" 
              className="h-12 sm:h-16"
            />
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-center mb-4">Reset Password</h2>
          <p className="text-center text-gray-600 dark:text-gray-400 mb-6 sm:mb-8">
            Enter your new password below.
          </p>

          {success && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
              Password reset successfully! Redirecting to login...
            </div>
          )}

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
            <div>
              <label className="block text-sm font-medium mb-2">New Password</label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="input text-base"
                placeholder="Enter new password"
                required
                disabled={loading || success || !token}
                minLength={8}
              />
              <p className="text-xs text-gray-500 mt-1">Must be at least 8 characters</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Confirm Password</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="input text-base"
                placeholder="Confirm new password"
                required
                disabled={loading || success || !token}
                minLength={8}
              />
            </div>

            <button 
              type="submit" 
              className="btn btn-primary w-full py-3" 
              disabled={loading || success || !token}
            >
              {loading ? 'Resetting...' : 'Reset Password'}
            </button>
          </form>

          <p className="text-center mt-6 text-gray-600 dark:text-gray-400">
            Remember your password?{' '}
            <Link to="/login" className="text-primary-600 hover:underline">
              Back to login
            </Link>
          </p>
        </div>
      </div>
      <Footer />
    </div>
  )
}
