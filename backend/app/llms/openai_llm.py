"""OpenAI Chat Completions LLM adapter."""
from __future__ import annotations

from app.llms.base import BaseLLM


class OpenAILLM(BaseLLM):
    provider_name = "openai"

    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, prompt: str) -> str:
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant analyzing a resume."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return (resp.choices[0].message.content or "").strip() or "[No response]"
