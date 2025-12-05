
from fastapi import APIRouter, WebSocket
from pydantic import BaseModel
from pathlib import Path
import asyncio
import json

from ..workflows.generic_builder import run_generic_builder

router = APIRouter()


class GenerateProjectRequest(BaseModel):
    project_name: str
    idea: str
    options: dict = {}


class GenerateProjectResponse(BaseModel):
    project_name: str
    idea: str
    plan: dict
    created_files: list


@router.post("/generate_project", response_model=GenerateProjectResponse)
async def generate_project(payload: GenerateProjectRequest):
    projects_root = Path(__file__).resolve().parents[2] / "projects"
    project_root = projects_root / payload.project_name
    project_root.mkdir(parents=True, exist_ok=True)

    # Save options for later (logs WS, deps, etc.)
    (project_root / "project.json").write_text(json.dumps(payload.options, indent=2))

    plan, created_files = await run_generic_builder(
        project_name=payload.project_name,
        idea=payload.idea,
    )

    return GenerateProjectResponse(
        project_name=payload.project_name,
        idea=payload.idea,
        plan=plan,
        created_files=created_files,
    )


@router.websocket("/ws/generate/{project_name}")
async def generate_project_live(websocket: WebSocket, project_name: str):
    await websocket.accept()

    try:
        await websocket.send_json({
            "event": "start",
            "message": f"🚀 Starting code generation for {project_name}...",
            "progress": 0,
        })

        projects_root = Path(__file__).resolve().parents[2] / "projects"
        frontend_root = projects_root / project_name / "frontend"
        frontend_root.mkdir(parents=True, exist_ok=True)

        # Example files to generate (you can later make this dynamic from plan)
        files_to_generate = {
            "src/App.jsx": [
                'export default function App() {',
                '  return (',
                '    <div style={{ padding: 30 }}>',
                '      <h1>🚀 AI Generated React App</h1>',
                '      <p>Live code generation in progress...</p>',
                '    </div>',
                '  );',
                '}',
            ],
            "src/pages/Home.jsx": [
                'export default function Home() {',
                '  return <h2>🏠 Welcome Home!</h2>;',
                '}',
            ],
            "src/services/api.js": [
                "import axios from 'axios';",
                "export default axios.create({ baseURL: 'http://127.0.0.1:8000' });",
            ],
        }

        total_files = len(files_to_generate)
        completed_files = 0

        for rel_path, lines in files_to_generate.items():
            full_path = frontend_root / rel_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Notify file creation
            await websocket.send_json({
                "event": "file_create",
                "file": rel_path,
                "message": f"Creating {rel_path}...",
            })

            current_lines: list[str] = []

            with open(full_path, "w", encoding="utf-8") as f:
                for line in lines:
                    f.write(line + "\n")
                    current_lines.append(line)

                    # Simulate typing
                    await asyncio.sleep(0.12)

                    # Single line typed
                    await websocket.send_json({
                        "event": "writing",
                        "file": rel_path,
                        "line": line,
                    })

                    # Live full content update (for editor)
                    await websocket.send_json({
                        "event": "update_editor",
                        "file": str(full_path),
                        "content": "\n".join(current_lines),
                    })

            completed_files += 1
            progress = int((completed_files / total_files) * 100)

            await websocket.send_json({
                "event": "progress",
                "progress": progress,
            })

            # Simple ETA = remaining files in seconds
            await websocket.send_json({
                "event": "eta",
                "seconds": max(1, total_files - completed_files),
            })

            # Also tell frontend to open this file in editor
            await websocket.send_json({
                "event": "open_in_editor",
                "file": str(full_path),
            })

        await websocket.send_json({
            "event": "finish",
            "message": "🎉 Project generation complete!",
            "progress": 100,
        })

    except Exception as e:
        await websocket.send_json({
            "event": "error",
            "message": str(e),
        })

    finally:
        await websocket.close()
