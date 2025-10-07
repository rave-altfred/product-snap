import { Link } from 'react-router-dom'
import { Camera, FolderOpen, Zap, Image as ImageIcon } from 'lucide-react'

export default function Dashboard() {
  return (
    <div className="p-4 sm:p-6 lg:p-8 animate-fade-in">
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
        <div className="stat-card">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold text-gray-600 dark:text-gray-400">SHOTS TODAY</span>
            <Zap className="text-primary-600" size={20} />
          </div>
          <p className="text-3xl font-bold">0 / 5</p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Free tier limit</p>
        </div>
        
        <div className="stat-card">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold text-gray-600 dark:text-gray-400">TOTAL SHOTS</span>
            <ImageIcon className="text-primary-600" size={20} />
          </div>
          <p className="text-3xl font-bold">0</p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">All time</p>
        </div>
        
        <div className="stat-card">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold text-gray-600 dark:text-gray-400">PLAN</span>
            <Camera className="text-primary-600" size={20} />
          </div>
          <p className="text-3xl font-bold">Free</p>
          <Link to="/billing" className="text-xs text-primary-600 hover:text-primary-700 mt-1 inline-block">Upgrade →</Link>
        </div>
      </div>
    </div>
  )
}
