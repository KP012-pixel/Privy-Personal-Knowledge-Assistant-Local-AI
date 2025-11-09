"""
Streamlit app that supports:
- Upload PDF/DOCX/TXT
- Ingest and index to FAISS using sentence-transformers
- Simple QA: embed query -> retrieve top chunks -> call local LLM (Ollama) for answer
This is a simple demo-level front end for Privy.
"""

import streamlit as st
from backend.ingestion import ingest_document
from backend.embeddings import embed_texts
from backend.vectorstore import FaissStore
from backend.llm import answer_from_context, is_ollama_available
import numpy as np
import os
import tempfile
import uuid

st.set_page_config(page_title="Privy — Personal Knowledge", layout="wide")
st.title("Privy — Personal Knowledge Assistant")
st.markdown("Professional UI · Local models · Privacy-first")

# Globals (in-memory for demo)
if "store" not in st.session_state:
    # Create a store once we know embedding dim after first embed
    st.session_state["store"] = None
if "chunks" not in st.session_state:
    st.session_state["chunks"] = []  # list of metadata dicts
if "dim" not in st.session_state:
    st.session_state["dim"] = None

col1, col2 = st.columns([1, 2])

with col1:
    st.header("Upload & Index")
    uploaded = st.file_uploader("Upload PDF / DOCX / TXT", type=['pdf', 'docx', 'txt'], accept_multiple_files=True)
    if uploaded:
        for f in uploaded:
            # Save temp file
            tmpdir = tempfile.gettempdir()
            fname = os.path.join(tmpdir, f"{uuid.uuid4().hex}-{f.name}")
            with open(fname, "wb") as out:
                out.write(f.getbuffer())
            st.info(f"Ingesting {f.name} ...")
            chunks = ingest_document(fname, source_name=f.name)
            if not chunks:
                st.warning("No extractable text found.")
                continue
            texts = [c['text'] for c in chunks]
            embs = embed_texts(texts)
            dim = embs.shape[1]
            if st.session_state["store"] is None:
                st.session_state["dim"] = dim
                st.session_state["store"] = FaissStore(dim=dim)
            st.session_state["store"].add(embs, chunks)
            st.session_state["chunks"].extend(chunks)
            st.success(f"Ingested {len(chunks)} chunks from {f.name}")

    st.write("---")
    st.subheader("Indexed documents")
    if st.session_state["chunks"]:
        # show top 10 sources
        from collections import Counter
        srcs = Counter([c['source'] for c in st.session_state["chunks"]])
        for s, cnt in srcs.most_common():
            st.write(f"- **{s}** — {cnt} chunks")
    else:
        st.write("No documents indexed yet. Upload a PDF or DOCX to begin.")

    st.write("---")
    st.markdown("**Model status**")
    st.write(f"Ollama available: {is_ollama_available()}")

with col2:
    st.header("Ask Privy")
    query = st.text_input("Ask a question about your indexed documents:")
    top_k = st.slider("Top K chunks to retrieve", 1, 10, 6)
    if st.button("Ask") and query.strip():
        if st.session_state["store"] is None or not st.session_state["chunks"]:
            st.warning("No indexed documents. Upload files first.")
        else:
            # Embed query
            q_emb = embed_texts([query])  # returns (1, dim)
            results = st.session_state["store"].search(q_emb, k=top_k)
            top_chunks = results[0] if results else []
            st.subheader("Retrieved context")
            for i, c in enumerate(top_chunks):
                st.markdown(f"**{i+1}.** `{c.get('chunk_id')}` — {c.get('source')} (page {c.get('page')}) — score: {c.get('score'):.3f}")
                snippet = c.get('text','')
                st.write(snippet[:600] + ("..." if len(snippet) > 600 else ""))

            st.info("Calling local LLM for final answer...")
            try:
                answer = answer_from_context(query, top_chunks)
                st.subheader("Answer")
                st.write(answer)
            except Exception as e:
                st.error(f"LLM call failed: {e}")

    st.write("---")
    st.markdown("**Export / Utilities**")
    if st.button("Clear index"):
        st.session_state["store"] = None
        st.session_state["chunks"] = []
        st.session_state["dim"] = None
        st.success("Index cleared.")
