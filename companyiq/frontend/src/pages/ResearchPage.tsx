import { useState, useRef, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  Send, Zap, Building2, TrendingUp,
  ChevronRight, Sparkles, Database
} from 'lucide-react'
import { researchApi } from '../services/api'
import { CompanyIntelligencePanel } from '../components/CompanyIntelligencePanel'
import { OpportunityPanel } from '../components/OpportunityPanel'
import clsx from 'clsx'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  intent?: string
  structuredData?: Record<string, unknown>
  latencyMs?: number
  isLoading?: boolean
}

const SUGGESTED_QUERIES = [
  "Research Tata Motors and identify EV opportunities",
  "Research Infosys focusing on AI and cloud services",
  "What opportunities exist for battery analytics?",
  "Who are the decision makers at Tata Motors?",
  "Create an account plan for Tata Motors",
  "What changed since the previous research?",
]

export default function ResearchPage() {
  const [searchParams] = useSearchParams()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState(searchParams.get('company') ? `Research ${searchParams.get('company')}` : '')
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'chat' | 'intelligence' | 'opportunities'>('chat')
  const [lastResult, setLastResult] = useState<Record<string, unknown> | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (text?: string) => {
    const msg = text || input.trim()
    if (!msg || loading) return
    setInput('')

    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: msg }
    const loadingMsg: Message = { id: Date.now().toString() + '_l', role: 'assistant', content: '', isLoading: true }
    setMessages(prev => [...prev, userMsg, loadingMsg])
    setLoading(true)

    try {
      const res = await researchApi.chat({
        message: msg,
        conversation_id: conversationId || undefined,
      })

      setConversationId(res.conversation_id)
      if (res.structured_data) setLastResult(res.structured_data)
      if (res.structured_data?.opportunities) setActiveTab('opportunities')
      else if (res.structured_data?.company_profile) setActiveTab('intelligence')

      setMessages(prev => prev
        .filter(m => !m.isLoading)
        .concat({
          id: res.message_id,
          role: 'assistant',
          content: res.content,
          intent: res.intent,
          structuredData: res.structured_data,
          latencyMs: res.latency_ms,
        })
      )
    } catch (err: unknown) {
      setMessages(prev => prev
        .filter(m => !m.isLoading)
        .concat({
          id: Date.now().toString(),
          role: 'assistant',
          content: 'Failed to connect to the research engine. Please check the backend is running.',
          intent: 'error',
        })
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-800/60 flex items-center justify-between flex-shrink-0">
        <div>
          <h1 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <Zap className="w-5 h-5 text-brand-400" />
            Company Research
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">AI-powered research with RAG evidence grounding</p>
        </div>
        {/* Pipeline indicator */}
        <div className="hidden md:flex items-center gap-1.5 text-xs text-slate-500">
          {['Research', 'Evidence', 'Intelligence', 'Opportunities', 'Plan'].map((step, i, arr) => (
            <span key={step} className="flex items-center gap-1.5">
              <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">{step}</span>
              {i < arr.length - 1 && <ChevronRight className="w-3 h-3" />}
            </span>
          ))}
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Chat panel */}
        <div className="flex flex-col w-full lg:w-[480px] xl:w-[520px] flex-shrink-0 border-r border-slate-800/60">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-center space-y-6 py-10 animate-fade-in">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-brand-600 to-brand-800 flex items-center justify-center shadow-xl shadow-brand-900/50">
                  <Sparkles className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-slate-200">CompanyIQ Research Assistant</h2>
                  <p className="text-slate-400 text-sm mt-2 max-w-sm">
                    Research any company with AI-powered analysis, evidence-grounded insights, and opportunity identification.
                  </p>
                </div>
                <div className="grid grid-cols-1 gap-2 w-full max-w-sm">
                  {SUGGESTED_QUERIES.map(q => (
                    <button key={q} onClick={() => sendMessage(q)}
                      className="text-left px-3 py-2.5 rounded-xl bg-slate-800/60 border border-slate-700/40 text-sm text-slate-300 hover:border-brand-700/50 hover:text-brand-300 transition-all">
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map(msg => (
              <div key={msg.id} className={clsx('flex', msg.role === 'user' ? 'justify-end' : 'justify-start')}>
                {msg.role === 'assistant' && (
                  <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-brand-600 to-brand-800 flex items-center justify-center flex-shrink-0 mr-2 mt-0.5">
                    <Zap className="w-3.5 h-3.5 text-white" />
                  </div>
                )}
                <div className={clsx(
                  'max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed',
                  msg.role === 'user'
                    ? 'bg-brand-700 text-white rounded-tr-sm'
                    : 'bg-slate-800/80 text-slate-200 rounded-tl-sm border border-slate-700/40'
                )}>
                  {msg.isLoading ? (
                    <div className="flex items-center gap-2 text-slate-400">
                      <span className="w-4 h-4 border-2 border-brand-400/30 border-t-brand-400 rounded-full animate-spin" />
                      Researching...
                    </div>
                  ) : (
                    <>
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                      <div className="flex items-center gap-3 mt-2 pt-2 border-t border-slate-700/30">
                        {msg.intent && (
                          <span className="text-xs text-slate-500 capitalize">{msg.intent}</span>
                        )}
                        {msg.latencyMs && (
                          <span className="text-xs text-slate-600">{(msg.latencyMs / 1000).toFixed(1)}s</span>
                        )}
                        {msg.structuredData?.data_label === 'DEMO_DATA' && (
                          <span className="badge-demo text-xs">Demo Data</span>
                        )}
                      </div>
                    </>
                  )}
                </div>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-slate-800/60 flex-shrink-0">
            <div className="flex items-end gap-2">
              <textarea
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage() } }}
                placeholder="Research a company, ask about opportunities, or create an account plan..."
                className="input flex-1 resize-none min-h-[48px] max-h-[120px] py-3 text-sm"
                rows={1}
              />
              <button onClick={() => sendMessage()} disabled={!input.trim() || loading} className="btn-primary p-3 flex-shrink-0">
                <Send className="w-4 h-4" />
              </button>
            </div>
            <p className="text-xs text-slate-600 mt-2">Press Enter to send · Shift+Enter for new line</p>
          </div>
        </div>

        {/* Results panel */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Tabs */}
          <div className="flex items-center gap-1 px-4 py-3 border-b border-slate-800/60 flex-shrink-0">
            {[
              { key: 'intelligence', label: 'Company Intelligence', icon: Building2 },
              { key: 'opportunities', label: 'Opportunities', icon: TrendingUp },
            ].map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                onClick={() => setActiveTab(key as typeof activeTab)}
                className={clsx(
                  'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
                  activeTab === key
                    ? 'bg-brand-600 text-white'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                )}
              >
                <Icon className="w-3.5 h-3.5" />
                {label}
              </button>
            ))}
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            {!lastResult ? (
              <div className="flex flex-col items-center justify-center h-full text-center text-slate-500 space-y-3">
                <Database className="w-12 h-12 text-slate-700" />
                <p className="text-sm">Research results will appear here</p>
                <p className="text-xs">Start by asking about a company in the chat</p>
              </div>
            ) : activeTab === 'intelligence' ? (
              <CompanyIntelligencePanel data={lastResult} />
            ) : (
              <OpportunityPanel opportunities={(lastResult?.opportunities as unknown[]) || []} />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
