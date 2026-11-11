"""Step 1: chunks -> (entity, relation, entity) triples via Gemini.

Results are cached per chunk id, so re-running only processes new chunks
(saves API quota if the run stops halfway).
"""
import argparse
import json

from kg.chunking import load_chunks
from kg.config import TRIPLES_FILE
from kg.llm import generate_json
from kg.ontology import ontology_text

PROMPT = """You extract a knowledge graph from Euro NCAP documents.

{ontology}

Rules:
- Use ONLY the entity types and relations listed above.
- Use short canonical names (e.g. "AEB Car-to-Car", not a full sentence).
- Only extract facts stated in the text. If nothing fits, return empty lists.

Return JSON exactly in this shape:
{{"entities": [{{"name": "...", "type": "..."}}],
  "relations": [{{"source": "...", "relation": "...", "target": "..."}}]}}

Text (from {source}, page {page}):
\"\"\"{text}\"\"\"
"""


def extract(limit: int | None = None) -> dict:
    chunks = load_chunks()
    cache = json.loads(TRIPLES_FILE.read_text()) if TRIPLES_FILE.exists() else {}
    todo = [c for c in chunks if c["id"] not in cache][: limit or None]
    print(f"{len(cache)} chunks cached, {len(todo)} to extract")

    for n, ch in enumerate(todo, 1):
        result = generate_json(PROMPT.format(ontology=ontology_text(), **ch))
        cache[ch["id"]] = {
            "source": ch["source"],
            "page": ch["page"],
            "entities": result.get("entities", []),
            "relations": result.get("relations", []),
        }
        if n % 10 == 0 or n == len(todo):  # save progress regularly
            TRIPLES_FILE.write_text(json.dumps(cache, indent=1), encoding="utf-8")
            print(f"  {n}/{len(todo)} done")
    return cache


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, help="only process N new chunks (for a quick test)")
    extract(ap.parse_args().limit)
