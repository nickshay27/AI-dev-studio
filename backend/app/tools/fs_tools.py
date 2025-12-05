from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2] / "projects"

def read_file(path: str) -> str:
    full_path = BASE_DIR / path
    if not full_path.exists():
        return ""
    return full_path.read_text(encoding="utf-8")

def write_file(path: str, content: str) -> str:
    full_path = BASE_DIR / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    return str(full_path)

def append_file(path: str, content: str) -> str:
    full_path = BASE_DIR / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    if full_path.exists():
        existing = full_path.read_text(encoding="utf-8")
    else:
        existing = ""
    full_path.write_text(existing + content, encoding="utf-8")
    return str(full_path)
