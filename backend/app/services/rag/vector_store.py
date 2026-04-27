import logging
import uuid
from typing import List, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class QdrantVectorStore:
    def __init__(self):
        self._available = False
        self.client = None
        self.settings = get_settings()
        self.collection_name = self.settings.qdrant_collection_name
        self._connect()

    def _connect(self) -> None:
        try:
            if self.settings.qdrant_url == ":memory:":
                self.client = QdrantClient(location=":memory:")
            else:
                self.client = QdrantClient(
                    url=self.settings.qdrant_url,
                    api_key=self.settings.qdrant_api_key or None,
                )
            # Ensure collection exists
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
                )
            self._available = True
        except Exception as e:
            logger.warning(f"Qdrant unavailable — vector search disabled: {e}")
            self._available = False
            self.client = None

    def insert_chunks(self, points: List[PointStruct]) -> None:
        if not self._available:
            self._connect()
        if not self._available:
            return
        try:
            self.client.upsert(collection_name=self.collection_name, points=points)
        except Exception as e:
            logger.warning(f"Failed to upsert to Qdrant: {e}")

    def search(self, query_vector: List[float], case_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search Qdrant with case_id filter. Gracefully returns [] if unavailable."""
        if not self._available:
            self._connect()
        if not self._available:
            return []
        try:
            # qdrant-client ≥1.7 uses query_points; handle both APIs
            flt = Filter(
                must=[FieldCondition(key="case_id", match=MatchValue(value=case_id))]
            )
            try:
                # New API (qdrant-client ≥ 1.7.3)
                results = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    query_filter=flt,
                    limit=limit,
                ).points
            except AttributeError:
                # Fallback for older qdrant-client
                results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    query_filter=flt,
                    limit=limit,
                )
            return [{"payload": r.payload, "score": r.score} for r in results]
        except Exception as e:
            logger.warning(f"Qdrant search failed: {e}")
            return []


_vector_store = None

def get_vector_store() -> QdrantVectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = QdrantVectorStore()
    return _vector_store
