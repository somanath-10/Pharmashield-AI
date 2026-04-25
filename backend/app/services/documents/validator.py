from fastapi import UploadFile, HTTPException

ALLOWED_MIME_TYPES = ["application/pdf", "text/plain"]
MAX_FILE_SIZE_MB = 10

def validate_document_upload(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are allowed.")
    if file.size and file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File size exceeds {MAX_FILE_SIZE_MB}MB limit.")
