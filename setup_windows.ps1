$ErrorActionPreference = "Stop"

if (-Not (Test-Path ".venv")) {
    python -m venv .venv
}
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "\nPulling Ollama models..."
ollama pull qwen3:8b
ollama pull nomic-embed-text

if (-Not (Test-Path ".env")) {
    Copy-Item .env.example .env
}

Write-Host "\nBuilding demo repository index..."
python ingest.py
python doctor.py

Write-Host "\nSetup complete. Run: streamlit run app.py"
