import uuid
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct
from typing import List, Dict, Any
from app.core.config import get_settings

class QdrantVectorStore:
    def __init__(self):
        settings = get_settings()
        if settings.qdrant_url == ":memory:":
            self.client = QdrantClient(location=":memory:")
        else:
            self.client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None)
        self.collection_name = settings.qdrant_collection_name
        
        # Ensure collection exists
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
        except Exception as e:
            print(f"Failed to connect to Qdrant or create collection: {e}")

    def insert_chunks(self, points: List[PointStruct]):
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
        except Exception as e:
            print(f"Failed to upsert to Qdrant: {e}")

    def search(self, query_vector: List[float], case_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter={
                    "must": [
                        {"key": "case_id", "match": {"value": case_id}}
                    ]
                },
                limit=limit
            )
            return [{"payload": r.payload, "score": r.score} for r in results]
        except Exception as e:
            print(f"Failed to search Qdrant: {e}")
            return []
            
vector_store = QdrantVectorStore()
