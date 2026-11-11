"""Step 2: clean the raw triples.

The hard part of a knowledge graph is naming: the LLM will write "AEB",
"Autonomous Emergency Braking" and "AEB system" for the same thing.
This step merges those and drops triples that break the ontology.
"""
import json
import re

from kg.config import CLEAN_FILE, TRIPLES_FILE
from kg.ontology import ENTITY_TYPES, is_valid

# Extend this as you spot duplicates in graph.html
ALIASES = {
    "autonomous emergency braking": "AEB",
    "aeb system": "AEB",
    "electronic stability control": "ESC",
    "lane keep assist": "LKA",
    "lane keeping assist": "LKA",
    "lane support systems": "LSS",
    "head injury criterion": "HIC15",
    "hic": "HIC15",
    "post-crash": "Post-Crash Safety",
    "post crash": "Post-Crash Safety",
    "post crash safety": "Post-Crash Safety",
    "overall rating scheme": "Overall Rating Scheme",
}

PREFIXES = ("euro ncap ",)   # "Euro NCAP Overall Rating Scheme" -> "Overall Rating Scheme"
_display: dict[str, str] = {}  # lower-case key -> first spelling seen


def canonical(name: str) -> str:
    clean = re.sub(r"\s+", " ", name.strip()).strip(" .,:;")
    key = clean.lower()
    for p in PREFIXES:
        if key.startswith(p) and len(key) > len(p) + 3:
            clean, key = clean[len(p):], key[len(p):]
    for k in (key, key.replace("-", " ")):  # "post-crash" == "post crash"
        if k in ALIASES:
            return ALIASES[k]
    # Case-insensitive merge: "Post-crash Safety" == "Post-Crash Safety"
    return _display.setdefault(key, clean)


def normalize() -> dict:
    raw = json.loads(TRIPLES_FILE.read_text(encoding="utf-8"))
    entities: dict[str, dict] = {}      # name -> {type, sources}
    relations: dict[tuple, dict] = {}   # (src, rel, tgt) -> {sources}
    dropped = 0

    for chunk in raw.values():
        cite = f"{chunk['source']} p.{chunk['page']}"
        types_here = {}
        for e in chunk["entities"]:
            name, etype = canonical(e.get("name", "")), e.get("type", "")
            if not name or etype not in ENTITY_TYPES:
                dropped += 1
                continue
            types_here[name] = etype
            node = entities.setdefault(name, {"type": etype, "sources": set()})
            node["sources"].add(cite)

        for r in chunk["relations"]:
            s, rel, t = canonical(r.get("source", "")), r.get("relation", ""), canonical(r.get("target", ""))
            st = types_here.get(s) or entities.get(s, {}).get("type")
            tt = types_here.get(t) or entities.get(t, {}).get("type")
            if not (st and tt and is_valid(st, rel, tt)):
                dropped += 1
                continue
            relations.setdefault((s, rel, t), {"sources": set()})["sources"].add(cite)

    clean = {
        "entities": [{"name": n, "type": d["type"], "sources": sorted(d["sources"])} for n, d in entities.items()],
        "relations": [{"source": s, "relation": r, "target": t, "sources": sorted(d["sources"])}
                      for (s, r, t), d in relations.items()],
        "dropped": dropped,
    }
    CLEAN_FILE.write_text(json.dumps(clean, indent=1), encoding="utf-8")
    print(f"{len(clean['entities'])} entities, {len(clean['relations'])} relations, {dropped} invalid items dropped")
    return clean


if __name__ == "__main__":
    normalize()