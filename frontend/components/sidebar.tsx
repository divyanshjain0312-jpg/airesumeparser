'use client'

import { Upload, Settings, Loader2, CheckCircle2, XCircle } from 'lucide-react'
import { useRef, useState } from 'react'
import { uploadPdf } from '@/lib/api'
import type { RAGConfig } from '@/lib/api'

export type SidebarConfig = RAGConfig

interface SidebarProps {
  config: SidebarConfig
  onConfigChange: (config: SidebarConfig) => void
  onProcess: () => void
  onUploadSuccess: (sessionId: string, filename: string) => void
  isProcessing: boolean
  hasSession: boolean
  uploadedFilename: string | null
}

type UploadState =
  | { kind: 'idle' }
  | { kind: 'uploading' }
  | { kind: 'success' }
  | { kind: 'error'; message: string }

export function Sidebar({
  config,
  onConfigChange,
  onProcess,
  onUploadSuccess,
  isProcessing,
  hasSession,
  uploadedFilename,
}: SidebarProps) {
  const [uploadState, setUploadState] = useState<UploadState>({ kind: 'idle' })
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleConfigUpdate = <K extends keyof SidebarConfig>(field: K, value: SidebarConfig[K]) => {
    onConfigChange({ ...config, [field]: value })
  }

  const handleFileSelected = async (file: File | null) => {
    if (!file) return
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setUploadState({ kind: 'error', message: 'Please choose a PDF file.' })
      return
    }
    setUploadState({ kind: 'uploading' })
    try {
      const res = await uploadPdf(file)
      setUploadState({ kind: 'success' })
      onUploadSuccess(res.session_id, res.filename)
    } catch (err: any) {
      setUploadState({ kind: 'error', message: err?.message || 'Upload failed' })
    }
  }

  const openFilePicker = () => fileInputRef.current?.click()

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    const file = e.dataTransfer.files?.[0] ?? null
    handleFileSelected(file)
  }

  return (
    <div className="fixed left-0 top-0 h-full w-64 bg-card border-r border-border p-6 overflow-y-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-xl font-bold text-foreground">AI Resume Parser</h1>
      </div>

      {/* Upload Section */}
      <div className="mb-8">
        <h2 className="text-sm font-semibold text-muted-foreground mb-3 uppercase tracking-wide">
          Upload
        </h2>

        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf,.pdf"
          className="hidden"
          onChange={(e) => handleFileSelected(e.target.files?.[0] ?? null)}
        />

        <div
          onClick={openFilePicker}
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          className="border-2 border-dashed border-border rounded-lg p-4 text-center cursor-pointer hover:border-primary hover:bg-input transition-colors"
        >
          {uploadState.kind === 'uploading' ? (
            <>
              <Loader2 className="w-6 h-6 mx-auto mb-2 text-primary animate-spin" />
              <p className="text-xs text-muted-foreground">Uploading...</p>
            </>
          ) : uploadState.kind === 'success' && uploadedFilename ? (
            <>
              <CheckCircle2 className="w-6 h-6 mx-auto mb-2 text-status-loaded" />
              <p className="text-xs text-foreground font-medium truncate">{uploadedFilename}</p>
              <p className="text-xs text-muted-foreground mt-1">Click to replace</p>
            </>
          ) : uploadState.kind === 'error' ? (
            <>
              <XCircle className="w-6 h-6 mx-auto mb-2 text-destructive" />
              <p className="text-xs text-destructive">{uploadState.message}</p>
              <p className="text-xs text-muted-foreground mt-1">Click to try again</p>
            </>
          ) : (
            <>
              <Upload className="w-6 h-6 mx-auto mb-2 text-muted-foreground" />
              <p className="text-xs text-muted-foreground">Drag & drop or click</p>
              <p className="text-xs text-muted-foreground">to upload PDF</p>
            </>
          )}
        </div>
      </div>

      {/* RAG Configuration */}
      <div className="mb-8">
        <h2 className="text-sm font-semibold text-muted-foreground mb-4 uppercase tracking-wide">
          RAG Configuration
        </h2>

        {/* Chunking Strategy */}
        <div className="mb-4">
          <label className="text-xs font-medium text-muted-foreground mb-2 block">
            Chunking Strategy
          </label>
          <select
            value={config.chunking}
            onChange={(e) => handleConfigUpdate('chunking', e.target.value)}
            className="w-full bg-input border border-border rounded px-3 py-2 text-sm text-foreground hover:border-primary focus:outline-none focus:border-primary"
          >
            <option value="recursive-character">Recursive Character</option>
            <option value="fixed-size">Fixed Size</option>
            <option value="token-based">Token-based</option>
            <option value="sentence-based">Sentence-based</option>
            <option value="semantic">Semantic</option>
            <option value="document-based">Document Based</option>
          </select>
        </div>

        {/* Embedding Model */}
        <div className="mb-4">
          <label className="text-xs font-medium text-muted-foreground mb-2 block">
            Embedding Model
          </label>
          <select
            value={config.embedding}
            onChange={(e) => handleConfigUpdate('embedding', e.target.value)}
            className="w-full bg-input border border-border rounded px-3 py-2 text-sm text-foreground hover:border-primary focus:outline-none focus:border-primary"
          >
            <option value="all-MiniLM-L6-v2">all-MiniLM-L6-v2</option>
            <option value="bge-small">BGE Small</option>
            <option value="bge-base">BGE Base</option>
            <option value="e5-small">E5 Small</option>
            <option value="instructor">Instructor</option>
          </select>
        </div>

        {/* Vector Database */}
        <div className="mb-4">
          <label className="text-xs font-medium text-muted-foreground mb-2 block">
            Vector Database
          </label>
          <select
            value={config.vectorDb}
            onChange={(e) => handleConfigUpdate('vectorDb', e.target.value)}
            className="w-full bg-input border border-border rounded px-3 py-2 text-sm text-foreground hover:border-primary focus:outline-none focus:border-primary"
          >
            <option value="faiss">FAISS</option>
          </select>
        </div>

        {/* LLM */}
        <div className="mb-4">
          <label className="text-xs font-medium text-muted-foreground mb-2 block">LLM</label>
          <select
            value={config.llm}
            onChange={(e) => handleConfigUpdate('llm', e.target.value)}
            className="w-full bg-input border border-border rounded px-3 py-2 text-sm text-foreground hover:border-primary focus:outline-none focus:border-primary"
          >
            <option value="gemini">Gemini</option>
            <option value="openai">OpenAI</option>
            <option value="claude">Claude</option>
            <option value="ollama">Ollama (local)</option>
            <option value="llama">Llama (via Ollama)</option>
            <option value="mistral">Mistral (via Ollama)</option>
          </select>
        </div>

        {/* Chunk Size */}
        <div className="mb-4">
          <label className="text-xs font-medium text-muted-foreground mb-2 block">
            Chunk Size: {config.chunkSize}
          </label>
          <input
            type="range"
            min={100}
            max={2000}
            step={100}
            value={config.chunkSize}
            onChange={(e) => handleConfigUpdate('chunkSize', parseInt(e.target.value))}
            className="w-full"
          />
        </div>

        {/* Chunk Overlap */}
        <div className="mb-4">
          <label className="text-xs font-medium text-muted-foreground mb-2 block">
            Chunk Overlap: {config.chunkOverlap}
          </label>
          <input
            type="range"
            min={0}
            max={500}
            step={50}
            value={config.chunkOverlap}
            onChange={(e) => handleConfigUpdate('chunkOverlap', parseInt(e.target.value))}
            className="w-full"
          />
        </div>

        {/* Top K */}
        <div className="mb-6">
          <label className="text-xs font-medium text-muted-foreground mb-2 block">
            Top K Retrieval: {config.topK}
          </label>
          <input
            type="range"
            min={1}
            max={20}
            step={1}
            value={config.topK}
            onChange={(e) => handleConfigUpdate('topK', parseInt(e.target.value))}
            className="w-full"
          />
        </div>
      </div>

      {/* Process Button */}
      <button
        onClick={onProcess}
        disabled={!hasSession || isProcessing}
        className="w-full bg-primary hover:bg-blue-600 text-primary-foreground font-medium py-2 px-4 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {isProcessing ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            Processing...
          </>
        ) : (
          'Process Resume'
        )}
      </button>
      {!hasSession && (
        <p className="text-xs text-muted-foreground mt-2 text-center">Upload a PDF first</p>
      )}
    </div>
  )
}
