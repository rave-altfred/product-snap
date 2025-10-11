import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Camera, FolderOpen, Zap, Image as ImageIcon, Loader } from 'lucide-react'
import { userApi } from '../lib/api'

interface UserStats {
  today_usage: number
  today_limit: number | null
  current_period_usage: number
  current_period_limit: number
  period: string
  total_jobs: number
  plan: string
  plan_raw: string
  remaining_jobs: number
}

export default function Dashboard() {
  const [stats, setStats] = useState<UserStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true)
        const response = await userApi.getStats()
        setStats(response.data)
        setError(null)
      } catch (err) {
        console.error('Failed to fetch user stats:', err)
        setError('Failed to load stats')
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-4xl mx-auto animate-fade-in">
      <div className="mb-8">
        <h1 className="text-3xl sm:text-4xl font-bold mb-2 text-gradient">Welcome Back!</h1>
        <p className="text-gray-600 dark:text-gray-300">Ready to create something amazing?</p>
      </div>
      
      {/* Quick Actions */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 max-w-4xl mb-8">
        <Link to="/new-shoot" className="feature-card group">
          <div className="flex items-center gap-5">
            <div className="feature-icon flex-shrink-0">
              <Camera size={28} />
            </div>
            <div className="min-w-0">
              <h2 className="text-xl font-bold mb-1 group-hover:text-primary-600 transition-colors">New Shoot</h2>
              <p className="text-sm text-gray-600 dark:text-gray-300">Create stunning product shots with AI</p>
            </div>
          </div>
        </Link>

        <Link to="/library" className="feature-card group">
          <div className="flex items-center gap-5">
            <div className="feature-icon flex-shrink-0">
              <FolderOpen size={28} />
            </div>
            <div className="min-w-0">
              <h2 className="text-xl font-bold mb-1 group-hover:text-primary-600 transition-colors">Library</h2>
              <p className="text-sm text-gray-600 dark:text-gray-300">Browse your generated images</p>
            </div>
          </div>
        </Link>
      </div>
      
      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-4xl">
        {loading ? (
          // Loading state
          Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="stat-card">
              <div className="flex items-center justify-center h-20">
                <Loader className="animate-spin text-primary-600" size={24} />
              </div>
            </div>
          ))
        ) : error ? (
          // Error state
          <div className="col-span-3 stat-card">
            <div className="text-center text-red-600">
              <p>{error}</p>
              <button 
                onClick={() => window.location.reload()} 
                className="text-sm text-primary-600 hover:text-primary-700 mt-2"
              >
                Retry
              </button>
            </div>
          </div>
        ) : stats ? (
          // Real data
          <>
            <div className="stat-card">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-gray-600 dark:text-gray-400">
                  {stats.period === 'day' ? 'SHOTS TODAY' : 'SHOTS THIS MONTH'}
                </span>
                <Zap className="text-primary-600" size={20} />
              </div>
              <p className="text-3xl font-bold">
                {stats.period === 'day' && stats.today_limit
                  ? `${stats.today_usage} / ${stats.today_limit}`
                  : `${stats.current_period_usage} / ${stats.current_period_limit}`
                }
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {stats.remaining_jobs} remaining this {stats.period}
              </p>
            </div>
            
            <div className="stat-card">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-gray-600 dark:text-gray-400">TOTAL SHOTS</span>
                <ImageIcon className="text-primary-600" size={20} />
              </div>
              <p className="text-3xl font-bold">{stats.total_jobs}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">All time</p>
            </div>
            
            <div className="stat-card">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-gray-600 dark:text-gray-400">PLAN</span>
                <Camera className="text-primary-600" size={20} />
              </div>
              <p className="text-3xl font-bold">{stats.plan}</p>
              {stats.plan === 'Free' ? (
                <Link to="/billing" className="text-xs text-primary-600 hover:text-primary-700 mt-1 inline-block">Upgrade →</Link>
              ) : (
                <Link to="/billing" className="text-xs text-primary-600 hover:text-primary-700 mt-1 inline-block">Manage →</Link>
              )}
            </div>
          </>
        ) : null}
      </div>
    </div>
  )
}
