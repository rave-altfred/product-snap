import { Link } from 'react-router-dom'
import { Camera, Sparkles, Zap } from 'lucide-react'

export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white">
      {/* Header */}
      <header className="container mx-auto px-6 py-6 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-primary-600">ProductSnap</h1>
        <div className="space-x-4">
          <Link to="/login" className="btn btn-secondary">
            Login
          </Link>
          <Link to="/register" className="btn btn-primary">
            Get Started
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="container mx-auto px-6 py-20 text-center">
        <h1 className="text-5xl font-bold mb-6">
          Transform Your Product Photos<br />
          <span className="text-primary-600">Into Professional Shots</span>
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          AI-powered product photography. Studio white backgrounds, model try-ons, 
          and lifestyle scenes—all from a single photo.
        </p>
        <Link to="/register" className="btn btn-primary text-lg px-8 py-3">
          Start Free Trial
        </Link>
      </section>

      {/* Features */}
      <section className="container mx-auto px-6 py-20">
        <div className="grid md:grid-cols-3 gap-8">
          <div className="card text-center">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Camera className="text-primary-600" size={32} />
            </div>
            <h3 className="text-xl font-bold mb-2">Studio White</h3>
            <p className="text-gray-600">
              Crisp, professional product shots on pure white backgrounds
            </p>
          </div>

          <div className="card text-center">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Sparkles className="text-primary-600" size={32} />
            </div>
            <h3 className="text-xl font-bold mb-2">Model Try-On</h3>
            <p className="text-gray-600">
              See your products on realistic models naturally
            </p>
          </div>

          <div className="card text-center">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Zap className="text-primary-600" size={32} />
            </div>
            <h3 className="text-xl font-bold mb-2">Lifestyle Scenes</h3>
            <p className="text-gray-600">
              Place products in authentic, photorealistic environments
            </p>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="container mx-auto px-6 py-20">
        <h2 className="text-3xl font-bold text-center mb-12">Simple, Transparent Pricing</h2>
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <div className="card">
            <h3 className="text-xl font-bold mb-2">Free</h3>
            <p className="text-3xl font-bold mb-4">$0<span className="text-sm text-gray-600">/month</span></p>
            <ul className="space-y-2 mb-6">
              <li>✓ 5 shots per day</li>
              <li>✓ All modes</li>
              <li>✓ Watermarked outputs</li>
            </ul>
            <Link to="/register" className="btn btn-secondary w-full">Start Free</Link>
          </div>

          <div className="card border-2 border-primary-500">
            <h3 className="text-xl font-bold mb-2">Personal</h3>
            <p className="text-3xl font-bold mb-4">$29<span className="text-sm text-gray-600">/month</span></p>
            <ul className="space-y-2 mb-6">
              <li>✓ 100 shots per month</li>
              <li>✓ All modes</li>
              <li>✓ No watermarks</li>
              <li>✓ Priority support</li>
            </ul>
            <Link to="/register" className="btn btn-primary w-full">Get Started</Link>
          </div>

          <div className="card">
            <h3 className="text-xl font-bold mb-2">Pro</h3>
            <p className="text-3xl font-bold mb-4">$99<span className="text-sm text-gray-600">/month</span></p>
            <ul className="space-y-2 mb-6">
              <li>✓ 1000 shots per month</li>
              <li>✓ All modes</li>
              <li>✓ No watermarks</li>
              <li>✓ Priority queue</li>
              <li>✓ Custom prompts</li>
            </ul>
            <Link to="/register" className="btn btn-primary w-full">Get Started</Link>
          </div>
        </div>
      </section>
    </div>
  )
}
