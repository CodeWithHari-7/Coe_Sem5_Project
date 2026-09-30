import React, { useState, useEffect } from 'react'
import {
  Database, UploadCloud, FileText, Layers, Trash2,
  RefreshCw, CheckCircle, AlertCircle, Eye, X, Sparkles, Building2
} from 'lucide-react'
import { documentsApi, companiesApi } from '../services/api'
import { useNavigate } from 'react-router-dom'

interface DocumentItem {
  id: string
  company_id: string
  title: string
  filename: string
  source_type: string
  status: string
  chunks_count: number
  word_count?: number
  created_at?: string
  error_message?: string
}

interface ChunkItem {
  id: string
  document_id: string
  chunk_index: number
  chunk_text: string
  vector_id?: string
  token_count?: number
}

interface CompanyItem {
  id: string
  name: string
  industry?: string
}

export default function SourcesPage() {
  const navigate = useNavigate()
  const [companies, setCompanies] = useState<CompanyItem[]>([])
  const [selectedCompanyId, setSelectedCompanyId] = useState<string>('')
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [activeTab, setActiveTab] = useState<'upload' | 'paste'>('upload')
  const [error, setError] = useState<string | null>(null)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)

  // Paste text state
  const [pasteTitle, setPasteTitle] = useState('')
  const [pasteType, setPasteType] = useState('annual_report')
  const [pasteContent, setPasteContent] = useState('')

  // File upload state
  const [fileToUpload, setFileToUpload] = useState<File | null>(null)
  const [fileType, setFileType] = useState('annual_report')
  const [fileTitle, setFileTitle] = useState('')

  // Chunk inspection modal
  const [selectedDocForChunks, setSelectedDocForChunks] = useState<DocumentItem | null>(null)
  const [docChunks, setDocChunks] = useState<ChunkItem[]>([])
  const [loadingChunks, setLoadingChunks] = useState(false)

  useEffect(() => {
    loadCompanies()
  }, [])

  useEffect(() => {
    loadDocuments(selectedCompanyId || undefined)
  }, [selectedCompanyId])

  const loadCompanies = async () => {
    try {
      const res = await companiesApi.list()
      const comps = res.items || res || []
      setCompanies(comps)
      if (comps.length > 0 && !selectedCompanyId) {
        setSelectedCompanyId(comps[0].id)
      }
    } catch (e: any) {
      console.error('Failed to load companies', e)
    }
  }

  const loadDocuments = async (compId?: string) => {
    setLoading(true)
    setError(null)
    try {
      const docs = await documentsApi.list(compId)
      setDocuments(docs || [])
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Failed to load documents')
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!fileToUpload) {
      setError('Please select a document file (.pdf, .docx, .txt, .md, .csv)')
      return
    }
    if (!selectedCompanyId) {
      setError('Please select a target company')
      return
    }

    setUploading(true)
    setError(null)
    try {
      await documentsApi.upload(
        selectedCompanyId,
        fileToUpload,
        fileType,
        fileTitle || fileToUpload.name
      )
      setSuccessMsg(`Document "${fileToUpload.name}" indexed successfully into ChromaDB!`)
      setFileToUpload(null)
      setFileTitle('')
      loadDocuments(selectedCompanyId)
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Failed to upload document')
    } finally {
      setUploading(false)
    }
  }

  const handlePasteIngest = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!pasteTitle.trim() || !pasteContent.trim()) {
      setError('Please provide both title and document text')
      return
    }
    if (!selectedCompanyId) {
      setError('Please select a target company')
      return
    }

    setUploading(true)
    setError(null)
    try {
      await documentsApi.ingestText({
        company_id: selectedCompanyId,
        title: pasteTitle,
        text: pasteContent,
        source_type: pasteType,
      })
      setSuccessMsg(`Text document "${pasteTitle}" chunked and indexed into ChromaDB!`)
      setPasteTitle('')
      setPasteContent('')
      loadDocuments(selectedCompanyId)
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Failed to ingest document text')
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (docId: string, title: string) => {
    if (!confirm(`Are you sure you want to delete "${title}" and its vector embeddings?`)) return
    try {
      await documentsApi.delete(docId)
      setSuccessMsg(`Document "${title}" removed from knowledge base.`)
      loadDocuments(selectedCompanyId)
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Failed to delete document')
    }
  }

  const inspectChunks = async (doc: DocumentItem) => {
    setSelectedDocForChunks(doc)
    setLoadingChunks(true)
    try {
      const chunks = await documentsApi.getChunks(doc.id)
      setDocChunks(chunks || [])
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Failed to fetch chunks')
    } finally {
      setLoadingChunks(false)
    }
  }

  const handleLaunchResearch = (compName: string) => {
    navigate('/research', { state: { prefillQuery: `Research ${compName} and identify high-value opportunities` } })
  }

  const selectedCompany = companies.find(c => c.id === selectedCompanyId)

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-3">
            <Database className="w-7 h-7 text-brand-400" />
            Research Sources & Grounded Knowledge Base
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Upload enterprise documents, reports, and whitepapers. Files are extracted, chunked, and embedded into local ChromaDB for verifiable RAG citations.
          </p>
        </div>

        {/* Company Selector */}
        <div className="flex items-center gap-3 bg-slate-900 border border-slate-800 rounded-xl px-4 py-2">
          <Building2 className="w-5 h-5 text-brand-400" />
          <div className="text-xs">
            <div className="text-slate-400 font-medium">Target Company</div>
            <select
              value={selectedCompanyId}
              onChange={e => setSelectedCompanyId(e.target.value)}
              className="bg-transparent text-slate-200 font-semibold focus:outline-none cursor-pointer text-sm"
            >
              <option value="" className="bg-slate-900 text-slate-400">All Ingested Accounts</option>
              {companies.map(c => (
                <option key={c.id} value={c.id} className="bg-slate-900 text-slate-200">
                  {c.name} {c.industry ? `(${c.industry})` : ''}
                </option>
              ))}
            </select>
          </div>
          <button
            onClick={() => loadDocuments(selectedCompanyId || undefined)}
            className="p-1.5 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-slate-200 transition"
            title="Refresh document index"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Alert Notices */}
      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-950/40 border border-red-800/40 rounded-xl text-red-300 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
          <button onClick={() => setError(null)} className="ml-auto text-red-400 hover:text-red-200"><X className="w-4 h-4" /></button>
        </div>
      )}

      {successMsg && (
        <div className="flex items-center gap-3 p-4 bg-emerald-950/40 border border-emerald-800/40 rounded-xl text-emerald-300 text-sm">
          <CheckCircle className="w-5 h-5 flex-shrink-0" />
          <span>{successMsg}</span>
          <button onClick={() => setSuccessMsg(null)} className="ml-auto text-emerald-400 hover:text-emerald-200"><X className="w-4 h-4" /></button>
        </div>
      )}

      {/* Top Split: Ingestion Form & Knowledge Base Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Document Ingestion Card (2 cols) */}
        <div className="lg:col-span-2 card p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h2 className="text-base font-semibold text-slate-200 flex items-center gap-2">
              <UploadCloud className="w-5 h-5 text-brand-400" />
              Ingest Grounded Evidence Document
            </h2>
            <div className="flex rounded-lg bg-slate-800/70 p-1 text-xs font-medium">
              <button
                type="button"
                onClick={() => setActiveTab('upload')}
                className={`px-3 py-1 rounded-md transition ${activeTab === 'upload' ? 'bg-brand-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
              >
                File Upload
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('paste')}
                className={`px-3 py-1 rounded-md transition ${activeTab === 'paste' ? 'bg-brand-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
              >
                Raw Text / Report
              </button>
            </div>
          </div>

          {activeTab === 'upload' ? (
            <form onSubmit={handleFileUpload} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Document Title (Optional)</label>
                  <input
                    type="text"
                    placeholder="e.g. Q4 Strategic Review 2024"
                    value={fileTitle}
                    onChange={e => setFileTitle(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-brand-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Source Category</label>
                  <select
                    value={fileType}
                    onChange={e => setFileType(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-brand-500"
                  >
                    <option value="annual_report">Annual Report / 10-K Filing</option>
                    <option value="whitepaper">Technical Whitepaper</option>
                    <option value="press_release">Press Release / News</option>
                    <option value="research_paper">Market Research Paper</option>
                    <option value="financial_report">Financial Statements</option>
                  </select>
                </div>
              </div>

              <div className="border-2 border-dashed border-slate-700 hover:border-brand-500/60 rounded-xl p-6 text-center transition cursor-pointer bg-slate-900/40">
                <input
                  type="file"
                  id="doc-upload-input"
                  accept=".pdf,.docx,.txt,.md,.csv,.json"
                  onChange={e => e.target.files && setFileToUpload(e.target.files[0])}
                  className="hidden"
                />
                <label htmlFor="doc-upload-input" className="cursor-pointer flex flex-col items-center">
                  <FileText className="w-10 h-10 text-brand-400 mb-2" />
                  {fileToUpload ? (
                    <div>
                      <span className="text-sm font-semibold text-brand-300">{fileToUpload.name}</span>
                      <span className="text-xs text-slate-400 block mt-0.5">({(fileToUpload.size / 1024).toFixed(1)} KB)</span>
                    </div>
                  ) : (
                    <div>
                      <span className="text-sm font-medium text-slate-300">Click to choose file or drag & drop</span>
                      <span className="text-xs text-slate-500 block mt-1">Supports PDF, DOCX, TXT, MD, CSV (Max 25MB)</span>
                    </div>
                  )}
                </label>
              </div>

              <button
                type="submit"
                disabled={uploading || !fileToUpload || !selectedCompanyId}
                className="w-full py-2.5 px-4 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-medium text-sm transition disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {uploading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Extracting Text & Generating ChromaDB Embeddings...
                  </>
                ) : (
                  <>
                    <UploadCloud className="w-4 h-4" />
                    Upload & Ingest to Vector Store
                  </>
                )}
              </button>
            </form>
          ) : (
            <form onSubmit={handlePasteIngest} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Document Title</label>
                  <input
                    type="text"
                    placeholder="e.g. Executive Interview Notes"
                    value={pasteTitle}
                    onChange={e => setPasteTitle(e.target.value)}
                    required
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-brand-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Source Category</label>
                  <select
                    value={pasteType}
                    onChange={e => setPasteType(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-brand-500"
                  >
                    <option value="annual_report">Annual Report / Filing</option>
                    <option value="whitepaper">Strategic Whitepaper</option>
                    <option value="press_release">Corporate Communication</option>
                    <option value="news">Industry News</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Document Content</label>
                <textarea
                  rows={6}
                  placeholder="Paste multi-paragraph corporate filing text, strategic priorities, financial highlights, or operational pain points..."
                  value={pasteContent}
                  onChange={e => setPasteContent(e.target.value)}
                  required
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-sm text-slate-200 font-mono focus:outline-none focus:border-brand-500"
                />
              </div>

              <button
                type="submit"
                disabled={uploading || !pasteContent.trim() || !pasteTitle.trim() || !selectedCompanyId}
                className="w-full py-2.5 px-4 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-medium text-sm transition disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {uploading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Chunking & Indexing Text...
                  </>
                ) : (
                  <>
                    <Layers className="w-4 h-4" />
                    Process Chunks & Ingest
                  </>
                )}
              </button>
            </form>
          )}
        </div>

        {/* Knowledge Base Status & Quick Guide */}
        <div className="card p-6 flex flex-col justify-between space-y-4">
          <div>
            <h2 className="text-base font-semibold text-slate-200 flex items-center gap-2 mb-3">
              <Sparkles className="w-5 h-5 text-amber-400" />
              Verifiable RAG Architecture
            </h2>
            <div className="space-y-3 text-xs text-slate-300">
              <div className="p-3 bg-slate-800/40 rounded-xl border border-slate-700/50">
                <span className="font-semibold text-brand-300 block mb-1">1. Multi-Format Ingestion</span>
                Parses PDF, DOCX, TXT, and Markdown files while stripping headers, footnotes, and formatting artifacts.
              </div>
              <div className="p-3 bg-slate-800/40 rounded-xl border border-slate-700/50">
                <span className="font-semibold text-brand-300 block mb-1">2. Semantic Chunking & ChromaDB</span>
                Segments documents into 500-token chunks with 50-token overlap, indexed with unique chunk IDs.
              </div>
              <div className="p-3 bg-slate-800/40 rounded-xl border border-slate-700/50">
                <span className="font-semibold text-brand-300 block mb-1">3. Citation Grounding</span>
                Every opportunity and account plan section references specific chunk IDs (<code className="text-amber-300">[Chunk #chk_...]</code>) for auditability.
              </div>
            </div>
          </div>

          {selectedCompany && (
            <div className="pt-2 border-t border-slate-800">
              <button
                onClick={() => handleLaunchResearch(selectedCompany.name)}
                className="w-full py-2.5 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-brand-300 font-semibold text-xs border border-brand-800/40 flex items-center justify-center gap-2 transition"
              >
                <Sparkles className="w-4 h-4 text-brand-400" />
                Launch Research for {selectedCompany.name}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Ingested Documents List */}
      <div className="card p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-brand-400" />
            <h2 className="text-base font-semibold text-slate-200">
              Ingested Documents ({documents.length})
            </h2>
          </div>
          <span className="text-xs text-slate-400">
            {selectedCompany ? `Filtered for ${selectedCompany.name}` : 'Showing all knowledge base documents'}
          </span>
        </div>

        {loading ? (
          <div className="py-12 text-center text-slate-400 flex items-center justify-center gap-2 text-sm">
            <RefreshCw className="w-5 h-5 animate-spin text-brand-400" />
            Loading knowledge base documents...
          </div>
        ) : documents.length === 0 ? (
          <div className="py-12 text-center text-slate-500 text-sm">
            No source documents uploaded for this company yet. Upload a corporate report or paste notes above to seed verifiable evidence.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="text-xs uppercase bg-slate-800/40 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Document Title</th>
                  <th className="py-3 px-4">Filename</th>
                  <th className="py-3 px-4">Source Type</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Chunks</th>
                  <th className="py-3 px-4">Words</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {documents.map(doc => (
                  <tr key={doc.id} className="hover:bg-slate-800/30 transition">
                    <td className="py-3 px-4 font-medium text-slate-200">{doc.title}</td>
                    <td className="py-3 px-4 font-mono text-xs text-slate-400">{doc.filename}</td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-slate-800 text-brand-300 border border-slate-700">
                        {doc.source_type.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                        doc.status === 'indexed' || doc.status === 'ready'
                          ? 'bg-emerald-950/50 text-emerald-300 border border-emerald-800/50'
                          : 'bg-amber-950/50 text-amber-300 border border-amber-800/50'
                      }`}>
                        <CheckCircle className="w-3 h-3" />
                        {doc.status}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-semibold text-slate-200">{doc.chunks_count}</span>
                    </td>
                    <td className="py-3 px-4 text-slate-400">{doc.word_count || '—'}</td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => inspectChunks(doc)}
                          className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 hover:text-white transition flex items-center gap-1"
                          title="Inspect chunks & vector IDs"
                        >
                          <Eye className="w-3.5 h-3.5 text-brand-400" />
                          View Chunks
                        </button>
                        <button
                          onClick={() => handleDelete(doc.id, doc.title)}
                          className="p-1.5 rounded-lg hover:bg-red-950/60 text-slate-400 hover:text-red-400 transition"
                          title="Delete document"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Chunk Inspection Modal */}
      {selectedDocForChunks && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-4xl w-full max-h-[85vh] flex flex-col shadow-2xl">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-5 border-b border-slate-800">
              <div>
                <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                  <Layers className="w-5 h-5 text-brand-400" />
                  Chunk Provenance: {selectedDocForChunks.title}
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Document ID: <code className="text-brand-300">{selectedDocForChunks.id}</code> | Total Chunks: {docChunks.length}
                </p>
              </div>
              <button
                onClick={() => setSelectedDocForChunks(null)}
                className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body: Chunks */}
            <div className="p-5 overflow-y-auto space-y-4">
              {loadingChunks ? (
                <div className="py-8 text-center text-slate-400 flex items-center justify-center gap-2 text-sm">
                  <RefreshCw className="w-4 h-4 animate-spin text-brand-400" />
                  Fetching chunk segments from database...
                </div>
              ) : docChunks.length === 0 ? (
                <div className="py-8 text-center text-slate-500 text-sm">
                  No chunks stored for this document.
                </div>
              ) : (
                docChunks.map((chunk, idx) => (
                  <div key={chunk.id} className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-brand-300 flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-brand-400 inline-block" />
                        Chunk #{idx + 1} (<code className="text-amber-300">{chunk.id}</code>)
                      </span>
                      <span className="text-slate-400 font-mono">
                        Vector ID: {chunk.vector_id || 'N/A'} {chunk.token_count ? `| ~${chunk.token_count} tokens` : ''}
                      </span>
                    </div>
                    <p className="text-xs text-slate-200 font-mono whitespace-pre-wrap leading-relaxed bg-slate-950/60 p-3 rounded-lg border border-slate-800">
                      {chunk.chunk_text}
                    </p>
                  </div>
                ))
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-slate-800 flex justify-end">
              <button
                onClick={() => setSelectedDocForChunks(null)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium transition"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
