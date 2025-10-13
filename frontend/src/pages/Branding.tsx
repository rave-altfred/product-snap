import { useEffect, useState } from 'react'
import { Palette, Type, Layers, Sparkles, Image as ImageIcon, Sun, Moon } from 'lucide-react'
import logo from '../assets/logo.png'
import banner1 from '../assets/banner1.png'
import banner2 from '../assets/banner2.png'
import banner3 from '../assets/banner3.png'

interface BrandingData {
  app_info: {
    name: string
    version: string
  }
  colors: {
    primary: Record<string, string>
    accent: Record<string, string>
    success: Record<string, string>
    semantic: any
  }
  typography: {
    font_family: { sans: string; description: string }
    font_weights: Record<string, number>
    font_sizes: Record<string, string>
  }
  spacing: {
    border_radius: Record<string, string>
    padding: Record<string, string>
  }
  shadows: Record<string, string>
  gradients: Record<string, any>
  animations: {
    transitions: Record<string, string>
    keyframes: Record<string, any>
    hover_effects: Record<string, string>
  }
  components: Record<string, any>
  assets: {
    logo: { primary: string; description: string }
    banners: Array<{ name: string; path: string; description: string }>
  }
  theme_modes: {
    light: any
    dark: any
    default_mode: string
    storage_key: string
  }
  design_principles: Record<string, string>
}

