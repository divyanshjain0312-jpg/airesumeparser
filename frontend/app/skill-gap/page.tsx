'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import {
  Target,
  Loader2,
  AlertCircle,
  CheckCircle2,
  XCircle,
  ExternalLink,
  Video,
  FileText,
  Copy,
  Check,
} from 'lucide-react'
import { Tabs } from '@/components/tabs'
import { Accordion, SkeletonLoader } from '@/components/accordion'
import {
  analyzeJD,
  loadSession,
  type AnalyzeJDResponse,
  type PersistedSession,
  type SkillGapItem,
} from '@/lib/api'

const importanceStyles: Record<string, string> = {
  required: 'bg-destructive/20 text-destructive',
  preferred: 'bg-status-chunked/20 text-status-chunked',
  'nice-to-have': 'bg-status-retrieved/20 text-status-retrieved',
}

function ScoreRing({ score }: { score: number }) {
  const radius = 52
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (score / 100) * circumference
  const color =
    score >= 70 ? 'var(--color-status-loaded)' : score >= 40 ? '#f59e0b' : 'var(--color-destructive)'
  return (
    <div className="relative w-32 h-32 flex-shrink-0">
      <svg className="w-32 h-32 -rotate-90" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r={radius} fill="none" stroke="var(--color-border)" strokeWidth="10" />
        <circle
          cx="60"
          cy="60"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.8s ease' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold text-foreground">{score}%</span>
        <span className="text-xs text-muted-foreground">match</span>
      </div>
    </div>
  )
}

function CourseCard({ skill }: { skill: SkillGapItem }) {
  return (
    <div className="space-y-3">
      {skill.courses.length === 0 ? (
        <p className="text-xs text-muted-foreground italic">
          No course recommendations available (YouTube API key not set, or no results).
        </p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {skill.courses.map((course) => (
            <a
              key={course.video_id}
              href={course.url}
              target="_blank"
              rel="noopener noreferrer"
              className="group block bg-input border border-border rounded-lg overflow-hidden hover:border-primary transition-colors"
            >
              {course.thumbnail ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={course.thumbnail}
                  alt={course.title}
                  className="w-full aspect-video object-cover"
                />
              ) : (
                <div className="w-full aspect-video bg-muted flex items-center justify-center">
                  <Video className="w-8 h-8 text-muted-foreground" />
                </div>
              )}
              <div className="p-3">
                <p className="text-xs font-medium text-foreground line-clamp-2 group-hover:text-primary transition-colors">
                  {course.title}
                </p>
                <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                  {course.channel}
                  <ExternalLink className="w-3 h-3" />
                </p>
              </div>
            </a>
          ))}
        </div>
      )}
    </div>
  )
}

