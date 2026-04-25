from typing import List, Dict, Any
import uuid

def build_citations(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    citations = []
    for chunk in chunks:
        payload = chunk.get("payload", {})
        
        snippet = payload.get("chunk_text", "")
        if len(snippet) > 150:
            snippet = snippet[:150] + "..."
            
        citations.append({
            "citation_id": f"cit_{uuid.uuid4().hex[:8]}",
            "document_name": payload.get("document_name", "Unknown Document"),
            "page_number": payload.get("page_number", 1),
            "section_title": payload.get("section_title"),
            "source_snippet": snippet,
            "chunk_id": payload.get("chunk_id")
        })
    return citations
