export enum JobMode {
  STUDIO_WHITE = 'studio_white',
  MODEL_TRYON = 'model_tryon',
  LIFESTYLE_SCENE = 'lifestyle_scene',
}

export enum JobStatus {
  PENDING = 'pending',
  QUEUED = 'queued',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

export interface Job {
  id: string
  mode: JobMode
  status: JobStatus
  input_url: string
  result_urls: string[]
  thumbnail_url?: string
  progress: number
  created_at: string
  completed_at?: string
  error_message?: string
}

export interface User {
  id: string
  email: string
  email_verified: boolean
  full_name?: string
  avatar_url?: string
  created_at: string
  is_admin: boolean
}

export interface Subscription {
  plan: 'free' | 'personal' | 'pro'
  status: 'active' | 'cancelled' | 'expired' | 'pending'
  current_period_end?: string
}
