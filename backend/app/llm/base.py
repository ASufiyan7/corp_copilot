from abc import ABC, abstractmethod
from pydantic_ai.models import Model

class LLMProvider(ABC):
    """
    Abstract base class defining the contract for LLM providers.
    """
    @abstractmethod
    def create_model(self, model_name: str) -> Model:
        """
        Create and return a PydanticAI Model instance.
        """
        pass
