import axios from 'axios'

// Use environment variable if available, otherwise default to production URL
// Note: Don't include /api in the base URL since endpoints already have it
const API_URL = import.meta.env.VITE_API_URL || 'https://lightclick.studio'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (!refreshToken) {
          throw new Error('No refresh token')
        }

        const response = await axios.post(`${API_URL}/api/auth/refresh`, {
          refresh_token: refreshToken,
        })

        const { access_token } = response.data
        localStorage.setItem('access_token', access_token)

        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return api(originalRequest)
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  register: (data: { email: string; password: string; full_name?: string }) =>
    api.post('/api/auth/register', data),
  
  login: (data: { email: string; password: string }) =>
    api.post('/api/auth/login', data),
  
  logout: () =>
    api.post('/api/auth/logout'),
  
  verifyEmail: (token: string) =>
    api.get(`/api/auth/verify-email?token=${token}`),
  
  forgotPassword: (email: string) =>
    api.post('/api/auth/forgot-password', { email }),
  
  resetPassword: (token: string, new_password: string) =>
    api.post('/api/auth/reset-password', { token, new_password }),
}

// User API
export const userApi = {
  getMe: () =>
    api.get('/api/users/me'),
  
  getStats: () =>
    api.get('/api/users/stats'),
}

// Jobs API
export const jobsApi = {
  create: (formData: FormData) =>
    api.post('/api/jobs/create', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }),
  
  list: (params?: { limit?: number; offset?: number }) =>
    api.get('/api/jobs/list', { params }),
  
  get: (jobId: string) =>
    api.get(`/api/jobs/${jobId}`),
  
  update: (jobId: string, data: { input_filename?: string }) =>
    api.patch(`/api/jobs/${jobId}`, data),
  
  delete: (jobId: string) =>
    api.delete(`/api/jobs/${jobId}`),
}

// Subscriptions API
export const subscriptionsApi = {
  getMySubscription: () =>
    api.get('/api/subscriptions/me'),
}
