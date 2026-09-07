// Zustand auth store — persists token and user to localStorage
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authApi } from '../services/api'

interface User {
  id: string
  email: string
  full_name: string
  role: string
  is_active: boolean
}

interface AuthState {
  token: string | null
  user: User | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  setAuth: (token: string, user: User) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,

      setAuth: (token, user) => {
        localStorage.setItem('companyiq_token', token)
        set({ token, user, isAuthenticated: true })
      },

      login: async (email, password) => {
        const data = await authApi.login(email, password)
        localStorage.setItem('companyiq_token', data.access_token)
        set({ token: data.access_token, user: data.user, isAuthenticated: true })
      },

      logout: () => {
        localStorage.removeItem('companyiq_token')
        localStorage.removeItem('companyiq_user')
        set({ token: null, user: null, isAuthenticated: false })
      },
    }),
    {
      name: 'companyiq_auth',
      partialize: (state) => ({ token: state.token, user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
)
