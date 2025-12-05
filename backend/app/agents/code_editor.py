import os
import asyncio
import pathlib
from ..model_router import call_llm
from ..tools.fs_tools import read_file, write_file


# -------------------------------
# 🔧 CLEAN UP AI OUTPUT
# -------------------------------
def clean_model_output(text: str) -> str:
    """
    Remove DeepSeek / Llama garbage tokens and malformed JSX artifacts.
    """
    garbage_tokens = [
        "<<｜begin▁of▁sentence｜>>",
        "<<｜begin▁of▁sentence｜>",
        "<<｜end▁of▁sentence｜>>",
        "<<｜end▁of▁sentence｜>",
        "<<",
        ">>",
        "▁",
    ]

    for g in garbage_tokens:
        text = text.replace(g, "")

    # Fix broken angle brackets
    text = text.replace("< <", "<").replace("> >", ">")

    # Sometimes DeepSeek outputs partial nonsense like: <div className=...
    # Ensure JSX doesn't accidentally start with invalid token
    return text.strip()


# -------------------------------
# 📌 FIX PATH HANDLING
# -------------------------------
def normalize_path(path: str) -> str:
    """Converts messy user paths into clean absolute paths."""
    path = path.strip().replace('"', '').replace("'", "")
    path = path.replace("\\", "/")
    path = path.replace(" /", "/").replace("/ ", "/")

    backend_root = pathlib.Path(__file__).resolve().parents[2]
    full = pathlib.Path(backend_root, path).resolve()

    return str(full)


# -------------------------------
# 🤖 AI CODE EDITOR
# -------------------------------
async def edit_file_with_ai(path: str, instruction: str) -> str:
    path = normalize_path(path)

    if not os.path.exists(path):
        raise FileNotFoundError(path)

    original = read_file(path)

    system = (
        "You are a senior software engineer.\n"
        "You rewrite the file EXACTLY according to the instruction.\n"
        "Return ONLY the updated file content.\n"
        "NO explanations, NO comments, NO markdown fences.\n"
    )

    user = (
        f"FILE PATH: {path}\n"
        f"INSTRUCTION: {instruction}\n\n"
        "---- ORIGINAL FILE ----\n"
        f"{original}\n"
        "---- END ORIGINAL FILE ----\n"
    )

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    raw = await asyncio.to_thread(
        call_llm,
        messages,
        json_mode=False,
        task_type="code",
    )

    updated = raw.strip()

    # Remove accidental ```
    if updated.startswith("```"):
        updated = updated.strip("`")
        # Remove filetype annotation
        if updated.lower().startswith(("json", "js", "jsx", "tsx", "ts", "py")):
            updated = updated.split("\n", 1)[1]

    # 🔥 FINAL CLEANUP FIX
    updated = clean_model_output(updated)

    write_file(path, updated)
    return path
