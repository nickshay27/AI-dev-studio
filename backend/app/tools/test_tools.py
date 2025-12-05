import subprocess
from pathlib import Path

PROJECTS_DIR = Path(__file__).resolve().parents[2] / "projects"

def run_tests(project_name: str, cmd: str = "pytest") -> str:
    project_dir = PROJECTS_DIR / project_name
    if not project_dir.exists():
        return f"Project {project_name} does not exist at {project_dir}"
    try:
        result = subprocess.run(
            cmd.split(),
            cwd=project_dir,
            capture_output=True,
            text=True,
        )
        return (
            f"Command: {cmd}\n"
            f"Exit code: {result.returncode}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}\n"
        )
    except FileNotFoundError:
        return f"Command '{cmd}' not found. Make sure it is installed."
