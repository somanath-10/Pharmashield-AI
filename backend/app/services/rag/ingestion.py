from typing import Dict, Any
import uuid
from qdrant_client.http.models import PointStruct
from app.models.domain import UserDocument, DocumentChunk, ExtractedMedicine, ExtractedLabValue, DocumentTypeEnum
from app.services.documents.classifier import classify_document
from app.services.documents.extractor import extract_medicines, extract_lab_values
from app.services.rag.chunking import chunk_document
from app.services.rag.embeddings import get_embedding_provider
from app.services.rag.vector_store import vector_store

async def ingest_document(doc: UserDocument, text: str) -> Dict[str, Any]:
    # 1. Classify
    doc_type = classify_document(text)
    doc.document_type = doc_type
    doc.text_content = text
    await doc.save()

    # 2. Extract structured data
    medicines = []
    if doc_type == DocumentTypeEnum.PRESCRIPTION:
        meds_data = extract_medicines(text)
        for md in meds_data:
            m = ExtractedMedicine(case_id=doc.case_id, document_id=doc.document_id, **md)
            await m.insert()
            medicines.append(m)

    lab_values = []
    if doc_type == DocumentTypeEnum.LAB_REPORT:
        labs_data = extract_lab_values(text)
        for ld in labs_data:
            l = ExtractedLabValue(case_id=doc.case_id, document_id=doc.document_id, **ld)
            await l.insert()
            lab_values.append(l)

    # 3. Chunking
    base_metadata = {
        "document_id": doc.document_id,
        "case_id": doc.case_id,
        "user_id": doc.user_id,
        "document_type": doc_type.value,
        "document_name": doc.file_name,
    }
    chunks = chunk_document(text, doc_type, base_metadata)

    # 4. Embed and Store
    embedding_provider = get_embedding_provider()
    points = []
    
    chunks_created = 0
    for chunk in chunks:
        chunk_text = chunk["text"]
        metadata = chunk["metadata"]
        
        # Save to MongoDB
        db_chunk = DocumentChunk(
            document_id=doc.document_id,
            case_id=doc.case_id,
            chunk_text=chunk_text,
            chunk_type=metadata.get("chunk_type", "generic"),
            metadata_json=metadata
        )
        await db_chunk.insert()
        
        # Embed
        vector = await embedding_provider.embed_text(chunk_text)
        
        # Qdrant Point
        point_id = str(uuid.uuid4())
        db_chunk.qdrant_point_id = point_id
        await db_chunk.save()
        
        payload = metadata.copy()
        payload["chunk_id"] = db_chunk.chunk_id
        payload["chunk_text"] = chunk_text
        
        points.append(PointStruct(id=point_id, vector=vector, payload=payload))
        chunks_created += 1

    if points:
        vector_store.insert_chunks(points)

    return {
        "document_id": doc.document_id,
        "status": "processed",
        "document_type": doc_type.value,
        "chunks_created": chunks_created,
        "medicines_extracted": [m.medicine_name for m in medicines],
        "lab_values_extracted": [{"test_name": l.test_name, "test_value": l.test_value} for l in lab_values]
    }
