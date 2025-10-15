import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { Clock, CheckCircle, XCircle, Play, Trash2, Grid, List, MoreVertical, Download, Edit2, Check, X } from 'lucide-react'
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
  const [dropdownOpen, setDropdownOpen] = useState<string | null>(null)
  const [editingJobId, setEditingJobId] = useState<string | null>(null)
  const [editingName, setEditingName] = useState<string>('')

  useEffect(() => {
    loadJobs()
  }, [])

  useEffect(() => {
    const handleClickOutside = () => setDropdownOpen(null)
    if (dropdownOpen) {
      document.addEventListener('click', handleClickOutside)
      return () => document.removeEventListener('click', handleClickOutside)
    }
  }, [dropdownOpen])

  // Check if there are any active jobs
  const hasActiveJobs = useMemo(() => {
    const active = jobs.some(job => job.status === 'queued' || job.status === 'processing' || job.status === 'pending')
    console.log('[Library] Active jobs check:', active, 'Total jobs:', jobs.length)
    return active
  }, [jobs])

  // Auto-refresh jobs while any are in progress
  useEffect(() => {
    console.log('[Library] Auto-refresh effect triggered, hasActiveJobs:', hasActiveJobs)
    
    if (!hasActiveJobs) {
      console.log('[Library] No active jobs, skipping auto-refresh')
      return
    }
    
    console.log('[Library] Setting up auto-refresh interval (3s)')
    const interval = setInterval(() => {
      console.log('[Library] Auto-refresh: reloading jobs...')
      loadJobs()
    }, 3000) // Refresh every 3 seconds
    
    return () => {
      console.log('[Library] Cleaning up auto-refresh interval')
      clearInterval(interval)
    }
  }, [hasActiveJobs])

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
      setDropdownOpen(null)
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete job')
    }
  }

  const downloadImage = async (url: string, filename: string) => {
    try {
      const response = await fetch(url)
      const blob = await response.blob()
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      // Replace extension with .png since generated images are PNG
      const nameWithoutExt = filename ? filename.replace(/\.[^/.]+$/, '') : 'product_image'
      link.download = `${nameWithoutExt}.png`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
      setDropdownOpen(null)
    } catch (err) {
      alert('Failed to download image')
    }
  }

  const startRename = (jobId: string, currentName: string) => {
    setEditingJobId(jobId)
    setEditingName(currentName || 'Untitled')
    setDropdownOpen(null)
  }

  const saveRename = async (jobId: string) => {
    if (!editingName.trim()) {
      alert('Name cannot be empty')
      return
    }
    
    try {
      // Update the job with new filename
      await jobsApi.update(jobId, { input_filename: editingName.trim() })
      setJobs(jobs.map(job => 
        job.id === jobId ? { ...job, input_filename: editingName.trim() } : job
      ))
      setEditingJobId(null)
      setEditingName('')
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to rename job')
    }
  }

  const cancelRename = () => {
    setEditingJobId(null)
    setEditingName('')
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
    <div className="px-6 py-4 sm:px-8 sm:py-6 lg:px-12 lg:py-8 animate-fade-in overflow-hidden">
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
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 w-full">
          {jobs.map((job) => (
            <div key={job.id} className="card hover:shadow-lg transition-shadow p-4 sm:p-6">
              <div className="relative mb-4 rounded-xl bg-gray-50 dark:bg-gray-800/50 overflow-hidden p-2">
                {job.thumbnail_url ? (
                  <div className="relative h-48">
                    <img
                      src={job.thumbnail_url}
                      alt={job.input_filename || 'Job result'}
                      className="w-full h-full object-contain cursor-pointer hover:opacity-90 transition-opacity rounded-lg bg-white dark:bg-gray-900"
                      loading="lazy"
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
                  </div>
                ) : (
                  <div className="w-full h-48 flex items-center justify-center">
                    <div className="text-center">
                      {getStatusIcon(job.status)}
                      <p className="text-sm text-gray-600 mt-2 capitalize">{job.status}</p>
                    </div>
                  </div>
                )}
                
                <div className="absolute top-2 right-2 z-10">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      setDropdownOpen(dropdownOpen === job.id ? null : job.id)
                    }}
                    className="p-1.5 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors shadow-md"
                    title="Options"
                  >
                    <MoreVertical size={16} />
                  </button>
                  
                  {dropdownOpen === job.id && (
                    <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 py-1 z-20">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          startRename(job.id, job.input_filename || 'Untitled')
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
                      >
                        <Edit2 size={16} />
                        Rename
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          downloadImage(job.thumbnail_url!, job.input_filename || 'image.jpg')
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
                      >
                        <Download size={16} />
                        Download
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          deleteJob(job.id)
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 flex items-center gap-2"
                      >
                        <Trash2 size={16} />
                        Delete
                      </button>
                    </div>
                  )}
                </div>
              </div>
              
              <div>
                <div className="flex items-center justify-between mb-2">
                  {editingJobId === job.id ? (
                    <div className="flex items-center gap-1 flex-1">
                      <input
                        type="text"
                        value={editingName}
                        onChange={(e) => setEditingName(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') saveRename(job.id)
                          if (e.key === 'Escape') cancelRename()
                        }}
                        className="flex-1 px-2 py-1 text-sm border border-primary-500 rounded focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                        autoFocus
                        onClick={(e) => e.stopPropagation()}
                      />
                      <button
                        onClick={() => saveRename(job.id)}
                        className="p-1 text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 rounded"
                        title="Save"
                      >
                        <Check size={16} />
                      </button>
                      <button
                        onClick={cancelRename}
                        className="p-1 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
                        title="Cancel"
                      >
                        <X size={16} />
                      </button>
                    </div>
                  ) : (
                    <h3 
                      className="font-medium truncate cursor-pointer hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                      onClick={() => startRename(job.id, job.input_filename || 'Untitled')}
                      title="Click to rename"
                    >
                      {job.input_filename || 'Untitled'}
                    </h3>
                  )}
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
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-3 w-full max-w-full" style={{ boxSizing: 'border-box' }}>
          {jobs.map((job) => (
            <div key={job.id} className="card p-3 sm:p-4 hover:shadow-lg transition-shadow hover:scale-100" style={{ width: '100%', maxWidth: '100%', overflow: 'hidden', boxSizing: 'border-box' }}>
              <div className="flex gap-2 sm:gap-3" style={{ width: '100%', maxWidth: '100%', minWidth: 0, boxSizing: 'border-box' }}>
                {/* Thumbnail */}
                <div className="flex-shrink-0">
                  {job.thumbnail_url ? (
                    <div className="w-16 h-16 sm:w-20 sm:h-20 bg-gray-50 dark:bg-gray-800/50 rounded-lg p-1 flex items-center justify-center">
                      <img
                        src={job.thumbnail_url}
                        alt={job.input_filename || 'Job result'}
                        className="w-full h-full object-contain rounded cursor-pointer hover:opacity-90 transition-opacity bg-white dark:bg-gray-900"
                        onClick={() => {
                          const urlsToOpen = job.result_urls && job.result_urls.length > 0 ? job.result_urls : [job.thumbnail_url!]
                          openImageModal(urlsToOpen, 0)
                        }}
                      />
                    </div>
                  ) : (
                    <div className="w-16 h-16 sm:w-20 sm:h-20 bg-gray-50 dark:bg-gray-800/50 rounded-lg flex items-center justify-center">
                      {getStatusIcon(job.status)}
                    </div>
                  )}
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0 max-w-full overflow-hidden">
                  <div className="flex items-start gap-2 mb-1 max-w-full">
                    {editingJobId === job.id ? (
                      <div className="flex items-center gap-1 flex-1 min-w-0">
                        <input
                          type="text"
                          value={editingName}
                          onChange={(e) => setEditingName(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') saveRename(job.id)
                            if (e.key === 'Escape') cancelRename()
                          }}
                          className="flex-1 min-w-0 px-2 py-1 text-xs border border-primary-500 rounded focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                          autoFocus
                          onClick={(e) => e.stopPropagation()}
                        />
                        <button
                          onClick={() => saveRename(job.id)}
                          className="p-0.5 text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 rounded flex-shrink-0"
                          title="Save"
                        >
                          <Check size={14} />
                        </button>
                        <button
                          onClick={cancelRename}
                          className="p-0.5 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded flex-shrink-0"
                          title="Cancel"
                        >
                          <X size={14} />
                        </button>
                      </div>
                    ) : (
                      <h3 
                        className="font-medium text-sm truncate flex-1 cursor-pointer hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                        onClick={() => startRename(job.id, job.input_filename || 'Untitled')}
                        title="Click to rename"
                      >
                        {job.input_filename || 'Untitled'}
                      </h3>
                    )}
                    <div className="flex items-center gap-1 flex-shrink-0">
                      <div className="relative">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            setDropdownOpen(dropdownOpen === job.id ? null : job.id)
                          }}
                          className="p-1 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
                          title="Options"
                        >
                          <MoreVertical size={16} />
                        </button>
                        
                        {dropdownOpen === job.id && (
                          <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 py-1 z-20">
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                startRename(job.id, job.input_filename || 'Untitled')
                              }}
                              className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
                            >
                              <Edit2 size={16} />
                              Rename
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                downloadImage(job.thumbnail_url!, job.input_filename || 'image.jpg')
                              }}
                              className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
                            >
                              <Download size={16} />
                              Download
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                deleteJob(job.id)
                              }}
                              className="w-full px-4 py-2 text-left text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 flex items-center gap-2"
                            >
                              <Trash2 size={16} />
                              Delete
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-xs text-gray-600 mb-1 truncate overflow-hidden">
                    {formatMode(job.mode)} • <span className="capitalize">{job.status}</span>
                  </div>
                  
                  <p className="text-xs text-gray-500 mb-1 truncate overflow-hidden">
                    {formatDate(job.created_at)}
                  </p>
                  
                  {job.error_message && (
                    <div className="text-xs text-red-600 mb-1" style={{ 
                      width: '100%', 
                      maxWidth: '100%',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                      display: 'block'
                    }} title={job.error_message}>
                      Error: {job.error_message}
                    </div>
                  )}
                  
                  {job.result_urls && job.result_urls.length > 0 && (
                    <button
                      onClick={() => openImageModal(job.result_urls, 0)}
                      className="text-xs text-primary-600 hover:text-primary-700 font-medium truncate text-left block"
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
