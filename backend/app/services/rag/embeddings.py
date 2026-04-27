import abc
from typing import List
import hashlib
import random

class EmbeddingProvider(abc.ABC):
    @abc.abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        pass

    @abc.abstractmethod
    async def embed_many(self, texts: List[str]) -> List[List[float]]:
        pass

class MockEmbeddingProvider(EmbeddingProvider):
    """
    Deterministic hash-based mock embedding provider.
    Same text always returns the same vector — ensuring search stability.
    Replace with a real provider (e.g. OpenAI, sentence-transformers) in production.
    """
    async def embed_text(self, text: str) -> List[float]:
        # Seed RNG from text hash so results are always deterministic
        seed = int(hashlib.sha256(text.encode()).hexdigest(), 16) % (2**32)
        rng = random.Random(seed)
        return [rng.uniform(-1, 1) for _ in range(384)]

    async def embed_many(self, texts: List[str]) -> List[List[float]]:
        return [await self.embed_text(t) for t in texts]

def get_embedding_provider() -> EmbeddingProvider:
    return MockEmbeddingProvider()
