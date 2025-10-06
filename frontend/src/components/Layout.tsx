import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { LogOut, Camera, FolderOpen, CreditCard, User, Home } from 'lucide-react'

export default function Layout() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()
  
  const isActive = (path: string) => location.pathname === path

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200">
        <div className="p-6">
          <Link to="/dashboard" className="block">
            <h1 className="text-2xl font-bold text-primary-600 hover:text-primary-700 transition-colors">ProductSnap</h1>
          </Link>
        </div>
        
        <nav className="px-4 space-y-2">
          <Link
            to="/dashboard"
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              isActive('/dashboard') 
                ? 'bg-primary-100 text-primary-700' 
                : 'hover:bg-gray-100'
            }`}
          >
            <Home size={20} />
            <span>Dashboard</span>
          </Link>
          
          <Link
            to="/new-shoot"
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              isActive('/new-shoot') 
                ? 'bg-primary-100 text-primary-700' 
                : 'hover:bg-gray-100'
            }`}
          >
            <Camera size={20} />
            <span>New Shoot</span>
          </Link>
          
          <Link
            to="/library"
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              isActive('/library') 
                ? 'bg-primary-100 text-primary-700' 
                : 'hover:bg-gray-100'
            }`}
          >
            <FolderOpen size={20} />
            <span>Library</span>
          </Link>
          
          <Link
            to="/billing"
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              isActive('/billing') 
                ? 'bg-primary-100 text-primary-700' 
                : 'hover:bg-gray-100'
            }`}
          >
            <CreditCard size={20} />
            <span>Billing</span>
          </Link>
          
          <Link
            to="/account"
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              isActive('/account') 
                ? 'bg-primary-100 text-primary-700' 
                : 'hover:bg-gray-100'
            }`}
          >
            <User size={20} />
            <span>Account</span>
          </Link>
        </nav>

        <div className="absolute bottom-0 w-64 p-4 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">{user?.email}</p>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="Logout"
            >
              <LogOut size={20} />
            </button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  )
}
