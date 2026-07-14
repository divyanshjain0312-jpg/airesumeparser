"""Ollama local LLM adapter using its HTTP API."""
from __future__ import annotations

import httpx

from app.llms.base import BaseLLM


class OllamaLLM(BaseLLM):
    provider_name = "ollama"

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2") -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    def generate(self, prompt: str) -> str:
        try:
            with httpx.Client(timeout=120.0) as client:
                resp = client.post(
                    f"{self.base_url}/api/generate",
                    json={"model": self.model, "prompt": prompt, "stream": False},
                )
                resp.raise_for_status()
                data = resp.json()
                return (data.get("response") or "").strip() or "[No response]"
        except Exception as e:
            raise RuntimeError(
                f"Ollama request failed. Is Ollama running at {self.base_url}? Underlying error: {e}"
            ) from e
