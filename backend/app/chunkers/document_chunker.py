"""Document-based chunker — splits by structural boundaries (blank lines)."""
from __future__ import annotations

import re
from typing import List

from app.chunkers.base import BaseChunker


class DocumentBasedChunker(BaseChunker):
    def split(self, text: str) -> List[str]:
        text = text.strip()
        if not text:
            return []

        # Split on paragraph breaks
        blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
        if not blocks:
            return []

        # Merge small blocks together up to chunk_size
        chunks: List[str] = []
        current = ""
        for block in blocks:
            if not current:
                current = block
            elif len(current) + len(block) + 2 <= self.chunk_size:
                current += "\n\n" + block
            else:
                chunks.append(current)
                current = block
        if current:
            chunks.append(current)

        # If any block exceeds chunk_size, hard-split it
        final: List[str] = []
        for c in chunks:
            if len(c) <= self.chunk_size:
                final.append(c)
                continue
            step = max(1, self.chunk_size - self.chunk_overlap)
            for start in range(0, len(c), step):
                end = start + self.chunk_size
                piece = c[start:end].strip()
                if piece:
                    final.append(piece)
                if end >= len(c):
                    break
        return final
