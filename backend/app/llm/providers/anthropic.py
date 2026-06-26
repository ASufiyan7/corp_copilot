import os
from pydantic_ai.models.anthropic import AnthropicModel
from app.llm.base import LLMProvider

class AnthropicProvider(LLMProvider):
    """
    Provider for Anthropic models using PydanticAI.
    """
    def create_model(self, model_name: str) -> AnthropicModel:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key
        return AnthropicModel(model_name=model_name)
