# Mapping to Sir's In-Class Labs 1-6

RepoSage deliberately keeps the course pattern visible.

| Sir's lab | RepoSage implementation |
|---|---|
| Lab 1 - LLM Generation Parameters | `temperature=0.1` for factual codebase answers |
| Lab 2 - Introduction to LangChain | `init_chat_model`, runnable model, `ChatPromptTemplate` |
| Lab 3 - Structured Output Generation | Pydantic `RepoSageResponse` + `with_structured_output` |
| Lab 4 - RAG | local documents -> `RecursiveCharacterTextSplitter(1000, 200)` -> `OllamaEmbeddings` -> Chroma -> similarity + BM25/EnsembleRetriever |
| Lab 5 - Advanced RAG | MMR and optional `MultiQueryRetriever` |
| Lab 6 - RAG with LangGraph | `State(TypedDict)` and `START -> retrieve -> generate -> END` |

## Project-specific additions only

1. A local repository loader instead of `WebBaseLoader`/PDF loaders.
2. Python AST parsing so functions/classes become retrievable evidence units.
3. Secret-file and build-directory exclusions.
4. File/symbol/line metadata in answers.
5. CLI, Streamlit and FastAPI wrappers around the same RAG logic.

These additions do not replace the class RAG pipeline; they adapt the input data and product surface to the codebase-debugging use case.
