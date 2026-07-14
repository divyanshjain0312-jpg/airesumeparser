"""Factory that instantiates an embedder from the frontend config string.

Handles the case-insensitive UI values (e.g. 'all-miniLM-L6-v2') and
applies model-specific query/passage prefixes when required
(E5 needs 'query: ' and 'passage: ' prefixes; BGE recommends a query
prefix for retrieval).
"""
from __future__ import annotations

from app.embeddings.base import BaseEmbedder
from app.embeddings.sentence_transformer_embedder import SentenceTransformerEmbedder


class EmbeddingFactory:
    # UI value → (HF model id, query_prefix, passage_prefix)
    _registry = {
        "all-minilm-l6-v2": ("sentence-transformers/all-MiniLM-L6-v2", "", ""),
        "bge-small": (
            "BAAI/bge-small-en-v1.5",
            "Represent this sentence for searching relevant passages: ",
            "",
        ),
        "bge-base": (
            "BAAI/bge-base-en-v1.5",
            "Represent this sentence for searching relevant passages: ",
            "",
        ),
        "e5-small": ("intfloat/e5-small-v2", "query: ", "passage: "),
        "instructor": ("hkunlp/instructor-base", "", ""),
    }

    @classmethod
    def create(cls, model_key: str) -> BaseEmbedder:
        key = (model_key or "").lower()
        entry = cls._registry.get(key)
        if entry is None:
            raise ValueError(
                f"Unknown embedding model: {model_key!r}. "
                f"Supported: {sorted(cls._registry)}"
            )
        hf_id, qp, pp = entry
        return SentenceTransformerEmbedder(hf_id=hf_id, query_prefix=qp, passage_prefix=pp)

    @classmethod
    def available_models(cls) -> list[str]:
        return sorted(cls._registry.keys())
