from rank_bm25 import BM25Okapi
from typing import List, Dict, Any

class KeywordStore:
    def __init__(self):
        self.documents = []
        self.payloads = []
        self.bm25 = None

    def index(self, chunks: List[Dict[str, Any]]):
        self.documents = [c["chunk_text"].lower().split() for c in chunks]
        self.payloads = [c for c in chunks]
        if self.documents:
            self.bm25 = BM25Okapi(self.documents)

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not self.bm25:
            return []
            
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        
        results = []
        for i, score in enumerate(scores):
            if score > 0:
                results.append({
                    "payload": self.payloads[i],
                    "score": score
                })
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
