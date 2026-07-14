"""SentenceTransformer-backed embedder used by all HuggingFace models.

Includes a module-level model cache so we don't reload weights on every request.
"""
from __future__ import annotations

import threading
from typing import Dict, List

import numpy as np

from app.embeddings.base import BaseEmbedder

_MODEL_CACHE: Dict[str, object] = {}
_CACHE_LOCK = threading.Lock()


def _load_model(hf_id: str):
    with _CACHE_LOCK:
        model = _MODEL_CACHE.get(hf_id)
        if model is None:
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer(hf_id)
            _MODEL_CACHE[hf_id] = model
        return model


class SentenceTransformerEmbedder(BaseEmbedder):
    def __init__(self, hf_id: str, query_prefix: str = "", passage_prefix: str = "") -> None:
        self.hf_id = hf_id
        self.model_name = hf_id
        self._query_prefix = query_prefix
        self._passage_prefix = passage_prefix
        self._model = _load_model(hf_id)
        self._dim: int = int(self._model.get_sentence_embedding_dimension())

    def embed(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self._dim), dtype=np.float32)
        prepped = [f"{self._passage_prefix}{t}" if self._passage_prefix else t for t in texts]
        vecs = self._model.encode(
            prepped,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return np.asarray(vecs, dtype=np.float32)

    def embed_query(self, text: str) -> np.ndarray:
        prepped = f"{self._query_prefix}{text}" if self._query_prefix else text
        vec = self._model.encode(
            [prepped],
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return np.asarray(vec[0], dtype=np.float32)

    @property
    def dimension(self) -> int:
        return self._dim
