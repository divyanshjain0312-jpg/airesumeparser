"""Query router — retrieval + LLM answer generation."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.models.schemas import QueryRequest, QueryResponse
from app.services.dependencies import get_rag_service
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["query"])


@router.post("/query", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    rag: RAGService = Depends(get_rag_service),
) -> QueryResponse:
    try:
        return rag.answer_question(
            session_id=request.session_id,
            question=request.question,
            config=request.config,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("Query failed")
        raise HTTPException(status_code=500, detail=f"Query failed: {e}") from e
