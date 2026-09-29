# RepoSage

RepoSage indexes a local repository and lets you ask questions about its code, documentation and logs. For example:

- "How is token expiry configured?"
- "Which function validates the Bearer header?"
- "Why could the database connection be timing out?"
- "Explain the authentication request flow."

It retrieves relevant files and symbols before producing an answer with observed evidence, likely causes and source locations. The main notebook follows the instructor's In-Class Labs 1-6 so the steps can be followed during a viva or code walkthrough.

## What it indexes

- It can index a local repository as well as the bundled example repository.
- Python files are indexed with class and function information from the AST.
- BM25 handles exact code tokens while Chroma handles semantic matches.
- Answers keep observed evidence separate from likely causes.
- Results include source paths, symbols and line metadata.
- Ollama provides both embeddings and generation.
- The repository includes CLI, Streamlit, FastAPI and retrieval-evaluation entry points.

## Sir-code mapping

| Lab | RepoSage |
|---|---|
| 1. LLM Generation Parameters | low `temperature=0.1` |
| 2. Introduction to LangChain | `init_chat_model` + `ChatPromptTemplate` |
| 3. Structured Output | Pydantic + `with_structured_output` |
| 4. RAG | loader -> 1000/200 splitter -> Ollama embeddings -> Chroma -> BM25 + EnsembleRetriever |
| 5. Advanced RAG | MMR + optional MultiQueryRetriever |
| 6. RAG With LangGraph | `START -> retrieve -> generate -> END` |

See `docs/SIR_CODE_MAPPING.md` for the exact adaptation notes.

---

# 1. Requirements

- Python **3.10-3.12**
- Ollama installed and running
- A GPU is recommended for `qwen3:8b`, but a smaller Ollama model can be configured in `.env`

# 2. Windows setup

Open PowerShell in this folder:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup_windows.ps1
```

Or manually:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
ollama pull qwen3:8b
ollama pull nomic-embed-text
python ingest.py
python doctor.py
```


# 2A. Bundled example data

The repository includes a ready-to-index corpus under `dataset/`:

- `dataset/knowledge_base/demo_repo/` - code, docs, config, logs, incidents and tests
- `dataset/source_manifest.csv` - source-level metadata and descriptions
- `dataset/evaluation/evaluation_questions.csv` - 20 labelled retrieval questions
- `dataset/README.md` - dataset design and usage notes

The default `python ingest.py` command indexes this bundled dataset, so no external download is required for the first demo.

# 3. Run the example

```powershell
python cli.py "How is token expiry configured?"
python cli.py "Why could the database connection be timing out?"
python cli.py "Explain the authentication flow."
```

# 4. Index another repository

```powershell
python ingest.py --repo "C:\Users\Kushagra\Desktop\my-project"
```

RepoSage indexes supported source/doc/log text files and skips `.git`, virtual environments, `node_modules`, common build folders, `.env`, and common SSH-key filenames.

Then ask:

```powershell
python cli.py "Which files implement authentication?"
```

# 5. Streamlit app

```powershell
streamlit run app.py
```

The sidebar can point to a repository and rebuild the index. The main screen shows the answer, observed evidence, likely causes, recommended steps, source references and retrieved chunks.

# 6. FastAPI

```powershell
uvicorn api:app --reload
```

Open `http://127.0.0.1:8000/docs` for Swagger UI.

Example request:

```json
POST /ask
{
  "question": "Where is JWT expiry configured?"
}
```

# 7. Retrieval evaluation

```powershell
python evaluate.py
```

This compares **similarity vs MMR vs hybrid** on 20 labelled demo questions and writes:

- `evaluation/retrieval_results.csv`
- `evaluation/retrieval_summary.csv`

Metrics:

- source hit
- symbol hit
- reciprocal rank

Do not put a retrieval score on the resume until this script has actually run on Kushagra's final machine/environment.

# 8. Notebook

Open:

`RepoSage_Sir_Style_RAG.ipynb`

This notebook shows the RAG pipeline in the same order as the six class labs.

# 9. Tests

```powershell
pytest -q
```

The unit tests check local repository loading, AST symbol extraction, secret-file exclusion, the evaluation set and notebook structure. Ollama-dependent integration is tested during `ingest.py`, `doctor.py` and the live demo rather than in unit tests.

# 10. Demo order

See `DEMO_SCRIPT.md` and `VIVA_QA.md`.

## Project limitations

- Static source code does not prove runtime behavior.
- Retrieval quality depends on what has been indexed.
- Large monorepos may require more selective indexing/metadata filters.
- The default chunking is deliberately kept close to Sir's 1000/200 class baseline rather than claiming it is universally optimal for code.
