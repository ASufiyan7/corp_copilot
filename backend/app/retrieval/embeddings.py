from sentence_transformers import SentenceTransformer
from app.config import settings

class EmbeddingService:
    """
    Service for generating vector embeddings locally using Sentence Transformers.
    By default, it uses BAAI/bge-small-en-v1.5 and loads it on CPU.
    """
    def __init__(self):
        self._model = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            model_name = settings.embedding_model
            try:
                # Try loading the model (downloads it if not cached locally)
                self._model = SentenceTransformer(model_name, device="cpu")
            except Exception as e:
                # Fallback to local files only if internet is disconnected/HF Hub is blocked
                try:
                    self._model = SentenceTransformer(model_name, device="cpu", local_files_only=True)
                except Exception:
                    raise e
        return self._model

    def embed_text(self, text: str) -> list[float]:
        """
        Generate a 384-dimensional embedding vector for a single string.
        """
        if not text:
            return [0.0] * settings.embedding_dimensions
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a list of strings efficiently using batching.
        """
        if not texts:
            return []
        embeddings = self.model.encode(texts, convert_to_numpy=True, batch_size=32)
        return embeddings.tolist()

# Singleton instance for application-wide use
embedding_service = EmbeddingService()
