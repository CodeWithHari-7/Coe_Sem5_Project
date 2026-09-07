// Company Intelligence Panel — displays structured research results
import { ChevronDown, ChevronRight, Shield, TrendingUp, Users, Cpu, AlertTriangle } from 'lucide-react'
import { useState } from 'react'
import clsx from 'clsx'

interface Props { data: Record<string, unknown> }

export function CompanyIntelligencePanel({ data }: Props) {
  const profile = (data?.company_profile || data) as Record<string, unknown>
  const [expanded, setExpanded] = useState<Set<string>>(new Set(['overview', 'strategic']))

  const toggle = (key: string) => setExpanded(prev => {
    const s = new Set(prev)
    s.has(key) ? s.delete(key) : s.add(key)
    return s
  })

  const conf = profile?.confidence as { value?: number; label?: string; basis?: string } | undefined
  const confidencePct = conf?.value ? Math.round(conf.value * 100) : 0

  const Section = ({ id, title, icon: Icon, children }: { id: string; title: string; icon: React.FC<{className?: string}>; children: React.ReactNode }) => (
    <div className="card border border-slate-800/60 overflow-hidden">
      <button className="w-full flex items-center justify-between px-4 py-3 hover:bg-slate-800/30 transition-colors" onClick={() => toggle(id)}>
        <div className="flex items-center gap-2 text-sm font-medium text-slate-200">
          <Icon className="w-4 h-4 text-brand-400" />
          {title}
        </div>
        {expanded.has(id) ? <ChevronDown className="w-4 h-4 text-slate-500" /> : <ChevronRight className="w-4 h-4 text-slate-500" />}
      </button>
      {expanded.has(id) && <div className="px-4 pb-4 border-t border-slate-800/40">{children}</div>}
    </div>
  )

  const ListItems = ({ items }: { items: unknown[] }) => (
    <ul className="mt-3 space-y-1.5">
      {(items || []).map((item, i) => (
        <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
          <span className="w-1.5 h-1.5 rounded-full bg-brand-500 mt-1.5 flex-shrink-0" />
          {String(item)}
        </li>
      ))}
    </ul>
  )

  if (!profile?.name && !profile?.company_name) {
    return <div className="text-slate-500 text-sm text-center py-8">No intelligence data available yet.</div>
  }

  return (
    <div className="space-y-3 animate-fade-in">
      {/* Header card */}
      <div className="card p-5 glow-brand">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-brand-700 to-brand-900 flex items-center justify-center text-xl font-bold text-brand-300 flex-shrink-0">
              {String(profile.name || '?').charAt(0)}
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-100">{String(profile.name || 'Company')}</h2>
              <p className="text-sm text-slate-400">{String(profile.industry || '')}</p>
              {(data as Record<string, unknown>)?.data_label === 'DEMO_DATA' && <span className="badge-demo mt-1">Demo Data</span>}
            </div>
          </div>
          {conf && (
            <div className="text-center flex-shrink-0">
              <div className={clsx(
                'text-2xl font-bold',
                confidencePct >= 80 ? 'text-emerald-400' : confidencePct >= 60 ? 'text-amber-400' : 'text-red-400'
              )}>
                {confidencePct}%
              </div>
              <div className="text-xs text-slate-500">Confidence</div>
              <div className="text-xs text-slate-600 capitalize">{conf.label}</div>
            </div>
          )}
        </div>
        {Boolean(profile.description) && (
          <p className="text-sm text-slate-300 mt-4 leading-relaxed">{String(profile.description)}</p>
        )}
      </div>

      <Section id="overview" title="Business Overview" icon={Shield}>
        <div className="mt-3 grid grid-cols-2 gap-3">
          {Boolean(profile.market_position) && <div className="col-span-2 p-3 rounded-lg bg-slate-800/40 text-sm text-slate-300"><span className="text-xs text-slate-500 block mb-1">Market Position</span>{String(profile.market_position)}</div>}
          {Boolean(profile.business_model) && <div className="col-span-2 p-3 rounded-lg bg-slate-800/40 text-sm text-slate-300"><span className="text-xs text-slate-500 block mb-1">Business Model</span>{String(profile.business_model)}</div>}
        </div>
      </Section>

      <Section id="products" title="Products & Services" icon={Cpu}>
        <ListItems items={(profile.products_services as unknown[]) || []} />
      </Section>

      <Section id="strategic" title="Strategic Priorities" icon={TrendingUp}>
        <ListItems items={(profile.strategic_priorities as unknown[]) || []} />
      </Section>

      <Section id="tech" title="Technology Focus" icon={Cpu}>
        <div className="flex flex-wrap gap-2 mt-3">
          {((profile.technologies as string[]) || []).map((t: string) => (
            <span key={t} className="px-2.5 py-1 rounded-lg bg-brand-950/60 border border-brand-800/30 text-brand-300 text-xs font-medium">{t}</span>
          ))}
        </div>
      </Section>

      <Section id="challenges" title="Potential Challenges" icon={AlertTriangle}>
        <ListItems items={(profile.potential_challenges as unknown[]) || []} />
      </Section>

      <Section id="stakeholders" title="Decision Maker Roles" icon={Users}>
        <ListItems items={(profile.decision_maker_roles as unknown[]) || []} />
        <p className="text-xs text-slate-600 mt-2">⚠️ AI hypothesis — verify actual decision makers before outreach</p>
      </Section>

      <Section id="recent" title="Recent Developments" icon={TrendingUp}>
        <ListItems items={(profile.recent_developments as unknown[]) || []} />
      </Section>
    </div>
  )
}
