from typing import List, Dict, Any
from app.models.domain import DocumentTypeEnum

def chunk_document(text: str, doc_type: DocumentTypeEnum, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Mock type-aware chunking for MVP
    chunks = []
    
    if doc_type == DocumentTypeEnum.PRESCRIPTION:
        # Split by newlines and group roughly
        lines = text.split("\n")
        chunk_text = ""
        for line in lines:
            if line.strip():
                chunk_text += line + "\n"
            if len(chunk_text) > 100: # Simple threshold
                chunk_meta = metadata.copy()
                chunk_meta["chunk_type"] = "medicine"
                chunks.append({"text": chunk_text.strip(), "metadata": chunk_meta})
                chunk_text = ""
        if chunk_text.strip():
            chunk_meta = metadata.copy()
            chunk_meta["chunk_type"] = "medicine"
            chunks.append({"text": chunk_text.strip(), "metadata": chunk_meta})
            
    elif doc_type == DocumentTypeEnum.LAB_REPORT:
        # Split by newlines
        lines = text.split("\n")
        chunk_text = ""
        for line in lines:
            if line.strip():
                chunk_text += line + "\n"
            if len(chunk_text) > 150:
                chunk_meta = metadata.copy()
                chunk_meta["chunk_type"] = "lab_value"
                chunks.append({"text": chunk_text.strip(), "metadata": chunk_meta})
                chunk_text = ""
        if chunk_text.strip():
            chunk_meta = metadata.copy()
            chunk_meta["chunk_type"] = "lab_value"
            chunks.append({"text": chunk_text.strip(), "metadata": chunk_meta})
            
    else:
        # Generic chunking
        paragraphs = text.split("\n\n")
        for p in paragraphs:
            if p.strip():
                chunk_meta = metadata.copy()
                chunk_meta["chunk_type"] = "generic"
                chunks.append({"text": p.strip(), "metadata": chunk_meta})
                
    return chunks
