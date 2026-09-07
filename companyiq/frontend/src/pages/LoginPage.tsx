import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { Zap, Eye, EyeOff, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const [email, setEmail] = useState('analyst@companyiq.demo')
  const [password, setPassword] = useState('Analyst@1234')
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { login } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      toast.success('Welcome to CompanyIQ!')
      navigate('/dashboard')
    } catch {
      setError('Invalid email or password. Try demo credentials below.')
    } finally {
      setLoading(false)
    }
  }

  const demoAccounts = [
    { role: 'Admin', email: 'admin@companyiq.demo', password: 'Admin@1234', color: 'text-purple-400' },
    { role: 'Manager', email: 'manager@companyiq.demo', password: 'Manager@1234', color: 'text-amber-400' },
    { role: 'Analyst', email: 'analyst@companyiq.demo', password: 'Analyst@1234', color: 'text-brand-400' },
  ]

  return (
    <div className="min-h-screen flex bg-slate-950">
      {/* Left — branding panel */}
      <div className="hidden lg:flex lg:flex-1 flex-col justify-between p-12 bg-gradient-to-br from-brand-950 via-slate-900 to-slate-950 border-r border-slate-800/40">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <span className="text-xl font-bold text-white">CompanyIQ</span>
        </div>

        <div className="space-y-8 animate-fade-in">
          <div>
            <h2 className="text-4xl font-bold text-white leading-tight">
              AI-Powered<br />Company Intelligence<br />
              <span className="text-brand-400">for Modern Teams</span>
            </h2>
            <p className="mt-4 text-slate-400 text-lg leading-relaxed">
              Research companies, identify opportunities, and generate editable account plans — powered by RAG and explainable AI.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {[
              { label: 'Research Sources', value: '6+', icon: '🔍' },
              { label: 'AI Confidence', value: '87%', icon: '🧠' },
              { label: 'Opportunities Found', value: '3x', icon: '🚀' },
              { label: 'Time Saved', value: '10h/week', icon: '⚡' },
            ].map(({ label, value, icon }) => (
              <div key={label} className="card p-4">
                <div className="text-2xl mb-1">{icon}</div>
                <div className="text-2xl font-bold text-brand-400">{value}</div>
                <div className="text-xs text-slate-500">{label}</div>
              </div>
            ))}
          </div>
        </div>

        <p className="text-xs text-slate-600">
          CompanyIQ v1.0 — Demo mode active. All research data is synthetic.
        </p>
      </div>

      {/* Right — login form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md animate-slide-up">
          {/* Mobile logo */}
          <div className="flex lg:hidden items-center gap-3 mb-8">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white">CompanyIQ</span>
          </div>

          <h2 className="text-2xl font-bold text-slate-100 mb-1">Sign in</h2>
          <p className="text-slate-400 text-sm mb-8">Use a demo account to explore the platform</p>

          {error && (
            <div className="flex items-center gap-2 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm mb-6">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm font-medium text-slate-300 mb-1.5 block">Email</label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="input"
                placeholder="you@company.com"
                required
              />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-300 mb-1.5 block">Password</label>
              <div className="relative">
                <input
                  type={showPass ? 'text' : 'password'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  className="input pr-12"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPass(!showPass)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                >
                  {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button type="submit" disabled={loading} className="btn-primary w-full justify-center py-3 text-base mt-2">
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                  Signing in...
                </span>
              ) : 'Sign In'}
            </button>
          </form>

          {/* Demo accounts */}
          <div className="mt-8">
            <p className="text-xs text-slate-500 mb-3 text-center">Quick demo access</p>
            <div className="space-y-2">
              {demoAccounts.map(acc => (
                <button
                  key={acc.role}
                  onClick={() => { setEmail(acc.email); setPassword(acc.password) }}
                  className="w-full flex items-center justify-between px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition-colors text-sm"
                >
                  <span className={`font-medium ${acc.color}`}>{acc.role}</span>
                  <span className="text-slate-500 text-xs">{acc.email}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
