import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, Camera, Image as ImageIcon, Wand2 } from 'lucide-react'
import { jobsApi } from '../lib/api'

type JobMode = 'STUDIO_WHITE' | 'MODEL_TRYON' | 'LIFESTYLE_SCENE'

interface ModeOption {
  id: JobMode
  name: string
  description: string
  icon: React.ReactNode
}

const modes: ModeOption[] = [
  {
    id: 'STUDIO_WHITE',
    name: 'Studio White',
    description: 'Clean white background for e-commerce',
    icon: <ImageIcon size={24} />
  },
  {
    id: 'MODEL_TRYON',
    name: 'Model Try-On',
    description: 'Show product on a model or person',
    icon: <Camera size={24} />
  },
  {
    id: 'LIFESTYLE_SCENE',
    name: 'Lifestyle Scene',
    description: 'Product in real-world setting',
    icon: <Wand2 size={24} />
  }
]

export default function NewShoot() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [selectedMode, setSelectedMode] = useState<JobMode>('STUDIO_WHITE')
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Please select a valid image file')
      return
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB')
      return
    }

    setSelectedFile(file)
    setError('')

    // Create preview URL
    const reader = new FileReader()
    reader.onload = (e) => {
      setPreviewUrl(e.target?.result as string)
    }
    reader.readAsDataURL(file)
  }

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault()
    const file = event.dataTransfer.files[0]
    if (file && fileInputRef.current) {
      // Simulate file selection by updating the file input
      const dataTransfer = new DataTransfer()
      dataTransfer.items.add(file)
      fileInputRef.current.files = dataTransfer.files
      
      const fakeEvent = {
        target: fileInputRef.current
      } as React.ChangeEvent<HTMLInputElement>
      handleFileSelect(fakeEvent)
    }
  }

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault()
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    
    if (!selectedFile) {
      setError('Please select an image')
      return
    }

    setLoading(true)
    setError('')

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('mode', selectedMode)
      if (prompt.trim()) {
        formData.append('prompt', prompt.trim())
      }

      await jobsApi.create(formData)
      
      // Navigate to library to see the new job
      navigate('/library')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create job')
    } finally {
      setLoading(false)
    }
  }

  const clearFile = () => {
    setSelectedFile(null)
    setPreviewUrl(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">New Shoot</h1>
      
      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Image Upload */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Upload Product Image</h2>
          
          {!selectedFile ? (
            <div
              className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-primary-500 transition-colors cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
            >
              <Upload size={48} className="mx-auto mb-4 text-gray-400" />
              <p className="text-lg mb-2">Drop your image here or click to browse</p>
              <p className="text-sm text-gray-500">Supports JPG, PNG, WebP up to 10MB</p>
            </div>
          ) : (
            <div className="relative">
              <img
                src={previewUrl || ''}
                alt="Preview"
                className="max-w-full max-h-96 mx-auto rounded-lg shadow-lg"
              />
              <button
                type="button"
                onClick={clearFile}
                className="absolute top-2 right-2 bg-red-500 text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-red-600 transition-colors"
              >
                ×
              </button>
              <div className="mt-4 text-center">
                <p className="text-sm text-gray-600">
                  <strong>{selectedFile.name}</strong> ({(selectedFile.size / 1024 / 1024).toFixed(1)} MB)
                </p>
              </div>
            </div>
          )}
          
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>

        {/* Mode Selection */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Choose Render Mode</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {modes.map((mode) => (
              <button
                key={mode.id}
                type="button"
                onClick={() => setSelectedMode(mode.id)}
                className={`p-4 border rounded-lg text-left transition-colors ${
                  selectedMode === mode.id
                    ? 'border-primary-500 bg-primary-50 text-primary-700'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <div className="flex items-center gap-3 mb-2">
                  {mode.icon}
                  <h3 className="font-medium">{mode.name}</h3>
                </div>
                <p className="text-sm text-gray-600">{mode.description}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Prompt Input */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Custom Prompt (Optional)</h2>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe any specific requirements or styling preferences..."
            className="w-full h-24 px-3 py-2 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            maxLength={500}
          />
          <p className="text-sm text-gray-500 mt-2">{prompt.length}/500 characters</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={!selectedFile || loading}
            className="btn btn-primary px-8 py-3 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Creating Job...' : 'Create Shoot'}
          </button>
        </div>
      </form>
    </div>
  )
}
