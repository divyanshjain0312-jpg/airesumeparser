"""Anthropic Claude LLM adapter."""
from __future__ import annotations

from app.llms.base import BaseLLM


class AnthropicLLM(BaseLLM):
    provider_name = "claude"

    def __init__(self, api_key: str, model: str = "claude-3-5-haiku-latest") -> None:
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured.")
        import anthropic

        self._client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def generate(self, prompt: str) -> str:
        message = self._client.messages.create(
            model=self.model,
            max_tokens=1024,
            system="You are a helpful assistant analyzing a resume.",
            messages=[{"role": "user", "content": prompt}],
        )
        parts = []
        for block in message.content:
            if getattr(block, "type", None) == "text":
                parts.append(block.text)
        return ("".join(parts)).strip() or "[No response]"
