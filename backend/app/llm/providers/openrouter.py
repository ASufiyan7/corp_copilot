import os
from pydantic_ai.models.openai import OpenAIModel
from app.llm.base import LLMProvider
from openai import AsyncOpenAI

class OpenRouterProvider(LLMProvider):
    """
    Provider for OpenRouter models (OpenAI compatible API).
    """
    def create_model(self, model_name: str) -> OpenAIModel:
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
        client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        return OpenAIModel(model_name=model_name, provider=client)
