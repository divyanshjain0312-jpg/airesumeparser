"""Process router — runs the ingestion pipeline for a session."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.config import Settings, get_settings
from app.models.schemas import ProcessRequest, ProcessResponse
from app.services.dependencies import get_rag_service
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["process"])


@router.post("/process", response_model=ProcessResponse)
async def process_resume(
    request: ProcessRequest,
    settings: Settings = Depends(get_settings),
    rag: RAGService = Depends(get_rag_service),
) -> ProcessResponse:
    pdf_path = settings.upload_path / f"{request.session_id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No uploaded PDF for session {request.session_id}. Upload first.",
        )

    try:
        return rag.process_resume(
            session_id=request.session_id,
            pdf_path=pdf_path,
            config=request.config,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("Processing failed")
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}") from e
