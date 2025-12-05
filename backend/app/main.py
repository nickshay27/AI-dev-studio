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
import socket


# internal imports
from .workflows.generic_builder import run_generic_builder
from .agents.code_editor import edit_file_with_ai
from .tools.fs_tools import read_file

# =============================================================================
# SETTINGS
# =============================================================================

# Path to npm on your machine
NPM_PATH = r"C:\Program Files\nodejs\npm.cmd"
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
# PROJECT GENERATION
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


# =============================================================================
# STREAM PROCESS LINES
# =============================================================================

async def stream_process_lines(proc: subprocess.Popen, websocket: WebSocket, project_name: str):
    vite_port = None

    try:
        while True:
            line = await asyncio.to_thread(proc.stdout.readline)
            if not line:
                break

            await websocket.send_text(line)

            # Detect actual Vite port from logs
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
# WEBSOCKET LOG HANDLER
# =============================================================================

@app.websocket("/ws/logs/{project_name}")
async def project_logs_socket(websocket: WebSocket, project_name: str):
    await websocket.accept()

    projects_root = Path(__file__).resolve().parents[1] / "projects"
    project_root = projects_root / project_name / "frontend"

    # ✔ Ensure frontend folder exists
    project_root.mkdir(parents=True, exist_ok=True)

    # 🔥 Create index.html, main.jsx, App.jsx, vite.config.mjs
    ensure_frontend_boilerplate(project_root, fixed_port)

    # Now folder exists for sure
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

        # 3) Stream Vite logs to frontend
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


# MOUNT ROUTER
app.include_router(router)
