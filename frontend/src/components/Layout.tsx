import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom'
import { useState } from 'react'
import { useAuthStore } from '../store/authStore'
import { LogOut, Camera, FolderOpen, CreditCard, User, Home, Menu, X } from 'lucide-react'
import { version } from '../version'
import logo from '../assets/logo.png'

export default function Layout() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  
  console.log('[Layout] Rendering with user:', user)
  
  const isActive = (path: string) => location.pathname === path
  
  const closeMobileMenu = () => setIsMobileMenuOpen(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
    closeMobileMenu()
  }

  const navItems = [
    { to: '/dashboard', icon: Home, label: 'Dashboard' },
    { to: '/new-shoot', icon: Camera, label: 'New Shoot' },
    { to: '/library', icon: FolderOpen, label: 'Library' },
    { to: '/billing', icon: CreditCard, label: 'Billing' },
    { to: '/account', icon: User, label: 'Account' },
  ]

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Mobile Header */}
      <header className="lg:hidden bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
        <div className="flex items-center justify-between">
          <Link to="/dashboard" onClick={closeMobileMenu} className="flex items-center gap-2">
            <img src={logo} alt="Light Click" className="h-8 w-8" />
            <h1 className="text-xl font-bold text-primary-600 dark:text-primary-400">Light Click</h1>
          </Link>
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 transition-colors"
            aria-label="Toggle menu"
          >
            {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </header>

      <div className="flex">
        {/* Desktop Sidebar */}
        <aside className="hidden lg:flex lg:flex-col lg:w-64 lg:fixed lg:inset-y-0 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
          <div className="p-6">
            <Link to="/dashboard" className="flex items-center gap-3 group">
              <img src={logo} alt="Light Click" className="h-10 w-10 transition-transform group-hover:scale-105" />
              <h1 className="text-2xl font-bold text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 transition-colors">Light Click</h1>
            </Link>
          </div>
          
          <nav className="flex-1 px-4 space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive(item.to) 
                      ? 'bg-primary-100 dark:bg-primary-900/50 text-primary-700 dark:text-primary-300' 
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <Icon size={20} />
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </nav>

          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">{user?.full_name || user?.email}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user?.email}</p>
              </div>
              <button
                onClick={handleLogout}
                className="ml-3 p-2 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="Logout"
              >
                <LogOut size={18} />
              </button>
            </div>
            <div className="mt-2 pt-2 border-t border-gray-100 dark:border-gray-700">
              <p className="text-[10px] text-gray-400 dark:text-gray-600 text-center font-mono" title="Application Version">
                v{version}
              </p>
            </div>
          </div>
        </aside>

        {/* Mobile Menu Overlay */}
        {isMobileMenuOpen && (
          <div className="lg:hidden fixed inset-0 z-50">
            <div 
              className="fixed inset-0 bg-black bg-opacity-50" 
              onClick={closeMobileMenu}
            />
            <div className="fixed top-0 left-0 w-80 max-w-xs h-full bg-white dark:bg-gray-800 shadow-xl">
              <div className="p-6">
                <Link to="/dashboard" onClick={closeMobileMenu} className="flex items-center gap-3">
                  <img src={logo} alt="Light Click" className="h-10 w-10" />
                  <h1 className="text-2xl font-bold text-primary-600 dark:text-primary-400">Light Click</h1>
                </Link>
              </div>
              
              <nav className="px-4 space-y-2">
                {navItems.map((item) => {
                  const Icon = item.icon
                  return (
                    <Link
                      key={item.to}
                      to={item.to}
                      onClick={closeMobileMenu}
                      className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                        isActive(item.to) 
                          ? 'bg-primary-100 dark:bg-primary-900/50 text-primary-700 dark:text-primary-300' 
                          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                      }`}
                    >
                      <Icon size={20} />
                      <span>{item.label}</span>
                    </Link>
                  )
                })}
              </nav>

              <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">{user?.full_name || user?.email}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user?.email}</p>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="ml-3 p-2 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                    title="Logout"
                  >
                    <LogOut size={18} />
                  </button>
                </div>
                <div className="mt-2 pt-2 border-t border-gray-100 dark:border-gray-700">
                  <p className="text-[10px] text-gray-400 dark:text-gray-600 text-center font-mono" title="Application Version">
                    v{version}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Main content */}
        <main className="flex-1 lg:pl-64">
          <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
