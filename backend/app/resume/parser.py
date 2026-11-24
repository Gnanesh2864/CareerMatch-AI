import io
import os
import re
from typing import Tuple
from fastapi import UploadFile, HTTPException
from pypdf import PdfReader
from app.config import settings

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Extracts raw text content from uploaded PDF or text file with defensive safeguards."""
    if len(file_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)}MB."
        )

    ext = filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in settings.ALLOWED_UPLOAD_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed types: {', '.join(settings.ALLOWED_UPLOAD_EXTENSIONS)}"
        )

    if ext == "pdf":
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            text_parts = []
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_parts.append(extracted)
            full_text = "\n".join(text_parts).strip()
            if not full_text:
                raise ValueError("No readable text found in PDF.")
            return full_text
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Could not parse PDF content safely: {str(e)}"
            )

    # For .txt or .docx/markdown text fallback
    try:
        return file_bytes.decode("utf-8", errors="replace").strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file text: {str(e)}")
