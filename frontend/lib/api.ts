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

// ---------- Skill-gap / JD analysis ----------

export interface CourseRecommendation {
  title: string
  channel: string
  video_id: string
  url: string
  thumbnail: string
  published_at: string
}

export interface SkillGapItem {
  skill: string
  importance: 'required' | 'preferred' | 'nice-to-have'
  courses: CourseRecommendation[]
}

export interface AnalyzeJDResponse {
  session_id: string
  job_title: string
  resume_skills: string[]
  jd_skills: string[]
  matched_skills: string[]
  missing_skills: SkillGapItem[]
  match_score: number
  ats_resume: string
  ats_summary: string
  llm_provider: string
  youtube_enabled: boolean
  processing_time_seconds: number
  debug_logs: string[]
}

export async function analyzeJD(
  sessionId: string,
  jobDescription: string,
  config: RAGConfig,
  maxCoursesPerSkill = 3,
): Promise<AnalyzeJDResponse> {
  const res = await fetch(`${BASE_URL}/api/analyze-jd`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      job_description: jobDescription,
      config,
      max_courses_per_skill: maxCoursesPerSkill,
    }),
  })
  return handleResponse<AnalyzeJDResponse>(res)
}

// ---------- Session persistence (shared across pages) ----------
// The skill-gap page runs on a separate route, so we persist the active
// session id + config in sessionStorage to carry them across navigation.

const SESSION_KEY = 'arp_session'

export interface PersistedSession {
  sessionId: string
  filename: string
  config: RAGConfig
  processed: boolean
}

export function saveSession(data: PersistedSession): void {
  if (typeof window === 'undefined') return
  try {
    window.sessionStorage.setItem(SESSION_KEY, JSON.stringify(data))
  } catch {
    /* ignore */
  }
}

export function loadSession(): PersistedSession | null {
  if (typeof window === 'undefined') return null
  try {
    const raw = window.sessionStorage.getItem(SESSION_KEY)
    return raw ? (JSON.parse(raw) as PersistedSession) : null
  } catch {
    return null
  }
}
