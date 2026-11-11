"""Text retrieval for GraphRAG.

Uses your existing RAG assistant's FAISS index if FAISS_INDEX_DIR is set
(LangChain format + Gemini embeddings). Otherwise falls back to TF-IDF over
chunks.json, so the project also runs on its own.
"""
from functools import lru_cache

from kg.config import FAISS_INDEX_DIR


@lru_cache(maxsize=1)
def _faiss_store():
    from langchain_community.vectorstores import FAISS
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    emb = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    return FAISS.load_local(FAISS_INDEX_DIR, emb, allow_dangerous_deserialization=True)


@lru_cache(maxsize=1)
def _tfidf():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from kg.chunking import load_chunks
    chunks = load_chunks()
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    return chunks, vec, vec.fit_transform(c["text"] for c in chunks)


def search(query: str, k: int = 4) -> list[dict]:
    """Return [{'text', 'source', 'page'}] for the k best chunks."""
    if FAISS_INDEX_DIR:
        docs = _faiss_store().similarity_search(query, k=k)
        return [{"text": d.page_content,
                 "source": d.metadata.get("source", "?"),
                 "page": d.metadata.get("page", "?")} for d in docs]
    chunks, vec, mat = _tfidf()
    scores = (mat @ vec.transform([query]).T).toarray().ravel()
    return [chunks[i] for i in scores.argsort()[::-1][:k] if scores[i] > 0]
