import { Link } from 'react-router-dom'
import { Camera, Sparkles, Zap, ArrowRight, Check } from 'lucide-react'

export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/20 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="nav-glass sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gradient">ProductSnap</h1>
          <div className="flex gap-3">
            <Link to="/login" className="btn btn-secondary text-sm">
              Login
            </Link>
            <Link to="/register" className="btn btn-primary text-sm">
              Get Started
              <ArrowRight className="inline ml-2" size={16} />
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="container mx-auto px-6 py-24 text-center animate-fade-in">
        <div className="inline-block px-4 py-2 bg-primary-100/50 dark:bg-primary-900/30 rounded-full mb-8 backdrop-blur-sm border border-primary-200 dark:border-primary-800">
          <span className="text-primary-700 dark:text-primary-300 font-semibold text-sm">✨ AI-Powered Photography Platform</span>
        </div>
        
        <h1 className="text-5xl md:text-7xl font-extrabold mb-8 leading-tight animate-slide-up">
          Transform Product Photos<br />
          <span className="text-gradient">Into Professional Shots</span>
        </h1>
        
        <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 mb-12 max-w-3xl mx-auto leading-relaxed">
          Create studio-quality product photography with AI. White backgrounds, model try-ons, 
          and lifestyle scenes in seconds.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center animate-scale-in">
          <Link to="/register" className="btn btn-primary text-lg px-10 py-4 group">
            Start Free
            <ArrowRight className="inline ml-2 group-hover:translate-x-1 transition-transform" size={20} />
          </Link>
          <Link to="#features" className="btn btn-secondary text-lg px-10 py-4">
            Learn More
          </Link>
        </div>
        
        <div className="mt-16 flex justify-center gap-8 text-sm text-gray-600 dark:text-gray-400">
          <div className="flex items-center gap-2">
            <Check className="text-success-600" size={20} />
            <span>No credit card required</span>
          </div>
          <div className="flex items-center gap-2">
            <Check className="text-success-600" size={20} />
            <span>5 free shots daily</span>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="container mx-auto px-6 py-24">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">Three Powerful Generation Modes</h2>
          <p className="text-xl text-gray-600 dark:text-gray-300">Professional results for every use case</p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8">
          <div className="feature-card text-center">
            <div className="feature-icon mx-auto mb-6">
              <Camera size={28} />
            </div>
            <h3 className="text-2xl font-bold mb-3">Studio White</h3>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
              Crisp, professional product shots on pure white backgrounds. Perfect for e-commerce.
            </p>
          </div>

          <div className="feature-card text-center">
            <div className="feature-icon mx-auto mb-6">
              <Sparkles size={28} />
            </div>
            <h3 className="text-2xl font-bold mb-3">Model Try-On</h3>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
              See your products on realistic models naturally. Bring your apparel to life.
            </p>
          </div>

          <div className="feature-card text-center">
            <div className="feature-icon mx-auto mb-6">
              <Zap size={28} />
            </div>
            <h3 className="text-2xl font-bold mb-3">Lifestyle Scenes</h3>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
              Place products in authentic, photorealistic environments. Tell your brand story.
            </p>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="container mx-auto px-6 py-24 bg-gradient-to-b from-transparent via-primary-50/30 to-transparent dark:via-primary-950/10">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">Simple, Transparent Pricing</h2>
          <p className="text-xl text-gray-600 dark:text-gray-300">Start free, upgrade as you grow</p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <div className="card-flat">
            <div className="text-sm font-semibold text-primary-600 dark:text-primary-400 mb-2">STARTER</div>
            <h3 className="text-2xl font-bold mb-4">Free</h3>
            <div className="mb-6">
              <span className="text-5xl font-extrabold">$0</span>
              <span className="text-gray-500 dark:text-gray-400 ml-2">/month</span>
            </div>
            <ul className="space-y-3 mb-8 text-gray-600 dark:text-gray-300">
              <li className="flex items-start gap-3">
                <Check className="text-success-600 flex-shrink-0 mt-0.5" size={20} />
                <span>5 shots per day</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="text-success-600 flex-shrink-0 mt-0.5" size={20} />
                <span>All three modes</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="text-success-600 flex-shrink-0 mt-0.5" size={20} />
                <span>Watermarked outputs</span>
              </li>
            </ul>
            <Link to="/register" className="btn btn-secondary w-full">Start Free</Link>
          </div>

          <div className="card border-2 border-primary-500 dark:border-primary-600 relative overflow-hidden">
            <div className="absolute top-0 right-0 bg-primary-600 text-white text-xs font-bold px-3 py-1 rounded-bl-lg">
              POPULAR
            </div>
            <div className="text-sm font-semibold text-primary-600 dark:text-primary-400 mb-2">BASIC</div>
            <h3 className="text-2xl font-bold mb-4">Basic</h3>
            <div className="mb-6">
              <span className="text-5xl font-extrabold">$9.99</span>
              <span className="text-gray-500 dark:text-gray-400 ml-2">/month</span>
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-6">
              or $99.99/year <span className="text-success-600 font-semibold">(save 17%)</span>
            </div>
            <ul className="space-y-3 mb-8 text-gray-600 dark:text-gray-300">
              <li className="flex items-start gap-3">
                <Check className="text-success-600 flex-shrink-0 mt-0.5" size={20} />
                <span>100 shots per month</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="text-success-600 flex-shrink-0 mt-0.5" size={20} />
                <span>All three modes</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="text-success-600 flex-shrink-0 mt-0.5" size={20} />
                <span>No watermarks</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="text-success-600 flex-shrink-0 mt-0.5" size={20} />
                <span>Email support</span>
              </li>
            </ul>
            <Link to="/register" className="btn btn-primary w-full">Get Started</Link>
          </div>

          <div className="card-flat">
            <div className="text-sm font-semibold text-primary-600 dark:text-primary-400 mb-2">PRO</div>
            <h3 className="text-2xl font-bold mb-4">Pro</h3>
            <div className="mb-6">
              <span className="text-5xl font-extrabold">$29.99</span>
              <span className="text-gray-500 dark:text-gray-400 ml-2">/month</span>
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-6">
              or $299.99/year <span className="text-success-600 font-semibold">(save 17%)</span>
            </div>
            <ul className="space-y-3 mb-8 text-gray-600 dark:text-gray-300">
              <li className="flex items-start gap-3">
                <Check className="text-success-600 flex-shrink-0 mt-0.5" size={20} />
                <span>1000 shots per month</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="text-success-600 flex-shrink-0 mt-0.5" size={20} />
                <span>All three modes</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="text-success-600 flex-shrink-0 mt-0.5" size={20} />
                <span>No watermarks</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="text-success-600 flex-shrink-0 mt-0.5" size={20} />
                <span>Priority queue</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="text-success-600 flex-shrink-0 mt-0.5" size={20} />
                <span>Custom prompts & API access</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="text-success-600 flex-shrink-0 mt-0.5" size={20} />
                <span>Priority support</span>
              </li>
            </ul>
            <Link to="/register" className="btn btn-primary w-full">Get Started</Link>
          </div>
        </div>
      </section>
      
      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-800 py-12 mt-20">
        <div className="container mx-auto px-6 text-center text-gray-600 dark:text-gray-400">
          <p className="mb-2">© 2025 ProductSnap. All rights reserved.</p>
          <p className="text-sm">Transform your products with AI-powered photography</p>
        </div>
      </footer>
    </div>
  )
}
