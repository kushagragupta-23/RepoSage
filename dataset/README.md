# RepoSage RAG Dataset

This folder contains the complete bundled knowledge corpus used by the RepoSage demo. It is intentionally small enough for a laptop demo but varied enough to demonstrate retrieval across code, documentation, configuration, logs, tests and incident reports.

## Folder structure

- `knowledge_base/demo_repo/src/` - Python application source code
- `knowledge_base/demo_repo/docs/` - architecture, API and troubleshooting documentation
- `knowledge_base/demo_repo/config/` - structured application configuration
- `knowledge_base/demo_repo/logs/` - runtime and deployment logs
- `knowledge_base/demo_repo/incidents/` - incident postmortem material
- `knowledge_base/demo_repo/tests/` - test code that can also be retrieved as evidence
- `source_manifest.csv` - one row per source document with category and description
- `evaluation/evaluation_questions.csv` - labelled retrieval questions with expected source/symbol

## Why this counts as a RAG dataset

RepoSage is a codebase RAG system, so its retrieval corpus is a repository rather than a conventional tabular ML dataset. The application loads these files as LangChain `Document` objects, attaches path/type metadata, creates additional AST-level Python function/class documents, chunks the corpus using Sir's 1000/200 baseline, embeds it with `OllamaEmbeddings`, and indexes it in Chroma.

## Evaluation

The labelled question set is used to compare similarity, MMR and hybrid BM25 + Chroma retrieval. It checks whether the expected source file and, when relevant, the expected Python symbol appear in the retrieved results.

## Using another repository

The bundled dataset is for immediate demonstration. Kushagra can replace it with any local project:

```powershell
python ingest.py --repo "C:\path\to\another-repository"
```

Do not index secrets such as `.env` files, private keys or credentials. RepoSage's loader excludes common secret filenames by default.
