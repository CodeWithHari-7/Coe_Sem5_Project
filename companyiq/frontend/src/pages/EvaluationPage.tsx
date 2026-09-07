// Evaluation Dashboard
import { useEffect, useState } from 'react'
import { BarChart3, TrendingUp, AlertCircle, CheckCircle, Target } from 'lucide-react'
import { evaluationApi } from '../services/api'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from 'recharts'

interface Metrics {
  system_type: string
  precision: number
  recall: number
  f1_score: number
  acceptance_rate: number
  avg_response_time_ms: number
  evidence_coverage: number
  false_positive_rate: number
  false_negative_rate: number
  failure_rate: number
  is_synthetic?: boolean
}

interface EvalData {
  baseline: Metrics
  ai_rag: Metrics
  improvement: Record<string, number>
  notes: string
}

export default function EvaluationPage() {
  const [data, setData] = useState<EvalData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    evaluationApi.get().then(setData).catch(() => setData(null)).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="p-6 text-slate-400">Loading evaluation data...</div>
  if (!data) return <div className="p-6 text-slate-400">No evaluation data available</div>

  const bl = data.baseline
  const ai = data.ai_rag

  const comparisonData = [
    { metric: 'Precision', baseline: +(bl.precision * 100).toFixed(1), ai_rag: +(ai.precision * 100).toFixed(1), target: 70 },
    { metric: 'Recall', baseline: +(bl.recall * 100).toFixed(1), ai_rag: +(ai.recall * 100).toFixed(1), target: 65 },
    { metric: 'F1 Score', baseline: +(bl.f1_score * 100).toFixed(1), ai_rag: +(ai.f1_score * 100).toFixed(1), target: 68 },
    { metric: 'Acceptance', baseline: +(bl.acceptance_rate * 100).toFixed(1), ai_rag: +(ai.acceptance_rate * 100).toFixed(1), target: 60 },
    { metric: 'Evidence Cov.', baseline: +(bl.evidence_coverage * 100).toFixed(1), ai_rag: +(ai.evidence_coverage * 100).toFixed(1), target: 75 },
  ]

  const radarData = [
    { subject: 'Precision', baseline: +(bl.precision * 100).toFixed(1), ai_rag: +(ai.precision * 100).toFixed(1) },
    { subject: 'Recall', baseline: +(bl.recall * 100).toFixed(1), ai_rag: +(ai.recall * 100).toFixed(1) },
    { subject: 'F1', baseline: +(bl.f1_score * 100).toFixed(1), ai_rag: +(ai.f1_score * 100).toFixed(1) },
    { subject: 'Acceptance', baseline: +(bl.acceptance_rate * 100).toFixed(1), ai_rag: +(ai.acceptance_rate * 100).toFixed(1) },
    { subject: 'Evidence', baseline: +(bl.evidence_coverage * 100).toFixed(1), ai_rag: +(ai.evidence_coverage * 100).toFixed(1) },
    { subject: 'Low Failure', baseline: +((1-bl.failure_rate) * 100).toFixed(1), ai_rag: +((1-ai.failure_rate) * 100).toFixed(1) },
  ]

  const improvementPct = data.improvement?.f1_score ?? data.improvement?.precision ?? 0

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6 animate-fade-in">
      <div>
        <h1 className="section-title"><BarChart3 className="w-5 h-5 text-brand-400" /> Evaluation Dashboard</h1>
        <p className="section-subtitle">Baseline vs. AI+RAG system comparison</p>
      </div>

      {/* Synthetic notice */}
      <div className="flex items-start gap-2 p-4 rounded-xl bg-amber-950/20 border border-amber-800/20 text-amber-300 text-sm">
        <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
        <p>{data.notes || '⚠️ Synthetic evaluation data. Real evaluation requires actual user feedback.'}</p>
      </div>

      {/* Summary metric */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'F1 Improvement', value: `+${improvementPct.toFixed(1)}%`, color: 'text-emerald-400', icon: TrendingUp },
          { label: 'AI F1 Score', value: `${(ai.f1_score * 100).toFixed(1)}%`, color: 'text-brand-400', icon: Target },
          { label: 'Acceptance Rate', value: `${(ai.acceptance_rate * 100).toFixed(1)}%`, color: 'text-amber-400', icon: CheckCircle },
          { label: 'Failure Rate', value: `${(ai.failure_rate * 100).toFixed(1)}%`, color: 'text-red-400', icon: AlertCircle },
        ].map(({ label, value, color, icon: Icon }) => (
          <div key={label} className="card p-4">
            <div className="flex items-center justify-between mb-2">
              <p className="text-xs text-slate-400">{label}</p>
              <Icon className={`w-4 h-4 ${color}`} />
            </div>
            <p className={`text-2xl font-bold ${color}`}>{value}</p>
            <p className="text-xs text-slate-600 mt-1">Synthetic Demo</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bar comparison */}
        <div className="card p-6">
          <h2 className="text-sm font-semibold text-slate-200 mb-4">Baseline vs. AI+RAG</h2>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparisonData} barGap={4}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="metric" tick={{ fill: '#64748b', fontSize: 10 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 10 }} domain={[0, 100]} />
                <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '12px', color: '#f1f5f9' }} />
                <Legend wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }} />
                <Bar dataKey="baseline" name="Baseline" fill="#475569" radius={[4, 4, 0, 0]} />
                <Bar dataKey="ai_rag" name="AI+RAG" fill="#3b5ef8" radius={[4, 4, 0, 0]} />
                <Bar dataKey="target" name="Target" fill="transparent" stroke="#34d399" strokeWidth={2} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Radar */}
        <div className="card p-6">
          <h2 className="text-sm font-semibold text-slate-200 mb-4">System Capability Radar</h2>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid stroke="#1e293b" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 10 }} />
                <Radar name="Baseline" dataKey="baseline" stroke="#475569" fill="#475569" fillOpacity={0.2} />
                <Radar name="AI+RAG" dataKey="ai_rag" stroke="#3b5ef8" fill="#3b5ef8" fillOpacity={0.3} />
                <Legend wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Detailed table */}
      <div className="card overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800/40">
          <h2 className="text-sm font-semibold text-slate-200">Detailed Metrics Comparison</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-800/40">
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Metric</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase">Baseline</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase">AI+RAG</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase">Improvement</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/40">
              {[
                { label: 'Precision', bv: bl.precision, av: ai.precision, key: 'precision' },
                { label: 'Recall', bv: bl.recall, av: ai.recall, key: 'recall' },
                { label: 'F1 Score', bv: bl.f1_score, av: ai.f1_score, key: 'f1_score' },
                { label: 'Acceptance Rate', bv: bl.acceptance_rate, av: ai.acceptance_rate, key: 'acceptance_rate' },
                { label: 'Evidence Coverage', bv: bl.evidence_coverage, av: ai.evidence_coverage, key: 'evidence_coverage' },
                { label: 'Avg Response Time', bv: bl.avg_response_time_ms, av: ai.avg_response_time_ms, key: 'response_time', isTime: true },
                { label: 'Failure Rate', bv: bl.failure_rate, av: ai.failure_rate, key: 'failure_rate', inverted: true },
              ].map(({ label, bv, av, key, isTime, inverted }) => {
                const imp = data.improvement?.[key]
                const improving = inverted ? imp !== undefined && imp > 0 : imp !== undefined && imp > 0
                return (
                  <tr key={label} className="hover:bg-slate-800/20">
                    <td className="px-6 py-3 text-slate-300 font-medium">{label}</td>
                    <td className="px-6 py-3 text-right text-slate-400">
                      {isTime ? `${bv.toFixed(0)}ms` : `${(bv * 100).toFixed(1)}%`}
                    </td>
                    <td className="px-6 py-3 text-right text-slate-200 font-medium">
                      {isTime ? `${av.toFixed(0)}ms` : `${(av * 100).toFixed(1)}%`}
                    </td>
                    <td className={`px-6 py-3 text-right font-semibold ${improving ? 'text-emerald-400' : 'text-red-400'}`}>
                      {imp !== undefined ? `${imp > 0 ? '+' : ''}${imp.toFixed(1)}%` : '—'}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
