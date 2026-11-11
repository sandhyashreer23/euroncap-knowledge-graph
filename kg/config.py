"""Central settings. Everything configurable lives here or in .env."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"


def _load_env() -> None:
    """Read .env from the project folder. Handles Windows quirks (BOM, UTF-16,
    quotes, spaces) without needing python-dotenv."""
    if not ENV_FILE.exists():
        return
    raw = ENV_FILE.read_bytes()
    text = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8-sig", "ignore")
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env()
DATA = ROOT / "data"
PDF_DIR = Path(os.getenv("PDF_DIR", DATA / "pdfs"))
OUT_DIR = DATA / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CHUNKS_FILE = OUT_DIR / "chunks.json"            # text chunks with source + page
TRIPLES_FILE = OUT_DIR / "triples_raw.json"      # LLM output, one entry per chunk
CLEAN_FILE = OUT_DIR / "triples_clean.json"      # after normalisation
GRAPH_FILE = OUT_DIR / "graph.json"              # networkx node-link JSON
GRAPH_HTML = OUT_DIR / "graph.html"              # pyvis visualisation

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1800"))      # characters
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Optional: reuse the FAISS index from your existing RAG assistant
FAISS_INDEX_DIR = os.getenv("FAISS_INDEX_DIR", "")