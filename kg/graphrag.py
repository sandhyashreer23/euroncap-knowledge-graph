"""Step 5: GraphRAG = graph facts + cited text chunks -> one grounded answer.

Vector search finds text that *sounds* similar; the graph adds what is
*connected* (e.g. which dummy and criteria a test uses), even if those
facts sit on other pages.
"""
import re
import time

import networkx as nx

from kg.llm import generate
from kg.retrieval import search


def match_entities(g: nx.MultiDiGraph, question: str, max_hits: int = 5) -> list[str]:
    """Find graph nodes whose name appears in the question (longest names first)."""
    q = question.lower()
    hits = [n for n in sorted(g.nodes, key=len, reverse=True)
            if len(n) > 2 and re.search(rf"\b{re.escape(n.lower())}\b", q)]
    return hits[:max_hits]


def graph_facts(g: nx.MultiDiGraph, nodes: list[str], hops: int = 1, limit: int = 40) -> list[str]:
    """Readable facts from the neighbourhood of the matched nodes."""
    facts, seen = [], set()
    frontier = set(nodes)
    for _ in range(hops):
        nxt = set()
        for n in frontier:
            for s, t, d in list(g.out_edges(n, data=True)) + list(g.in_edges(n, data=True)):
                key = (s, d["relation"], t)
                if key not in seen:
                    seen.add(key)
                    facts.append(f"{s} --{d['relation']}--> {t}  [{', '.join(d['sources'][:2])}]")
                    nxt.update((s, t))
        frontier = nxt - set(nodes)
    return facts[:limit]


PROMPT = """Answer the question about Euro NCAP using ONLY the context below.
Cite sources as (document, page), using ONLY the [document, p.X] label in front of each
passage or fact. Ignore page numbers printed inside the text itself (e.g. "Version 7.1.3 ... 17").
If the context is not enough, say so.

Graph facts (entity --RELATION--> entity [source]):
{facts}

Text passages:
{passages}

Question: {question}
Answer:"""


def answer(g: nx.MultiDiGraph, question: str, use_graph: bool = True) -> dict:
    t0 = time.perf_counter()
    nodes = match_entities(g, question) if use_graph else []
    facts = graph_facts(g, nodes) if nodes else []
    chunks = search(question)
    passages = "\n\n".join(f"[{c['source']}, p.{c['page']}] {c['text']}" for c in chunks)
    text = generate(PROMPT.format(facts="\n".join(facts) or "(none)",
                                  passages=passages or "(none)", question=question))
    return {"answer": text, "matched_entities": nodes, "graph_facts": facts,
            "chunks": chunks, "seconds": round(time.perf_counter() - t0, 2)}


if __name__ == "__main__":
    from kg.graph_build import load
    graph = load()
    q = input("Question: ")
    res = answer(graph, q)
    print("\nEntities:", res["matched_entities"])
    print("\n".join(res["graph_facts"][:10]))
    print("\n" + res["answer"])