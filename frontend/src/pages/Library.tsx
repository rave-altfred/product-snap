import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Clock, CheckCircle, XCircle, Play, Trash2 } from 'lucide-react'
import { jobsApi } from '../lib/api'

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

  if (loading) {
    return (
      <div className="p-8">
        <h1 className="text-3xl font-bold mb-8">Library</h1>
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-8">
        <h1 className="text-3xl font-bold mb-8">Library</h1>
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Library</h1>
        <Link to="/new-shoot" className="btn btn-primary">
          New Shoot
        </Link>
      </div>
      
      {jobs.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <Clock size={64} className="mx-auto mb-4" />
            <p className="text-xl mb-2">No jobs yet</p>
            <p className="text-gray-600">Create your first product shoot to get started.</p>
          </div>
          <Link to="/new-shoot" className="btn btn-primary">
            Create New Shoot
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {jobs.map((job) => (
            <div key={job.id} className="card hover:shadow-lg transition-shadow">
              <div className="relative">
                {job.thumbnail_url ? (
                  <img
                    src={job.thumbnail_url}
                    alt={job.input_filename || 'Job result'}
                    className="w-full h-48 object-cover rounded-t-lg"
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
                
                {job.result_urls.length > 0 && (
                  <div className="mt-3">
                    <p className="text-xs text-gray-500 mb-1">{job.result_urls.length} results</p>
                    <div className="flex flex-wrap gap-1">
                      {job.result_urls.slice(0, 3).map((url, index) => (
                        <img
                          key={index}
                          src={url}
                          alt={`Result ${index + 1}`}
                          className="w-16 h-16 object-cover rounded border cursor-pointer hover:opacity-75"
                          onClick={() => window.open(url, '_blank')}
                        />
                      ))}
                      {job.result_urls.length > 3 && (
                        <div className="w-16 h-16 bg-gray-100 rounded border flex items-center justify-center text-xs text-gray-500">
                          +{job.result_urls.length - 3}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
