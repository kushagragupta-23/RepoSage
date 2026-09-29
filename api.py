from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from rag_pipeline import ask, index_info, ingest

app = FastAPI(title="RepoSage API", version="1.0.0")


class AskRequest(BaseModel):
    question: str


class IngestRequest(BaseModel):
    repo_path: str


@app.get("/health")
def health():
    return {"status": "ok", "index": index_info()}


@app.post("/ingest")
def build_index(request: IngestRequest):
    try:
        return ingest(request.repo_path, rebuild=True)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"{type(exc).__name__}: {exc}") from exc


@app.post("/ask")
def ask_reposage(request: AskRequest):
    try:
        answer, docs = ask(request.question)
        return {
            "answer": answer.model_dump(),
            "retrieved": [
                {
                    "path": d.metadata.get("relative_path"),
                    "symbol": d.metadata.get("symbol"),
                    "line_start": d.metadata.get("line_start"),
                    "line_end": d.metadata.get("line_end"),
                }
                for d in docs
            ],
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"{type(exc).__name__}: {exc}") from exc
