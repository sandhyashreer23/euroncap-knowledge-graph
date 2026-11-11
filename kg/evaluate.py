"""Step 6 (optional but strong for interviews): compare plain RAG vs GraphRAG.

Fill data/eval_questions.json with ~10-20 questions and keywords a correct
answer must contain. Gives you honest numbers for the resume.
"""
import json

from kg.config import DATA
from kg.graph_build import load
from kg.graphrag import answer


def score(text: str, keywords: list[str]) -> float:
    t = text.lower()
    return sum(k.lower() in t for k in keywords) / max(len(keywords), 1)


def run() -> None:
    questions = json.loads((DATA / "eval_questions.json").read_text(encoding="utf-8"))
    g = load()
    rows = []
    for q in questions:
        rag = answer(g, q["question"], use_graph=False)
        grag = answer(g, q["question"], use_graph=True)
        rows.append((score(rag["answer"], q["keywords"]), score(grag["answer"], q["keywords"]),
                     rag["seconds"], grag["seconds"]))
        print(f"- {q['question'][:60]:60}  RAG {rows[-1][0]:.2f} | GraphRAG {rows[-1][1]:.2f}")
    n = len(rows)
    print(f"\nKeyword coverage  RAG: {sum(r[0] for r in rows)/n:.0%}   GraphRAG: {sum(r[1] for r in rows)/n:.0%}")
    print(f"Avg response time RAG: {sum(r[2] for r in rows)/n:.1f}s  GraphRAG: {sum(r[3] for r in rows)/n:.1f}s")


if __name__ == "__main__":
    run()
