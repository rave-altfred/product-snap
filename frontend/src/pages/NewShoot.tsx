import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, Camera, Image as ImageIcon, Wand2, X } from 'lucide-react'
import { jobsApi, api } from '../lib/api'
import { useAuthStore } from '../store/authStore'

type JobMode = 'STUDIO_WHITE' | 'MODEL_TRYON' | 'LIFESTYLE_SCENE'

type ShadowOption = 'drop_shadow' | 'no_shadow'
type ModelGender = 'male' | 'female'
type SceneEnvironment = 'indoor' | 'outdoor'

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
  console.log('[NewShoot] Component mounting')
  
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [selectedMode, setSelectedMode] = useState<JobMode>('STUDIO_WHITE')
  const [shadowOption, setShadowOption] = useState<ShadowOption>('drop_shadow')
  const [modelGender, setModelGender] = useState<ModelGender>('female')
  const [sceneEnvironment, setSceneEnvironment] = useState<SceneEnvironment>('indoor')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showCamera, setShowCamera] = useState(false)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const navigate = useNavigate()
  const { logout } = useAuthStore()
  
  console.log('[NewShoot] State initialized:', { selectedFile, selectedMode, shadowOption })

  // Cleanup camera stream on unmount
  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop())
      }
    }
  }, [stream])

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    console.log('File selected:', file.name, 'Type:', file.type, 'Size:', file.size)

    // Validate file type - check MIME type or file extension for HEIC/HEIF
    const fileExt = file.name.toLowerCase().split('.').pop() || ''
    const isHeic = fileExt === 'heic' || fileExt === 'heif'
    const hasValidMimeType = file.type.startsWith('image/') || file.type === 'image/heic' || file.type === 'image/heif'
    
    if (!hasValidMimeType && !isHeic) {
      console.error('File type validation failed:', file.type, 'Extension:', fileExt)
      setError('Please select a valid image file (JPG, PNG, WebP, HEIC/HEIF)')
      return
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB')
      return
    }

    setSelectedFile(file)
    setError('')

    // Create preview URL - use server-side conversion for HEIC
    const createPreview = async () => {
      try {
        if (isHeic) {
          // For HEIC files, send to server for conversion
          console.log('Uploading HEIC to server for preview conversion...')
          const formData = new FormData()
          formData.append('file', file)
          
          const response = await api.post('/api/preview/generate', formData, {
            responseType: 'blob',
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          })
          
          // Create object URL from the JPEG blob
          const blobUrl = URL.createObjectURL(response.data)
          setPreviewUrl(blobUrl)
          console.log('HEIC preview generated successfully')
        } else {
          // For other formats, use FileReader as before
          const reader = new FileReader()
          reader.onload = (e) => {
            console.log('Preview generated successfully')
            setPreviewUrl(e.target?.result as string)
          }
          reader.onerror = (e) => {
            console.error('Error reading file for preview:', e)
            setPreviewUrl(null)
          }
          reader.readAsDataURL(file)
        }
      } catch (error) {
        console.error('Error generating preview:', error)
        console.log('Will show placeholder instead. Original file will still be uploaded correctly.')
        // Still allow upload even if preview fails
        setPreviewUrl(null)
      }
    }
    
    createPreview()
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
      formData.append('mode', selectedMode.toLowerCase())
      
      // Add sub-options based on mode
      if (selectedMode === 'STUDIO_WHITE') {
        formData.append('shadow_option', shadowOption)
      } else if (selectedMode === 'MODEL_TRYON') {
        formData.append('model_gender', modelGender)
      } else if (selectedMode === 'LIFESTYLE_SCENE') {
        formData.append('scene_environment', sceneEnvironment)
      }

      await jobsApi.create(formData)
      
      // Navigate to library to see the new job
      navigate('/library')
    } catch (err: any) {
      // Handle authentication errors
      if (err.response?.status === 401) {
        logout()
        navigate('/login')
        return
      }
      
      // Show other errors
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
    stopCamera()
  }

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'environment' // Use back camera on mobile
        } 
      })
      
      setStream(mediaStream)
      setShowCamera(true)
      setError('')
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
    } catch (err) {
      setError('Could not access camera. Please check permissions.')
      console.error('Camera error:', err)
    }
  }

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
    setShowCamera(false)
  }

  const takePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return
    
    const video = videoRef.current
    const canvas = canvasRef.current
    const context = canvas.getContext('2d')
    
    if (!context) return
    
    // Set canvas dimensions to match video
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    
    // Draw the video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height)
    
    // Convert canvas to blob
    canvas.toBlob((blob) => {
      if (!blob) return
      
      // Create a file from the blob
      const file = new File([blob], `camera-photo-${Date.now()}.jpg`, {
        type: 'image/jpeg',
        lastModified: Date.now()
      })
      
      setSelectedFile(file)
      setPreviewUrl(canvas.toDataURL('image/jpeg', 0.9))
      stopCamera()
    }, 'image/jpeg', 0.9)
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl sm:text-3xl font-bold mb-6 sm:mb-8">New Shoot</h1>
      
      <form onSubmit={handleSubmit} className="space-y-6 sm:space-y-8">
        {/* Image Upload */}
        <div className="card">
          <h2 className="text-lg sm:text-xl font-semibold mb-4">Capture or Upload Product Image</h2>
          
          {showCamera ? (
            <div className="relative">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                className="w-full max-h-96 rounded-lg bg-black"
              />
              <canvas ref={canvasRef} className="hidden" />
              
              <div className="absolute top-4 right-4 flex gap-2">
                <button
                  type="button"
                  onClick={stopCamera}
                  className="p-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
                  title="Close camera"
                >
                  <X size={20} />
                </button>
              </div>
              
              <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
                <button
                  type="button"
                  onClick={takePhoto}
                  className="w-16 h-16 bg-white border-4 border-gray-300 rounded-full hover:bg-gray-100 transition-colors flex items-center justify-center"
                  title="Take photo"
                >
                  <div className="w-12 h-12 bg-gray-300 rounded-full"></div>
                </button>
              </div>
            </div>
          ) : !selectedFile ? (
            <div className="space-y-4">
              <div
                className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 sm:p-12 text-center hover:border-primary-500 dark:hover:border-primary-400 transition-colors cursor-pointer"
                onClick={() => fileInputRef.current?.click()}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
              >
                <Upload size={36} className="sm:w-12 sm:h-12 mx-auto mb-4 text-gray-400 dark:text-gray-500" />
                <p className="text-base sm:text-lg mb-2 text-gray-900 dark:text-gray-100">Drop your image here or click to browse</p>
                <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400">Supports JPG, PNG, WebP, HEIC/HEIF up to 10MB</p>
              </div>
              
              <div className="text-center">
                <div className="text-gray-500 dark:text-gray-400 mb-3">or</div>
                <button
                  type="button"
                  onClick={startCamera}
                  className="btn btn-secondary inline-flex items-center gap-2"
                >
                  <Camera size={20} />
                  Take Photo with Camera
                </button>
              </div>
            </div>
          ) : (
            <div>
              <div className="relative">
                {previewUrl ? (
                  <img
                    src={previewUrl}
                    alt="Preview"
                    className="max-w-full max-h-96 mx-auto rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 object-contain bg-gray-50 dark:bg-gray-900"
                    onError={(e) => {
                      console.log('Preview image failed to load, hiding...')
                      e.currentTarget.style.display = 'none'
                      const placeholder = e.currentTarget.nextElementSibling
                      if (placeholder) {
                        (placeholder as HTMLElement).style.display = 'flex'
                      }
                    }}
                  />
                ) : null}
                <div 
                  className="max-w-full h-96 mx-auto rounded-lg shadow-lg bg-gray-100 dark:bg-gray-800 flex-col items-center justify-center"
                  style={{ display: previewUrl ? 'none' : 'flex' }}
                >
                  <ImageIcon size={64} className="text-gray-400 dark:text-gray-600 mb-4" />
                  <p className="text-gray-600 dark:text-gray-400">Preview not available</p>
                  <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">File ready to upload</p>
                </div>
              </div>
              <div className="mt-4 text-center space-y-3">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  <strong>{selectedFile.name}</strong> ({(selectedFile.size / 1024 / 1024).toFixed(1)} MB)
                </p>
                <button
                  type="button"
                  onClick={clearFile}
                  className="btn btn-secondary inline-flex items-center gap-2"
                >
                  <X size={16} />
                  Upload Another Image
                </button>
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
        <div className={`card ${!selectedFile ? 'opacity-60' : ''}`}>
          <h2 className="text-lg sm:text-xl font-semibold mb-4">
            Choose Render Mode
            {!selectedFile && <span className="text-sm font-normal text-gray-500 dark:text-gray-400 ml-2">(Upload an image first)</span>}
          </h2>
          <div className="space-y-3 sm:space-y-0 sm:grid sm:grid-cols-2 lg:grid-cols-3 sm:gap-3 sm:gap-4">
            {modes.map((mode) => (
              <div key={mode.id} className="space-y-3">
                <button
                  type="button"
                  onClick={() => selectedFile && setSelectedMode(mode.id)}
                  disabled={!selectedFile}
                  className={`w-full p-4 border rounded-lg text-left transition-colors min-h-[6.5rem] flex flex-col justify-center ${
                    !selectedFile
                      ? 'cursor-not-allowed border-gray-200 dark:border-gray-700 text-gray-400 dark:text-gray-600'
                      : selectedMode === mode.id
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                      : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500 text-gray-900 dark:text-gray-100'
                  }`}
                >
                  <div className="flex items-center gap-3 mb-2">
                    {mode.icon}
                    <h3 className="font-medium">{mode.name}</h3>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{mode.description}</p>
                </button>

                {/* Sub-options for Studio White */}
                {selectedFile && selectedMode === 'STUDIO_WHITE' && mode.id === 'STUDIO_WHITE' && (
                  <div className="px-2">
                    <h3 className="text-sm font-medium mb-2">Shadow Style</h3>
                    <div className="grid grid-cols-2 gap-2">
                      <button
                        type="button"
                        onClick={() => setShadowOption('drop_shadow')}
                        className={`p-2 border rounded-lg text-center text-xs transition-colors ${
                          shadowOption === 'drop_shadow'
                            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500 text-gray-900 dark:text-gray-100'
                        }`}
                      >
                        <div className="font-medium">Drop Shadow</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Subtle depth</div>
                      </button>
                      <button
                        type="button"
                        onClick={() => setShadowOption('no_shadow')}
                        className={`p-2 border rounded-lg text-center text-xs transition-colors ${
                          shadowOption === 'no_shadow'
                            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500 text-gray-900 dark:text-gray-100'
                        }`}
                      >
                        <div className="font-medium">No Shadow</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Pure white</div>
                      </button>
                    </div>
                  </div>
                )}

                {/* Sub-options for Model Try-On */}
                {selectedFile && selectedMode === 'MODEL_TRYON' && mode.id === 'MODEL_TRYON' && (
                  <div className="px-2">
                    <h3 className="text-sm font-medium mb-2">Model Gender</h3>
                    <div className="grid grid-cols-2 gap-2">
                      <button
                        type="button"
                        onClick={() => setModelGender('female')}
                        className={`p-2 border rounded-lg text-center text-xs transition-colors ${
                          modelGender === 'female'
                            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500 text-gray-900 dark:text-gray-100'
                        }`}
                      >
                        <div className="font-medium">Female Model</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Feminine</div>
                      </button>
                      <button
                        type="button"
                        onClick={() => setModelGender('male')}
                        className={`p-2 border rounded-lg text-center text-xs transition-colors ${
                          modelGender === 'male'
                            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500 text-gray-900 dark:text-gray-100'
                        }`}
                      >
                        <div className="font-medium">Male Model</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Masculine</div>
                      </button>
                    </div>
                  </div>
                )}

                {/* Sub-options for Lifestyle Scene */}
                {selectedFile && selectedMode === 'LIFESTYLE_SCENE' && mode.id === 'LIFESTYLE_SCENE' && (
                  <div className="px-2">
                    <h3 className="text-sm font-medium mb-2">Environment</h3>
                    <div className="grid grid-cols-2 gap-2">
                      <button
                        type="button"
                        onClick={() => setSceneEnvironment('indoor')}
                        className={`p-2 border rounded-lg text-center text-xs transition-colors ${
                          sceneEnvironment === 'indoor'
                            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500 text-gray-900 dark:text-gray-100'
                        }`}
                      >
                        <div className="font-medium">Indoor</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Kitchen, desk, bedroom</div>
                      </button>
                      <button
                        type="button"
                        onClick={() => setSceneEnvironment('outdoor')}
                        className={`p-2 border rounded-lg text-center text-xs transition-colors ${
                          sceneEnvironment === 'outdoor'
                            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500 text-gray-900 dark:text-gray-100'
                        }`}
                      >
                        <div className="font-medium">Outdoor</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Garden, cafe, street</div>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-100 dark:bg-red-900/20 border border-red-400 dark:border-red-500 text-red-700 dark:text-red-400 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Submit Button */}
        <div className="flex justify-center sm:justify-end">
          <button
            type="submit"
            disabled={!selectedFile || loading}
            className="btn btn-primary w-full sm:w-auto px-6 sm:px-8 py-3 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Creating Job...' : 'Create Shoot'}
          </button>
        </div>
      </form>
    </div>
  )
}
