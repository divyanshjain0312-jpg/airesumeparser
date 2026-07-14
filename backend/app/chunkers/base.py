"""Abstract base for chunking strategies."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


class BaseChunker(ABC):
    """Interface every chunker implements."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @abstractmethod
    def split(self, text: str) -> List[str]:
        """Return a list of non-empty chunks."""

    @property
    def name(self) -> str:
        return self.__class__.__name__
