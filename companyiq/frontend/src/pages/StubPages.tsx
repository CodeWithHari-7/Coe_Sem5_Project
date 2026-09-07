// Stub pages for routes not yet fully built
import { TrendingUp, Database, History, Settings } from 'lucide-react'

function ComingSoon({ title, icon: Icon, desc }: { title: string; icon: React.FC<{className?: string}>; desc: string }) {
  return (
    <div className="p-6 flex flex-col items-center justify-center min-h-[60vh] text-center animate-fade-in">
      <div className="w-16 h-16 rounded-2xl bg-slate-800/60 flex items-center justify-center mb-4">
        <Icon className="w-8 h-8 text-brand-400" />
      </div>
      <h1 className="text-xl font-bold text-slate-200 mb-2">{title}</h1>
      <p className="text-slate-400 text-sm max-w-xs">{desc}</p>
      <span className="mt-4 badge-ai">Available in full build</span>
    </div>
  )
}

export function OpportunitiesPage() {
  return <ComingSoon title="Opportunities" icon={TrendingUp} desc="View and manage all identified opportunities across your research portfolio." />
}

export function SourcesPage() {
  return <ComingSoon title="Research Sources" icon={Database} desc="Manage ingested documents, web sources, and knowledge base content for RAG retrieval." />
}

export function HistoryPage() {
  return <ComingSoon title="Research History" icon={History} desc="Browse all past research sessions, compare results, and view change timelines." />
}

export function SettingsPage() {
  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6 animate-fade-in">
      <h1 className="section-title"><Settings className="w-5 h-5 text-brand-400" /> Settings</h1>
      <div className="card p-6 space-y-4">
        <h2 className="text-base font-semibold text-slate-200">Environment Configuration</h2>
        <div className="space-y-3 text-sm">
          {[
            { label: 'LLM Provider', value: 'DEMO (Set LLM_PROVIDER in .env)' },
            { label: 'Demo Mode', value: 'Active — set DEMO_MODE=false for live AI' },
            { label: 'Vector DB', value: 'ChromaDB (local)' },
            { label: 'Embedding Model', value: 'text-embedding-3-small' },
          ].map(({ label, value }) => (
            <div key={label} className="flex items-center justify-between p-3 rounded-xl bg-slate-800/40">
              <span className="text-slate-400">{label}</span>
              <span className="text-slate-200 font-mono text-xs">{value}</span>
            </div>
          ))}
        </div>
        <div className="p-4 rounded-xl bg-brand-950/30 border border-brand-800/30 text-sm text-brand-300">
          <p className="font-semibold mb-1">To enable live AI research:</p>
          <ol className="space-y-1 text-xs text-brand-400 list-decimal list-inside">
            <li>Add your OpenAI API key to backend/.env</li>
            <li>Set LLM_PROVIDER=openai</li>
            <li>Set DEMO_MODE=false</li>
            <li>Restart the backend server</li>
          </ol>
        </div>
      </div>
    </div>
  )
}
