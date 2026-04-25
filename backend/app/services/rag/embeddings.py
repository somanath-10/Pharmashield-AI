import abc
from typing import List
import random

class EmbeddingProvider(abc.ABC):
    @abc.abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        pass

    @abc.abstractmethod
    async def embed_many(self, texts: List[str]) -> List[List[float]]:
        pass

class MockEmbeddingProvider(EmbeddingProvider):
    async def embed_text(self, text: str) -> List[float]:
        # Return a mock 384-dimensional vector (like sentence-transformers)
        return [random.uniform(-1, 1) for _ in range(384)]

    async def embed_many(self, texts: List[str]) -> List[List[float]]:
        return [await self.embed_text(t) for t in texts]

def get_embedding_provider() -> EmbeddingProvider:
    return MockEmbeddingProvider()
