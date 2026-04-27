from fastapi import UploadFile, HTTPException

ALLOWED_MIME_TYPES = [
    "application/pdf",
    "text/plain",
    "image/jpeg",
    "image/png",
    "image/webp",
]

IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE_MB = 10

def validate_document_upload(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Unsupported file type. Please upload a PDF, TXT, JPG, or PNG file."
        )
    if file.size and file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File size exceeds {MAX_FILE_SIZE_MB} MB limit.")

def is_image_upload(file: UploadFile) -> bool:
    return file.content_type in IMAGE_MIME_TYPES
