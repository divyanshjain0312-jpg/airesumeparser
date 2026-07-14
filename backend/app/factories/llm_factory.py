"""Factory that instantiates an LLM provider from the frontend config string."""
from __future__ import annotations

from app.config import Settings
from app.llms.anthropic_llm import AnthropicLLM
from app.llms.base import BaseLLM
from app.llms.gemini_llm import GeminiLLM
from app.llms.ollama_llm import OllamaLLM
from app.llms.openai_llm import OpenAILLM


class LLMFactory:
    @classmethod
    def create(cls, provider: str, settings: Settings) -> BaseLLM:
        key = (provider or "").lower()

        if key == "gemini":
            return GeminiLLM(api_key=settings.gemini_api_key, model=settings.gemini_model)
        if key == "openai":
            return OpenAILLM(api_key=settings.openai_api_key, model=settings.openai_model)
        if key == "claude":
            return AnthropicLLM(
                api_key=settings.anthropic_api_key, model=settings.anthropic_model
            )
        if key in ("ollama", "llama", "mistral", "huggingface"):
            # For 'llama' / 'mistral' / 'huggingface' selections in the UI, route
            # through Ollama running locally, which supports both model families.
            model = settings.ollama_default_model
            if key == "llama":
                model = "llama3.2"
            elif key == "mistral":
                model = "mistral"
            return OllamaLLM(base_url=settings.ollama_base_url, model=model)

        raise ValueError(f"Unknown LLM provider: {provider!r}")

    @classmethod
    def available_providers(cls) -> list[str]:
        return ["gemini", "openai", "claude", "ollama", "llama", "mistral"]