export default function SkillGapPage() {
  const [session, setSession] = useState<PersistedSession | null>(null)
  const [jobDescription, setJobDescription] = useState('')
  const [result, setResult] = useState<AnalyzeJDResponse | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    setSession(loadSession())
  }, [])

  const canAnalyze =
    session?.processed && jobDescription.trim().length >= 20 && !isAnalyzing

  const handleAnalyze = async () => {
    if (!session?.sessionId) return
    setIsAnalyzing(true)
    setError(null)
    setResult(null)
    try {
      const res = await analyzeJD(session.sessionId, jobDescription.trim(), session.config)
      setResult(res)
    } catch (err: any) {
      setError(err?.message || 'Analysis failed')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleCopy = async () => {
    if (!result) return
    try {
      await navigator.clipboard.writeText(result.ats_resume)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      /* ignore */
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <main className="max-w-5xl mx-auto p-8">
        <Tabs />

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2 flex items-center gap-3">
            <Target className="w-8 h-8 text-primary" />
            Skill Gap & Course Finder
          </h1>
          <p className="text-muted-foreground">
            Paste a job description to see which skills you're missing and the courses to close the gap.
          </p>
        </div>

        {/* No session guard */}
        {!session?.processed && (
          <div className="mb-8 p-6 bg-card border border-border rounded-lg text-center">
            <FileText className="w-10 h-10 mx-auto mb-3 text-muted-foreground" />
            <p className="text-foreground font-medium mb-2">No processed resume found</p>
            <p className="text-sm text-muted-foreground mb-4">
              Upload and process a resume on the Resume Parser tab first, then come back here.
            </p>
            <Link
              href="/"
              className="inline-block bg-primary hover:bg-blue-600 text-primary-foreground font-medium py-2 px-4 rounded transition-colors text-sm"
            >
              Go to Resume Parser
            </Link>
          </div>
        )}

        {/* JD input */}
        {session?.processed && (
          <div className="mb-8">
            <div className="bg-card border border-border rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                  Job Description
                </h2>
                <span className="text-xs text-muted-foreground flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-status-loaded" />
                  {session.filename}
                </span>
              </div>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                disabled={isAnalyzing}
                rows={8}
                placeholder="Paste the full job description here (responsibilities, requirements, tech stack)..."
                className="w-full bg-input border border-border rounded px-3 py-2 text-sm text-foreground focus:outline-none focus:border-primary disabled:opacity-50 resize-y"
              />
              <div className="flex items-center justify-between mt-3">
                <p className="text-xs text-muted-foreground">
                  {jobDescription.trim().length < 20
                    ? `Paste at least 20 characters (${jobDescription.trim().length}/20)`
                    : `Using ${session.config.llm} · top-${session.config.topK} retrieval`}
                </p>
                <button
                  onClick={handleAnalyze}
                  disabled={!canAnalyze}
                  className="bg-primary hover:bg-blue-600 text-primary-foreground font-medium py-2 px-4 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 text-sm"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Target className="w-4 h-4" />
                      Analyze Gap
                    </>
                  )}
                </button>
              </div>
              {error && (
                <div className="mt-3 p-3 bg-destructive/10 border border-destructive/40 rounded flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-destructive flex-shrink-0 mt-0.5" />
                  <p className="text-xs text-destructive">{error}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Loading skeleton */}
        {isAnalyzing && (
          <div className="bg-card border border-border rounded-lg p-6 mb-8">
            <SkeletonLoader />
          </div>
        )}

        {/* Results */}
        {result && !isAnalyzing && (
          <div className="space-y-8">
            {/* Score + counts */}
            <div className="bg-card border border-border rounded-lg p-6">
              <div className="flex items-center gap-6 flex-wrap">
                <ScoreRing score={result.match_score} />
                <div className="flex-1 min-w-[200px]">
                  <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                    Target Role
                  </p>
                  <h3 className="text-xl font-bold text-foreground mb-3">{result.job_title}</h3>
                  <div className="flex gap-6">
                    <div>
                      <p className="text-2xl font-bold text-status-loaded">
                        {result.matched_skills.length}
                      </p>
                      <p className="text-xs text-muted-foreground">skills matched</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-destructive">
                        {result.missing_skills.length}
                      </p>
                      <p className="text-xs text-muted-foreground">skills missing</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-foreground">
                        {result.jd_skills.length}
                      </p>
                      <p className="text-xs text-muted-foreground">skills required</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Matched skills */}
            <div>
              <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-status-loaded" />
                Skills You Have ({result.matched_skills.length})
              </h2>
              {result.matched_skills.length === 0 ? (
                <p className="text-sm text-muted-foreground italic">
                  No direct matches found. Focus on the missing skills below.
                </p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {result.matched_skills.map((s) => (
                    <span
                      key={s}
                      className="px-3 py-1 text-xs font-medium rounded-full bg-status-loaded/20 text-status-loaded"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Missing skills + courses */}
            <div>
              <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
                <XCircle className="w-5 h-5 text-destructive" />
                Skills to Learn ({result.missing_skills.length})
              </h2>

              {!result.youtube_enabled && (
                <div className="mb-4 p-3 bg-status-chunked/10 border border-status-chunked/40 rounded flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-status-chunked flex-shrink-0 mt-0.5" />
                  <p className="text-xs text-status-chunked">
                    Course recommendations are off. Add a YOUTUBE_API_KEY to your backend .env to
                    see YouTube courses for each missing skill.
                  </p>
                </div>
              )}

              {result.missing_skills.length === 0 ? (
                <p className="text-sm text-muted-foreground italic">
                  You cover all the skills in this job description.
                </p>
              ) : (
                <Accordion
                  items={result.missing_skills.map((skill) => ({
                    id: skill.skill,
                    title: skill.skill,
                    badge: (
                      <span
                        className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                          importanceStyles[skill.importance] || importanceStyles.required
                        }`}
                      >
                        {skill.importance}
                      </span>
                    ),
                    content: <CourseCard skill={skill} />,
                  }))}
                />
              )}
            </div>

            {/* ATS resume */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-foreground flex items-center gap-2">
                  <FileText className="w-5 h-5 text-primary" />
                  ATS-Optimized Resume
                </h2>
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-2 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
                >
                  {copied ? (
                    <>
                      <Check className="w-4 h-4 text-status-loaded" />
                      Copied
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4" />
                      Copy
                    </>
                  )}
                </button>
              </div>
              {result.ats_summary && (
                <p className="text-sm text-muted-foreground mb-3 bg-input border border-border rounded p-3">
                  {result.ats_summary}
                </p>
              )}
              <pre className="whitespace-pre-wrap text-sm text-foreground bg-card border border-border rounded-lg p-6 max-h-[600px] overflow-y-auto font-sans">
                {result.ats_resume}
              </pre>
            </div>

            {/* Debug logs */}
            <details className="bg-card border border-border rounded-lg">
              <summary className="px-6 py-4 text-sm font-semibold text-muted-foreground cursor-pointer">
                Debug Logs · {result.processing_time_seconds}s
              </summary>
              <div className="border-t border-border px-6 py-4">
                <pre className="text-xs font-mono text-muted-foreground whitespace-pre-wrap">
                  {result.debug_logs.join('\n')}
                </pre>
              </div>
            </details>
          </div>
        )}
      </main>
    </div>
  )
}
