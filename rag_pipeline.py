from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import List
from uuid import uuid4

import pandas as pd
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

# Sir Lab 2 / Lab 4 pattern
from langchain.chat_models import init_chat_model
# Sir Lab 4 / Lab 5 pattern
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain.retrievers import BM25Retriever, EnsembleRetriever
# Sir Lab 5 pattern
from langchain.retrievers.multi_query import MultiQueryRetriever
# Sir Lab 6 pattern
from langgraph.graph import START, StateGraph, END

from repo_loader import load_repository, list_python_symbols

load_dotenv(override=True)

PROJECT_ROOT = Path(__file__).resolve().parent
DEMO_REPO = PROJECT_ROOT / "dataset" / "knowledge_base" / "demo_repo"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"
INDEX_INFO = PROJECT_ROOT / ".reposage_index.json"
EVAL_FILE = PROJECT_ROOT / "evaluation" / "evaluation_questions.csv"

TOP_K = int(os.getenv("TOP_K", "4"))
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "ollama").lower().strip()
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "qwen3:8b")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
GROQ_CHAT_MODEL = os.getenv("GROQ_CHAT_MODEL", "openai/gpt-oss-20b")


class RepoSageResponse(BaseModel):
    answer: str = Field(description="Grounded answer to the codebase or debugging question")
    observed_evidence: list[str] = Field(description="Concrete facts directly supported by retrieved repository evidence")
    likely_causes: list[str] = Field(description="Possible causes; keep empty when the question is not diagnostic")
    recommended_steps: list[str] = Field(description="Safe next debugging or code-navigation steps")
    source_references: list[str] = Field(description="Files/functions used, ideally path plus line or symbol")
    information_gap: bool = Field(description="True if the retrieved repository evidence is insufficient")


def get_llm():
    """Keep Sir's init_chat_model pattern; only the provider/model is configurable."""
    if MODEL_PROVIDER == "groq":
        return init_chat_model(
            GROQ_CHAT_MODEL,
            model_provider="groq",
            temperature=0.1,
        )
    return init_chat_model(
        OLLAMA_CHAT_MODEL,
        model_provider="ollama",
        temperature=0.1,
    )


def get_embeddings():
    # Same embedding class/model pattern as Sir's RAG labs.
    return OllamaEmbeddings(model=OLLAMA_EMBED_MODEL)


def _source_text_map(docs: list[Document]) -> dict[str, str]:
    out = {}
    for doc in docs:
        if doc.metadata.get("symbol_type") == "file" or doc.metadata.get("symbol_type") is None:
            out.setdefault(doc.metadata.get("relative_path", ""), doc.page_content)
    return out


def split_documents(docs: list[Document]) -> list[Document]:
    # Sir Lab 4 baseline retained: 1000-character chunks with 200 overlap.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
    )
    splits = text_splitter.split_documents(docs)

    # Small RepoSage addition: derive approximate line ranges for easier source references.
    originals = _source_text_map(docs)
    for split in splits:
        path = split.metadata.get("relative_path", "")
        original = originals.get(path)
        start_index = split.metadata.get("start_index")
        if original is not None and isinstance(start_index, int):
            line_start = original.count("\n", 0, start_index) + 1
            line_end = line_start + split.page_content.count("\n")
            split.metadata.setdefault("line_start", line_start)
            split.metadata.setdefault("line_end", line_end)
    return splits


def _write_index_info(repo_path: Path, document_count: int, chunk_count: int) -> None:
    INDEX_INFO.write_text(json.dumps({
        "repo_path": str(repo_path),
        "document_count": document_count,
        "chunk_count": chunk_count,
        "embedding_model": OLLAMA_EMBED_MODEL,
    }, indent=2), encoding="utf-8")


def index_info() -> dict:
    if not INDEX_INFO.exists():
        return {}
    return json.loads(INDEX_INFO.read_text(encoding="utf-8"))


def indexed_repo_path() -> Path:
    info = index_info()
    return Path(info.get("repo_path", DEMO_REPO)).expanduser().resolve()


def ingest(repo_path: str | Path | None = None, rebuild: bool = True) -> dict:
    repo_root = Path(repo_path or DEMO_REPO).expanduser().resolve()
    docs = load_repository(repo_root)
    if not docs:
        raise RuntimeError(f"No supported source/doc/log files found under {repo_root}")
    splits = split_documents(docs)

    if rebuild and CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)

    vector_store_chroma = Chroma(
        collection_name="reposage-rag",
        embedding_function=get_embeddings(),
        persist_directory=str(CHROMA_DIR),
    )
    uuids = [str(uuid4()) for _ in range(len(splits))]
    vector_store_chroma.add_documents(documents=splits, ids=uuids)
    _write_index_info(repo_root, len(docs), len(splits))
    return index_info()


def _runtime():
    if not CHROMA_DIR.exists() or not INDEX_INFO.exists():
        raise RuntimeError("RepoSage index not found. Run: python ingest.py")
    repo_root = indexed_repo_path()
    if not repo_root.exists():
        raise RuntimeError(f"Previously indexed repository no longer exists: {repo_root}")
    docs = load_repository(repo_root)
    splits = split_documents(docs)
    vector_store_chroma = Chroma(
        collection_name="reposage-rag",
        embedding_function=get_embeddings(),
        persist_directory=str(CHROMA_DIR),
    )
    return splits, vector_store_chroma


def get_similarity_retriever(k: int = TOP_K):
    _, vector_store_chroma = _runtime()
    return vector_store_chroma.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )


def get_mmr_retriever(k: int = TOP_K):
    _, vector_store_chroma = _runtime()
    return vector_store_chroma.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k},
    )


