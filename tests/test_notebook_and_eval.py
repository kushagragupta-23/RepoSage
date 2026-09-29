import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_evaluation_dataset_has_twenty_questions():
    with (ROOT / "evaluation" / "evaluation_questions.csv").open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 20
    assert all(row["expected_source"] for row in rows)


def test_notebook_is_valid_json_and_has_lab_sections():
    nb = json.loads((ROOT / "RepoSage_Sir_Style_RAG.ipynb").read_text(encoding="utf-8"))
    text = "\n".join("".join(cell.get("source", [])) for cell in nb["cells"])
    for phrase in [
        "Initial Setup", "OllamaEmbeddings", "RecursiveCharacterTextSplitter",
        "Chroma", "BM25Retriever", "MultiQueryRetriever", "StateGraph",
    ]:
        assert phrase in text
