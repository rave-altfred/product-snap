import { Link } from 'react-router-dom'
import { Camera, Sparkles, Zap, ArrowRight, Check, Upload, Wand2, Download, ChevronDown } from 'lucide-react'
import { useState, useEffect } from 'react'
import logo from '../assets/logo.png'
import banner1 from '../assets/banner1.png'
import banner2 from '../assets/banner2.png'
import banner3 from '../assets/banner3.png'
import Footer from '../components/Footer'

export default function Landing() {
  const [showStickyBottom, setShowStickyBottom] = useState(false)
  const [expandedMode, setExpandedMode] = useState<number | null>(null)

  useEffect(() => {
    const heroObserver = new IntersectionObserver(
      ([entry]) => {
        const pricingSection = document.getElementById('pricing')
        if (pricingSection) {
          const pricingRect = pricingSection.getBoundingClientRect()
          const isPricingVisible = pricingRect.top < window.innerHeight && pricingRect.bottom > 0
          setShowStickyBottom(!entry.isIntersecting && !isPricingVisible)
        } else {
          setShowStickyBottom(!entry.isIntersecting)
        }
      },
      { threshold: 0 }
    )

    const heroElement = document.getElementById('hero-cta')
    if (heroElement) {
      heroObserver.observe(heroElement)
    }

    return () => heroObserver.disconnect()
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Sticky Header - Mobile Optimized */}
      <header className="sticky top-0 z-40 backdrop-blur-md bg-white/90 dark:bg-slate-900/70 border-b border-gray-200 dark:border-white/10 h-14">
        <div className="max-w-screen-xl mx-auto h-full px-3 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <img src={logo} alt="LightClick" className="h-8 w-8 md:h-10 md:w-10" width="32" height="32" loading="eager" />
            <span className="text-base md:text-xl font-bold bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent">LightClick</span>
          </div>
          <div className="flex gap-2 items-center">
            <Link to="/login" className="hidden sm:inline-block px-3 py-2 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-white/10 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500">
              Login
            </Link>
            <Link to="/register" className="px-3 md:px-4 py-2 rounded-lg text-sm font-semibold bg-primary-600 hover:bg-primary-700 text-white transition-colors min-h-[44px] flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-400">
              Start Free
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section - Mobile First */}
      <section className="scroll-mt-16 max-w-screen-lg mx-auto px-4 py-6 md:py-10 text-center">
        <h1 className="text-[clamp(26px,5.5vw,40px)] md:text-5xl lg:text-6xl font-bold leading-tight mb-3 text-gray-900 dark:text-white">
          Transform Product Photos<br />
          <span className="text-gradient">Into Professional Shots</span>
        </h1>
        
        <p className="text-[15px] md:text-xl leading-snug text-gray-600 dark:text-slate-300 mb-4 max-w-2xl mx-auto line-clamp-3">
          Create studio-quality product photography with AI. White backgrounds, model try-ons, and lifestyle scenes in seconds.
        </p>
        
        <div id="hero-cta" className="flex flex-col space-y-3 max-w-sm mx-auto mb-3">
          <Link to="/register" className="w-full h-12 rounded-xl text-base font-semibold bg-primary-600 hover:bg-primary-700 text-white transition-colors flex items-center justify-center gap-2 shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-400 group">
            Start Free
            <ArrowRight className="group-hover:translate-x-1 transition-transform" size={18} />
          </Link>
          <Link to="#modes" className="w-full h-12 rounded-xl text-base font-semibold bg-gray-100 dark:bg-white/10 hover:bg-gray-200 dark:hover:bg-white/20 text-gray-800 dark:text-white transition-colors flex items-center justify-center border border-gray-300 dark:border-white/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-400">
            Learn More
          </Link>
        </div>
        
        <div className="text-xs text-gray-500 dark:text-slate-400 mt-2">
          No card • 5 free gens • All modes
        </div>
        
        {/* Image Showcase - Compact Thumbnails */}
        <div className="mt-4 flex justify-center gap-2 md:gap-3">
          <img src={banner1} alt="Product before AI enhancement" className="w-[30%] md:w-[22%] lg:w-[18%] rounded-lg aspect-[2/1] object-cover shadow-sm" width="195" height="98" loading="eager" fetchpriority="high" decoding="async" />
          <img src={banner2} alt="AI processing product photo" className="w-[30%] md:w-[22%] lg:w-[18%] rounded-lg aspect-[2/1] object-cover shadow-sm" width="195" height="98" loading="lazy" decoding="async" />
          <img src={banner3} alt="Professional product shot result" className="w-[30%] md:w-[22%] lg:w-[18%] rounded-lg aspect-[2/1] object-cover shadow-sm" width="195" height="98" loading="lazy" decoding="async" />
        </div>
      </section>

      {/* Compact Chip Stepper - Mobile First */}
      <section className="bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-primary-950/30 dark:to-accent-950/30 py-6 md:py-8">
        <div className="max-w-screen-xl mx-auto px-4">
          <h2 className="text-xl md:text-3xl font-bold text-center mb-4 md:mb-6 text-gray-900 dark:text-white">
            <span className="text-gradient">3 Simple Steps</span> to Pro Photos
          </h2>
          {/* Mobile: Horizontal chips */}
          <div className="md:hidden flex items-center justify-between gap-2 overflow-x-auto snap-x px-2">
            <div className="shrink-0 snap-start rounded-full bg-white dark:bg-slate-800/80 border border-gray-300 dark:border-white/10 px-3 py-2 flex items-center gap-2 shadow-sm">
              <Upload className="text-primary-400" size={18} />
              <span className="text-sm font-medium text-gray-800 dark:text-white">Upload</span>
            </div>
            <div className="shrink-0 snap-start rounded-full bg-white dark:bg-slate-800/80 border border-gray-300 dark:border-white/10 px-3 py-2 flex items-center gap-2 shadow-sm">
              <Wand2 className="text-accent-400" size={18} />
              <span className="text-sm font-medium text-gray-800 dark:text-white">AI Magic</span>
            </div>
            <div className="shrink-0 snap-start rounded-full bg-white dark:bg-slate-800/80 border border-gray-300 dark:border-white/10 px-3 py-2 flex items-center gap-2 shadow-sm">
              <Download className="text-primary-400" size={18} />
              <span className="text-sm font-medium text-gray-800 dark:text-white">Download</span>
            </div>
          </div>
          {/* Desktop: Original grid */}
          <div className="hidden md:grid grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div className="flex flex-col items-center text-center">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center mb-3 shadow-sm">
                <Upload className="text-white" size={28} />
              </div>
              <h3 className="font-bold text-lg mb-1 text-gray-900 dark:text-white">Upload</h3>
              <p className="text-sm text-gray-600 dark:text-gray-300">Quick snap with your phone</p>
            </div>
            <div className="flex flex-col items-center text-center">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-accent-500 to-accent-600 flex items-center justify-center mb-3 shadow-sm">
                <Wand2 className="text-white" size={28} />
              </div>
              <h3 className="font-bold text-lg mb-1 text-gray-900 dark:text-white">AI Magic</h3>
              <p className="text-sm text-gray-600 dark:text-gray-300">Instantly processed & enhanced</p>
            </div>
            <div className="flex flex-col items-center text-center">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary-600 to-accent-600 flex items-center justify-center mb-3 shadow-sm">
                <Download className="text-white" size={28} />
              </div>
              <h3 className="font-bold text-lg mb-1 text-gray-900 dark:text-white">Download</h3>
              <p className="text-sm text-gray-600 dark:text-gray-300">Studio-quality ready to use</p>
            </div>
          </div>
        </div>
      </section>

      {/* Generation Modes - Accordion on Mobile */}
      <section id="modes" className="max-w-screen-xl mx-auto px-4 py-10 md:py-16">
        <div className="text-center mb-4 md:mb-8">
          <h2 className="text-2xl md:text-4xl font-bold mb-2 text-gray-900 dark:text-white">Three Powerful Modes</h2>
          <p className="text-sm md:text-base text-gray-600 dark:text-gray-300">Professional results for every use case</p>
        </div>
        
        {/* Mobile: Accordion List */}
        <div className="md:hidden space-y-3">
          {[
            { id: 0, icon: Camera, title: 'Studio White', desc: 'Crisp product shots on pure white backgrounds—perfect for e-commerce.', gradient: 'from-primary-500 to-primary-600' },
            { id: 1, icon: Sparkles, title: 'Model Try-On', desc: 'Products on realistic models naturally—bring your apparel to life.', gradient: 'from-accent-500 to-accent-600' },
            { id: 2, icon: Zap, title: 'Lifestyle Scenes', desc: 'Products in photorealistic environments—tell your brand story.', gradient: 'from-primary-600 to-accent-600' }
          ].map((mode) => {
            const Icon = mode.icon
            const isExpanded = expandedMode === mode.id
            return (
              <div key={mode.id} className="bg-white dark:bg-slate-900/60 border border-gray-200 dark:border-white/10 rounded-2xl overflow-hidden shadow-sm">
                <button
                  onClick={() => setExpandedMode(isExpanded ? null : mode.id)}
                  className="w-full flex items-center gap-3 py-3 px-4 text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 min-h-[64px]"
                  aria-expanded={isExpanded}
                >
                  <div className={`size-8 rounded-md bg-gradient-to-br ${mode.gradient} flex items-center justify-center shrink-0`}>
                    <Icon className="text-white" size={18} />
                  </div>
                  <span className="text-lg font-bold text-gray-900 dark:text-white flex-grow">{mode.title}</span>
                  <ChevronDown className={`text-gray-600 dark:text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`} size={20} />
                </button>
                {isExpanded && (
                  <div className="px-4 pb-4 pt-2">
                    <p className="text-sm text-gray-600 dark:text-slate-300 leading-relaxed">{mode.desc}</p>
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* Desktop: Original Grid */}
        <div className="hidden md:grid md:grid-cols-3 gap-5">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm hover:shadow-md transition-all">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center mb-3">
              <Camera className="text-white" size={24} />
            </div>
            <h3 className="text-xl font-bold mb-2 text-gray-900 dark:text-white">Studio White</h3>
            <p className="text-sm text-gray-600 dark:text-gray-300">
              Crisp product shots on pure white backgrounds—perfect for e-commerce.
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm hover:shadow-md transition-all">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-accent-500 to-accent-600 flex items-center justify-center mb-3">
              <Sparkles className="text-white" size={24} />
            </div>
            <h3 className="text-xl font-bold mb-2 text-gray-900 dark:text-white">Model Try-On</h3>
            <p className="text-sm text-gray-600 dark:text-gray-300">
              Products on realistic models naturally—bring your apparel to life.
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm hover:shadow-md transition-all">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-600 to-accent-600 flex items-center justify-center mb-3">
              <Zap className="text-white" size={24} />
            </div>
            <h3 className="text-xl font-bold mb-2 text-gray-900 dark:text-white">Lifestyle Scenes</h3>
            <p className="text-sm text-gray-600 dark:text-gray-300">
              Products in photorealistic environments—tell your brand story.
            </p>
          </div>
        </div>
      </section>

      {/* Pricing - Compact Mobile */}
      <section id="pricing" className="max-w-screen-xl mx-auto px-4 py-10 md:py-16">
        <div className="text-center mb-4 md:mb-8">
          <h2 className="text-2xl md:text-4xl font-bold mb-2 text-gray-900 dark:text-white">Simple, Transparent Pricing</h2>
          <p className="text-sm md:text-base text-gray-600 dark:text-gray-300">Start free, upgrade as you grow</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-5 max-w-5xl mx-auto">
          <div className="bg-white dark:bg-slate-900/60 border border-gray-200 dark:border-white/10 rounded-2xl p-4 flex flex-col shadow-sm">
            <div className="text-xs font-semibold text-primary-400 mb-1">STARTER</div>
            <div className="mb-3">
              <span className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white">$0</span>
              <span className="text-gray-500 dark:text-gray-400 text-sm">/mo</span>
            </div>
            <ul className="space-y-2 mb-4 text-sm text-gray-600 dark:text-gray-300 flex-grow">
              <li className="flex items-start gap-2">
                <Check className="text-success-500 flex-shrink-0 mt-0.5" size={16} />
                <span>5 image generations</span>
              </li>
              <li className="flex items-start gap-2">
                <Check className="text-success-500 flex-shrink-0 mt-0.5" size={16} />
                <span>All three modes</span>
              </li>
              <li className="flex items-start gap-2">
                <Check className="text-success-500 flex-shrink-0 mt-0.5" size={16} />
                <span>Watermarked outputs</span>
              </li>
            </ul>
            <Link to="/register" className="w-full h-12 rounded-lg text-base text-center font-semibold bg-gray-100 dark:bg-white/10 hover:bg-gray-200 dark:hover:bg-white/20 text-gray-800 dark:text-white transition-colors flex items-center justify-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-400">Start Free</Link>
          </div>

          <div className="bg-white dark:bg-slate-900/60 border-2 border-primary-500 rounded-2xl p-4 flex flex-col relative shadow-sm">
            <div className="absolute -top-2.5 left-1/2 -translate-x-1/2 bg-gradient-to-r from-orange-500 to-orange-600 text-white text-xs font-bold px-3 py-1 rounded-full shadow-sm">
              BEST VALUE
            </div>
            <div className="text-xs font-semibold text-primary-400 mb-1 mt-1">BASIC</div>
            <div className="mb-2">
              <span className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white">$9.99</span>
              <span className="text-gray-500 dark:text-gray-400 text-sm">/mo</span>
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mb-3">
              $99.99/yr <span className="text-success-500 font-semibold">(save 17%)</span>
            </div>
            <ul className="space-y-2 mb-4 text-sm text-gray-600 dark:text-gray-300 flex-grow">
              <li className="flex items-start gap-2">
                <Check className="text-success-500 flex-shrink-0 mt-0.5" size={16} />
                <span>100 generations/month</span>
              </li>
              <li className="flex items-start gap-2">
                <Check className="text-success-500 flex-shrink-0 mt-0.5" size={16} />
                <span>All three modes</span>
              </li>
              <li className="flex items-start gap-2">
                <Check className="text-success-500 flex-shrink-0 mt-0.5" size={16} />
                <span>Email support</span>
              </li>
            </ul>
            <Link to="/register" className="w-full h-12 rounded-lg text-base text-center font-semibold bg-primary-600 hover:bg-primary-700 text-white transition-colors flex items-center justify-center mt-3 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-400">Get Started</Link>
          </div>

          <div className="bg-white dark:bg-slate-900/60 border border-gray-200 dark:border-white/10 rounded-2xl p-4 flex flex-col shadow-sm">
            <div className="text-xs font-semibold text-primary-400 mb-1">PRO</div>
            <div className="mb-2">
              <span className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white">$34.99</span>
              <span className="text-gray-500 dark:text-gray-400 text-sm">/mo</span>
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mb-3">
              $349.99/yr <span className="text-success-500 font-semibold">(save 17%)</span>
            </div>
            <ul className="space-y-2 mb-4 text-sm text-gray-600 dark:text-gray-300 flex-grow">
              <li className="flex items-start gap-2">
                <Check className="text-success-500 flex-shrink-0 mt-0.5" size={16} />
                <span>500 generations/month</span>
              </li>
              <li className="flex items-start gap-2">
                <Check className="text-success-500 flex-shrink-0 mt-0.5" size={16} />
                <span>All three modes</span>
              </li>
              <li className="flex items-start gap-2">
                <Check className="text-success-500 flex-shrink-0 mt-0.5" size={16} />
                <span>Priority queue & support</span>
              </li>
            </ul>
            <Link to="/register" className="w-full h-12 rounded-lg text-base text-center font-semibold bg-primary-600 hover:bg-primary-700 text-white transition-colors flex items-center justify-center mt-3 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-400">Get Started</Link>
          </div>
        </div>
        
        <p className="text-center text-xs text-gray-500 dark:text-slate-400 mt-3">
          💡 Yearly plans = ~2 months free
        </p>
      </section>
      
      {/* Sticky Bottom CTA (Mobile Only) - Conditional */}
      {showStickyBottom && (
        <div className="md:hidden fixed inset-x-0 bottom-0 z-40 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-t border-gray-200 dark:border-white/10 px-4 py-3 animate-slide-up">
          <Link to="/register" className="w-full h-12 rounded-xl text-base font-semibold bg-primary-600 hover:bg-primary-700 text-white transition-colors flex items-center justify-center gap-2 shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-400">
            Start Free
            <ArrowRight size={18} />
          </Link>
        </div>
      )}
      
      {/* Footer */}
      <Footer />
    </div>
  )
}
