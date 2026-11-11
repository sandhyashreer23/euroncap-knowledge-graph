"""The mini-ontology: which kinds of things exist and how they may relate.

Think of it as the dictionary the whole graph must speak. The LLM may only
use these entity types and relations, which keeps the graph consistent.
"""

ENTITY_TYPES = {
    "Protocol":     "A Euro NCAP assessment protocol or test document, e.g. 'AEB Car-to-Car Test Protocol'",
    "Test":         "A specific test or scenario, e.g. 'CCRs', 'Full Width Frontal Impact', 'Pole Side Impact'",
    "Criterion":    "A measured value or pass/fail criterion, e.g. 'Head Injury Criterion (HIC15)', 'impact speed reduction'",
    "Dummy":        "A crash test dummy, e.g. 'Hybrid III 50th', 'Q6', 'WorldSID'",
    "System":       "A vehicle safety system or technology, e.g. 'AEB', 'Lane Keep Assist', 'ESC'",
    "Category":     "An assessment area, e.g. 'Adult Occupant Protection', 'Vulnerable Road User Protection'",
    "VehicleClass": "A vehicle or target type, e.g. 'M1 passenger car', 'Global Vehicle Target', 'cyclist target'",
    "Parameter":    "A test condition, e.g. 'test speed', 'overlap', 'impact angle'",
}

RELATIONS = {
    "DEFINES":      ("Protocol", "Test"),
    "BELONGS_TO":   ("Test", "Category"),
    "MEASURES":     ("Test", "Criterion"),
    "USES":         ("Test", "Dummy"),
    "EVALUATES":    ("Test", "System"),
    "APPLIES_TO":   ("Test", "VehicleClass"),
    "HAS_PARAMETER": ("Test", "Parameter"),
    "PART_OF":      ("Protocol", "Category"),
}


def ontology_text() -> str:
    """Human/LLM-readable description used inside the extraction prompt."""
    ents = "\n".join(f"- {k}: {v}" for k, v in ENTITY_TYPES.items())
    rels = "\n".join(f"- {r}: {s} -> {t}" for r, (s, t) in RELATIONS.items())
    return f"Entity types:\n{ents}\n\nAllowed relations (source -> target):\n{rels}"


def is_valid(src_type: str, relation: str, tgt_type: str) -> bool:
    """True only if the triple respects the ontology."""
    return RELATIONS.get(relation) == (src_type, tgt_type)
