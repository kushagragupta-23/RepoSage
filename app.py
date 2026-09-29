from pathlib import Path
import streamlit as st

from rag_pipeline import DEMO_REPO, ask, index_info, ingest

st.set_page_config(page_title="RepoSage", page_icon="🧭", layout="wide")
st.title("RepoSage")
st.caption("Local codebase intelligence & debugging RAG - built from Sir's Labs 1-6 patterns")

with st.sidebar:
    st.subheader("Repository index")
    current = index_info()
    default_path = current.get("repo_path", str(DEMO_REPO))
    repo_path = st.text_input("Local repository path", value=default_path)
    if st.button("Build / rebuild index", use_container_width=True):
        with st.spinner("Indexing repository with Ollama embeddings..."):
            try:
                info = ingest(repo_path, rebuild=True)
                st.success(f"Indexed {info['chunk_count']} chunks")
            except Exception as exc:
                st.error(f"Indexing failed: {type(exc).__name__}: {exc}")
    st.write("Current index")
    st.json(index_info() or {"status": "not built"})

question = st.text_area(
    "Ask about the indexed codebase",
    value="How is token expiry configured?",
    height=90,
)

if st.button("Ask RepoSage", type="primary"):
    with st.spinner("Retrieving repository evidence and generating answer..."):
        try:
            answer, docs = ask(question)
        except Exception as exc:
            st.error(f"Request failed: {type(exc).__name__}: {exc}")
        else:
            st.subheader("Answer")
            st.write(answer.answer)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Observed evidence")
                for item in answer.observed_evidence:
                    st.markdown(f"- {item}")
                if answer.likely_causes:
                    st.markdown("#### Likely causes")
                    for item in answer.likely_causes:
                        st.markdown(f"- {item}")
            with c2:
                st.markdown("#### Recommended steps")
                for item in answer.recommended_steps:
                    st.markdown(f"- {item}")
                st.metric("Information gap", "Yes" if answer.information_gap else "No")

            st.markdown("#### Source references")
            for item in answer.source_references:
                st.code(item)

            with st.expander("Retrieved chunks"):
                for i, doc in enumerate(docs, 1):
                    st.markdown(f"**{i}. {doc.metadata.get('relative_path')} - {doc.metadata.get('symbol','')}**")
                    st.text(doc.page_content[:1200])
