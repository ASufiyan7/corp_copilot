import os
from pydantic_ai.models.openai import OpenAIModel
from app.config import settings
from app.llm.base import LLMProvider

class OpenAIProvider(LLMProvider):
    """
    Provider for OpenAI models using PydanticAI.
    """
    def create_model(self, model_name: str) -> OpenAIModel:
        if settings.openai_api_key:
            os.environ["OPENAI_API_KEY"] = settings.openai_api_key
        return OpenAIModel(model_name=model_name)
