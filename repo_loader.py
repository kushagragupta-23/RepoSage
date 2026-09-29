from __future__ import annotations

import ast
from pathlib import Path
from langchain_core.documents import Document

SUPPORTED_SUFFIXES = {
    ".py", ".md", ".txt", ".log", ".sql", ".json", ".yaml", ".yml",
    ".toml", ".ini", ".cfg", ".js", ".ts", ".tsx", ".jsx", ".java",
    ".go", ".rs", ".sh", ".ps1"
}

SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "dist", "build", "__pycache__",
    ".idea", ".vscode", ".pytest_cache", ".mypy_cache", "chroma_db"
}

SKIP_FILENAMES = {".env", ".env.local", ".env.production", "id_rsa", "id_ed25519"}
MAX_FILE_BYTES = 750_000


def _safe_relative(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.name


def _base_metadata(path: Path, repo_root: Path) -> dict:
    return {
        "source": path.name,
        "relative_path": _safe_relative(path, repo_root),
        "category": path.parent.name,
        "suffix": path.suffix.lower(),
        "document_type": "code" if path.suffix.lower() in {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs"} else "documentation",
    }


def python_symbol_documents(path: Path, repo_root: Path) -> list[Document]:
    """Project-specific addition: create class/function units with AST while retaining the full file."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    base = _base_metadata(path, repo_root)
    docs = [Document(page_content=text, metadata={**base, "symbol_type": "file", "symbol": path.name, "line_start": 1})]
    try:
        tree = ast.parse(text)
        lines = text.splitlines()
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            start = max(getattr(node, "lineno", 1) - 1, 0)
            end = getattr(node, "end_lineno", None) or min(start + 60, len(lines))
            snippet = "\n".join(lines[start:end])
            docs.append(Document(
                page_content=snippet,
                metadata={
                    **base,
                    "symbol_type": type(node).__name__,
                    "symbol": node.name,
                    "line_start": start + 1,
                    "line_end": end,
                },
            ))
    except SyntaxError:
        pass
    return docs


def should_index(path: Path) -> bool:
    if path.name in SKIP_FILENAMES:
        return False
    if path.suffix.lower() not in SUPPORTED_SUFFIXES:
        return False
    if any(part in SKIP_DIRS for part in path.parts):
        return False
    try:
        return path.stat().st_size <= MAX_FILE_BYTES
    except OSError:
        return False


def load_repository(repo_path: str | Path) -> list[Document]:
    repo_root = Path(repo_path).expanduser().resolve()
    if not repo_root.exists() or not repo_root.is_dir():
        raise ValueError(f"Repository path does not exist or is not a directory: {repo_root}")

    docs: list[Document] = []
    for path in sorted(repo_root.rglob("*")):
        if not path.is_file() or not should_index(path):
            continue
        if path.suffix.lower() == ".py":
            docs.extend(python_symbol_documents(path, repo_root))
        else:
            text = path.read_text(encoding="utf-8", errors="ignore")
            docs.append(Document(page_content=text, metadata=_base_metadata(path, repo_root)))
    return docs


def list_python_symbols(repo_path: str | Path, relative_path: str) -> list[dict]:
    repo_root = Path(repo_path).expanduser().resolve()
    path = (repo_root / relative_path).resolve()
    if repo_root not in path.parents and path != repo_root:
        raise ValueError("Path must stay inside the indexed repository")
    text = path.read_text(encoding="utf-8", errors="ignore")
    tree = ast.parse(text)
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.append({
                "name": node.name,
                "type": type(node).__name__,
                "line_start": getattr(node, "lineno", None),
                "line_end": getattr(node, "end_lineno", None),
            })
    return sorted(out, key=lambda x: (x["line_start"] or 0, x["name"]))
