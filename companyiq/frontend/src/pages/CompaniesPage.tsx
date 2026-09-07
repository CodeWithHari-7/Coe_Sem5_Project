// Companies list page
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Building2, Plus, Search, RefreshCw, ExternalLink } from 'lucide-react'
import { companiesApi } from '../services/api'
import toast from 'react-hot-toast'

interface Company { id: string; name: string; industry?: string; size?: string; country?: string; is_demo: boolean; last_researched_at?: string }

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)
  const [newName, setNewName] = useState('')
  const [newIndustry, setNewIndustry] = useState('')
  const navigate = useNavigate()

  const load = () => {
    setLoading(true)
    companiesApi.list({ search: search || undefined })
      .then(setCompanies).catch(() => toast.error('Failed to load companies')).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [search])

  const addCompany = async () => {
    if (!newName.trim()) return
    try {
      const c = await companiesApi.create({ name: newName, industry: newIndustry })
      setCompanies(p => [c, ...p])
      setNewName(''); setNewIndustry(''); setShowAdd(false)
      toast.success(`${c.name} added!`)
    } catch { toast.error('Failed to add company') }
  }

  const refresh = async (id: string, name: string) => {
    toast.loading(`Researching ${name}...`, { id: 'refresh' })
    try {
      await companiesApi.refresh(id)
      toast.success('Research complete!', { id: 'refresh' })
      load()
    } catch { toast.error('Research failed', { id: 'refresh' }) }
  }

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="section-title"><Building2 className="w-5 h-5 text-brand-400" /> Companies</h1>
          <p className="section-subtitle">{companies.length} companies in your workspace</p>
        </div>
        <button onClick={() => setShowAdd(true)} className="btn-primary"><Plus className="w-4 h-4" /> Add Company</button>
      </div>

      {showAdd && (
        <div className="card p-4 border border-brand-800/30 animate-slide-up">
          <h3 className="text-sm font-semibold text-slate-200 mb-3">Add New Company</h3>
          <div className="flex gap-3">
            <input value={newName} onChange={e => setNewName(e.target.value)} placeholder="Company name" className="input-sm flex-1" />
            <input value={newIndustry} onChange={e => setNewIndustry(e.target.value)} placeholder="Industry (optional)" className="input-sm flex-1" />
            <button onClick={addCompany} className="btn-primary text-sm">Add</button>
            <button onClick={() => setShowAdd(false)} className="btn-ghost text-sm">Cancel</button>
          </div>
        </div>
      )}

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search companies..." className="input pl-9" />
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => <div key={i} className="skeleton h-28 rounded-2xl" />)}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {companies.map(c => (
            <div key={c.id} className="card-hover p-5 space-y-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-800 to-brand-950 flex items-center justify-center text-brand-400 font-bold">
                  {c.name.charAt(0)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-slate-200 truncate">{c.name}</p>
                  <p className="text-xs text-slate-500 truncate">{c.industry || 'Industry unknown'}</p>
                </div>
                {c.is_demo && <span className="badge-demo">Demo</span>}
              </div>
              <div className="flex items-center gap-2">
                <button onClick={() => navigate(`/research?company=${c.name}`)} className="btn-primary text-xs py-1.5 flex-1 justify-center">
                  <ExternalLink className="w-3 h-3" /> Research
                </button>
                <button onClick={() => refresh(c.id, c.name)} className="btn-secondary text-xs py-1.5 px-2.5">
                  <RefreshCw className="w-3 h-3" />
                </button>
              </div>
              {c.last_researched_at && (
                <p className="text-xs text-slate-600">Last researched: {new Date(c.last_researched_at).toLocaleDateString()}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
