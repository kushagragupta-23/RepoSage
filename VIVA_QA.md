# RepoSage Viva / Interview Questions

## Why is this RAG instead of a normal chatbot?
The answer is grounded in a custom repository corpus. The system retrieves relevant code/docs/logs first and passes only that context to the model.

## Why BM25 + vector retrieval?
BM25 is strong for exact identifiers, function names and error strings. Vector search is useful for semantic paraphrases. Sir's Lab 4 already introduced the ensemble pattern, so RepoSage reuses it.

## Why Chroma?
It is the vector store used in the class RAG flow and supports persistent local storage, which keeps the project simple for a laptop demo.

## Why Ollama?
Kushagra has a GPU laptop. Ollama allows local generation and embeddings, which creates a strong privacy/offline engineering story while keeping the class LangChain interface.

## What is AST parsing?
Python's `ast` module parses source code into a syntax tree. RepoSage extracts functions and classes as additional documents so a query for a symbol can retrieve a focused code unit instead of only a large file chunk.

## Why not chunk code only with AST?
The project intentionally keeps Sir's `RecursiveCharacterTextSplitter` baseline for the main RAG experiment. AST documents are an additional metadata-aware source, not a replacement for the taught chunking approach.

## What does MultiQueryRetriever do?
It uses an LLM to generate alternate formulations of the same query, retrieves for those variants, and combines evidence. It is useful as an Advanced RAG experiment but is not required for every production request.

## What does LangGraph add here?
The final workflow makes retrieval and generation explicit nodes: START -> retrieve -> generate -> END. This mirrors Sir's Lab 6 and can later be expanded with routing or tool nodes.

## How do you evaluate it?
The included question set defines an expected source file and, for some questions, an expected Python symbol. The script compares similarity, MMR and hybrid retrieval using source hit, symbol hit and reciprocal rank.

## Main limitation?
Retrieval cannot find information that was never indexed. Static code also does not prove production runtime behavior; logs/tests/runtime traces would be needed for stronger diagnosis.
