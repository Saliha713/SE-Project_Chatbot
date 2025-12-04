import io
import os
from PyPDF2 import PdfReader
from embedding import embed_text
from storage import ensure_index, index, metadata, save_index

def extract_pages(file_bytes):
    reader = PdfReader(io.BytesIO(file_bytes))
    return [{"page": i+1, "text": p.extract_text() or ""} for i, p in enumerate(reader.pages)]

def chunk_text(text, size=1000, overlap=200):
    chunks, start = [], 0
    while start < len(text):
        end = min(start+size, len(text))
        chunk = text[start:end].strip()
        if chunk: chunks.append(chunk)
        start += size - overlap
    return chunks

def ingest_pdf_bytes(file_bytes, source_name=""):
    pages = extract_pages(file_bytes)
    ensure_index()

    new_chunks, meta = [], []
    for p in pages:
        for chunk in chunk_text(p["text"]):
            new_chunks.append(chunk)
            meta.append({"page": p["page"], "text_snippet": chunk[:500], "source": source_name})

    vectors = embed_text(new_chunks)
    index.add(vectors)
    metadata.extend(meta)
    save_index()
    return len(meta)
