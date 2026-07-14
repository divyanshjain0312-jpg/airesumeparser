// lib/api.ts
// Typed client for the FastAPI backend.

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, '') || 'http://localhost:8000'

// ---------- Types (must match backend Pydantic schemas) ----------

export interface RAGConfig {
  chunking: string
  embedding: string
  vectorDb: string
  llm: string
  chunkSize: number
  chunkOverlap: number
  topK: number
}

export interface UploadResponse {
  session_id: string
  filename: string
  size_bytes: number
  message: string
}

export interface ChunkPreview {
  index: number
  content: string
  char_count: number
}

export interface ProcessResponse {
  session_id: string
  extracted_text: string
  extracted_text_preview: string
  total_pages: number
  total_characters: number
  chunks: ChunkPreview[]
  num_chunks: number
  embedding_dimension: number
  embedding_model: string
  processing_time_seconds: number
  debug_logs: string[]
}

export interface RetrievedChunk {
  index: number
  content: string
  score: number
}

export interface QueryResponse {
  session_id: string
  question: string
  retrieved_chunks: RetrievedChunk[]
  final_prompt: string
  answer: string
  llm_provider: string
  processing_time_seconds: number
  debug_logs: string[]
}

// ---------- Helpers ----------

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `Request failed (${res.status})`
    try {
      const body = await res.json()
      if (body?.detail) detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail)
    } catch {
      /* ignore parse errors */
    }
    throw new Error(detail)
  }
  return res.json() as Promise<T>
}

// ---------- API methods ----------

export async function uploadPdf(file: File): Promise<UploadResponse> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE_URL}/api/upload`, {
    method: 'POST',
    body: form,
  })
  return handleResponse<UploadResponse>(res)
}

export async function processResume(
  sessionId: string,
  config: RAGConfig,
): Promise<ProcessResponse> {
  const res = await fetch(`${BASE_URL}/api/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, config }),
  })
  return handleResponse<ProcessResponse>(res)
}

export async function askQuestion(
  sessionId: string,
  question: string,
  config: RAGConfig,
): Promise<QueryResponse> {
  const res = await fetch(`${BASE_URL}/api/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, question, config }),
  })
  return handleResponse<QueryResponse>(res)
}
