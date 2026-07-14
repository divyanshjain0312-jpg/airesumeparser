"""Pydantic schemas for request/response payloads."""
from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


# ---------- Config ----------

ChunkingStrategy = Literal[
    "recursive-character",
    "fixed-size",
    "token-based",
    "sentence-based",
    "semantic",
    "document-based",
]

EmbeddingModel = Literal[
    "all-miniLM-L6-v2",
    "all-MiniLM-L6-v2",
    "bge-small",
    "bge-base",
    "e5-small",
    "instructor",
]

LLMProvider = Literal["gemini", "openai", "claude", "mistral", "llama", "ollama", "huggingface"]


class RAGConfig(BaseModel):
    chunking: ChunkingStrategy = "recursive-character"
    embedding: EmbeddingModel = "all-MiniLM-L6-v2"
    vectorDb: Literal["faiss", "chromadb"] = "faiss"  # UI may send chromadb; backend always uses FAISS
    llm: LLMProvider = "gemini"
    chunkSize: int = Field(1000, ge=100, le=4000)
    chunkOverlap: int = Field(200, ge=0, le=1000)
    topK: int = Field(5, ge=1, le=20)


# ---------- Upload ----------

class UploadResponse(BaseModel):
    session_id: str
    filename: str
    size_bytes: int
    message: str


# ---------- Process ----------

class ProcessRequest(BaseModel):
    session_id: str
    config: RAGConfig


class ChunkPreview(BaseModel):
    index: int
    content: str
    char_count: int


class ProcessResponse(BaseModel):
    session_id: str
    extracted_text: str
    extracted_text_preview: str
    total_pages: int
    total_characters: int
    chunks: List[ChunkPreview]
    num_chunks: int
    embedding_dimension: int
    embedding_model: str
    processing_time_seconds: float
    debug_logs: List[str]


# ---------- Query ----------

class QueryRequest(BaseModel):
    session_id: str
    question: str = Field(..., min_length=1)
    config: RAGConfig


class RetrievedChunk(BaseModel):
    index: int
    content: str
    score: float


class QueryResponse(BaseModel):
    session_id: str
    question: str
    retrieved_chunks: List[RetrievedChunk]
    final_prompt: str
    answer: str
    llm_provider: str
    processing_time_seconds: float
    debug_logs: List[str]


# ---------- Meta ----------

class HealthResponse(BaseModel):
    status: str
    version: str


class ErrorResponse(BaseModel):
    detail: str
