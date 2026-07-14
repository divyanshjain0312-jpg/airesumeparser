"""High-level RAG orchestration service.

Split into two operations that mirror the UI:
  - process_resume(): PDF → clean → chunk → embed → FAISS store
  - answer_question(): embed query → retrieve top-K → build prompt → LLM
"""
from __future__ import annotations

from pathlib import Path
from typing import List

from app.config import Settings
from app.factories.chunker_factory import ChunkerFactory
from app.factories.embedding_factory import EmbeddingFactory
from app.factories.llm_factory import LLMFactory
from app.models.schemas import (
    ChunkPreview,
    ProcessResponse,
    QueryResponse,
    RAGConfig,
    RetrievedChunk,
)
from app.utils.logger import DebugLogger
from app.utils.pdf_extractor import clean_text, extract_text_from_pdf
from app.vectordb.faiss_service import FAISSSessionManager


class RAGService:
    def __init__(self, settings: Settings, session_manager: FAISSSessionManager) -> None:
        self.settings = settings
        self.session_manager = session_manager

    # ---------- Ingestion ----------

    def process_resume(
        self,
        session_id: str,
        pdf_path: Path,
        config: RAGConfig,
    ) -> ProcessResponse:
        log = DebugLogger()
        log.log(f"Starting resume processing for session {session_id}")
        log.log(f"Config: chunking={config.chunking}, embedding={config.embedding}, llm={config.llm}")
        log.log(f"chunk_size={config.chunkSize}, chunk_overlap={config.chunkOverlap}, top_k={config.topK}")

        # 1. Extract PDF text
        log.log(f"Reading PDF: {pdf_path.name}")
        raw_text, page_count = extract_text_from_pdf(pdf_path)
        log.log(f"PDF parsed: {page_count} page(s), {len(raw_text)} chars raw")

        # 2. Clean
        cleaned = clean_text(raw_text)
        log.log(f"Text cleaned: {len(cleaned)} chars after normalization")

        if not cleaned:
            raise ValueError("No text could be extracted from the uploaded PDF.")

        # 3. Load embedder (needed before semantic chunking too)
        log.log(f"Loading embedding model: {config.embedding}")
        embedder = EmbeddingFactory.create(config.embedding)
        log.log(f"Embedding model ready: {embedder.model_name} (dim={embedder.dimension})")

        # 4. Chunk
        log.log(f"Chunking with strategy: {config.chunking}")
        chunker = ChunkerFactory.create(
            strategy=config.chunking,
            chunk_size=config.chunkSize,
            chunk_overlap=config.chunkOverlap,
            embedder=embedder,
        )
        chunks = chunker.split(cleaned)
        if not chunks:
            raise ValueError("Chunking produced 0 chunks. Try different chunk parameters.")
        avg_size = int(sum(len(c) for c in chunks) / len(chunks))
        log.log(f"Created {len(chunks)} chunks (avg size: {avg_size} chars)")

        # 5. Embed
        log.log("Generating embeddings for all chunks...")
        embeddings = embedder.embed(chunks)
        log.log(f"Embedded {embeddings.shape[0]} chunks (shape={tuple(embeddings.shape)})")

        # 6. Store in FAISS (fresh index per session — replaces any prior one)
        log.log(f"Building FAISS index (dim={embedder.dimension})")
        store = self.session_manager.create(session_id, dimension=embedder.dimension)
        store.add(embeddings, chunks)
        log.log(f"Stored {store.size()} vectors in FAISS")

        log.log(f"Processing complete in {log.elapsed_seconds}s")

        preview_text = cleaned[:2000] + ("..." if len(cleaned) > 2000 else "")
        chunk_previews: List[ChunkPreview] = [
            ChunkPreview(
                index=i,
                content=(c if len(c) <= 500 else c[:500] + "..."),
                char_count=len(c),
            )
            for i, c in enumerate(chunks)
        ]

        return ProcessResponse(
            session_id=session_id,
            extracted_text=cleaned,
            extracted_text_preview=preview_text,
            total_pages=page_count,
            total_characters=len(cleaned),
            chunks=chunk_previews,
            num_chunks=len(chunks),
            embedding_dimension=embedder.dimension,
            embedding_model=embedder.model_name,
            processing_time_seconds=log.elapsed_seconds,
            debug_logs=log.lines,
        )

    # ---------- Query ----------

    def answer_question(
        self,
        session_id: str,
        question: str,
        config: RAGConfig,
    ) -> QueryResponse:
        log = DebugLogger()
        log.log(f"Query received for session {session_id}: {question!r}")

        store = self.session_manager.get(session_id)
        if store is None:
            raise ValueError(
                "No processed session found. Upload a resume and click Process Resume first."
            )
        log.log(f"FAISS index has {store.size()} vectors")

        # Embed query with the SAME embedding model used at ingest time.
        # (In this simple app we trust the frontend to keep the config consistent.)
        log.log(f"Embedding query with model: {config.embedding}")
        embedder = EmbeddingFactory.create(config.embedding)
        if embedder.dimension != store.dimension:
            raise ValueError(
                f"Embedding dimension mismatch (query: {embedder.dimension}, "
                f"index: {store.dimension}). Re-process the resume with the same embedding model."
            )
        q_vec = embedder.embed_query(question)

        # Retrieve
        log.log(f"Retrieving top {config.topK} chunks")
        hits = store.search(q_vec, top_k=config.topK)
        log.log(f"Retrieved {len(hits)} chunks (top score: {hits[0][1]:.3f})" if hits else "No hits")

        retrieved = [
            RetrievedChunk(index=idx, content=text, score=round(score, 4))
            for idx, score, text in hits
        ]

        # Build the final prompt
        context_block = "\n\n---\n\n".join(
            f"[Chunk {r.index} | score={r.score}]\n{r.content}" for r in retrieved
        )
        final_prompt = (
            "You are analyzing a candidate's resume. Use ONLY the context below to answer the "
            "question. If the answer is not present in the context, say you don't know based "
            "on the resume.\n\n"
            f"Context:\n{context_block}\n\n"
            f"Question: {question}\n\n"
            "Answer:"
        )
        log.log(f"Final prompt built ({len(final_prompt)} chars)")

        # LLM call
        log.log(f"Calling LLM provider: {config.llm}")
        llm = LLMFactory.create(config.llm, self.settings)
        answer = llm.generate(final_prompt)
        log.log(f"LLM response received ({len(answer)} chars)")

        log.log(f"Query complete in {log.elapsed_seconds}s")

        return QueryResponse(
            session_id=session_id,
            question=question,
            retrieved_chunks=retrieved,
            final_prompt=final_prompt,
            answer=answer,
            llm_provider=llm.provider_name,
            processing_time_seconds=log.elapsed_seconds,
            debug_logs=log.lines,
        )
