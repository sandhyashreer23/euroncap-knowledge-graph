"""One command for the whole pipeline:  python run_pipeline.py [--limit 20]"""
import argparse
import json

from kg.chunking import chunk_pdfs
from kg.config import CHUNKS_FILE
from kg.extract import extract
from kg.graph_build import build_graph, save, stats
from kg.normalize import normalize
from kg.visualize import render

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, help="extract only N chunks (quick test before the full run)")
    ap.add_argument("--rechunk", action="store_true", help="re-read the PDFs")
    args = ap.parse_args()

    if args.rechunk or not CHUNKS_FILE.exists():
        chunk_pdfs()
    extract(args.limit)
    graph = build_graph(normalize())
    save(graph)
    render(graph)
    print(json.dumps(stats(graph), indent=2))
