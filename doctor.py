import os
import shutil
import subprocess
import sys
from pathlib import Path

print("Python:", sys.version.split()[0])
print("Project:", Path(__file__).resolve().parent)
print("Ollama executable:", shutil.which("ollama") or "NOT FOUND")

if shutil.which("ollama"):
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        print("\nOllama models:\n", result.stdout.strip() or result.stderr.strip())
    except Exception as exc:
        print("Could not query Ollama:", exc)

required = ["OLLAMA_CHAT_MODEL", "OLLAMA_EMBED_MODEL"]
for key in required:
    print(f"{key}={os.getenv(key, '(using default)')}")

try:
    from rag_pipeline import index_info
    info = index_info()
    print("\nIndex:", info or "NOT BUILT - run python ingest.py")
except Exception as exc:
    print("Pipeline import check failed:", type(exc).__name__, exc)
