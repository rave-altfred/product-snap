import { useState } from 'react'
import { Link } from 'react-router-dom'
import { authApi } from '../lib/api'
import Footer from '../components/Footer'
import logo from '../assets/lightclick-logo-noborder.png'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess(false)
    setLoading(true)

    try {
      await authApi.forgotPassword(email)
      setSuccess(true)
      setEmail('')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send reset email')
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
          <h2 className="text-2xl sm:text-3xl font-bold text-center mb-4">Forgot Password?</h2>
          <p className="text-center text-gray-600 dark:text-gray-400 mb-6 sm:mb-8">
            Enter your email address and we'll send you a link to reset your password.
          </p>

          {success && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
              If that email exists in our system, a password reset link has been sent.
            </div>
          )}

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
            <div>
              <label className="block text-sm font-medium mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input text-base"
                placeholder="your@email.com"
                required
                disabled={loading}
              />
            </div>

            <button 
              type="submit" 
              className="btn btn-primary w-full py-3" 
              disabled={loading}
            >
              {loading ? 'Sending...' : 'Send Reset Link'}
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
