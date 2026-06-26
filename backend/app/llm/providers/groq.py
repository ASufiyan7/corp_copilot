import os
from pydantic_ai.models.groq import GroqModel
from app.config import settings
from app.llm.base import LLMProvider

class GroqProvider(LLMProvider):
    """
    Provider for Groq models using PydanticAI.
    """
    def create_model(self, model_name: str) -> GroqModel:
        if settings.groq_api_key:
            os.environ["GROQ_API_KEY"] = settings.groq_api_key
        return GroqModel(model_name=model_name)
