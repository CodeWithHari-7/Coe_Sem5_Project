// Opportunity panel — score breakdown, evidence, explainability
import { useState } from 'react'
import { TrendingUp, ChevronDown, ChevronRight, CheckCircle, XCircle, Info } from 'lucide-react'
import { feedbackApi } from '../services/api'
import toast from 'react-hot-toast'
import clsx from 'clsx'

interface ScoreBreakdown {
  business_relevance: number
  recent_activity: number
  product_fit: number
  historical_similarity: number
  evidence_confidence: number
  overall: number
  level: string
}

interface Evidence {
  source_type: string
  title: string
  snippet: string
  relevance_score: number
  publication_date?: string
}

interface Opp {
  id?: string
  title: string
  description: string
  what: string
  why: string
  evidence: Evidence[]
  confidence: { value: number; label: string }
  limitations: string
  score_breakdown: ScoreBreakdown
  insufficient_evidence?: boolean
}

function ScoreBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-slate-400">{label}</span>
        <span className={`font-semibold ${color}`}>{value.toFixed(0)}</span>
      </div>
      <div className="score-bar">
        <div className={`score-fill ${color.replace('text-', 'bg-')}`} style={{ width: `${value}%` }} />
      </div>
    </div>
  )
}

function LevelBadge({ level }: { level: string }) {
  return (
    <span className={clsx(
      'badge',
      level === 'HIGH' ? 'badge-high' : level === 'MEDIUM' ? 'badge-medium' : level === 'LOW' ? 'badge-low' : 'badge-very-low'
    )}>
      {level}
    </span>
  )
}

function OpportunityCard({ opp }: { opp: Opp }) {
  const [expanded, setExpanded] = useState(false)
  const [feedbackLoading, setFeedbackLoading] = useState<string | null>(null)

  const score = opp.score_breakdown
  const overall = score?.overall ?? 0
  const level = score?.level ?? 'LOW'

  const submitFeedback = async (type: string) => {
    if (!opp.id) return
    setFeedbackLoading(type)
    try {
      await feedbackApi.submit(opp.id, {
        recommendation_id: opp.id,
        feedback_type: type,
      })
      toast.success(`Feedback recorded: ${type}`)
    } catch {
      toast.error('Failed to record feedback')
    } finally {
      setFeedbackLoading(null)
    }
  }

  return (
    <div className="card-hover p-5 space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <LevelBadge level={level} />
            <span className="text-2xl font-bold text-slate-100">{overall.toFixed(0)}</span>
            <span className="text-xs text-slate-500">/100</span>
          </div>
          <h3 className="text-base font-semibold text-slate-100">{opp.title}</h3>
          <p className="text-sm text-slate-400 mt-0.5">{opp.description}</p>
        </div>
        <button onClick={() => setExpanded(!expanded)} className="p-1.5 rounded-lg hover:bg-slate-800 transition-colors">
          {expanded ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
        </button>
      </div>

      {/* Score breakdown */}
      {score && (
        <div className="space-y-2.5 pt-2 border-t border-slate-800/40">
          <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Score Breakdown</p>
          <ScoreBar label="Business Relevance (30%)" value={score.business_relevance} color="text-brand-400" />
          <ScoreBar label="Recent Activity (25%)" value={score.recent_activity} color="text-emerald-400" />
          <ScoreBar label="Product Fit (20%)" value={score.product_fit} color="text-amber-400" />
          <ScoreBar label="Historical Similarity (15%)" value={score.historical_similarity} color="text-purple-400" />
          <ScoreBar label="Evidence Confidence (10%)" value={score.evidence_confidence} color="text-cyan-400" />
        </div>
      )}

      {/* Expanded detail */}
      {expanded && (
        <div className="space-y-4 border-t border-slate-800/40 pt-4 animate-fade-in">
          {/* Explainability */}
          <div className="space-y-3">
            <div className="p-3 rounded-xl bg-slate-800/40">
              <p className="text-xs font-semibold text-brand-400 uppercase tracking-wider mb-1">WHAT</p>
              <p className="text-sm text-slate-300">{opp.what}</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-800/40">
              <p className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-1">WHY</p>
              <p className="text-sm text-slate-300">{opp.why}</p>
            </div>
            {opp.limitations && (
              <div className="p-3 rounded-xl bg-amber-950/20 border border-amber-800/20">
                <p className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-1">⚠️ LIMITATIONS</p>
                <p className="text-sm text-amber-300/80">{opp.limitations}</p>
              </div>
            )}
          </div>

          {/* Evidence */}
          {opp.evidence?.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Evidence ({opp.evidence.length})</p>
              <div className="space-y-2">
                {opp.evidence.map((ev, i) => (
                  <div key={i} className="evidence-item">
                    <div className="w-6 h-6 rounded-md bg-brand-950 border border-brand-800/40 flex items-center justify-center text-xs font-bold text-brand-400 flex-shrink-0">
                      {i + 1}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-slate-300 truncate">{ev.title}</p>
                      <p className="text-xs text-slate-500 mt-0.5 line-clamp-2">{ev.snippet}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-slate-600 capitalize">{ev.source_type}</span>
                        {ev.relevance_score > 0 && (
                          <span className="text-xs text-brand-500">{(ev.relevance_score * 100).toFixed(0)}% relevant</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Feedback */}
          <div className="flex items-center gap-2 pt-2 border-t border-slate-800/40">
            <span className="text-xs text-slate-500">Your feedback:</span>
            <button onClick={() => submitFeedback('accept')} disabled={!!feedbackLoading} className="btn-success text-xs py-1 px-2.5">
              <CheckCircle className="w-3 h-3" /> Accept
            </button>
            <button onClick={() => submitFeedback('reject')} disabled={!!feedbackLoading} className="btn-danger text-xs py-1 px-2.5">
              <XCircle className="w-3 h-3" /> Reject
            </button>
            <button onClick={() => submitFeedback('needs_more_evidence')} disabled={!!feedbackLoading} className="btn-ghost text-xs py-1 px-2.5">
              <Info className="w-3 h-3" /> Need Evidence
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export function OpportunityPanel({ opportunities }: { opportunities: unknown[] }) {
  if (!opportunities?.length) {
    return (
      <div className="flex flex-col items-center justify-center h-48 text-slate-500 text-sm space-y-2">
        <TrendingUp className="w-10 h-10 text-slate-700" />
        <p>No opportunities identified yet</p>
      </div>
    )
  }

  return (
    <div className="space-y-3 animate-fade-in">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-slate-300">{opportunities.length} Opportunities Identified</p>
        <p className="text-xs text-slate-500">Sorted by overall score</p>
      </div>
      {(opportunities as Opp[])
        .sort((a, b) => (b.score_breakdown?.overall ?? 0) - (a.score_breakdown?.overall ?? 0))
        .map((opp, i) => <OpportunityCard key={i} opp={opp} />)}
    </div>
  )
}
