# Resume Bullets

Use only metrics that you have actually measured after running the project.

- Built **RepoSage**, a local-first codebase intelligence and debugging assistant using LangChain, LangGraph, Ollama and Chroma, grounding responses in repository source code, documentation and application logs.
- Implemented **hybrid BM25 + semantic retrieval**, Python AST-based function/class indexing, metadata-rich source references and Pydantic structured responses to separate observed evidence from diagnostic hypotheses.
- Developed an end-to-end evaluation and serving workflow with similarity/MMR/hybrid retrieval comparison, Streamlit UI, FastAPI endpoints and fully local LLM/embedding inference through Ollama.

After evaluation, optionally add a measured retrieval metric, for example: "achieved X% source hit@4 on a 12-question labelled retrieval set." Do not add a number until it has been produced by `python evaluate.py` on the final environment.
