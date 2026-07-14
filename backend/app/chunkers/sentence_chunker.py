"""Sentence-based chunker — packs sentences until chunk_size is reached."""
from __future__ import annotations

import re
from typing import List

from app.chunkers.base import BaseChunker


def _split_sentences(text: str) -> List[str]:
    try:
        import nltk

        try:
            nltk.data.find("tokenizers/punkt_tab")
        except LookupError:
            try:
                nltk.download("punkt_tab", quiet=True)
            except Exception:
                pass
        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            try:
                nltk.download("punkt", quiet=True)
            except Exception:
                pass
        from nltk.tokenize import sent_tokenize

        return sent_tokenize(text)
    except Exception:
        # Regex fallback
        return re.split(r"(?<=[.!?])\s+", text)


class SentenceChunker(BaseChunker):
    def split(self, text: str) -> List[str]:
        text = text.strip()
        if not text:
            return []

        sentences = [s.strip() for s in _split_sentences(text) if s.strip()]
        if not sentences:
            return []

        chunks: List[str] = []
        current: List[str] = []
        current_len = 0

        for sent in sentences:
            sent_len = len(sent)
            if current and current_len + sent_len + 1 > self.chunk_size:
                chunks.append(" ".join(current).strip())
                # Overlap: keep the tail sentences up to chunk_overlap chars
                if self.chunk_overlap > 0:
                    tail: List[str] = []
                    tail_len = 0
                    for s in reversed(current):
                        if tail_len + len(s) + 1 > self.chunk_overlap:
                            break
                        tail.insert(0, s)
                        tail_len += len(s) + 1
                    current = tail
                    current_len = tail_len
                else:
                    current = []
                    current_len = 0

            current.append(sent)
            current_len += sent_len + 1

        if current:
            chunks.append(" ".join(current).strip())

        return [c for c in chunks if c]
