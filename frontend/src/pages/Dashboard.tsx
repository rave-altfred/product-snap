import { Link } from 'react-router-dom'
import { Camera, FolderOpen } from 'lucide-react'

export default function Dashboard() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
      
      <div className="grid md:grid-cols-2 gap-6 max-w-4xl">
        <Link to="/new-shoot" className="card hover:shadow-lg transition-shadow">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
              <Camera className="text-primary-600" size={32} />
            </div>
            <div>
              <h2 className="text-xl font-bold">New Shoot</h2>
              <p className="text-gray-600">Create a new product shot</p>
            </div>
          </div>
        </Link>

        <Link to="/library" className="card hover:shadow-lg transition-shadow">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
              <FolderOpen className="text-primary-600" size={32} />
            </div>
            <div>
              <h2 className="text-xl font-bold">Library</h2>
              <p className="text-gray-600">View your generated images</p>
            </div>
          </div>
        </Link>
      </div>
    </div>
  )
}
