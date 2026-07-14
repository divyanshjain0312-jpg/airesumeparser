"""Abstract base for embedding models."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

import numpy as np


class BaseEmbedder(ABC):
    """Interface every embedder implements."""

    model_name: str = "base"

    @abstractmethod
    def embed(self, texts: List[str]) -> np.ndarray:
        """Return a (n, dim) numpy array of float32 embeddings."""

    @abstractmethod
    def embed_query(self, text: str) -> np.ndarray:
        """Return a (dim,) numpy array for a single query."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        ...