def get_hybrid_retriever(k: int = TOP_K):
    all_splits, vector_store_chroma = _runtime()
    # Sir Lab 4: BM25 + Chroma using EnsembleRetriever and the same 0.7/0.3 weighting idea.
    bm25_retriever = BM25Retriever.from_documents(documents=all_splits)
    bm25_retriever.k = k
    chroma_retriever = vector_store_chroma.as_retriever(search_kwargs={"k": k})
    return EnsembleRetriever(
        retrievers=[bm25_retriever, chroma_retriever],
        weights=[0.7, 0.3],
    )


def get_multiquery_retriever(k: int = 2):
    base_retriever = get_similarity_retriever(k=k)
    return MultiQueryRetriever.from_llm(
        retriever=base_retriever,
        llm=get_llm(),
        include_original=True,
    )


def select_retriever(method: str):
    method = method.lower().strip()
    if method == "similarity":
        return get_similarity_retriever()
    if method == "mmr":
        return get_mmr_retriever()
    if method == "multiquery":
        return get_multiquery_retriever()
    return get_hybrid_retriever()


def format_docs(docs: list[Document]) -> str:
    formatted = []
    for doc in docs:
        m = doc.metadata
        line_start = m.get("line_start")
        line_end = m.get("line_end")
        line_text = f"{line_start}-{line_end}" if line_start else "unknown"
        symbol = m.get("symbol")
        formatted.append(
            f"SOURCE: {m.get('source')}\n"
            f"PATH: {m.get('relative_path')}\n"
            f"SYMBOL: {symbol or 'n/a'}\n"
            f"LINES: {line_text}\n"
            f"TYPE: {m.get('document_type')}\n"
            f"CONTENT:\n{doc.page_content}"
        )
    return "\n\n".join(formatted)


system_message_template = """You are RepoSage, a local codebase intelligence and debugging assistant.

Use ONLY the retrieved repository context supplied below. Do not invent files, functions, configuration values, logs, bugs, or runtime behavior.

Rules:
1. Put direct repository facts in observed_evidence.
2. Put uncertain diagnostic possibilities in likely_causes; do not present them as confirmed.
3. Give safe, concrete debugging/navigation steps.
4. Include useful source references such as path, symbol, or line range when available.
5. If the retrieved evidence cannot answer the question, clearly say so and set information_gap=true.
6. Never reveal or infer secrets. Secret files are intentionally excluded from indexing.

Retrieved context:
{context}
"""

reposage_prompt = ChatPromptTemplate([
    ("system", system_message_template),
    ("human", "Developer question: {question}"),
])


def answer_with_lcel(question: str, method: str = "hybrid"):
    retriever = select_retriever(method)
    docs = retriever.invoke(question)
    context = format_docs(docs)
    structured_llm = get_llm().with_structured_output(RepoSageResponse)
    answer = (reposage_prompt | structured_llm).invoke({
        "question": question,
        "context": context,
    })
    return answer, docs


class State(TypedDict):
    question: str
    context: List[Document]
    answer: RepoSageResponse


def retrieve(state: State):
    retriever = get_hybrid_retriever()
    retrieved_docs = retriever.invoke(state["question"])
    return {"context": retrieved_docs}


def generate(state: State):
    context = format_docs(state["context"])
    structured_llm = get_llm().with_structured_output(RepoSageResponse)
    response = (reposage_prompt | structured_llm).invoke({
        "question": state["question"],
        "context": context,
    })
    return {"answer": response}


def build_graph():
    # Sir Lab 6: START -> retrieve -> generate -> END.
    graph_builder = StateGraph(State)
    graph_builder.add_node("retrieve", retrieve)
    graph_builder.add_node("generate", generate)
    graph_builder.add_edge(START, "retrieve")
    graph_builder.add_edge("retrieve", "generate")
    graph_builder.add_edge("generate", END)
    return graph_builder.compile()


def ask(question: str):
    result = build_graph().invoke({"question": question})
    return result["answer"], result["context"]


def retrieve_only(question: str, method: str = "hybrid") -> list[Document]:
    return select_retriever(method).invoke(question)


def evaluate_retrieval(method: str = "hybrid") -> pd.DataFrame:
    eval_df = pd.read_csv(EVAL_FILE)
    rows = []
    for _, row in eval_df.iterrows():
        try:
            docs = retrieve_only(row["question"], method=method)
            paths = [d.metadata.get("relative_path", "") for d in docs]
            symbols = [d.metadata.get("symbol", "") for d in docs]
            expected_source = row["expected_source"]
            expected_symbol = str(row.get("expected_symbol", "") or "")
            source_hit = int(any(expected_source == p or p.endswith(expected_source) for p in paths))
            symbol_hit = int(not expected_symbol or expected_symbol == "nan" or expected_symbol in symbols)
            reciprocal_rank = 0.0
            for rank, p in enumerate(paths, 1):
                if expected_source == p or p.endswith(expected_source):
                    reciprocal_rank = 1.0 / rank
                    break
            rows.append({
                "question_id": row["question_id"],
                "method": method,
                "question": row["question"],
                "expected_source": expected_source,
                "source_hit": source_hit,
                "symbol_hit": symbol_hit,
                "reciprocal_rank": reciprocal_rank,
                "retrieved_paths": " | ".join(paths),
            })
        except Exception as exc:
            rows.append({
                "question_id": row["question_id"],
                "method": method,
                "question": row["question"],
                "expected_source": row["expected_source"],
                "source_hit": 0,
                "symbol_hit": 0,
                "reciprocal_rank": 0.0,
                "retrieved_paths": f"ERROR: {type(exc).__name__}: {exc}",
            })
    return pd.DataFrame(rows)


def symbols(relative_path: str) -> list[dict]:
    return list_python_symbols(indexed_repo_path(), relative_path)
