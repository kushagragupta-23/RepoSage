# RepoSage Architecture

```text
Local repository
   |
   +-- source code
   +-- documentation
   +-- logs/config text
   |
Repository loader + Python AST symbol extraction
   |
RecursiveCharacterTextSplitter (1000 / 200)
   |
OllamaEmbeddings: nomic-embed-text
   |
Chroma persistent vector store
   |
   +-----------------------------+
   |                             |
BM25 lexical retrieval     Chroma semantic retrieval
   |                             |
   +------ EnsembleRetriever ----+
                 |
          retrieved evidence
                 |
          ChatPromptTemplate
                 |
       local Ollama chat model
                 |
     Pydantic structured output
                 |
LangGraph: START -> retrieve -> generate -> END
                 |
    CLI / Streamlit / FastAPI
```

## Why hybrid retrieval?

Code questions often contain exact identifiers (`ACCESS_TOKEN_EXPIRE_MINUTES`, function names, error strings) where BM25 is useful, while semantic retrieval helps when the developer describes the same concept using different words.

## Privacy model

Generation and embeddings can both run locally through Ollama. RepoSage skips common secret files such as `.env` and SSH private-key filenames and ignores common build/dependency directories.
