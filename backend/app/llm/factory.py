from pydantic_ai.models import Model
from app.llm.providers.groq import GroqProvider
from app.llm.providers.openai import OpenAIProvider
from app.llm.providers.anthropic import AnthropicProvider
from app.llm.providers.openrouter import OpenRouterProvider

class LLMFactory:
    """
    Factory class for constructing PydanticAI Model instances.
    """
    def __init__(self):
        self._providers = {
            "groq": GroqProvider(),
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
            "openrouter": OpenRouterProvider()
        }

    def create(self, provider_name: str, model_name: str) -> Model:
        provider = self._providers.get(provider_name.lower())
        if not provider:
            raise ValueError(
                f"Unsupported LLM provider: {provider_name}. "
                f"Allowed providers: {list(self._providers.keys())}"
            )
        return provider.create_model(model_name)

# Singleton factory instance
llm_factory = LLMFactory()
