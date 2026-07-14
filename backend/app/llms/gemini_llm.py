"""Google Gemini LLM adapter."""
from __future__ import annotations

from app.llms.base import BaseLLM


class GeminiLLM(BaseLLM):
    provider_name = "gemini"

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash") -> None:
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        self._client = genai.GenerativeModel(model)
        self.model = model

    def generate(self, prompt: str) -> str:
        response = self._client.generate_content(prompt)
        # Some SDK versions may return None text if safety-blocked
        return (getattr(response, "text", None) or "").strip() or "[No response]"
