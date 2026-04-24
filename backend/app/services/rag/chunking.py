from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path
from typing import Any

from pypdf import PdfReader


def chunk_section_aware_text(
    text: str,
    *,
    source_type: str,
    source_name: str,
    source_url: str | None = None,
    document_title: str | None = None,
    default_section: str = "general",
    extra_metadata: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    sections: list[tuple[str, list[str]]] = []
    current_section = default_section
    current_lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.isupper() and len(line) < 80:
            if current_lines:
                sections.append((current_section, current_lines))
            current_section = line.lower().replace(" ", "_")
            current_lines = []
            continue
        if line.endswith(":") and len(line) < 90:
            if current_lines:
                sections.append((current_section, current_lines))
            current_section = line[:-1].strip().lower().replace(" ", "_")
            current_lines = []
            continue
        current_lines.append(line)
    if current_lines:
        sections.append((current_section, current_lines))

    chunks: list[dict[str, Any]] = []
    for section_name, lines in sections or [(default_section, [text])]:
        paragraph: list[str] = []
        for line in lines:
            paragraph.append(line)
            if len(" ".join(paragraph)) >= 500:
                chunks.append(
                    _chunk_payload(
                        " ".join(paragraph),
                        source_type=source_type,
                        source_name=source_name,
                        source_url=source_url,
                        document_title=document_title,
                        section_title=section_name,
                        extra_metadata=extra_metadata,
                    )
                )
                paragraph = []
        if paragraph:
            chunks.append(
                _chunk_payload(
                    " ".join(paragraph),
                    source_type=source_type,
                    source_name=source_name,
                    source_url=source_url,
                    document_title=document_title,
                    section_title=section_name,
                    extra_metadata=extra_metadata,
                )
            )
    return chunks


def parse_uploaded_document(path: Path, content_type: str, raw_bytes: bytes) -> str:
    if content_type == "application/pdf" or path.suffix.lower() == ".pdf":
        with path.open("rb") as file_obj:
            reader = PdfReader(file_obj)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
    if content_type == "text/csv" or path.suffix.lower() == ".csv":
        text = raw_bytes.decode("utf-8", errors="ignore")
        csv_reader = csv.reader(StringIO(text))
        return "\n".join(", ".join(row) for row in csv_reader)
    return raw_bytes.decode("utf-8", errors="ignore")


def _chunk_payload(
    text: str,
    *,
    source_type: str,
    source_name: str,
    source_url: str | None,
    document_title: str | None,
    section_title: str,
    extra_metadata: dict[str, Any] | None,
) -> dict[str, Any]:
    metadata = {"source_type": source_type, "section": section_title}
    if extra_metadata:
        metadata.update(extra_metadata)
    return {
        "source_type": source_type,
        "source_name": source_name,
        "source_url": source_url,
        "document_title": document_title,
        "section_title": section_title,
        "chunk_text": text,
        "metadata_json": metadata,
    }
