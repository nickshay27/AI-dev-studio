from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pathlib import Path
import subprocess
import asyncio
import json
import random
import subprocess
import time
import sys

from ..services.settings import NPM_PATH, FIXED_PORT, running_processes
from ..services.boilerplate import create_frontend_boilerplate, setup_tailwind
from ..services.dependencies import install_dependencies

router = APIRouter()


def get_projects_root() -> Path:
    # backend/app/routers/... → parents[2] = backend
    return Path(__file__).resolve().parents[2] / "projects"




@router.post("/run_project")
def run_project(data: dict):
    project = data.get("project_name")
    if not project:
        raise HTTPException(400, "project_name is required")

    backend_root = Path(__file__).resolve().parents[1]
    project_root = backend_root / "projects" / project / "frontend"

    if not project_root.exists():
        raise HTTPException(404, "Frontend folder missing")

    # Select dynamic free port
    port = random.randint(4000, 9000)

    # Save port so frontend can connect
    running_processes[project] = {
        "port": port,
        "process": None,
    }

    # Start Vite dev server in new console window
    proc = subprocess.Popen(
        [NPM_PATH, "run", "dev", "--", "--port", str(port), "--host"],
        cwd=str(project_root),
        creationflags=subprocess.CREATE_NEW_CONSOLE    # <-- IMPORTANT
    )

    running_processes[project]["process"] = proc

    # Give Vite time to boot
    time.sleep(1)

    return {"status": "running", "url": f"http://127.0.0.1:{port}"}


@router.post("/stop_project")
def stop_project(data: dict):
    project = data.get("project_name")

    info = running_processes.get(project)

    if info and info["process"] and info["process"].poll() is None:
        info["process"].terminate()

    running_processes.pop(project, None)
    return {"status": "stopped"}


@router.websocket("/ws/logs/{project_name}")
async def project_logs_socket(websocket: WebSocket, project_name: str):
    await websocket.accept()

    projects_root = get_projects_root()
    project_root = projects_root / project_name
    frontend = project_root / "frontend"

    if not Path(NPM_PATH).exists():
        await websocket.send_text(f"[ERROR] npm not found at: {NPM_PATH}\n")
        await websocket.close()
        return

    # Read options if present
    options_file = project_root / "project.json"
    options = json.loads(options_file.read_text()) if options_file.exists() else {}

    # Ensure boilerplate exists
    create_frontend_boilerplate(frontend, FIXED_PORT)

    # Install optional deps
    await install_dependencies(options, frontend, websocket)

    # Tailwind if enabled
    if options.get("tailwind"):
        setup_tailwind(frontend)
        await websocket.send_text("✨ Tailwind configured!\n")

    await websocket.send_text(f"🚀 Starting Vite dev server on port {FIXED_PORT}...\n")

    proc = subprocess.Popen(
        [NPM_PATH, "run", "dev", "--", "--port", str(FIXED_PORT), "--host"],
        cwd=str(frontend),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    running_processes[project_name] = proc

    try:
        while True:
            line = await asyncio.to_thread(proc.stdout.readline)
            if not line:
                break

            await websocket.send_text(line)

    except WebSocketDisconnect:
        # user closed terminal tab
        pass

    finally:
        await websocket.close()
        running_processes.pop(project_name, None)
