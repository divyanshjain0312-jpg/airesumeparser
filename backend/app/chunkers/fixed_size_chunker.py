"""Fixed-size character chunker (uniform chunks)."""
from __future__ import annotations

from typing import List

from app.chunkers.base import BaseChunker


class FixedSizeChunker(BaseChunker):
    def split(self, text: str) -> List[str]:
        text = text.strip()
        if not text:
            return []
        step = max(1, self.chunk_size - self.chunk_overlap)
        chunks: List[str] = []
        for start in range(0, len(text), step):
            end = start + self.chunk_size
            piece = text[start:end].strip()
            if piece:
                chunks.append(piece)
            if end >= len(text):
                break
        return chunks
