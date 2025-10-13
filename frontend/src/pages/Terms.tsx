import { Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import logo from '../assets/logo.png'
import Footer from '../components/Footer'

export default function Terms() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-50 shadow-lg sticky top-0 z-50 border-b border-gray-200 dark:border-gray-300">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <Link to="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <img src={logo} alt="LightClick" className="h-12 w-12" />
            <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-accent-600 bg-clip-text text-transparent">LightClick</h1>
          </Link>
          <Link to="/" className="btn bg-gray-100 hover:bg-gray-200 dark:bg-gray-200 dark:hover:bg-gray-300 text-gray-800 dark:text-gray-900 text-sm">
            <ArrowLeft className="inline mr-2" size={16} />
            Back to Home
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-12 max-w-4xl">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-8 md:p-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 text-gray-900 dark:text-white">Terms of Service</h1>
          <p className="text-gray-600 dark:text-gray-400 mb-8">
            Last updated: <time dateTime="2025-10-08">October 8, 2025</time>
          </p>
          
          <p className="text-gray-700 dark:text-gray-300 mb-8 leading-relaxed">
            Welcome to <strong>LightClick Studio</strong> ("we", "our", or "us"). These Terms of Service ("Terms") govern your access to and use of our website, apps, and related services ("Service"). By using the Service, you agree to these Terms.
          </p>

          {/* Table of Contents */}
          <nav className="bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg p-6 mb-12" aria-label="Table of contents">
            <strong className="text-lg font-semibold text-gray-900 dark:text-white block mb-4">Contents</strong>
            <ol className="space-y-2 text-gray-700 dark:text-gray-300">
              <li><a href="#overview" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">1. Overview</a></li>
              <li><a href="#eligibility" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">2. Eligibility</a></li>
              <li><a href="#account" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">3. Account Registration</a></li>
              <li><a href="#plans" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">4. Plans & Pricing</a></li>
              <li><a href="#payments" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">5. Payment & Renewal</a></li>
              <li><a href="#refunds" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">6. Refund Policy</a></li>
              <li><a href="#fairuse" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">7. Usage & Fair Use</a></li>
              <li><a href="#ip" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">8. Intellectual Property & Ownership</a></li>
              <li><a href="#liability" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">9. Liability Limitation & Disclaimers</a></li>
              <li><a href="#termination" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">10. Termination</a></li>
              <li><a href="#changes" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">11. Changes to These Terms</a></li>
              <li><a href="#law" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">12. Governing Law</a></li>
              <li><a href="#contact" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">13. Contact</a></li>
            </ol>
          </nav>

          {/* Sections */}
          <section id="overview" className="mb-12 pb-12 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">1. Overview</h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              LightClick Studio provides AI-powered tools that transform user-uploaded product photos into professional product shots. The Service is operated from Israel and available worldwide.
            </p>
          </section>

          <section id="eligibility" className="mb-12 pb-12 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">2. Eligibility</h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              You must be at least 18 years old and capable of entering into a binding agreement to use the Service.
            </p>
          </section>

          <section id="account" className="mb-12 pb-12 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">3. Account Registration</h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              To access premium features, you may need an account. You agree to provide accurate information and keep your credentials secure. You are responsible for activity under your account.
            </p>
          </section>

          <section id="plans" className="mb-12 pb-12 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">4. Plans & Pricing</h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed mb-4">
              We offer monthly and yearly subscriptions:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 mb-4">
              <li><strong>Basic:</strong> 100 image generations per month</li>
              <li><strong>Pro:</strong> 500 image generations per month</li>
            </ul>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed mb-4">
              Current prices (USD): Basic Monthly $9.99, Pro Monthly $29.90, Basic Yearly $99.90, Pro Yearly $299.90. We may update plan features or prices with reasonable notice.
            </p>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed italic">
              Note: Generations are counted per billing period and do not roll over.
            </p>
          </section>

          <section id="payments" className="mb-12 pb-12 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">5. Payment & Renewal</h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              Payments are processed by third-party providers. Subscriptions auto-renew unless cancelled before the renewal date. You can cancel anytime from your account; access remains until the paid period ends.
            </p>
          </section>

          <section id="refunds" className="mb-12 pb-12 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">6. Refund Policy</h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              Because the Service is delivered digitally and accessible immediately, refunds are generally not available once a billing period begins. We may grant refunds or credits at our sole discretion in exceptional cases (e.g., duplicate charges or verified technical issues).
            </p>
          </section>

          <section id="fairuse" className="mb-12 pb-12 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">7. Usage & Fair Use</h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              Each plan includes a fixed number of image generations per period. Automated, abusive, or disruptive use is prohibited. We may rate-limit, suspend, or terminate accounts that violate these Terms or harm service integrity.
            </p>
          </section>

          <section id="ip" className="mb-12 pb-12 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">8. Intellectual Property & Ownership</h2>
            <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300">
              <li>All software, models, and platform materials are owned by LightClick Studio.</li>
              <li>You retain ownership of content you upload.</li>
              <li>Generated outputs are licensed to you for personal and commercial use, subject to these Terms and any third-party rights in your inputs.</li>
              <li>You must not upload content that infringes third-party rights or violates law.</li>
            </ul>
          </section>

          <section id="liability" className="mb-12 pb-12 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">9. Liability Limitation & Disclaimers</h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              The Service is provided "as is" without warranties of any kind. To the fullest extent permitted by law, we disclaim liability for indirect, incidental, special, consequential, or punitive damages, and any loss of profits, data, or business, arising from or related to your use of the Service.
            </p>
          </section>

          <section id="termination" className="mb-12 pb-12 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">10. Termination</h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              We may suspend or terminate your access for violations of these Terms, illegal activity, or actions that threaten service integrity. Upon termination, your right to use the Service ceases immediately.
            </p>
          </section>

          <section id="changes" className="mb-12 pb-12 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">11. Changes to These Terms</h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              We may update these Terms from time to time. Material changes will be announced on this page or via email. Continued use after the effective date constitutes acceptance.
            </p>
          </section>

          <section id="law" className="mb-12 pb-12 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">12. Governing Law</h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              These Terms are governed by the laws of the State of Israel. Courts in Tel Aviv, Israel shall have exclusive jurisdiction, unless a different mandatory consumer forum applies by law.
            </p>
          </section>

          <section id="contact" className="mb-12">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">13. Contact</h2>
            <div className="text-gray-700 dark:text-gray-300 leading-relaxed">
              <p className="mb-2"><strong>LightClick Studio</strong></p>
              <p className="mb-2">Tel Aviv, Israel</p>
              <p className="mb-4">Email: <a href="mailto:support@lightclick.studio" className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300">support@lightclick.studio</a></p>
              <p className="text-gray-600 dark:text-gray-400">See also: <Link to="/privacy" className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300">Privacy Policy</Link></p>
            </div>
          </section>
        </div>
      </main>

      {/* Footer */}
      <Footer />
    </div>
  )
}
