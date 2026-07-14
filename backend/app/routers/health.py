"""Health-check router."""
from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version="1.0.0")


@router.get("/", response_model=HealthResponse)
async def root() -> HealthResponse:
    return HealthResponse(status="ok", version="1.0.0")
