from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from fastapi import FastAPI


from ..tools.fs_tools import read_file
from ..agents.code_editor import edit_file_with_ai

router = APIRouter()
app = FastAPI()


def build_tree(path: Path):
    tree = []
    for item in path.iterdir():
        node = {
            "name": item.name,
            "path": str(item),
            "type": "file" if item.is_file() else "folder",
        }
        if item.is_dir():
            node["children"] = build_tree(item)
        tree.append(node)
    return tree


@router.get("/projects/{project_name}/tree")
async def get_project_tree(project_name: str):
    root = Path(__file__).resolve().parents[2] / "projects"
    project_dir = root / project_name

    if not project_dir.exists():
        raise HTTPException(404, "Project not found")

    return {"tree": build_tree(project_dir)}


@router.get("/file")
async def get_file(path: str):
    p = Path(path)

    if not p.exists():
        raise HTTPException(404, f"File not found: {path}")

    try:
        content = p.read_text(encoding="utf-8")
    except Exception:
        content = ""

    return {"content": content}

class EditFileRequest(BaseModel):
    path: str
    instruction: str


class EditFileResponse(BaseModel):
    path: str
    content: str


@router.post("/edit_file", response_model=EditFileResponse)
async def edit_file(payload: EditFileRequest):
    updated_path = await edit_file_with_ai(payload.path, payload.instruction)
    return EditFileResponse(
        path=updated_path,
        content=read_file(updated_path),
    )
