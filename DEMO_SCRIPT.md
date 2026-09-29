# 6-8 Minute Demo Script

## 1. Problem (45 sec)
"Developers joining an unfamiliar repository waste time searching code, docs and logs separately. RepoSage retrieves repository evidence first, then answers from that evidence."

## 2. Show the class mapping (45 sec)
Open `docs/SIR_CODE_MAPPING.md`. Explain that the core follows Labs 1-6: low-temperature model, LangChain prompt, structured output, Chroma + BM25 hybrid RAG, MultiQuery experiment, and LangGraph.

## 3. Build index (60 sec)
```powershell
python ingest.py
```
Point out that Python AST parsing adds function/class metadata, but chunking remains Sir's 1000/200 baseline.

## 4. Question 1 - code navigation (60 sec)
```powershell
python cli.py "How is token expiry configured?"
```
Show that the answer references `src/config.py` and the 30-minute default.

## 5. Question 2 - debugging (90 sec)
```powershell
python cli.py "Why could the database connection be timing out?"
```
Show the difference between observed log evidence and likely causes.

## 6. UI (60 sec)
```powershell
streamlit run app.py
```
Ask "Explain the authentication flow" and expand retrieved chunks.

## 7. Evaluation (60 sec)
```powershell
python evaluate.py
```
Explain source hit rate and reciprocal rank across similarity, MMR and hybrid retrieval. Do not claim a winning method until the evaluation has actually been run on the demo machine.

## 8. Limitation (30 sec)
RepoSage only knows indexed repository content. It cannot prove runtime behavior that is not present in code/logs/docs, and it intentionally excludes common secret files.
