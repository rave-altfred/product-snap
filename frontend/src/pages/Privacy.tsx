import { Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import logo from '../assets/logo.png'
import Footer from '../components/Footer'

export default function Privacy() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-50 shadow-lg sticky top-0 z-50 border-b border-gray-200 dark:border-gray-300">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <Link to="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <img src={logo} alt="Light Click" className="h-12 w-12" />
            <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-accent-600 bg-clip-text text-transparent">Light Click</h1>
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
          <h1 className="text-4xl md:text-5xl font-bold mb-4 text-gray-900 dark:text-white">Privacy Policy</h1>
          <p className="text-gray-600 dark:text-gray-400 mb-8">
            Last updated: <time dateTime="2025-10-11">October 11, 2025</time>
          </p>
          
          <p className="text-gray-700 dark:text-gray-300 mb-8 leading-relaxed">
            Welcome to <strong>LightClick Studio</strong> ("we", "our", "us"). This Privacy Policy explains how we collect, use, and protect your information when you use our website, web application, and related services (the "Service"). By using the Service, you agree to this Policy.
          </p>

          {/* Table of Contents */}
          <nav className="bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg p-6 mb-12" aria-label="Table of contents">
            <strong className="text-lg font-semibold text-gray-900 dark:text-white block mb-4">Contents</strong>
            <ol className="space-y-2 text-gray-700 dark:text-gray-300">
              <li><a href="#who" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">1. Who We Are</a></li>
              <li><a href="#info" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">2. Information We Collect</a></li>
              <li><a href="#use" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">3. How We Use Information</a></li>
              <li><a href="#gdpr" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">4. Legal Bases (GDPR)</a></li>
              <li><a href="#retention" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">5. Data Storage & Retention</a></li>
              <li><a href="#sharing" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">6. Data Sharing & Disclosure</a></li>
              <li><a href="#cookies" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">7. Cookies & Analytics</a></li>
              <li><a href="#transfers" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">8. International Transfers</a></li>
              <li><a href="#rights" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">9. Your Rights</a></li>
              <li><a href="#security" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">10. Data Security</a></li>
              <li><a href="#children" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">11. Children's Privacy</a></li>
              <li><a href="#changes" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">12. Changes to This Policy</a></li>
              <li><a href="#contact" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">13. Contact</a></li>
            </ol>
          </nav>

          {/* Sections */}
          <section id="who" className="mb-12 pb-12 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">1. Who We Are</h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              LightClick Studio is a creative technology service based in Israel, providing AI-powered tools to generate professional product images. Our Service is available worldwide.
            </p>
          </section>

          <section id="info" className="mb-12 pb-12 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">2. Information We Collect</h2>
            
            <h3 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">a) Information you provide</h3>
            <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 mb-4">
              <li><strong>Account data:</strong> name, email, password (encrypted).</li>
              <li><strong>Billing data:</strong> handled by third-party processors (e.g., Stripe/PayPal). We do not store full card numbers.</li>
              <li><strong>Uploaded content:</strong> images/files you upload for processing; stored temporarily to provide the Service and may be auto-deleted after a set period.</li>
            </ul>
            
            <h3 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">b) Information collected automatically</h3>
            <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 mb-4">
              <li><strong>Usage data:</strong> pages viewed, actions taken, session duration.</li>
              <li><strong>Device/log data:</strong> IP address, browser type, OS, timestamps.</li>
              <li><strong>Cookies:</strong> for session management, preferences, and analytics.</li>
            </ul>
            
            <h3 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">c) Communications</h3>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              If you contact us (e.g., email/support), we may retain your messages to assist you.
            </p>
          </section>

          <section id="use" className="mb-12 pb-12 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">3. How We Use Information</h2>
            <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 mb-4">
              <li>Operate, maintain, and improve the Service.</li>
              <li>Process your image generations and deliver results.</li>
              <li>Manage subscriptions, payments, and accounts.</li>
              <li>Communicate service notices and support.</li>
              <li>Detect, prevent, and address fraud or abuse.</li>
              <li>Comply with legal obligations.</li>
            </ul>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              We do <strong>not</strong> sell or rent your personal information.
            </p>
          </section>

          <section id="gdpr" className="mb-12 pb-12 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">4. Legal Bases (GDPR)</h2>
            <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300">
              <li><strong>Consent</strong> (e.g., analytics, marketing emails where applicable).</li>
              <li><strong>Contract</strong> (to deliver paid services at your request).</li>
              <li><strong>Legitimate interests</strong> (service improvement, security, fraud prevention).</li>
              <li><strong>Legal obligations</strong> (e.g., tax and accounting requirements).</li>
            </ul>
          </section>

          <section id="retention" className="mb-12 pb-12 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">5. Data Storage & Retention</h2>
            <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 mb-4">
              <li><strong>Uploaded content</strong> is stored temporarily for processing/quality assurance and may be deleted automatically after a defined period.</li>
              <li><strong>Account data</strong> is kept while your account is active.</li>
              <li><strong>Billing records</strong> are kept for the minimum period required by law.</li>
              <li><strong>Analytics data</strong> may be retained in aggregated or anonymized form.</li>
            </ul>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              You can request deletion of your account and associated data (see <a href="#rights" className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300">Your Rights</a>).
            </p>
          </section>

          <section id="sharing" className="mb-12 pb-12 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">6. Data Sharing & Disclosure</h2>
            <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300">
              <li><strong>Service providers:</strong> hosting, analytics, payments, email. They must follow comparable privacy/security standards.</li>
              <li><strong>Legal compliance:</strong> if required by law or to protect rights, safety, and integrity.</li>
              <li><strong>Business transfers:</strong> if we undergo a merger, acquisition, or asset sale (we'll notify users).</li>
            </ul>
          </section>

          <section id="cookies" className="mb-12 pb-12 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">7. Cookies & Analytics</h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              We use cookies and similar technologies for authentication, preferences, and analytics (e.g., Google Analytics). You can control cookies via your browser settings; some features may not function without them.
            </p>
          </section>

          <section id="transfers" className="mb-12 pb-12 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">8. International Transfers</h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              Your information may be processed outside your country. We implement appropriate safeguards (e.g., standard contractual clauses) to comply with applicable laws, including GDPR.
            </p>
          </section>

          <section id="rights" className="mb-12 pb-12 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">9. Your Rights</h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed mb-4">
              Depending on your location, you may have rights to:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 mb-4">
              <li>Access, correct, or delete your personal data.</li>
              <li>Withdraw consent (where processing is based on consent).</li>
              <li>Object to or restrict certain processing.</li>
              <li>Request data portability.</li>
            </ul>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              To exercise rights, email us at <a href="mailto:support@lightclick.studio" className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300">support@lightclick.studio</a>. We may need to verify your identity.
            </p>
          </section>

          <section id="security" className="mb-12 pb-12 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">10. Data Security</h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              We use appropriate technical and organizational measures (encryption, secure hosting, access controls). However, no online system is 100% secure.
            </p>
          </section>

          <section id="children" className="mb-12 pb-12 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">11. Children's Privacy</h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              The Service is not directed to children under 16, and we do not knowingly collect their data. If you believe a child has provided information, contact us to remove it.
            </p>
          </section>

          <section id="changes" className="mb-12 pb-12 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">12. Changes to This Policy</h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              We may update this Policy from time to time. Material changes will be posted here or sent by email. Continued use after the effective date constitutes acceptance.
            </p>
          </section>

          <section id="contact" className="mb-12">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">13. Contact</h2>
            <div className="text-gray-700 dark:text-gray-300 leading-relaxed">
              <p className="mb-2"><strong>LightClick Studio</strong></p>
              <p className="mb-2">Tel Aviv, Israel</p>
              <p className="mb-4">Email: <a href="mailto:support@lightclick.studio" className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300">support@lightclick.studio</a></p>
            </div>
          </section>
        </div>
      </main>

      {/* Footer */}
      <Footer />
    </div>
  )
}
