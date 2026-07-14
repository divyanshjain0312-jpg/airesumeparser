"""Shared FastAPI dependency providers."""
from __future__ import annotations

from fastapi import Depends

from app.config import Settings, get_settings
from app.services.rag_service import RAGService
from app.vectordb.faiss_service import FAISSSessionManager, get_session_manager


def get_faiss_manager(settings: Settings = Depends(get_settings)) -> FAISSSessionManager:
    return get_session_manager(settings.vector_db_path)


def get_rag_service(
    settings: Settings = Depends(get_settings),
    manager: FAISSSessionManager = Depends(get_faiss_manager),
) -> RAGService:
    return RAGService(settings=settings, session_manager=manager)
