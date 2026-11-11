"""Step 0: PDFs -> page-aware text chunks (source + page kept for citations)."""
import json
from pathlib import Path

from pypdf import PdfReader

from kg.config import CHUNK_OVERLAP, CHUNK_SIZE, CHUNKS_FILE, PDF_DIR


def split_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return []
    out, start = [], 0
    while start < len(text):
        out.append(text[start:start + size])
        start += size - overlap
    return out


def chunk_pdfs(pdf_dir: Path = PDF_DIR) -> list[dict]:
    chunks = []
    pdfs = sorted(pdf_dir.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"No PDFs found in {pdf_dir}. Copy your Euro NCAP PDFs there.")
    for pdf in pdfs:
        reader = PdfReader(pdf)
        for page_no, page in enumerate(reader.pages, start=1):
            for i, piece in enumerate(split_text(page.extract_text() or "")):
                chunks.append({
                    "id": f"{pdf.stem}-p{page_no}-{i}",
                    "source": pdf.name,
                    "page": page_no,
                    "text": piece,
                })
    CHUNKS_FILE.write_text(json.dumps(chunks, indent=1), encoding="utf-8")
    print(f"Chunked {len(pdfs)} PDFs into {len(chunks)} chunks -> {CHUNKS_FILE.name}")
    return chunks


def load_chunks() -> list[dict]:
    return json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))


if __name__ == "__main__":
    chunk_pdfs()
