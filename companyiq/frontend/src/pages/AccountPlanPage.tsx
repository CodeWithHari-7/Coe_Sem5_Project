// Account Plan Page — fully editable sections with AI/Human status tracking
import { useEffect, useState } from 'react'
import {
  FileText, Edit3, XCircle, Save,
  ChevronDown, ChevronRight, Sparkles, User, Check,
  Download
} from 'lucide-react'
import { plansApi, companiesApi } from '../services/api'
import toast from 'react-hot-toast'

interface Section {
  id: string
  title: string
  content: string
  section_type: string
  status: 'AI_GENERATED' | 'HUMAN_MODIFIED' | 'HUMAN_APPROVED'
  priority: string
  confidence?: number
  human_note?: string
  order: number
}

interface Plan {
  id: string
  title: string
  company_id: string
  version: number
  status: string
  sections: Section[]
  ai_confidence: number
  created_at: string
}

function SectionCard({ section, onUpdate, onApprove, onReject }: {
  section: Section
  onUpdate: (id: string, content: string, note: string, status: Section['status']) => void
  onApprove: (id: string) => void
  onReject: (id: string) => void
}) {
  const [editing, setEditing] = useState(false)
  const [content, setContent] = useState(section.content)
  const [note, setNote] = useState(section.human_note || '')
  const [expanded, setExpanded] = useState(true)

  const statusConfig = {
    AI_GENERATED: { label: 'AI Generated', icon: Sparkles, color: 'badge-purple' },
    HUMAN_MODIFIED: { label: 'Human Modified', icon: User, color: 'badge-amber' },
    HUMAN_APPROVED: { label: 'Human Approved', icon: Check, color: 'badge-green' },
  }
  const sc = statusConfig[section.status]

  const save = () => {
    onUpdate(section.id, content, note, 'HUMAN_MODIFIED')
    setEditing(false)
    toast.success('Section updated')
  }

  return (
    <div className="card border border-slate-800/60 overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 bg-slate-900/60">
        <div className="flex items-center gap-2">
          <button onClick={() => setExpanded(!expanded)}>
            {expanded ? <ChevronDown className="w-4 h-4 text-slate-500" /> : <ChevronRight className="w-4 h-4 text-slate-500" />}
          </button>
          <h3 className="text-sm font-semibold text-slate-200">{section.title}</h3>
          <span className={sc.color + ' badge'}><sc.icon className="w-3 h-3" />{sc.label}</span>
        </div>
        <div className="flex items-center gap-1.5">
          {!editing && section.status === 'AI_GENERATED' && (
            <>
              <button onClick={() => onApprove(section.id)} className="btn-success text-xs py-1 px-2.5">
                <Check className="w-3 h-3" /> Approve
              </button>
              <button onClick={() => setEditing(true)} className="btn-secondary text-xs py-1 px-2.5">
                <Edit3 className="w-3 h-3" /> Edit
              </button>
              <button onClick={() => onReject(section.id)} className="btn-danger text-xs py-1 px-2.5">
                <XCircle className="w-3 h-3" /> Reject
              </button>
            </>
          )}
          {!editing && section.status !== 'AI_GENERATED' && (
            <button onClick={() => setEditing(true)} className="btn-ghost text-xs py-1 px-2.5">
              <Edit3 className="w-3 h-3" /> Edit
            </button>
          )}
        </div>
      </div>

      {expanded && (
        <div className="px-4 py-4 border-t border-slate-800/40">
          {editing ? (
            <div className="space-y-3">
              <textarea
                value={content}
                onChange={e => setContent(e.target.value)}
                className="input w-full min-h-[120px] text-sm font-mono"
                rows={6}
              />
              <input
                value={note}
                onChange={e => setNote(e.target.value)}
                placeholder="Add a note about this change..."
                className="input"
              />
              <div className="flex items-center gap-2">
                <button onClick={save} className="btn-primary text-xs py-1.5 px-3">
                  <Save className="w-3 h-3" /> Save Changes
                </button>
                <button onClick={() => { setContent(section.content); setEditing(false) }} className="btn-ghost text-xs py-1.5 px-3">
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <>
              <p className="text-sm text-slate-300 whitespace-pre-wrap leading-relaxed">{section.content}</p>
              {section.human_note && (
                <div className="mt-3 p-2.5 rounded-lg bg-teal-950/20 border border-teal-800/20 text-xs text-teal-300">
                  <span className="font-semibold">Note:</span> {section.human_note}
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}

export default function AccountPlanPage() {
  const [_plans, setPlans] = useState<Plan[]>([])
  const [selectedPlan, setSelectedPlan] = useState<Plan | null>(null)
  const [companies, setCompanies] = useState<{ id: string; name: string }[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    companiesApi.list().then(setCompanies).catch(() => {})
  }, [])

  const createPlan = async (companyId: string) => {
    setLoading(true)
    try {
      const plan = await plansApi.create({ company_id: companyId })
      setSelectedPlan(plan)
      setPlans(p => [plan, ...p])
      toast.success('Account plan created!')
    } catch {
      toast.error('Failed to create account plan')
    } finally {
      setLoading(false)
    }
  }

  const updateSection = async (sectionId: string, content: string, note: string, status: Section['status']) => {
    if (!selectedPlan) return
    const updated = selectedPlan.sections.map(s =>
      s.id === sectionId ? { ...s, content, human_note: note, status } : s
    )
    const plan = await plansApi.update(selectedPlan.id, { sections: updated })
    setSelectedPlan(plan)
  }

  const approveSection = async (sectionId: string) => {
    if (!selectedPlan) return
    const updated = selectedPlan.sections.map(s =>
      s.id === sectionId ? { ...s, status: 'HUMAN_APPROVED' as const } : s
    )
    const plan = await plansApi.update(selectedPlan.id, { sections: updated })
    setSelectedPlan(plan)
    toast.success('Section approved!')
  }

  const rejectSection = (sectionId: string) => {
    if (!selectedPlan) return
    const updated = selectedPlan.sections.filter(s => s.id !== sectionId)
    plansApi.update(selectedPlan.id, { sections: updated })
      .then(plan => { setSelectedPlan(plan); toast.success('Section removed') })
  }

  const exportPlan = () => {
    if (!selectedPlan) return
    const text = selectedPlan.sections.map(s => `## ${s.title}\n\n${s.content}`).join('\n\n---\n\n')
    const blob = new Blob([`# ${selectedPlan.title}\n\n${text}`], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `account-plan-v${selectedPlan.version}.md`; a.click()
    toast.success('Plan exported!')
  }

  const aiCount = selectedPlan?.sections?.filter(s => s.status === 'AI_GENERATED').length ?? 0
  const approvedCount = selectedPlan?.sections?.filter(s => s.status === 'HUMAN_APPROVED').length ?? 0
  const modifiedCount = selectedPlan?.sections?.filter(s => s.status === 'HUMAN_MODIFIED').length ?? 0

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="section-title"><FileText className="w-5 h-5 text-brand-400" /> Account Plans</h1>
          <p className="section-subtitle">AI-generated editable account plans with human override</p>
        </div>
        <div className="flex items-center gap-2">
          {selectedPlan && (
            <>
              <button onClick={exportPlan} className="btn-secondary text-sm">
                <Download className="w-4 h-4" /> Export
              </button>
              <span className="text-xs text-slate-500">v{selectedPlan.version}</span>
            </>
          )}
        </div>
      </div>

      {!selectedPlan ? (
        <div className="space-y-4">
          <div className="card p-6">
            <h2 className="text-base font-semibold text-slate-200 mb-4">Create Account Plan</h2>
            <p className="text-sm text-slate-400 mb-4">Select a company to generate an AI-powered account plan</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {companies.slice(0, 6).map(c => (
                <button key={c.id} onClick={() => createPlan(c.id)} disabled={loading}
                  className="card-hover p-4 text-left flex items-center gap-3 group">
                  <div className="w-10 h-10 rounded-xl bg-brand-950 border border-brand-800/30 flex items-center justify-center text-brand-400 font-bold">
                    {c.name.charAt(0)}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-200">{c.name}</p>
                    <p className="text-xs text-slate-500">Generate plan →</p>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Plan meta */}
          <div className="card p-4 flex items-center justify-between gap-4">
            <div>
              <h2 className="text-base font-semibold text-slate-100">{selectedPlan.title}</h2>
              <p className="text-xs text-slate-500 mt-0.5">Version {selectedPlan.version} · AI Confidence: {Math.round((selectedPlan.ai_confidence || 0) * 100)}%</p>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 text-xs">
                <span className="badge-ai"><Sparkles className="w-3 h-3" />{aiCount} AI</span>
                <span className="badge-human"><User className="w-3 h-3" />{modifiedCount} Modified</span>
                <span className="badge-high"><Check className="w-3 h-3" />{approvedCount} Approved</span>
              </div>
              <button onClick={() => setSelectedPlan(null)} className="btn-ghost text-xs">← Back</button>
            </div>
          </div>

          {/* Sections */}
          <div className="space-y-3">
            {(selectedPlan.sections || [])
              .sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
              .map(section => (
                <SectionCard
                  key={section.id}
                  section={section}
                  onUpdate={updateSection}
                  onApprove={approveSection}
                  onReject={rejectSection}
                />
              ))}
          </div>
        </div>
      )}
    </div>
  )
}
