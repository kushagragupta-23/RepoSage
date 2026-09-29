from pathlib import Path

from repo_loader import load_repository, list_python_symbols, should_index

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "dataset" / "knowledge_base" / "demo_repo"


def test_demo_repository_loads_documents():
    docs = load_repository(DEMO)
    assert len(docs) >= 8
    paths = {d.metadata.get("relative_path") for d in docs}
    assert "src/auth.py" in paths
    assert "logs/app.log" in paths


def test_python_ast_symbols_are_created():
    docs = load_repository(DEMO)
    symbols = {d.metadata.get("symbol") for d in docs}
    assert "create_access_token" in symbols
    assert "validate_bearer_header" in symbols


def test_symbol_inspector():
    symbols = list_python_symbols(DEMO, "src/auth.py")
    names = {item["name"] for item in symbols}
    assert "create_access_token" in names


def test_secret_filename_is_skipped(tmp_path):
    secret = tmp_path / ".env"
    secret.write_text("SECRET=value", encoding="utf-8")
    assert should_index(secret) is False
