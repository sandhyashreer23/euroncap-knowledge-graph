"""Offline tests (no API key needed):  pytest -q"""
from kg.graph_build import build_graph, stats
from kg.graphrag import graph_facts, match_entities
from kg.normalize import canonical
from kg.ontology import is_valid

CLEAN = {
    "entities": [
        {"name": "Pole Side Impact", "type": "Test", "sources": ["side.pdf p.3"]},
        {"name": "WorldSID", "type": "Dummy", "sources": ["side.pdf p.4"]},
        {"name": "Adult Occupant Protection", "type": "Category", "sources": ["side.pdf p.1"]},
    ],
    "relations": [
        {"source": "Pole Side Impact", "relation": "USES", "target": "WorldSID", "sources": ["side.pdf p.4"]},
        {"source": "Pole Side Impact", "relation": "BELONGS_TO", "target": "Adult Occupant Protection",
         "sources": ["side.pdf p.1"]},
    ],
}


def test_ontology_rules():
    assert is_valid("Test", "USES", "Dummy")
    assert not is_valid("Dummy", "USES", "Test")


def test_alias_merging():
    assert canonical("Autonomous Emergency Braking") == "AEB"
    assert canonical("  WorldSID. ") == "WorldSID"
    assert canonical("Post-crash Safety") == canonical("Post-Crash Safety") == "Post-Crash Safety"
    assert canonical("Euro NCAP Overall Rating Scheme") == "Overall Rating Scheme"
    assert canonical("Crash Protection") == canonical("crash protection")


def test_graph_and_stats():
    g = build_graph(CLEAN)
    s = stats(g)
    assert s["entities"] == 3 and s["relations"] == 2 and s["documents"] == 1


def test_graphrag_context():
    g = build_graph(CLEAN)
    hits = match_entities(g, "Which dummy is used in the pole side impact test?")
    assert hits == ["Pole Side Impact"]
    assert any("WorldSID" in f for f in graph_facts(g, hits))