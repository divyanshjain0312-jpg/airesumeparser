"""Abstract base for LLM providers."""
from __future__ import annotations

from abc import ABC, abstractmethod


class BaseLLM(ABC):
    provider_name: str = "base"

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Return the model's completion for the given prompt."""
