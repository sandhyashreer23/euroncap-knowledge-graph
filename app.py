"""Streamlit UI:  streamlit run app.py"""
import streamlit as st
import streamlit.components.v1 as components

from kg.config import GRAPH_FILE, GRAPH_HTML
from kg.graph_build import load, stats
from kg.graphrag import answer
from kg.visualize import render

st.set_page_config(page_title="Euro NCAP Knowledge Graph", layout="wide")
st.title("Euro NCAP Knowledge Graph & GraphRAG")

if not GRAPH_FILE.exists():
    st.warning("No graph yet. Run `python run_pipeline.py` first.")
    st.stop()


@st.cache_resource
def get_graph():
    return load()


g = get_graph()
ask_tab, graph_tab, stats_tab = st.tabs(["Ask", "Graph", "Stats"])

with ask_tab:
    q = st.text_input("Question", placeholder="Which dummy and criteria are used in the pole side impact test?")
    use_graph = st.toggle("Use knowledge graph (GraphRAG)", value=True)
    if q:
        with st.spinner("Thinking..."):
            res = answer(g, q, use_graph=use_graph)
        st.markdown(res["answer"])
        st.caption(f"{res['seconds']} s · matched entities: {', '.join(res['matched_entities']) or 'none'}")
        with st.expander(f"Graph facts used ({len(res['graph_facts'])})"):
            st.code("\n".join(res["graph_facts"]) or "none")
        with st.expander("Source passages"):
            for c in res["chunks"]:
                st.markdown(f"**{c['source']}, p.{c['page']}** — {c['text'][:400]}...")

with graph_tab:
    hubs = [n for n, _ in sorted(g.degree, key=lambda x: -x[1])]
    default = hubs.index("Frontal Impact") + 1 if "Frontal Impact" in hubs else 1
    choice = st.selectbox("Focus on an entity (or show the whole graph)",
                          ["Whole graph"] + hubs, index=default)
    hops = st.radio("Neighbourhood depth", [1, 2], horizontal=True) if choice != "Whole graph" else 1
    focus_html = GRAPH_HTML.with_name("graph_focus.html")
    if choice == "Whole graph":
        if not GRAPH_HTML.exists():
            render(g)
        html_file = GRAPH_HTML
    else:
        render(g, path=focus_html, focus=choice, hops=hops)
        html_file = focus_html
    components.html(html_file.read_text(encoding="utf-8"), height=800, scrolling=True)

with stats_tab:
    s = stats(g)
    c1, c2, c3 = st.columns(3)
    c1.metric("Entities", s["entities"])
    c2.metric("Relations", s["relations"])
    c3.metric("Documents", s["documents"])
    st.subheader("Entities by type")
    st.bar_chart(s["entities_by_type"])
    st.subheader("Most connected")
    st.table({"entity": [n for n, _ in s["most_connected"]], "connections": [d for _, d in s["most_connected"]]})