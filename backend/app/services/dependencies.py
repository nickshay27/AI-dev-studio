from pathlib import Path
import subprocess
from fastapi import WebSocket


async def install_dependencies(options: dict, frontend: Path, websocket: WebSocket) -> None:
    """
    Install selected npm dependencies based on project options.
    """
    deps: list[str] = []

    if options.get("axios"):
        deps.append("axios")
    if options.get("router"):
        deps.append("react-router-dom")
    if options.get("zustand"):
        deps.append("zustand")
    if options.get("charts"):
        deps += ["chart.js", "react-chartjs-2"]

    ui = options.get("ui")
    if ui == "mui":
        deps += ["@mui/material", "@emotion/react", "@emotion/styled"]
    elif ui == "shadcn":
        deps += ["class-variance-authority", "tailwind-merge"]

    # Tailwind dev deps
    if options.get("tailwind"):
        deps += ["-D", "tailwindcss", "postcss", "autoprefixer"]

    if not deps:
        return

    await websocket.send_text("📦 Installing dependencies...\n")
    subprocess.run(["npm", "install"] + deps, cwd=str(frontend), shell=True)
    await websocket.send_text("✅ Dependencies installed!\n")