export default function Branding() {
  const [branding, setBranding] = useState<BrandingData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/branding')
      .then((res) => res.json())
      .then((data) => {
        setBranding(data)
        setLoading(false)
      })
      .catch((err) => {
        console.error('Failed to load branding:', err)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
      </div>
    )
  }

  if (!branding) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-red-500">Failed to load branding data</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-4 text-gradient">
            {branding.app_info.name} Design System
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400">
            Version {branding.app_info.version} • Complete Branding Guidelines
          </p>
        </div>

        {/* Design Principles */}
        <section className="mb-16">
          <div className="card">
            <div className="flex items-center gap-3 mb-6">
              <Sparkles className="w-8 h-8 text-primary-500" />
              <h2 className="text-3xl font-bold">Design Principles</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(branding.design_principles).map(([key, value]) => (
                <div key={key} className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                  <h3 className="font-semibold text-lg capitalize mb-2 text-primary-600 dark:text-primary-400">
                    {key.replace(/_/g, ' ')}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{value}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Colors */}
        <section className="mb-16">
          <div className="card">
            <div className="flex items-center gap-3 mb-6">
              <Palette className="w-8 h-8 text-primary-500" />
              <h2 className="text-3xl font-bold">Color Palette</h2>
            </div>

            {/* Primary Colors */}
            <div className="mb-8">
              <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                Primary Colors
                <span className="text-sm font-normal text-gray-500">
                  {branding.colors.primary.description}
                </span>
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
                {Object.entries(branding.colors.primary)
                  .filter(([key]) => !isNaN(Number(key)))
                  .map(([shade, color]) => (
                    <div key={shade} className="group">
                      <div
                        className="h-20 rounded-lg shadow-md mb-2 cursor-pointer hover:scale-105 transition-transform"
                        style={{ backgroundColor: color as string }}
                        title={`Click to copy: ${color}`}
                        onClick={() => {
                          navigator.clipboard.writeText(color as string)
                          alert(`Copied ${color} to clipboard!`)
                        }}
                      />
                      <div className="text-center">
                        <p className="text-xs font-medium">{shade}</p>
                        <p className="text-xs text-gray-500 font-mono">{color}</p>
                      </div>
                    </div>
                  ))}
              </div>
            </div>

            {/* Accent Colors */}
            <div className="mb-8">
              <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                Accent Colors
                <span className="text-sm font-normal text-gray-500">
                  {branding.colors.accent.description}
                </span>
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
                {Object.entries(branding.colors.accent)
                  .filter(([key]) => !isNaN(Number(key)))
                  .map(([shade, color]) => (
                    <div key={shade} className="group">
                      <div
                        className="h-20 rounded-lg shadow-md mb-2 cursor-pointer hover:scale-105 transition-transform"
                        style={{ backgroundColor: color as string }}
                        title={`Click to copy: ${color}`}
                        onClick={() => {
                          navigator.clipboard.writeText(color as string)
                          alert(`Copied ${color} to clipboard!`)
                        }}
                      />
                      <div className="text-center">
                        <p className="text-xs font-medium">{shade}</p>
                        <p className="text-xs text-gray-500 font-mono">{color}</p>
                      </div>
                    </div>
                  ))}
              </div>
            </div>

            {/* Success Colors */}
            <div>
              <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                Success Colors
                <span className="text-sm font-normal text-gray-500">
                  {branding.colors.success.description}
                </span>
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
                {Object.entries(branding.colors.success)
                  .filter(([key]) => !isNaN(Number(key)))
                  .map(([shade, color]) => (
                    <div key={shade} className="group">
                      <div
                        className="h-20 rounded-lg shadow-md mb-2 cursor-pointer hover:scale-105 transition-transform"
                        style={{ backgroundColor: color as string }}
                        title={`Click to copy: ${color}`}
                        onClick={() => {
                          navigator.clipboard.writeText(color as string)
                          alert(`Copied ${color} to clipboard!`)
                        }}
                      />
                      <div className="text-center">
                        <p className="text-xs font-medium">{shade}</p>
                        <p className="text-xs text-gray-500 font-mono">{color}</p>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </section>

        {/* Typography */}
        <section className="mb-16">
          <div className="card">
            <div className="flex items-center gap-3 mb-6">
              <Type className="w-8 h-8 text-primary-500" />
              <h2 className="text-3xl font-bold">Typography</h2>
            </div>

            <div className="space-y-8">
              {/* Font Family */}
              <div>
                <h3 className="text-xl font-semibold mb-3">Font Family</h3>
                <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                  <p className="font-mono text-sm mb-2">{branding.typography.font_family.sans}</p>
                  <p className="text-gray-600 dark:text-gray-400 text-sm">
                    {branding.typography.font_family.description}
                  </p>
                </div>
              </div>

              {/* Font Sizes */}
              <div>
                <h3 className="text-xl font-semibold mb-3">Font Sizes</h3>
                <div className="space-y-2">
                  {Object.entries(branding.typography.font_sizes).map(([name, size]) => (
                    <div
                      key={name}
                      className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg"
                    >
                      <span
                        className="font-medium"
                        style={{ fontSize: size as string }}
                      >
                        {name} - The quick brown fox jumps
                      </span>
                      <span className="text-sm text-gray-500 font-mono ml-4">{size}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Font Weights */}
              <div>
                <h3 className="text-xl font-semibold mb-3">Font Weights</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {Object.entries(branding.typography.font_weights).map(([name, weight]) => (
                    <div
                      key={name}
                      className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg text-center"
                    >
                      <p style={{ fontWeight: weight as number }} className="text-2xl mb-2">
                        Aa
                      </p>
                      <p className="text-sm font-medium capitalize">{name}</p>
                      <p className="text-xs text-gray-500">{weight}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Shadows */}
        <section className="mb-16">
          <div className="card">
            <div className="flex items-center gap-3 mb-6">
              <Layers className="w-8 h-8 text-primary-500" />
              <h2 className="text-3xl font-bold">Shadows & Effects</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(branding.shadows)
                .filter(([key]) => key !== 'description')
                .map(([name, shadow]) => (
                  <div key={name} className="p-6 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                    <div
                      className="h-24 bg-white dark:bg-gray-800 rounded-lg mb-3"
                      style={{ boxShadow: shadow as string }}
                    />
                    <p className="font-medium capitalize">{name.replace(/_/g, ' ')}</p>
                    <p className="text-xs text-gray-500 font-mono mt-1">{shadow}</p>
                  </div>
                ))}
            </div>
          </div>
        </section>

        {/* Theme Modes */}
        <section className="mb-16">
          <div className="card">
            <div className="flex items-center gap-3 mb-6">
              <div className="flex gap-2">
                <Sun className="w-8 h-8 text-yellow-500" />
                <Moon className="w-8 h-8 text-indigo-500" />
              </div>
              <h2 className="text-3xl font-bold">Theme Modes</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Light Mode */}
              <div className="p-6 bg-gray-50 rounded-xl border-2 border-gray-200">
                <h3 className="text-xl font-semibold mb-4 text-gray-900">Light Mode</h3>
                <div className="space-y-2 text-sm text-gray-900">
                  <p><strong>Background:</strong> {branding.theme_modes.light.background}</p>
                  <p><strong>Text:</strong> {branding.theme_modes.light.text}</p>
                  <p><strong>Card BG:</strong> {branding.theme_modes.light.card_bg}</p>
                  <p><strong>Border:</strong> {branding.theme_modes.light.border}</p>
                </div>
              </div>

              {/* Dark Mode */}
              <div className="p-6 bg-gray-900 rounded-xl border-2 border-gray-700">
                <h3 className="text-xl font-semibold mb-4 text-gray-100">Dark Mode</h3>
                <div className="space-y-2 text-sm text-gray-300">
                  <p><strong>Background:</strong> {branding.theme_modes.dark.background}</p>
                  <p><strong>Text:</strong> {branding.theme_modes.dark.text}</p>
                  <p><strong>Card BG:</strong> {branding.theme_modes.dark.card_bg}</p>
                  <p><strong>Border:</strong> {branding.theme_modes.dark.border}</p>
                </div>
              </div>
            </div>
            <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <p className="text-sm">
                <strong>Default Mode:</strong> {branding.theme_modes.default_mode} •{' '}
                <strong>Storage Key:</strong> {branding.theme_modes.storage_key}
              </p>
            </div>
          </div>
        </section>

        {/* Assets */}
        <section className="mb-16">
          <div className="card">
            <div className="flex items-center gap-3 mb-6">
              <ImageIcon className="w-8 h-8 text-primary-500" />
              <h2 className="text-3xl font-bold">Brand Assets</h2>
            </div>

            {/* Logo */}
            <div className="mb-6">
              <h3 className="text-xl font-semibold mb-3">Logo</h3>
              <div className="p-6 bg-gray-50 dark:bg-gray-700/50 rounded-xl flex items-center gap-4">
                <img
                  src={logo}
                  alt="ProductSnap Logo"
                  className="h-16 object-contain"
                />
                <div>
                  <p className="font-medium">Primary ProductSnap logo</p>
                  <p className="text-sm text-gray-500">src/assets/logo.png</p>
                </div>
              </div>
            </div>

            {/* Banners */}
            <div>
              <h3 className="text-xl font-semibold mb-3">Banners</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                  <img
                    src={banner1}
                    alt="banner1"
                    className="w-full h-32 object-cover rounded-lg mb-2"
                  />
                  <p className="font-medium">banner1</p>
                  <p className="text-xs text-gray-500">Banner image 1</p>
                </div>
                <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                  <img
                    src={banner2}
                    alt="banner2"
                    className="w-full h-32 object-cover rounded-lg mb-2"
                  />
                  <p className="font-medium">banner2</p>
                  <p className="text-xs text-gray-500">Banner image 2</p>
                </div>
                <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                  <img
                    src={banner3}
                    alt="banner3"
                    className="w-full h-32 object-cover rounded-lg mb-2"
                  />
                  <p className="font-medium">banner3</p>
                  <p className="text-xs text-gray-500">Banner image 3</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Components Preview */}
        <section className="mb-16">
          <div className="card">
            <h2 className="text-3xl font-bold mb-6">Component Examples</h2>
            
            <div className="space-y-6">
              {/* Buttons */}
              <div>
                <h3 className="text-xl font-semibold mb-3">Buttons</h3>
                <div className="flex flex-wrap gap-4">
                  <button className="btn btn-primary">Primary Button</button>
                  <button className="btn btn-secondary">Secondary Button</button>
                  <button className="btn btn-primary" disabled>Disabled Button</button>
                </div>
              </div>

              {/* Inputs */}
              <div>
                <h3 className="text-xl font-semibold mb-3">Input Fields</h3>
                <input
                  type="text"
                  className="input max-w-md"
                  placeholder="Example input field..."
                />
              </div>

              {/* Cards */}
              <div>
                <h3 className="text-xl font-semibold mb-3">Cards</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="card-flat">
                    <h4 className="font-semibold mb-2">Flat Card</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      A simple card with minimal styling
                    </p>
                  </div>
                  <div className="stat-card">
                    <h4 className="font-semibold mb-2">Stat Card</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Used for displaying statistics
                    </p>
                  </div>
                  <div className="feature-card group">
                    <div className="feature-icon mb-3">
                      <Sparkles className="w-6 h-6" />
                    </div>
                    <h4 className="font-semibold mb-2">Feature Card</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Hover to see animation
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <div className="text-center text-gray-500 text-sm">
          <p>Design System • {branding.app_info.name} v{branding.app_info.version}</p>
          <p className="mt-2">
            Access this data programmatically at{' '}
            <code className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded">
              GET /api/branding
            </code>
          </p>
        </div>
        </div>
      </div>
    </div>
  )
}
