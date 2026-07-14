"""Skill normalization + set-diff helpers.

The LLM extracts raw skill strings from the resume and the job description.
Those strings are messy ("React.js", "ReactJS", "react", "REACT") so we
normalize them to a canonical form before comparing, and keep a mapping back
to a nice display label.
"""
from __future__ import annotations

import re
from typing import Dict, List, Tuple

# Common aliases → canonical display name.
# Extend freely; anything not listed just gets lower-cased/trimmed.
_ALIASES: Dict[str, str] = {
    "reactjs": "React",
    "react.js": "React",
    "react js": "React",
    "nodejs": "Node.js",
    "node js": "Node.js",
    "node.js": "Node.js",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "psql": "PostgreSQL",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "gcp": "Google Cloud",
    "aws": "AWS",
    "amazon web services": "AWS",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "dl": "Deep Learning",
    "nlp": "NLP",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "rest api": "REST APIs",
    "restful api": "REST APIs",
    "rest apis": "REST APIs",
    "restful apis": "REST APIs",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "next": "Next.js",
    "nextjs": "Next.js",
    "next.js": "Next.js",
}


def _canonical_key(skill: str) -> str:
    """Reduce a skill to a comparison key (lowercase, stripped, alias-resolved)."""
    s = skill.strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = s.strip(" .,-/")
    return _ALIASES.get(s, s)


def _display_label(skill: str) -> str:
    """Return a nice display label for a raw skill string."""
    key = _canonical_key(skill)
    # If we have a canonical alias whose value differs, use it.
    if key in _ALIASES.values():
        return key
    # Otherwise title-case, but keep short all-caps acronyms as-is.
    raw = skill.strip()
    if raw.isupper() and len(raw) <= 5:
        return raw
    return raw[:1].upper() + raw[1:] if raw else raw


def normalize_skills(skills: List[str]) -> List[str]:
    """De-duplicate a raw skill list, preserving first-seen display labels."""
    seen: Dict[str, str] = {}
    for raw in skills:
        if not raw or not raw.strip():
            continue
        key = _canonical_key(raw)
        if key and key not in seen:
            seen[key] = _display_label(raw)
    return list(seen.values())


def diff_skills(
    resume_skills: List[str], jd_skills: List[str]
) -> Tuple[List[str], List[str]]:
    """Return (matched, missing) display labels.

    matched = JD skills the resume already has.
    missing = JD skills absent from the resume.
    """
    resume_keys = {_canonical_key(s) for s in resume_skills}

    matched: List[str] = []
    missing: List[str] = []
    seen_missing: set[str] = set()

    for jd in jd_skills:
        key = _canonical_key(jd)
        if not key:
            continue
        if key in resume_keys:
            matched.append(_display_label(jd))
        elif key not in seen_missing:
            seen_missing.add(key)
            missing.append(_display_label(jd))

    return matched, missing
