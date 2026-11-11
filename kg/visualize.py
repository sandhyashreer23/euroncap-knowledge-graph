"""Step 4: interactive HTML picture of the graph (pyvis).

render(graph)                       -> whole graph (overview, can look busy)
render(graph, focus="Frontal Impact") -> one entity and its neighbours (clear, readable)
"""
from pathlib import Path

import networkx as nx
from pyvis.network import Network

from kg.config import GRAPH_HTML
from kg.graph_build import load

COLORS = {
    "Protocol": "#1F3864", "Test": "#2E75B6", "Criterion": "#C55A11", "Dummy": "#7F6000",
    "System": "#548235", "Category": "#7030A0", "VehicleClass": "#BF9000", "Parameter": "#808080",
}


def focus_subgraph(g: nx.MultiDiGraph, node: str, hops: int = 1) -> nx.MultiDiGraph:
    """The node plus everything within `hops` steps, in either direction."""
    keep = nx.ego_graph(g.to_undirected(as_view=True), node, radius=hops).nodes
    return g.subgraph(keep).copy()


def legend_html() -> str:
    items = "".join(
        f'<span style="display:inline-block;margin:0 12px 4px 0;font:13px sans-serif;">'
        f'<span style="display:inline-block;width:12px;height:12px;border-radius:50%;'
        f'background:{c};margin-right:5px;vertical-align:middle;"></span>{t}</span>'
        for t, c in COLORS.items())
    return f'<div style="padding:8px 4px;">{items}</div>'


def render(graph=None, path=GRAPH_HTML, focus: str | None = None, hops: int = 1) -> str:
    g = graph if graph is not None else load()
    if focus:
        g = focus_subgraph(g, focus, hops)

    net = Network(height="720px", width="100%", directed=True, bgcolor="#ffffff", cdn_resources="in_line")
    for node, d in g.nodes(data=True):
        net.add_node(
            node, label=node, color=COLORS.get(d["type"], "#999"),
            title=f"{d['type']}\nSources: {', '.join(d['sources'][:5])}",
            size=30 if node == focus else 12 + 2 * min(g.degree(node), 10),
            font={"size": 18 if node == focus else 14, "color": "#222"},
        )
    for s, t, d in g.edges(data=True):
        net.add_edge(s, t, label=d["relation"] if focus else "",  # edge labels only in focus view
                     title=f"{d['relation']} | {', '.join(d['sources'][:3])}", arrows="to",
                     font={"size": 11, "align": "middle"}, color="#9DB3CC")

    if focus:
        net.repulsion(node_distance=220, spring_length=200)
    else:
        net.force_atlas_2based(gravity=-60, spring_length=120)

    # Write as UTF-8 ourselves: pyvis' write_html uses the Windows default
    # encoding (cp1252), which crashes on special characters.
    html = net.generate_html(notebook=False).replace("<body>", "<body>" + legend_html(), 1)
    Path(path).write_text(html, encoding="utf-8")
    print(f"Graph picture -> {path}")
    return str(path)


if __name__ == "__main__":
    render()