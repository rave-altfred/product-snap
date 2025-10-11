import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Clock, CheckCircle, XCircle, Play, Trash2, Grid, List } from 'lucide-react'
import { jobsApi } from '../lib/api'
import ImageModal from '../components/ImageModal'

interface Job {
  id: string
  mode: string
  status: string
  input_filename: string | null
  result_urls: string[]
  thumbnail_url: string | null
  created_at: string
  progress: string
  error_message: string | null
}

export default function Library() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedImages, setSelectedImages] = useState<string[]>([])
  const [selectedImageIndex, setSelectedImageIndex] = useState<number>(0)
  const [viewMode, setViewMode] = useState<'gallery' | 'list'>('gallery')

  useEffect(() => {
    loadJobs()
  }, [])

  const loadJobs = async () => {
    try {
      const response = await jobsApi.list({ limit: 50, offset: 0 })
      setJobs(response.data.jobs || [])
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load jobs')
    } finally {
      setLoading(false)
    }
  }

  const deleteJob = async (jobId: string) => {
    if (!confirm('Are you sure you want to delete this job?')) return
    
    try {
      await jobsApi.delete(jobId)
      setJobs(jobs.filter(job => job.id !== jobId))
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete job')
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return <CheckCircle className="text-green-500" size={20} />
      case 'failed':
      case 'cancelled':
        return <XCircle className="text-red-500" size={20} />
      case 'processing':
        return <Play className="text-blue-500" size={20} />
      default:
        return <Clock className="text-yellow-500" size={20} />
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatMode = (mode: string) => {
    return mode.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
  }

  const openImageModal = (images: string[], index: number) => {
    setSelectedImages(images)
    setSelectedImageIndex(index)
  }

  const closeImageModal = () => {
    setSelectedImages([])
    setSelectedImageIndex(0)
  }

  if (loading) {
    return (
      <div className="px-6 py-8 sm:px-8 lg:px-12">
        <h1 className="text-3xl font-bold mb-8">Library</h1>
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="px-6 py-8 sm:px-8 lg:px-12">
        <h1 className="text-3xl font-bold mb-8">Library</h1>
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      </div>
    )
  }

  return (
    <div className="px-6 py-4 sm:px-8 sm:py-6 lg:px-12 lg:py-8">
      <div className="flex items-center justify-between gap-3 mb-6 sm:mb-8">
        <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold">Library</h1>
        <div className="flex gap-2">
          <div className="flex border border-gray-300 rounded-lg overflow-hidden">
            <button
              onClick={() => setViewMode('gallery')}
              className={`p-2 ${viewMode === 'gallery' ? 'bg-primary-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}
              title="Gallery view"
            >
              <Grid size={18} />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 ${viewMode === 'list' ? 'bg-primary-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}
              title="List view"
            >
              <List size={18} />
            </button>
          </div>
          <Link to="/new-shoot" className="btn btn-primary text-sm px-3 py-2 whitespace-nowrap">
            New Shoot
          </Link>
        </div>
      </div>
      
      {jobs.length === 0 ? (
        <div className="text-center py-8 sm:py-12">
          <div className="text-gray-400 mb-4">
            <Clock size={48} className="sm:w-16 sm:h-16 mx-auto mb-4" />
            <p className="text-lg sm:text-xl mb-2">No jobs yet</p>
            <p className="text-sm sm:text-base text-gray-600 px-4">Create your first product shoot to get started.</p>
          </div>
          <Link to="/new-shoot" className="btn btn-primary w-full sm:w-auto max-w-xs mx-auto block sm:inline-block">
            Create New Shoot
          </Link>
        </div>
      ) : viewMode === 'gallery' ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 w-full">
          {jobs.map((job) => (
            <div key={job.id} className="card hover:shadow-lg transition-shadow">
              <div className="relative">
                {job.thumbnail_url ? (
                  <img
                    src={job.thumbnail_url}
                    alt={job.input_filename || 'Job result'}
                    className="w-full h-48 object-cover rounded-t-lg cursor-pointer hover:opacity-90 transition-opacity"
                    style={{ imageRendering: 'auto' }}
                    onClick={() => {
                      console.log('Job data:', { 
                        id: job.id, 
                        has_result_urls: !!job.result_urls, 
                        result_urls_length: job.result_urls?.length || 0,
                        result_urls: job.result_urls,
                        thumbnail_url: job.thumbnail_url
                      })
                      const urlsToOpen = job.result_urls && job.result_urls.length > 0 ? job.result_urls : [job.thumbnail_url!]
                      console.log('Opening modal with URLs:', urlsToOpen)
                      openImageModal(urlsToOpen, 0)
                    }}
                  />
                ) : (
                  <div className="w-full h-48 bg-gray-200 rounded-t-lg flex items-center justify-center">
                    <div className="text-center">
                      {getStatusIcon(job.status)}
                      <p className="text-sm text-gray-600 mt-2 capitalize">{job.status}</p>
                      {job.status === 'processing' && job.progress && (
                        <div className="mt-2">
                          <div className="w-24 bg-gray-300 rounded-full h-2 mx-auto">
                            <div 
                              className="bg-blue-500 h-2 rounded-full transition-all"
                              style={{ width: `${job.progress}%` }}
                            ></div>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">{job.progress}%</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}
                
                <button
                  onClick={() => deleteJob(job.id)}
                  className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
                  title="Delete job"
                >
                  <Trash2 size={16} />
                </button>
              </div>
              
              <div className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium truncate">
                    {job.input_filename || 'Untitled'}
                  </h3>
                  {getStatusIcon(job.status)}
                </div>
                
                <p className="text-sm text-gray-600 mb-2">
                  Mode: {formatMode(job.mode)}
                </p>
                
                <p className="text-xs text-gray-500">
                  {formatDate(job.created_at)}
                </p>
                
                {job.error_message && (
                  <p className="text-xs text-red-600 mt-2 truncate" title={job.error_message}>
                    Error: {job.error_message}
                  </p>
                )}
                
                {job.result_urls && job.result_urls.length > 0 && (
                  <div className="mt-3">
                    <button
                      onClick={() => openImageModal(job.result_urls, 0)}
                      className="text-xs text-primary-600 hover:text-primary-700 font-medium"
                    >
                      View {job.result_urls.length} {job.result_urls.length === 1 ? 'result' : 'results'} →
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-3 w-full">
          {jobs.map((job) => (
            <div key={job.id} className="card p-3 sm:p-4 hover:shadow-lg transition-shadow w-full">
              <div className="flex gap-2 sm:gap-3 w-full">
                {/* Thumbnail */}
                <div className="flex-shrink-0">
                  {job.thumbnail_url ? (
                    <img
                      src={job.thumbnail_url}
                      alt={job.input_filename || 'Job result'}
                      className="w-16 h-16 sm:w-20 sm:h-20 object-cover rounded cursor-pointer hover:opacity-90 transition-opacity"
                      onClick={() => {
                        const urlsToOpen = job.result_urls && job.result_urls.length > 0 ? job.result_urls : [job.thumbnail_url!]
                        openImageModal(urlsToOpen, 0)
                      }}
                    />
                  ) : (
                    <div className="w-16 h-16 sm:w-20 sm:h-20 bg-gray-200 rounded flex items-center justify-center">
                      {getStatusIcon(job.status)}
                    </div>
                  )}
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0 overflow-hidden" style={{ maxWidth: 'calc(100vw - 120px)' }}>
                  <div className="flex items-start gap-2 mb-1">
                    <h3 className="font-medium text-sm truncate flex-1 min-w-0 max-w-full">{job.input_filename || 'Untitled'}</h3>
                    <div className="flex items-center gap-1 flex-shrink-0">
                      <div className="hidden sm:block">{getStatusIcon(job.status)}</div>
                      <button
                        onClick={() => deleteJob(job.id)}
                        className="p-1 text-red-500 hover:bg-red-50 rounded transition-colors"
                        title="Delete job"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                  
                  <div className="text-xs text-gray-600 mb-1 truncate">
                    {formatMode(job.mode)} • <span className="capitalize">{job.status}</span>
                  </div>
                  
                  <p className="text-xs text-gray-500 mb-1 truncate">
                    {formatDate(job.created_at)}
                  </p>
                  
                  {job.error_message && (
                    <p className="text-xs text-red-600 mb-1 truncate" title={job.error_message}>
                      Error: {job.error_message}
                    </p>
                  )}
                  
                  {job.result_urls && job.result_urls.length > 0 && (
                    <button
                      onClick={() => openImageModal(job.result_urls, 0)}
                      className="text-xs text-primary-600 hover:text-primary-700 font-medium"
                    >
                      View {job.result_urls.length} {job.result_urls.length === 1 ? 'result' : 'results'} →
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedImages.length > 0 && (
        <ImageModal
          images={selectedImages}
          currentIndex={selectedImageIndex}
          onClose={closeImageModal}
          onNavigate={setSelectedImageIndex}
        />
      )}
    </div>
  )
}
