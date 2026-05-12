"""Extractors — Extracao de texto de PDF e DOCX."""

import io
import re
from pypdf import PdfReader
from docx import Document


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Roteia para o extrator correto baseado na extensao do arquivo."""
    name = filename.lower()
    if name.endswith(".pdf"):
        return _extract_pdf(file_bytes)
    if name.endswith(".docx"):
        return _extract_docx(file_bytes)
    raise ValueError(f"Formato nao suportado: {filename}. Use PDF ou DOCX.")


def _extract_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    raw_text = "\n\n".join(pages)
    return _post_process_text(raw_text)


def _extract_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    raw_text = "\n\n".join(paragraphs)
    return _post_process_text(raw_text)


def _post_process_text(text: str) -> str:
    """Corrige artefatos comuns de extracao de texto."""
    text = re.sub(r"\bR\s+(\d[\d.,]*)", r"R$ \1", text)
    text = re.sub(r"\bR(\d[\d.,]*)", r"R$ \1", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"-(\n+)(?=[a-záéíóúãõâêîôûç])", r"\1", text, flags=re.IGNORECASE)
    return text
