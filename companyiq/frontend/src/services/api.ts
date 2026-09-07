// API service layer — all backend calls go through here
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
})

// Auth token injection
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('companyiq_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 401 redirect
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('companyiq_token')
      localStorage.removeItem('companyiq_user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ── Auth ────────────────────────────────────────────────
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }).then(r => r.data),
  register: (data: { email: string; password: string; full_name: string; role: string }) =>
    api.post('/auth/register', data).then(r => r.data),
  me: () => api.get('/auth/me').then(r => r.data),
  logout: () => api.post('/auth/logout').then(r => r.data),
}

// ── Companies ──────────────────────────────────────────
export const companiesApi = {
  list: (params?: { search?: string; industry?: string; page?: number }) =>
    api.get('/companies', { params }).then(r => r.data),
  get: (id: string) => api.get(`/companies/${id}`).then(r => r.data),
  create: (data: { name: string; industry?: string; website?: string; country?: string }) =>
    api.post('/companies', data).then(r => r.data),
  getResearch: (id: string) => api.get(`/companies/${id}/research`).then(r => r.data),
  refresh: (id: string, focus_area?: string) =>
    api.post(`/companies/${id}/refresh`, null, { params: { focus_area } }).then(r => r.data),
  getOpportunities: (id: string) => api.get(`/companies/${id}/opportunities`).then(r => r.data),
  getUpdates: (id: string) => api.get(`/companies/${id}/updates`).then(r => r.data),
}

// ── Research / Chat ────────────────────────────────────
export const researchApi = {
  chat: (data: {
    message: string
    company_id?: string
    conversation_id?: string
    context?: Record<string, unknown>
  }) => api.post('/research/chat', data).then(r => r.data),
}

// ── Account Plans ──────────────────────────────────────
export const plansApi = {
  create: (data: { company_id: string; focus?: string }) =>
    api.post('/account-plans', data).then(r => r.data),
  get: (id: string) => api.get(`/account-plans/${id}`).then(r => r.data),
  update: (id: string, data: { title?: string; sections?: unknown[]; status?: string }) =>
    api.put(`/account-plans/${id}`, data).then(r => r.data),
  getVersions: (id: string) => api.get(`/account-plans/${id}/versions`).then(r => r.data),
}

// ── Feedback ───────────────────────────────────────────
export const feedbackApi = {
  submit: (recId: string, data: {
    recommendation_id: string
    company_id?: string
    feedback_type: string
    feedback_text?: string
    modified_content?: string
  }) => api.post(`/recommendations/${recId}/feedback`, data).then(r => r.data),
}

// ── Notifications ──────────────────────────────────────
export const notificationsApi = {
  list: (unread_only?: boolean) =>
    api.get('/notifications', { params: { unread_only } }).then(r => r.data),
  markRead: (id: string) => api.post(`/notifications/${id}/read`).then(r => r.data),
}

// ── Evaluation ─────────────────────────────────────────
export const evaluationApi = {
  get: () => api.get('/evaluation').then(r => r.data),
}

// ── Dashboard ──────────────────────────────────────────
export const dashboardApi = {
  stats: () => api.get('/dashboard/stats').then(r => r.data),
}

// ── Health ─────────────────────────────────────────────
export const healthApi = {
  check: () => api.get('/health').then(r => r.data),
}

export default api
