"""Token-based chunker using tiktoken encoding."""
from __future__ import annotations

from typing import List

from app.chunkers.base import BaseChunker


class TokenChunker(BaseChunker):
    """Splits by token count. chunk_size/overlap are interpreted as tokens.

    Falls back to word-based splitting if tiktoken can't load an encoder.
    """

    def split(self, text: str) -> List[str]:
        text = text.strip()
        if not text:
            return []
        try:
            import tiktoken

            enc = tiktoken.get_encoding("cl100k_base")
            tokens = enc.encode(text)
            step = max(1, self.chunk_size - self.chunk_overlap)
            chunks: List[str] = []
            for start in range(0, len(tokens), step):
                end = start + self.chunk_size
                piece = enc.decode(tokens[start:end]).strip()
                if piece:
                    chunks.append(piece)
                if end >= len(tokens):
                    break
            return chunks
        except Exception:
            # Fallback: word-based approximation (1 word ≈ 1.3 tokens)
            words = text.split()
            step = max(1, self.chunk_size - self.chunk_overlap)
            return [
                " ".join(words[i : i + self.chunk_size]).strip()
                for i in range(0, len(words), step)
                if words[i : i + self.chunk_size]
            ]
