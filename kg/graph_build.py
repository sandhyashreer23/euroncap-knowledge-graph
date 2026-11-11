"""Step 3: clean triples -> networkx graph (+ the numbers for your resume)."""
import json
from collections import Counter

import networkx as nx
from networkx.readwrite import json_graph

from kg.config import CLEAN_FILE, GRAPH_FILE


def build_graph(clean: dict) -> nx.MultiDiGraph:
    g = nx.MultiDiGraph()
    for e in clean["entities"]:
        g.add_node(e["name"], type=e["type"], sources=e["sources"])
    for r in clean["relations"]:
        g.add_edge(r["source"], r["target"], relation=r["relation"], sources=r["sources"])
    return g


def stats(g: nx.MultiDiGraph) -> dict:
    sources = {s.split(" p.")[0] for _, d in g.nodes(data=True) for s in d.get("sources", [])}
    return {
        "entities": g.number_of_nodes(),
        "relations": g.number_of_edges(),
        "documents": len(sources),
        "entities_by_type": dict(Counter(d["type"] for _, d in g.nodes(data=True))),
        "relations_by_type": dict(Counter(d["relation"] for *_, d in g.edges(data=True))),
        "most_connected": sorted(g.degree, key=lambda x: -x[1])[:10],
    }


def save(g: nx.MultiDiGraph) -> None:
    GRAPH_FILE.write_text(json.dumps(json_graph.node_link_data(g, edges="links")), encoding="utf-8")


def load() -> nx.MultiDiGraph:
    return json_graph.node_link_graph(json.loads(GRAPH_FILE.read_text(encoding="utf-8")),
                                      directed=True, multigraph=True, edges="links")


if __name__ == "__main__":
    graph = build_graph(json.loads(CLEAN_FILE.read_text(encoding="utf-8")))
    save(graph)
    print(json.dumps(stats(graph), indent=2))
