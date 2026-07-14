'use client'

import { useState } from 'react'
import {
  FileText,
  Clock,
  Layers,
  BarChart3,
  Send,
  Loader2,
  AlertCircle,
} from 'lucide-react'
import { Sidebar, type SidebarConfig } from '@/components/sidebar'
import { StatusCard } from '@/components/status-card'
import { StatusBadge } from '@/components/status-badge'
import { Accordion, SkeletonLoader, CodeBlock } from '@/components/accordion'
import { Tabs } from '@/components/tabs'
import {
  processResume,
  askQuestion,
  saveSession,
  type ProcessResponse,
  type QueryResponse,
} from '@/lib/api'

const DEFAULT_CONFIG: SidebarConfig = {
  chunking: 'recursive-character',
  embedding: 'all-MiniLM-L6-v2',
  vectorDb: 'faiss',
  llm: 'gemini',
  chunkSize: 1000,
  chunkOverlap: 200,
  topK: 5,
}

export default function Page() {
  // --- config lives here so both sidebar and process/query can read it ---
  const [config, setConfig] = useState<SidebarConfig>(DEFAULT_CONFIG)

  // --- session ---
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [uploadedFilename, setUploadedFilename] = useState<string | null>(null)

  // --- pipeline results ---
  const [processResult, setProcessResult] = useState<ProcessResponse | null>(null)
  const [queryResult, setQueryResult] = useState<QueryResponse | null>(null)

  // --- pipeline flags ---
  const [isProcessing, setIsProcessing] = useState(false)
  const [isQuerying, setIsQuerying] = useState(false)
  const [processError, setProcessError] = useState<string | null>(null)
  const [queryError, setQueryError] = useState<string | null>(null)

  // --- question box ---
  const [question, setQuestion] = useState('Summarize this candidate’s experience.')

  const handleUploadSuccess = (id: string, filename: string) => {
    setSessionId(id)
    setUploadedFilename(filename)
    // Reset any previous run — a new upload starts a new session
    setProcessResult(null)
    setQueryResult(null)
    setProcessError(null)
    setQueryError(null)
    // Persist so the Skill Gap page can reuse this session
    saveSession({ sessionId: id, filename, config, processed: false })
  }

  const handleConfigChange = (newConfig: SidebarConfig) => {
    setConfig(newConfig)
    if (sessionId && uploadedFilename) {
      saveSession({
        sessionId,
        filename: uploadedFilename,
        config: newConfig,
        processed: processResult !== null,
      })
    }
  }

  const handleProcess = async () => {
    if (!sessionId) return
    setIsProcessing(true)
    setProcessError(null)
    setQueryResult(null)
    setQueryError(null)
    try {
      const res = await processResume(sessionId, config)
      setProcessResult(res)
      // Mark this session processed so the Skill Gap page can use it
      if (uploadedFilename) {
        saveSession({ sessionId, filename: uploadedFilename, config, processed: true })
      }
    } catch (err: any) {
      setProcessError(err?.message || 'Processing failed')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleAsk = async () => {
    if (!sessionId || !processResult || !question.trim()) return
    setIsQuerying(true)
    setQueryError(null)
    try {
      const res = await askQuestion(sessionId, question.trim(), config)
      setQueryResult(res)
    } catch (err: any) {
      setQueryError(err?.message || 'Query failed')
    } finally {
      setIsQuerying(false)
    }
  }

  // --- derive card values from live state ---
  const uploadStatusValue = uploadedFilename ? 'Loaded' : 'No file'
  const uploadStatusState: 'idle' | 'loading' | 'success' | 'error' = isProcessing
    ? 'loading'
    : processResult
    ? 'success'
    : uploadedFilename
    ? 'success'
    : 'idle'

  const processingTimeValue = isProcessing
    ? '...'
    : processResult
    ? `${processResult.processing_time_seconds}s`
    : queryResult
    ? `${queryResult.processing_time_seconds}s (query)`
    : '—'

  const embeddingInfoValue = processResult
    ? `${processResult.embedding_dimension}-d`
    : '—'

  const numChunksValue = processResult ? String(processResult.num_chunks) : '—'

  // --- accordion content ---
  const accordionItems = [
    {
      id: 'extracted-text',
      title: 'Extracted Text Preview',
      badge: processResult ? <StatusBadge status="parsed" /> : null,
      content: isProcessing ? (
        <SkeletonLoader />
      ) : processResult ? (
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground">
            {processResult.total_pages} page(s) · {processResult.total_characters.toLocaleString()} chars
          </p>
          <pre className="whitespace-pre-wrap text-xs bg-input border border-border rounded p-3 max-h-72 overflow-y-auto">
            {processResult.extracted_text_preview}
          </pre>
        </div>
      ) : (
        <p className="text-xs italic">Process a resume to see the extracted text.</p>
      ),
    },
    {
      id: 'chunks',
      title: 'Chunk Preview',
      badge: processResult ? <StatusBadge status="chunked" /> : null,
      content: isProcessing ? (
        <SkeletonLoader />
      ) : processResult ? (
        <div className="space-y-3">
          <p className="text-xs text-muted-foreground">
            {processResult.num_chunks} chunks total · showing first{' '}
            {Math.min(processResult.chunks.length, 8)}
          </p>
          {processResult.chunks.slice(0, 8).map((c) => (
            <div
              key={c.index}
              className="bg-input p-3 rounded border border-border text-xs"
            >
              <p className="text-muted-foreground mb-2">
                Chunk {c.index} · {c.char_count} chars
              </p>
              <p className="whitespace-pre-wrap">{c.content}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-xs italic">Chunks appear after processing.</p>
      ),
    },
    {
      id: 'retrieved-chunks',
      title: 'Retrieved Chunks',
      badge: queryResult ? <StatusBadge status="retrieved" /> : null,
      content: isQuerying ? (
        <SkeletonLoader />
      ) : queryResult ? (
        <div className="space-y-2">
          <p className="text-muted-foreground text-xs">
            Top {queryResult.retrieved_chunks.length} chunks retrieved for the question
          </p>
          {queryResult.retrieved_chunks.map((r, i) => (
            <div key={r.index} className="flex items-start gap-2">
              <span className="text-primary font-semibold">{i + 1}.</span>
              <p className="text-xs flex-1">
                <span className="text-muted-foreground">
                  [chunk {r.index} · score {r.score.toFixed(3)}]
                </span>{' '}
                {r.content.slice(0, 200)}
                {r.content.length > 200 ? '…' : ''}
              </p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-xs italic">Ask a question below to see retrieved chunks.</p>
      ),
    },
    {
      id: 'final-prompt',
      title: 'Final Prompt Sent to LLM',
      badge: queryResult ? <StatusBadge status="generated" /> : null,
      content: isQuerying ? (
        <SkeletonLoader />
      ) : queryResult ? (
        <CodeBlock code={queryResult.final_prompt} />
      ) : (
        <p className="text-xs italic">Ask a question below to see the LLM prompt.</p>
      ),
    },
    {
      id: 'llm-answer',
      title: 'LLM Answer',
      badge: queryResult ? <StatusBadge status="generated" /> : null,
      content: isQuerying ? (
        <SkeletonLoader />
      ) : queryResult ? (
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground">
            Answered by <span className="text-foreground">{queryResult.llm_provider}</span> in{' '}
            {queryResult.processing_time_seconds}s
          </p>
          <p className="text-sm whitespace-pre-wrap">{queryResult.answer}</p>
        </div>
      ) : (
        <p className="text-xs italic">The LLM answer will appear here.</p>
      ),
    },
    {
      id: 'source-chunks',
      title: 'Source Chunks',
      badge: queryResult ? <StatusBadge status="retrieved" /> : null,
      content: isQuerying ? (
        <SkeletonLoader />
      ) : queryResult ? (
        <div className="space-y-2">
          {queryResult.retrieved_chunks.map((r) => (
            <div key={r.index} className="text-xs bg-input p-2 rounded border border-border">
              <p className="text-muted-foreground">
                Chunk #{r.index} · similarity {r.score.toFixed(3)}
              </p>
              <p className="mt-1 whitespace-pre-wrap">{r.content}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-xs italic">Source chunks appear once a question is answered.</p>
      ),
    },
    {
      id: 'debug-logs',
      title: 'Debug Logs',
      badge: processResult || queryResult ? <StatusBadge status="loaded" /> : null,
      content: isProcessing || isQuerying ? (
        <SkeletonLoader />
      ) : processResult || queryResult ? (
        <CodeBlock
          code={[
            ...(processResult?.debug_logs ?? []),
            ...(queryResult ? ['---'] : []),
            ...(queryResult?.debug_logs ?? []),
          ].join('\n')}
        />
      ) : (
        <p className="text-xs italic">Logs will stream in once you run the pipeline.</p>
      ),
    },
  ]

  return (
    <div className="flex h-screen bg-background">
      <Sidebar
        config={config}
        onConfigChange={handleConfigChange}
        onProcess={handleProcess}
        onUploadSuccess={handleUploadSuccess}
        isProcessing={isProcessing}
        hasSession={sessionId !== null}
        uploadedFilename={uploadedFilename}
      />

      <main className="flex-1 ml-64 overflow-auto">
        <div className="p-8">
          {/* Tab navigation */}
          <Tabs />

          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground mb-2">
              AI Resume Parser Playground
            </h1>
            <p className="text-muted-foreground">
              Analyze resumes with RAG and LLM capabilities
            </p>
          </div>

          {/* Errors */}
          {processError && (
            <div className="mb-4 p-4 bg-destructive/10 border border-destructive/40 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-destructive">Processing failed</p>
                <p className="text-xs text-destructive/80 mt-1">{processError}</p>
              </div>
            </div>
          )}

          {/* Status Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <StatusCard
              title="Upload Status"
              value={uploadStatusValue}
              icon={<FileText className="w-6 h-6" />}
              status={uploadStatusState}
            />
            <StatusCard
              title="Processing Time"
              value={processingTimeValue}
              icon={<Clock className="w-6 h-6" />}
              status={
                isProcessing || isQuerying
                  ? 'loading'
                  : processResult
                  ? 'success'
                  : 'idle'
              }
            />
            <StatusCard
              title="Embedding Dimension"
              value={embeddingInfoValue}
              icon={<Layers className="w-6 h-6" />}
              status={processResult ? 'success' : 'idle'}
            />
            <StatusCard
              title="Number of Chunks"
              value={numChunksValue}
              icon={<BarChart3 className="w-6 h-6" />}
              status={processResult ? 'success' : 'idle'}
            />
          </div>

          {/* Ask a question */}
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-foreground mb-4">Ask the Resume</h2>
            <div className="bg-card border border-border rounded-lg p-4">
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                disabled={!processResult || isQuerying}
                rows={2}
                placeholder="e.g. What are the candidate's cloud skills?"
                className="w-full bg-input border border-border rounded px-3 py-2 text-sm text-foreground focus:outline-none focus:border-primary disabled:opacity-50 resize-none"
              />
              <div className="flex items-center justify-between mt-3">
                <p className="text-xs text-muted-foreground">
                  {processResult
                    ? `Ready · using ${config.llm} + top-${config.topK} retrieval`
                    : 'Process a resume first to enable Q&A'}
                </p>
                <button
                  onClick={handleAsk}
                  disabled={!processResult || isQuerying || !question.trim()}
                  className="bg-primary hover:bg-blue-600 text-primary-foreground font-medium py-2 px-4 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 text-sm"
                >
                  {isQuerying ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Asking...
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4" />
                      Ask
                    </>
                  )}
                </button>
              </div>
              {queryError && (
                <div className="mt-3 p-3 bg-destructive/10 border border-destructive/40 rounded flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-destructive flex-shrink-0 mt-0.5" />
                  <p className="text-xs text-destructive">{queryError}</p>
                </div>
              )}
            </div>
          </div>

          {/* Expandable Sections */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-foreground mb-4">Analysis Results</h2>
            <Accordion items={accordionItems} />
          </div>

          {/* Footer */}
          <div className="mt-8 pt-8 border-t border-border text-center text-sm text-muted-foreground">
            <p>
              Frontend: Next.js + Tailwind · Backend: FastAPI + FAISS · Fully wired end-to-end
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
