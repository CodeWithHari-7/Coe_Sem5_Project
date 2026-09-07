// Notifications page
import { useEffect, useState } from 'react'
import { Bell, CheckCircle, AlertTriangle, Info } from 'lucide-react'
import { notificationsApi } from '../services/api'
import clsx from 'clsx'

interface Notification { id: string; title: string; message: string; notification_type: string; impact_level: string; is_read: boolean; created_at: string; company_id?: string }

export default function NotificationsPage() {
  const [notifs, setNotifs] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    notificationsApi.list().then(setNotifs).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const markRead = async (id: string) => {
    await notificationsApi.markRead(id)
    setNotifs(p => p.map(n => n.id === id ? { ...n, is_read: true } : n))
  }

  const impactIcon = (impact: string) => {
    if (impact === 'high') return <AlertTriangle className="w-4 h-4 text-red-400" />
    if (impact === 'medium') return <Info className="w-4 h-4 text-amber-400" />
    return <CheckCircle className="w-4 h-4 text-emerald-400" />
  }

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-4 animate-fade-in">
      <div>
        <h1 className="section-title"><Bell className="w-5 h-5 text-brand-400" /> Notifications</h1>
        <p className="section-subtitle">Research updates and change alerts</p>
      </div>

      {loading ? (
        <div className="space-y-3">{[...Array(4)].map((_, i) => <div key={i} className="skeleton h-20 rounded-2xl" />)}</div>
      ) : notifs.length === 0 ? (
        <div className="card p-12 text-center text-slate-500">
          <Bell className="w-12 h-12 text-slate-700 mx-auto mb-3" />
          <p>No notifications yet</p>
          <p className="text-xs mt-1">Refresh research on a company to detect changes</p>
        </div>
      ) : (
        <div className="space-y-3">
          {notifs.map(n => (
            <div key={n.id} className={clsx('card p-4 flex items-start gap-4', !n.is_read && 'border-brand-800/40 bg-brand-950/20')}>
              <div className="flex-shrink-0 mt-0.5">{impactIcon(n.impact_level)}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <p className="text-sm font-semibold text-slate-200">{n.title}</p>
                  {!n.is_read && <span className="w-2 h-2 rounded-full bg-brand-500 flex-shrink-0" />}
                </div>
                <p className="text-sm text-slate-400">{n.message}</p>
                <p className="text-xs text-slate-600 mt-1">{new Date(n.created_at).toLocaleString()}</p>
              </div>
              {!n.is_read && (
                <button onClick={() => markRead(n.id)} className="btn-ghost text-xs py-1 px-2">Mark read</button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
