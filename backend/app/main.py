"""FastAPI application entrypoint."""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import health, upload, process, query

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="AI Resume Parser API",
    description="RAG pipeline for resume analysis: PDF → chunks → embeddings → FAISS → LLM.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(upload.router)
app.include_router(process.router)
app.include_router(query.router)


@app.on_event("startup")
async def startup() -> None:
    logger.info("Upload dir: %s", settings.upload_path.resolve())
    logger.info("Vector DB dir: %s", settings.vector_db_path.resolve())
    logger.info("CORS origins: %s", settings.cors_origins_list)
