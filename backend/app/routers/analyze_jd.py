"""Analyze-JD router — skill-gap analysis + ATS rewrite + course recommendations."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.models.schemas import AnalyzeJDRequest, AnalyzeJDResponse
from app.services.dependencies import get_skillgap_service
from app.services.skillgap_service import SkillGapService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["skill-gap"])


@router.post("/analyze-jd", response_model=AnalyzeJDResponse)
async def analyze_jd(
    request: AnalyzeJDRequest,
    service: SkillGapService = Depends(get_skillgap_service),
) -> AnalyzeJDResponse:
    try:
        return service.analyze(
            session_id=request.session_id,
            job_description=request.job_description,
            config=request.config,
            max_courses_per_skill=request.max_courses_per_skill,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("Skill-gap analysis failed")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}") from e
