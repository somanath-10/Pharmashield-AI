from typing import List, Dict, Any
from app.services.rag.vector_store import get_vector_store
from app.services.rag.keyword_store import KeywordStore
from app.services.rag.query_expansion import expand_query
from app.services.rag.reranker import rerank_chunks
from app.services.rag.embeddings import get_embedding_provider
from app.models.domain import DocumentChunk

async def hybrid_retrieve(query: str, case_id: str, role: str) -> List[Dict[str, Any]]:
    # 1. Expand query
    expanded_query = expand_query(query, role)
    
    # 2. Vector Search
    embedding_provider = get_embedding_provider()
    query_vector = await embedding_provider.embed_text(expanded_query)
    vector_store = get_vector_store()
    vector_results = vector_store.search(query_vector, case_id, limit=5)
    
    # 3. Keyword Search
    # Fetch all chunks for this case from DB for on-the-fly BM25
    db_chunks = await DocumentChunk.find(DocumentChunk.case_id == case_id).to_list()
    chunks_data = [
        {
            "chunk_text": c.chunk_text,
            "chunk_id": c.chunk_id,
            "document_id": c.document_id,
            "document_name": c.metadata_json.get("document_name"),
            "chunk_type": c.chunk_type
        } for c in db_chunks
    ]
    
    keyword_store = KeywordStore()
    keyword_store.index(chunks_data)
    keyword_results = keyword_store.search(expanded_query, limit=5)
    
    # 4. Merge and Deduplicate
    merged = {}
    
    for r in vector_results:
        chunk_id = r["payload"].get("chunk_id")
        if chunk_id:
            merged[chunk_id] = r
            
    for r in keyword_results:
        chunk_id = r["payload"].get("chunk_id")
        if chunk_id:
            if chunk_id in merged:
                # Combine scores
                merged[chunk_id]["score"] += r["score"]
            else:
                merged[chunk_id] = r
                
    merged_results = list(merged.values())
    
    # 5. Rerank
    reranked = rerank_chunks(merged_results, query)
    
    return reranked[:5]
