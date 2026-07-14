"""Skill-gap + ATS-rewrite orchestration.

Pipeline:
  1. Get the resume text (from the already-processed FAISS session).
  2. Ask the LLM to extract resume skills (JSON).
  3. Ask the LLM to extract JD skills + importance + job title (JSON).
  4. Diff resume vs JD -> matched / missing skills.
  5. For each missing skill, fetch YouTube courses.
  6. Ask the LLM to produce an ATS-optimized resume rewrite.
  7. Compute a match score and return everything.

Reuses the existing LLMFactory so the same provider dropdown works here.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Tuple

from app.config import Settings
from app.factories.llm_factory import LLMFactory
from app.models.schemas import (
    AnalyzeJDResponse,
    CourseRecommendation,
    RAGConfig,
    SkillGapItem,
)
from app.services.youtube_service import YouTubeService
from app.utils.logger import DebugLogger
from app.utils.skill_extractor import diff_skills, normalize_skills
from app.vectordb.faiss_service import FAISSSessionManager


def _extract_json(raw: str) -> Any:
    """Pull the first JSON object/array out of an LLM response.

    LLMs love to wrap JSON in ```json fences or add prose; strip all that.
    """
    if not raw:
        raise ValueError("Empty LLM response")
    text = raw.strip()
    # Remove code fences
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    # Find the outermost {...} or [...]
    start = min(
        [i for i in (text.find("{"), text.find("[")) if i != -1],
        default=-1,
    )
    if start == -1:
        raise ValueError(f"No JSON found in LLM response: {text[:200]}")
    # Try progressively from the end for a valid parse
    for end in range(len(text), start, -1):
        snippet = text[start:end]
        try:
            return json.loads(snippet)
        except json.JSONDecodeError:
            continue
    raise ValueError(f"Could not parse JSON from LLM response: {text[:200]}")


class SkillGapService:
    def __init__(self, settings: Settings, session_manager: FAISSSessionManager) -> None:
        self.settings = settings
        self.session_manager = session_manager

    # ---- resume text retrieval ----

    def _get_resume_text(self, session_id: str) -> str:
        """Reconstruct resume text from the session's stored chunks."""
        store = self.session_manager.get(session_id)
        if store is None:
            raise ValueError(
                "No processed session found. Upload a resume and click "
                "Process Resume on the main page first."
            )
        # The stored chunks together approximate the full resume text.
        return "\n".join(store.chunks)

    # ---- LLM skill extraction ----

    def _extract_resume_skills(self, llm, resume_text: str, log: DebugLogger) -> List[str]:
        prompt = (
            "Extract ALL technical and professional skills from the resume below. "
            "Return ONLY a JSON array of short skill strings, no prose. "
            'Example: ["Python", "React", "AWS", "Project Management"].\n\n'
            f"Resume:\n{resume_text[:6000]}\n\nJSON array:"
        )
        raw = llm.generate(prompt)
        try:
            data = _extract_json(raw)
            skills = [str(s) for s in data if str(s).strip()]
        except Exception as e:
            log.error(f"Resume skill JSON parse failed ({e}); falling back to line split")
            skills = [ln.strip("-• ") for ln in raw.splitlines() if ln.strip()]
        return normalize_skills(skills)

    def _extract_jd_skills(
        self, llm, jd_text: str, log: DebugLogger
    ) -> Tuple[str, List[Tuple[str, str]]]:
        """Return (job_title, [(skill, importance), ...])."""
        prompt = (
            "From the job description below, extract:\n"
            "1. the job title\n"
            "2. every skill/technology/qualification mentioned, each tagged with "
            'importance as one of "required", "preferred", or "nice-to-have".\n'
            "Return ONLY JSON in this exact shape, no prose:\n"
            '{"job_title": "...", "skills": [{"skill": "Python", "importance": "required"}]}\n\n'
            f"Job Description:\n{jd_text[:6000]}\n\nJSON:"
        )
        raw = llm.generate(prompt)
        job_title = "Target Role"
        pairs: List[Tuple[str, str]] = []
        try:
            data = _extract_json(raw)
            job_title = str(data.get("job_title") or job_title).strip()
            for entry in data.get("skills", []):
                skill = str(entry.get("skill", "")).strip()
                imp = str(entry.get("importance", "required")).strip().lower()
                if imp not in ("required", "preferred", "nice-to-have"):
                    imp = "required"
                if skill:
                    pairs.append((skill, imp))
        except Exception as e:
            log.error(f"JD skill JSON parse failed ({e}); falling back to line split")
            for ln in raw.splitlines():
                s = ln.strip("-• ")
                if s:
                    pairs.append((s, "required"))
        return job_title, pairs

    def _generate_ats_resume(
        self,
        llm,
        resume_text: str,
        jd_text: str,
        missing_skills: List[str],
        log: DebugLogger,
    ) -> Tuple[str, str]:
        gap_hint = (
            f"The candidate is currently missing these JD skills: {', '.join(missing_skills)}. "
            "Where the candidate has genuine related experience, surface it with matching keywords; "
            "do NOT fabricate skills they don't have."
            if missing_skills
            else "The candidate already covers the JD's core skills; focus on keyword alignment and phrasing."
        )
        prompt = (
            "You are an expert resume writer and ATS (Applicant Tracking System) optimizer. "
            "Rewrite the resume below so it is optimized for the target job description: use strong "
            "action verbs, quantifiable achievements, and keywords from the JD that the candidate "
            "genuinely qualifies for. Keep it truthful. Output clean Markdown with clear sections "
            "(Summary, Skills, Experience, Education).\n\n"
            f"{gap_hint}\n\n"
            f"=== TARGET JOB DESCRIPTION ===\n{jd_text[:3000]}\n\n"
            f"=== CURRENT RESUME ===\n{resume_text[:5000]}\n\n"
            "=== ATS-OPTIMIZED RESUME (Markdown) ==="
        )
        ats_resume = llm.generate(prompt)

        summary_prompt = (
            "In 2-3 sentences, summarize the key changes you would make to optimize this resume "
            f"for the job. Missing skills to address: {', '.join(missing_skills) or 'none'}."
        )
        try:
            ats_summary = llm.generate(summary_prompt)
        except Exception:
            ats_summary = "ATS-optimized rewrite generated with JD keyword alignment."
        return ats_resume.strip(), ats_summary.strip()

    # ---- main entry ----

    def analyze(
        self,
        session_id: str,
        job_description: str,
        config: RAGConfig,
        max_courses_per_skill: int = 3,
    ) -> AnalyzeJDResponse:
        log = DebugLogger()
        log.log(f"Skill-gap analysis started for session {session_id}")

        resume_text = self._get_resume_text(session_id)
        log.log(f"Loaded resume text ({len(resume_text)} chars)")

        llm = LLMFactory.create(config.llm, self.settings)
        log.log(f"Using LLM provider: {llm.provider_name}")

        # 1. resume skills
        log.log("Extracting resume skills via LLM...")
        resume_skills = self._extract_resume_skills(llm, resume_text, log)
        log.log(f"Resume skills: {len(resume_skills)} found")

        # 2. JD skills
        log.log("Extracting JD skills via LLM...")
        job_title, jd_pairs = self._extract_jd_skills(llm, job_description, log)
        jd_skills_raw = [s for s, _ in jd_pairs]
        jd_skills = normalize_skills(jd_skills_raw)
        importance_map: Dict[str, str] = {}
        for skill, imp in jd_pairs:
            importance_map.setdefault(skill.strip().lower(), imp)
        log.log(f"JD '{job_title}': {len(jd_skills)} skills found")

        # 3. diff
        matched, missing = diff_skills(resume_skills, jd_skills)
        log.log(f"Matched: {len(matched)} | Missing: {len(missing)}")

        # 4. match score
        total = len(jd_skills) if jd_skills else 1
        match_score = round(100.0 * len(matched) / total, 1)
        log.log(f"Match score: {match_score}%")

        # 5. YouTube courses for missing skills
        yt = YouTubeService(self.settings.youtube_api_key)
        if yt.enabled:
            log.log(f"Fetching YouTube courses for {len(missing)} missing skills...")
        else:
            log.log("YOUTUBE_API_KEY not set — skipping course recommendations")

        missing_items: List[SkillGapItem] = []
        for skill in missing:
            imp = importance_map.get(skill.strip().lower(), "required")
            courses: List[CourseRecommendation] = []
            if yt.enabled:
                try:
                    courses = yt.search_courses(skill, max_results=max_courses_per_skill)
                    log.log(f"  {skill}: {len(courses)} course(s)")
                except Exception as e:
                    log.error(f"  {skill}: YouTube fetch failed ({e})")
            missing_items.append(
                SkillGapItem(skill=skill, importance=imp, courses=courses)  # type: ignore[arg-type]
            )

        # 6. ATS rewrite
        log.log("Generating ATS-optimized resume...")
        ats_resume, ats_summary = self._generate_ats_resume(
            llm, resume_text, job_description, missing, log
        )
        log.log(f"ATS resume generated ({len(ats_resume)} chars)")

        log.log(f"Analysis complete in {log.elapsed_seconds}s")

        return AnalyzeJDResponse(
            session_id=session_id,
            job_title=job_title,
            resume_skills=resume_skills,
            jd_skills=jd_skills,
            matched_skills=matched,
            missing_skills=missing_items,
            match_score=match_score,
            ats_resume=ats_resume,
            ats_summary=ats_summary,
            llm_provider=llm.provider_name,
            youtube_enabled=yt.enabled,
            processing_time_seconds=log.elapsed_seconds,
            debug_logs=log.lines,
        )
