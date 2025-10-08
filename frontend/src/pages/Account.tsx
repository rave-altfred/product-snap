import { useState, useEffect } from 'react'
import { User, Mail, Calendar, Key, LogOut, AlertCircle, Check } from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import { api } from '../lib/api'

interface UserProfile {
  id: string
  email: string
  full_name: string | null
  created_at: string
  oauth_provider: string | null
}

export default function Account() {
  const { user, logout } = useAuthStore()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  
  // Form states
  const [fullName, setFullName] = useState('')
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [updating, setUpdating] = useState(false)

  useEffect(() => {
    fetchProfile()
  }, [])

  const fetchProfile = async () => {
    try {
      setLoading(true)
      const data = await api.get('/users/me')
      setProfile(data)
      setFullName(data.full_name || '')
    } catch (err: any) {
      setError(err.message || 'Failed to load profile')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setUpdating(true)
      setError(null)
      setSuccess(null)
      
      await api.put('/users/me', { full_name: fullName })
      setSuccess('Profile updated successfully')
      await fetchProfile()
    } catch (err: any) {
      setError(err.message || 'Failed to update profile')
    } finally {
      setUpdating(false)
    }
  }

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (newPassword !== confirmPassword) {
      setError('New passwords do not match')
      return
    }
    
    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters long')
      return
    }

    try {
      setUpdating(true)
      setError(null)
      setSuccess(null)
      
      await api.post('/users/change-password', {
        current_password: currentPassword,
        new_password: newPassword
      })
      
      setSuccess('Password changed successfully')
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (err: any) {
      setError(err.message || 'Failed to change password')
    } finally {
      setUpdating(false)
    }
  }

  const handleLogout = () => {
    if (confirm('Are you sure you want to logout?')) {
      logout()
    }
  }

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-8"></div>
          <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded mb-4"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-2">Account Settings</h1>
      <p className="text-gray-600 dark:text-gray-400 mb-8">Manage your profile and account preferences</p>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6 flex items-start gap-3">
          <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
          <div>
            <h3 className="font-semibold text-red-900 dark:text-red-200">Error</h3>
            <p className="text-red-700 dark:text-red-300 text-sm">{error}</p>
          </div>
        </div>
      )}

      {success && (
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 mb-6 flex items-start gap-3">
          <Check className="text-green-600 flex-shrink-0 mt-0.5" size={20} />
          <div>
            <h3 className="font-semibold text-green-900 dark:text-green-200">Success</h3>
            <p className="text-green-700 dark:text-green-300 text-sm">{success}</p>
          </div>
        </div>
      )}

      {/* Profile Information */}
      <div className="card mb-6">
        <h2 className="text-xl font-bold mb-6">Profile Information</h2>
        
        <div className="flex items-center gap-4 mb-6 pb-6 border-b border-gray-200 dark:border-gray-700">
          <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
            <User className="text-primary-600 dark:text-primary-400" size={32} />
          </div>
          <div>
            <h3 className="font-bold text-lg">{profile?.full_name || 'No name set'}</h3>
            <p className="text-gray-600 dark:text-gray-400 flex items-center gap-2">
              <Mail size={14} />
              {profile?.email}
            </p>
            {profile?.oauth_provider && (
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Signed in with {profile.oauth_provider}
              </p>
            )}
          </div>
        </div>

        <form onSubmit={handleUpdateProfile}>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Full Name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="input w-full"
              placeholder="Enter your full name"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Email Address</label>
            <input
              type="email"
              value={profile?.email || ''}
              disabled
              className="input w-full bg-gray-100 dark:bg-gray-800 cursor-not-allowed"
            />
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Email cannot be changed
            </p>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Member Since</label>
            <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
              <Calendar size={16} />
              {profile?.created_at && new Date(profile.created_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </div>
          </div>

          <button
            type="submit"
            disabled={updating}
            className="btn btn-primary"
          >
            {updating ? 'Updating...' : 'Update Profile'}
          </button>
        </form>
      </div>

      {/* Change Password */}
      {!profile?.oauth_provider && (
        <div className="card mb-6">
          <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
            <Key size={20} />
            Change Password
          </h2>

          <form onSubmit={handleChangePassword}>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Current Password</label>
              <input
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                className="input w-full"
                placeholder="Enter current password"
                required
              />
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">New Password</label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="input w-full"
                placeholder="Enter new password"
                required
                minLength={8}
              />
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Must be at least 8 characters long
              </p>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Confirm New Password</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="input w-full"
                placeholder="Confirm new password"
                required
              />
            </div>

            <button
              type="submit"
              disabled={updating}
              className="btn btn-primary"
            >
              {updating ? 'Changing...' : 'Change Password'}
            </button>
          </form>
        </div>
      )}

      {/* Danger Zone */}
      <div className="card border-2 border-red-200 dark:border-red-800">
        <h2 className="text-xl font-bold mb-4 text-red-600 dark:text-red-400">Danger Zone</h2>
        
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold mb-1">Logout</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Sign out of your account on this device
            </p>
          </div>
          <button
            onClick={handleLogout}
            className="btn btn-secondary text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 flex items-center gap-2"
          >
            <LogOut size={16} />
            Logout
          </button>
        </div>
      </div>
    </div>
  )
}
