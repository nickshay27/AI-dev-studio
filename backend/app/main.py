from dotenv import load_dotenv
load_dotenv()

from fastapi import (
    FastAPI,
    HTTPException,
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from pathlib import Path

import subprocess
import asyncio
import re

# internal imports
from .workflows.generic_builder import run_generic_builder
from .agents.code_editor import edit_file_with_ai
from .tools.fs_tools import read_file

# =============================================================================
# SETTINGS
# =============================================================================

# Path to npm on your machine
NPM_PATH = r"C:\Program Files\nodejs\npm.cmd"   # keep this as on your machine
fixed_port = 3000

router = APIRouter()
running_processes: Dict[str, subprocess.Popen] = {}

# =============================================================================
# SIMPLE RUN / STOP PROJECT
# =============================================================================

@router.post("/run_project")
def run_project(data: dict):
    project = data.get("project_name")
    if not project:
        raise HTTPException(400, "project_name is required")

    backend_root = Path(__file__).resolve().parents[1]
    project_root = backend_root / "projects" / project
    frontend_dir = project_root / "frontend"

    if not frontend_dir.exists():
        raise HTTPException(404, f"Frontend folder not found at {frontend_dir}")

    if not Path(NPM_PATH).exists():
        raise HTTPException(500, f"npm not found at: {NPM_PATH}")

    # Frontend will open this URL in new tab
    return {"status": "ready", "url": f"http://127.0.0.1:{fixed_port}"}


@router.post("/stop_project")
def stop_project(data: dict):
    project = data.get("project_name")
    if not project:
        raise HTTPException(400, "project_name is required")

    proc = running_processes.get(project)
    if proc and proc.poll() is None:
        proc.terminate()

    running_processes.pop(project, None)
    return {"status": "stopped"}


# =============================================================================
# MAIN FASTAPI APP
# =============================================================================

app = FastAPI(title="AI Dev Team")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


# =============================================================================
# PROJECT GENERATION (HTTP)
# =============================================================================

class GenerateProjectRequest(BaseModel):
    project_name: str
    idea: str


class GenerateProjectResponse(BaseModel):
    project_name: str
    idea: str
    plan: Dict[str, Any]
    created_files: List[str]


@app.post("/generate_project", response_model=GenerateProjectResponse)
async def generate_project(payload: GenerateProjectRequest):
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


# =============================================================================
# LIVE PROJECT GENERATION (SHOW TYPING + PROGRESS)
#   /ws/generate/{project_name}
#   → frontend uses this to show code typing in Monaco editor
# =============================================================================

@app.websocket("/ws/generate/{project_name}")
async def generate_project_live(websocket: WebSocket, project_name: str):
    await websocket.accept()

    try:
        await websocket.send_json({
            "event": "start",
            "message": f"🚀 Starting code generation for {project_name}...",
            "progress": 0,
        })

        projects_root = Path(__file__).resolve().parents[1] / "projects"
        project_root = projects_root / project_name / "frontend"
        project_root.mkdir(parents=True, exist_ok=True)

        # Example files we "type out" live
        files_to_generate = {
            "src/App.jsx": [
                "export default function App() {",
                "  return (",
                "    <div style={{ padding: 30 }}>",
                f"      <h1>🚀 AI Generated React App – {project_name}</h1>",
                "      <p>Code is being generated live...</p>",
                "    </div>",
                "  );",
                "}",
            ],
            "src/pages/Home.jsx": [
                "export default function Home() {",
                "  return <h2>🏠 Welcome Home!</h2>;",
                "}",
            ],
            "src/services/api.js": [
                "import axios from 'axios';",
                "export default axios.create({ baseURL: 'http://127.0.0.1:8000' });",
            ],
        }

        total = len(files_to_generate)
        completed = 0

        for file_path, lines in files_to_generate.items():
            full = project_root / file_path
            full.parent.mkdir(parents=True, exist_ok=True)

            await websocket.send_json({
                "event": "file_create",
                "file": file_path,
            })

            written_lines = []

            with open(full, "w", encoding="utf-8") as f:
                for line in lines:
                    f.write(line + "\n")
                    written_lines.append(line)

                    # send live update to editor
                    await websocket.send_json({
                        "event": "editor_update",
                        "file": file_path,
                        "content": "\n".join(written_lines),
                    })

                    # simulate typing
                    await asyncio.sleep(0.12)

            completed += 1
            progress = int((completed / total) * 100)

            await websocket.send_json({
                "event": "progress",
                "progress": progress,
            })

            await websocket.send_json({
                "event": "eta",
                "seconds": max(1, total - completed),
            })

        await websocket.send_json({
            "event": "finish",
            "progress": 100,
            "message": "🎉 Project generation complete!",
        })

    except Exception as e:
        await websocket.send_json({
            "event": "error",
            "message": str(e),
        })

    finally:
        await websocket.close()


# =============================================================================
# LIST PROJECTS
# =============================================================================

@app.get("/projects")
async def list_projects():
    root = Path(__file__).resolve().parents[1] / "projects"
    root.mkdir(exist_ok=True)
    return {"projects": [p.name for p in root.iterdir() if p.is_dir()]}


# =============================================================================
# FILE TREE
# =============================================================================

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


@app.get("/projects/{project_name}/tree")
async def get_project_tree(project_name: str):
    root = Path(__file__).resolve().parents[1] / "projects"
    project_dir = root / project_name

    if not project_dir.exists():
        raise HTTPException(404, "Project not found")

    return {"tree": build_tree(project_dir)}


# =============================================================================
# FRONTEND BOILERPLATE (for /ws/logs)
#   → NOW ALSO CREATES package.json IF MISSING (fixes npm ENOENT)
# =============================================================================

def ensure_frontend_boilerplate(frontend_path: Path, port: int = 3000):
    """Ensure required Vite React files exist for a new project."""

    # Create frontend folder if missing
    frontend_path.mkdir(parents=True, exist_ok=True)

    # Create src folder
    src_path = frontend_path / "src"
    src_path.mkdir(exist_ok=True)

    index_html = frontend_path / "index.html"
    main_jsx = src_path / "main.jsx"
    app_jsx = src_path / "App.jsx"
    vite_config = frontend_path / "vite.config.mjs"
    package_json = frontend_path / "package.json"

    # ----- index.html -----
    if not index_html.exists():
        index_html.write_text(f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Vite App</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
""")

    # ----- main.jsx -----
    if not main_jsx.exists():
        main_jsx.write_text("""import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
""")

    # ----- App.jsx -----
    if not app_jsx.exists():
        app_jsx.write_text("""export default function App() {
  return (
    <h1 style={{ textAlign: 'center', marginTop: '40px' }}>
      🚀 New Vite React Project Ready!
    </h1>
  );
}
""")

    # ----- vite.config.mjs -----
    if not vite_config.exists():
        vite_config.write_text(f"""import {{ defineConfig }} from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({{
  plugins: [react()],
  server: {{
    port: {port},
    host: true
  }}
}})
""")

    # ----- package.json (NEW: avoids npm ENOENT) -----
    if not package_json.exists():
        package_json.write_text(f"""{{
  "name": "ai-project-frontend",
  "version": "0.0.1",
  "private": true,
  "scripts": {{
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }},
  "dependencies": {{
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  }},
  "devDependencies": {{
    "@vitejs/plugin-react": "^4.0.0",
    "vite": "^5.0.0"
  }}
}}
""")


# =============================================================================
# STREAM PROCESS LINES (for Vite logs)
# =============================================================================

async def stream_process_lines(proc: subprocess.Popen, websocket: WebSocket, project_name: str):
    vite_port = None

    try:
        while True:
            line = await asyncio.to_thread(proc.stdout.readline)
            if not line:
                break

            await websocket.send_text(line)

            # Detect actual Vite port from logs (even though we fix to 3000, this is safe)
            match = re.search(r"http://localhost:(\d+)", line)
            if match:
                detected_port = match.group(1)
                if not vite_port:
                    vite_port = detected_port
                    await websocket.send_text(f"\n🔗 VITE_PORT:{vite_port}\n")

    finally:
        if running_processes.get(project_name) is proc:
            running_processes.pop(project_name, None)


# =============================================================================
# WEBSOCKET LOG HANDLER (TERMINAL + VITE)
# =============================================================================

@app.websocket("/ws/logs/{project_name}")
async def project_logs_socket(websocket: WebSocket, project_name: str):
    await websocket.accept()

    projects_root = Path(__file__).resolve().parents[1] / "projects"
    project_root = projects_root / project_name / "frontend"

    # ✔ Ensure frontend folder exists + minimal vite app + package.json
    project_root.mkdir(parents=True, exist_ok=True)
    ensure_frontend_boilerplate(project_root, fixed_port)

    node_modules = project_root / "node_modules"

    try:
        # 1) npm install if needed
        if not node_modules.exists():
            await websocket.send_text("📦 Installing dependencies (npm install)...\n")
            install_proc = subprocess.Popen(
                [NPM_PATH, "install"],
                cwd=str(project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            await stream_process_lines(install_proc, websocket, project_name)
            install_proc.wait()
            await websocket.send_text("\n✅ Dependencies installed!\n\n")

        # 2) Start Vite dev server
        await websocket.send_text(f"🚀 Starting Vite dev server on port {fixed_port}...\n")

        dev_proc = subprocess.Popen(
            [NPM_PATH, "run", "dev", "--", "--port", str(fixed_port), "--host"],
            cwd=str(project_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        running_processes[project_name] = dev_proc

        await websocket.send_text("[WAITING_FOR_VITE]\n")

        # 3) Stream Vite logs to frontend (Terminal)
        await stream_process_lines(dev_proc, websocket, project_name)

    except Exception as e:
        await websocket.send_text(f"[ERROR] {str(e)}\n")

    finally:
        await websocket.close()


# =============================================================================
# FILE READER
# =============================================================================

@app.get("/file")
async def get_file(path: str):
    file_path = Path(path)
    if not file_path.exists():
        raise HTTPException(404, f"File not found: {path}")
    return {"content": read_file(str(file_path))}


# =============================================================================
# AI EDITOR
# =============================================================================

class EditFileRequest(BaseModel):
    path: str
    instruction: str


class EditFileResponse(BaseModel):
    path: str
    content: str


@app.post("/edit_file", response_model=EditFileResponse)
async def edit_file(payload: EditFileRequest):
    updated_path = await edit_file_with_ai(payload.path, payload.instruction)
    return EditFileResponse(path=updated_path, content=read_file(updated_path))


# =============================================================================
# MOUNT ROUTER
# =============================================================================

app.include_router(router)
