from typing import List, Dict, Any

def rerank_chunks(chunks: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    # Simple heuristic reranking
    query_lower = query.lower()
    
    for chunk in chunks:
        score = float(chunk.get("score", 0.0))
        payload = chunk.get("payload", {})
        text = payload.get("chunk_text", "").lower()
        
        # Boost exact keyword matches
        if any(word in text for word in query_lower.split()):
            score += 0.5
            
        # Boost specific types
        if payload.get("chunk_type") in ["medicine", "lab_value"]:
            score += 0.2
            
        chunk["rerank_score"] = score
        
    # Sort by rerank_score
    chunks.sort(key=lambda x: x.get("rerank_score", 0.0), reverse=True)
    return chunks
