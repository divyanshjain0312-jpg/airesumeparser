"""Semantic chunker — groups adjacent sentences by embedding similarity.

Uses langchain_experimental.SemanticChunker when an embedding model is
supplied, else falls back to a percentile-based split with SentenceTransformers.
"""
from __future__ import annotations

from typing import List, Optional

import numpy as np

from app.chunkers.base import BaseChunker
from app.chunkers.sentence_chunker import _split_sentences


class SemanticChunker(BaseChunker):
    """Simple, dependency-light semantic chunker.

    Steps: split into sentences → embed each sentence → find breakpoints
    where cosine distance between adjacent sentences exceeds the
    percentile threshold → group between breakpoints.

    We accept an optional pre-built embedder to avoid re-loading models.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        embedder: Optional[object] = None,
        breakpoint_percentile: float = 90.0,
    ) -> None:
        super().__init__(chunk_size, chunk_overlap)
        self._embedder = embedder
        self._breakpoint_percentile = breakpoint_percentile

    def _get_embedder(self):
        if self._embedder is not None:
            return self._embedder
        from sentence_transformers import SentenceTransformer

        self._embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        return self._embedder

    def split(self, text: str) -> List[str]:
        text = text.strip()
        if not text:
            return []

        sentences = [s.strip() for s in _split_sentences(text) if s.strip()]
        if len(sentences) <= 1:
            return sentences

        embedder = self._get_embedder()
        # Embed sentences
        if hasattr(embedder, "encode"):
            vectors = np.array(embedder.encode(sentences, show_progress_bar=False))
        else:
            # BaseEmbedder-compatible object
            vectors = np.array(embedder.embed(sentences))

        # Cosine distances between consecutive sentences
        def _cosine(a: np.ndarray, b: np.ndarray) -> float:
            na = np.linalg.norm(a)
            nb = np.linalg.norm(b)
            if na == 0 or nb == 0:
                return 1.0
            return 1.0 - float(np.dot(a, b) / (na * nb))

        distances = [_cosine(vectors[i], vectors[i + 1]) for i in range(len(sentences) - 1)]
        if not distances:
            return sentences

        threshold = float(np.percentile(distances, self._breakpoint_percentile))

        # Build chunks by grouping sentences between breakpoints
        chunks: List[str] = []
        current: List[str] = [sentences[0]]
        for i, dist in enumerate(distances):
            if dist > threshold and current:
                chunks.append(" ".join(current).strip())
                current = []
            current.append(sentences[i + 1])
        if current:
            chunks.append(" ".join(current).strip())

        # Enforce chunk_size ceiling by splitting oversize chunks
        final: List[str] = []
        for c in chunks:
            if len(c) <= self.chunk_size:
                final.append(c)
                continue
            # Break oversize chunk by char size with overlap
            step = max(1, self.chunk_size - self.chunk_overlap)
            for start in range(0, len(c), step):
                end = start + self.chunk_size
                piece = c[start:end].strip()
                if piece:
                    final.append(piece)
                if end >= len(c):
                    break
        return [c for c in final if c]
