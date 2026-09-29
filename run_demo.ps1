$ErrorActionPreference = "Stop"
.\.venv\Scripts\Activate.ps1
python doctor.py
python cli.py "How is token expiry configured?"
