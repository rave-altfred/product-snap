import { Link } from 'react-router-dom'
import { Camera, FolderOpen } from 'lucide-react'

export default function Dashboard() {
  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <h1 className="text-2xl sm:text-3xl font-bold mb-6 sm:mb-8">Dashboard</h1>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6 max-w-4xl">
        <Link to="/new-shoot" className="card hover:shadow-lg transition-shadow">
          <div className="flex items-center gap-3 sm:gap-4">
            <div className="w-12 h-12 sm:w-16 sm:h-16 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
              <Camera className="text-primary-600" size={24} />
            </div>
            <div className="min-w-0">
              <h2 className="text-lg sm:text-xl font-bold">New Shoot</h2>
              <p className="text-sm sm:text-base text-gray-600">Create a new product shot</p>
            </div>
          </div>
        </Link>

        <Link to="/library" className="card hover:shadow-lg transition-shadow">
          <div className="flex items-center gap-3 sm:gap-4">
            <div className="w-12 h-12 sm:w-16 sm:h-16 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
              <FolderOpen className="text-primary-600" size={24} />
            </div>
            <div className="min-w-0">
              <h2 className="text-lg sm:text-xl font-bold">Library</h2>
              <p className="text-sm sm:text-base text-gray-600">View your generated images</p>
            </div>
          </div>
        </Link>
      </div>
    </div>
  )
}
