"""Recursive character text splitter — the default LangChain strategy."""
from __future__ import annotations

from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.chunkers.base import BaseChunker


class RecursiveCharacterChunker(BaseChunker):
    def split(self, text: str) -> List[str]:
        if not text.strip():
            return []
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )
        return [c for c in splitter.split_text(text) if c.strip()]
