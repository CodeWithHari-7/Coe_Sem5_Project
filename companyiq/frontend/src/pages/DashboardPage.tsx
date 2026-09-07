import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Building2, FileText, CheckCircle,
  AlertCircle, ArrowRight, Zap
} from 'lucide-react'
import { dashboardApi } from '../services/api'
import { useAuthStore } from '../store/authStore'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const activityData = [
  { day: 'Mon', researches: 4, plans: 2 },
  { day: 'Tue', researches: 7, plans: 3 },
  { day: 'Wed', researches: 5, plans: 4 },
  { day: 'Thu', researches: 9, plans: 5 },
  { day: 'Fri', researches: 12, plans: 6 },
  { day: 'Sat', researches: 3, plans: 1 },
  { day: 'Sun', researches: 6, plans: 3 },
]

interface Stats {
  total_companies: number
  active_plans: number
  total_plans: number
  acceptance_rate: number
  avg_response_time_ms: number
  unread_notifications: number
  recent_companies: { id: string; name: string; industry: string; is_demo: boolean }[]
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  const navigate = useNavigate()
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    dashboardApi.stats()
      .then(setStats)
      .catch(() => setStats({
        total_companies: 10, active_plans: 3, total_plans: 7,
        acceptance_rate: 68, avg_response_time_ms: 1850,
        unread_notifications: 2,
        recent_companies: [
          { id: '1', name: 'Tata Motors', industry: 'Automotive / EV', is_demo: true },
          { id: '2', name: 'Infosys', industry: 'IT Services', is_demo: true },
        ]
      }))
      .finally(() => setLoading(false))
  }, [])

  const metricCards = [
    { label: 'Researched Companies', value: stats?.total_companies ?? '—', icon: Building2, color: 'text-brand-400', bg: 'bg-brand-950/40 border-brand-800/30' },
    { label: 'Active Account Plans', value: stats?.active_plans ?? '—', icon: FileText, color: 'text-emerald-400', bg: 'bg-emerald-950/30 border-emerald-800/20' },
    { label: 'Acceptance Rate', value: stats ? `${stats.acceptance_rate}%` : '—', icon: CheckCircle, color: 'text-amber-400', bg: 'bg-amber-950/30 border-amber-800/20' },
    { label: 'Avg Response Time', value: stats ? `${(stats.avg_response_time_ms / 1000).toFixed(1)}s` : '—', icon: Zap, color: 'text-purple-400', bg: 'bg-purple-950/30 border-purple-800/20' },
  ]

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">
            Welcome back, {user?.full_name?.split(' ')[0]} 👋
          </h1>
          <p className="text-slate-400 text-sm mt-0.5">Here's your research intelligence overview</p>
        </div>
        <button onClick={() => navigate('/research')} className="btn-primary">
          <Zap className="w-4 h-4" />
          Start Research
        </button>
      </div>

      {/* Demo banner */}
      <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-300 text-sm">
        <AlertCircle className="w-4 h-4 flex-shrink-0" />
        <span><strong>Demo Mode Active</strong> — All data is synthetic. Set <code className="text-xs bg-slate-800 px-1 rounded">DEMO_MODE=false</code> and add your LLM API key for live research.</span>
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {metricCards.map(({ label, value, icon: Icon, color, bg }) => (
          <div key={label} className={`card p-5 border ${bg}`}>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{label}</span>
              <div className={`p-2 rounded-lg bg-slate-800/60`}>
                <Icon className={`w-4 h-4 ${color}`} />
              </div>
            </div>
            {loading ? (
              <div className="skeleton h-8 w-20 rounded" />
            ) : (
              <div className={`text-3xl font-bold ${color}`}>{value}</div>
            )}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Activity chart */}
        <div className="xl:col-span-2 card p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-semibold text-slate-100">Research Activity</h2>
              <p className="text-xs text-slate-400">This week's research and planning sessions</p>
            </div>
            <span className="badge-demo">Demo Data</span>
          </div>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={activityData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorR" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b5ef8" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b5ef8" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorP" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#34d399" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#34d399" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="day" tick={{ fill: '#64748b', fontSize: 11 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
                <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '12px', color: '#f1f5f9' }} />
                <Area type="monotone" dataKey="researches" stroke="#3b5ef8" fill="url(#colorR)" strokeWidth={2} name="Researches" />
                <Area type="monotone" dataKey="plans" stroke="#34d399" fill="url(#colorP)" strokeWidth={2} name="Plans" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent companies */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-slate-100">Recent Companies</h2>
            <button onClick={() => navigate('/companies')} className="text-xs text-brand-400 hover:text-brand-300">
              View all
            </button>
          </div>
          <div className="space-y-3">
            {stats?.recent_companies?.map(company => (
              <button
                key={company.id}
                onClick={() => navigate(`/research?company=${company.name}`)}
                className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-slate-800/60 transition-colors text-left group"
              >
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-800 to-brand-950 flex items-center justify-center text-brand-400 text-sm font-bold flex-shrink-0">
                  {company.name.charAt(0)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-200 truncate">{company.name}</p>
                  <p className="text-xs text-slate-500 truncate">{company.industry}</p>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-brand-400 transition-colors" />
              </button>
            ))}
          </div>
          <button onClick={() => navigate('/research')} className="btn-primary w-full justify-center mt-4">
            <Zap className="w-4 h-4" />
            Research a Company
          </button>
        </div>
      </div>
    </div>
  )
}
