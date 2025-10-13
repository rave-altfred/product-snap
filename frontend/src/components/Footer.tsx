import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="mt-auto bg-gray-50 dark:bg-gray-900">
      <div className="border-t border-gray-200 dark:border-gray-700 py-6">
        <div className="container mx-auto px-8 text-center text-gray-600 dark:text-gray-400">
          <p className="text-sm mb-2">© {new Date().getFullYear()} LightClick. All rights reserved.</p>
          <div className="flex justify-center gap-4 mb-2 text-sm">
            <Link to="/terms" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">
              Terms of Service
            </Link>
            <span>•</span>
            <Link to="/privacy" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">
              Privacy Policy
            </Link>
          </div>
          <p className="text-sm">Transform your products with AI-powered photography ✨</p>
        </div>
      </div>
    </footer>
  )
}
