from app.models.domain import DocumentTypeEnum

def classify_document(text: str) -> DocumentTypeEnum:
    text_lower = text.lower()
    
    if "rx" in text_lower or "tab" in text_lower or "cap" in text_lower:
        return DocumentTypeEnum.PRESCRIPTION
        
    if any(keyword in text_lower for keyword in ["hba1c", "hemoglobin", "wbc", "reference range"]):
        return DocumentTypeEnum.LAB_REPORT
        
    if any(keyword in text_lower for keyword in ["discharge summary", "admission", "diagnosis"]):
        return DocumentTypeEnum.DISCHARGE_SUMMARY
        
    if any(keyword in text_lower for keyword in ["invoice", "mrp", "gst"]):
        return DocumentTypeEnum.INVOICE
        
    return DocumentTypeEnum.OTHER
