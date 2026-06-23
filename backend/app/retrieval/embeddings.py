from sentence_transformers import SentenceTransformer
from app.config import settings

class EmbeddingService:
    """
    Service for generating vector embeddings locally using Sentence Transformers.
    By default, it uses BAAI/bge-small-en-v1.5 and loads it on CPU.
    """
    def __init__(self):
        # Explicitly set device to CPU for lightweight and predictable performance.
        self.model = SentenceTransformer(settings.embedding_model, device="cpu")

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
