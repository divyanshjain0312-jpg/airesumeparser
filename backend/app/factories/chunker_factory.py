"""Factory that instantiates a chunker from the frontend config string."""
from __future__ import annotations

from typing import Optional

from app.chunkers.base import BaseChunker
from app.chunkers.document_chunker import DocumentBasedChunker
from app.chunkers.fixed_size_chunker import FixedSizeChunker
from app.chunkers.recursive_chunker import RecursiveCharacterChunker
from app.chunkers.semantic_chunker import SemanticChunker
from app.chunkers.sentence_chunker import SentenceChunker
from app.chunkers.token_chunker import TokenChunker
from app.embeddings.base import BaseEmbedder


class ChunkerFactory:
    _registry = {
        "recursive-character": RecursiveCharacterChunker,
        "fixed-size": FixedSizeChunker,
        "token-based": TokenChunker,
        "sentence-based": SentenceChunker,
        "semantic": SemanticChunker,
        "document-based": DocumentBasedChunker,
    }

    @classmethod
    def create(
        cls,
        strategy: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        embedder: Optional[BaseEmbedder] = None,
    ) -> BaseChunker:
        key = (strategy or "").lower()
        chunker_cls = cls._registry.get(key)
        if chunker_cls is None:
            raise ValueError(
                f"Unknown chunking strategy: {strategy!r}. "
                f"Supported: {sorted(cls._registry)}"
            )
        if chunker_cls is SemanticChunker:
            return SemanticChunker(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                embedder=embedder,
            )
        return chunker_cls(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    @classmethod
    def available_strategies(cls) -> list[str]:
        return sorted(cls._registry.keys())
