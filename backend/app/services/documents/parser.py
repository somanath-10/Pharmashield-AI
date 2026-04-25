import io
from pypdf import PdfReader
from fastapi import UploadFile

async def extract_text_from_file(file: UploadFile) -> str:
    # Read the content
    content = await file.read()
    
    # Reset file cursor so it can be saved later
    await file.seek(0)
    
    if file.content_type == "text/plain":
        return content.decode("utf-8")
        
    elif file.content_type == "application/pdf":
        pdf_file = io.BytesIO(content)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    else:
        raise ValueError(f"Unsupported content type: {file.content_type}")
