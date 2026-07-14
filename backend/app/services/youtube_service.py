"""YouTube Data API v3 client for course recommendations.

Uses the public `search.list` endpoint (no OAuth needed, just an API key).
Each search costs 100 quota units; the free daily quota is 10,000 units
(~100 searches/day), so we cache per-skill results in memory for the process
lifetime to avoid burning quota on repeat requests.

If no YOUTUBE_API_KEY is configured, methods return empty lists and the
caller degrades gracefully (skill gaps are still shown, just without videos).
"""
from __future__ import annotations

import threading
from typing import Dict, List

import httpx

from app.models.schemas import CourseRecommendation

_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

# Simple in-process cache: {(skill_query, max_results): [CourseRecommendation]}
_CACHE: Dict[str, List[CourseRecommendation]] = {}
_CACHE_LOCK = threading.Lock()


class YouTubeService:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key or ""

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def search_courses(self, skill: str, max_results: int = 3) -> List[CourseRecommendation]:
        """Return up to `max_results` tutorial videos for a skill."""
        if not self.enabled:
            return []

        query = f"{skill} full course tutorial for beginners"
        cache_key = f"{query}::{max_results}"
        with _CACHE_LOCK:
            cached = _CACHE.get(cache_key)
        if cached is not None:
            return cached

        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "order": "relevance",
            "videoEmbeddable": "true",
            "safeSearch": "strict",
            "relevanceLanguage": "en",
            "key": self.api_key,
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(_SEARCH_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPStatusError as e:
            # Quota exceeded (403) or bad key — degrade gracefully.
            raise RuntimeError(
                f"YouTube API error ({e.response.status_code}). "
                "Check your YOUTUBE_API_KEY and daily quota."
            ) from e
        except Exception as e:
            raise RuntimeError(f"YouTube request failed: {e}") from e

        results: List[CourseRecommendation] = []
        for item in data.get("items", []):
            vid = item.get("id", {}).get("videoId")
            snippet = item.get("snippet", {})
            if not vid:
                continue
            thumbs = snippet.get("thumbnails", {})
            thumb_url = (
                thumbs.get("medium", {}).get("url")
                or thumbs.get("default", {}).get("url")
                or ""
            )
            results.append(
                CourseRecommendation(
                    title=snippet.get("title", "Untitled"),
                    channel=snippet.get("channelTitle", "Unknown"),
                    video_id=vid,
                    url=f"https://www.youtube.com/watch?v={vid}",
                    thumbnail=thumb_url,
                    published_at=snippet.get("publishedAt", ""),
                )
            )

        with _CACHE_LOCK:
            _CACHE[cache_key] = results
        return results
