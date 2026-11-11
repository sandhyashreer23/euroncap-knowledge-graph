# Euro NCAP Knowledge Graph & GraphRAG

Turns Euro NCAP protocols into an **ontology-based knowledge graph** and answers questions with
**GraphRAG**: connected graph facts plus cited text passages.

Plain RAG finds text that *sounds* similar to a question. A knowledge graph adds what is *connected*:
which dummy a test uses, which criteria it measures, which assessment area it belongs to, even when
those facts sit on different pages or in different documents.

## Pipeline

```
PDFs ─► chunks (source + page) ─► Gemini extraction (ontology-constrained JSON)
     ─► normalisation (alias merging, ontology validation) ─► networkx graph
     ─► pyvis visualisation  +  GraphRAG answers (graph facts + FAISS/TF-IDF passages)
```

## Ontology

| Relation | Source → Target |
|---|---|
| DEFINES | Protocol → Test |
| BELONGS_TO | Test → Category |
| MEASURES | Test → Criterion |
| USES | Test → Dummy |
| EVALUATES | Test → System |
| APPLIES_TO | Test → VehicleClass |
| HAS_PARAMETER | Test → Parameter |
| PART_OF | Protocol → Category |

Defined in `kg/ontology.py`. Triples that break these rules are dropped during normalisation.

## Project structure

```
kg/
  config.py        settings and file paths
  ontology.py      entity types + allowed relations
  llm.py           Gemini wrapper (retry, JSON mode)
  chunking.py      PDFs -> page-aware chunks
  extract.py       chunks -> triples (cached, resumable)
  normalize.py     alias merging + ontology validation
  graph_build.py   networkx graph + statistics
  visualize.py     interactive HTML graph (pyvis)
  retrieval.py     FAISS (from the RAG assistant) or TF-IDF fallback
  graphrag.py      graph facts + passages -> cited answer
  evaluate.py      RAG vs GraphRAG comparison
run_pipeline.py    runs everything
app.py             Streamlit UI (Ask / Graph / Stats)
tests/             offline pytest tests
```

## Run it

```bash
pip install -r requirements.txt
cp .env.example .env              # add your GEMINI_API_KEY
# copy your Euro NCAP PDFs into data/pdfs/

python run_pipeline.py --limit 20  # quick test on 20 chunks
python run_pipeline.py             # full run (resumes where it stopped)
streamlit run app.py
pytest -q
python -m kg.evaluate              # optional: RAG vs GraphRAG numbers
```

To reuse the FAISS index from the RAG assistant, set `FAISS_INDEX_DIR` in `.env`
and install the commented packages in `requirements.txt`.

## Results

| Metric | Value |
|---|---|
| Documents | _fill in_ |
| Entities | _fill in_ |
| Relations | _fill in_ |
| Keyword coverage, RAG vs GraphRAG | _fill in_ |

## Lessons learned

The hardest part was not building the graph but keeping names consistent: the LLM writes
"AEB", "Autonomous Emergency Braking" and "AEB system" for the same concept. `normalize.py`
merges these with an alias table and rejects triples that violate the ontology.
