import io
import logging
from fastapi import UploadFile

logger = logging.getLogger(__name__)


async def extract_text_from_file(file: UploadFile) -> str:
    """Extract text from an uploaded file. Never raises — always returns some text."""
    content = await file.read()
    await file.seek(0)

    if file.content_type == "text/plain":
        return content.decode("utf-8", errors="replace")

    if file.content_type in ("application/pdf", "application/octet-stream"):
        try:
            from pypdf import PdfReader
            pdf_file = io.BytesIO(content)
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
            if text.strip():
                return text
        except Exception as e:
            logger.warning(f"pypdf extraction failed for {file.filename}: {e}")

        # Fallback to raw text decode — always succeeds
        return content.decode("latin-1", errors="replace")

    # Images, unknown types → return placeholder so ingestion can continue
    logger.info(f"Unsupported type {file.content_type} for {file.filename} — using placeholder.")
    return f"Uploaded document: {file.filename or 'unknown'}"
