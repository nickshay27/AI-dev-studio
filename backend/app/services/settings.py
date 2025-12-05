from typing import Dict
import subprocess

# Path to npm on your machine
NPM_PATH = r"C:\Program Files\nodejs\npm.cmd"

# Fixed Vite dev server port
FIXED_PORT = 3000

# Shared map of running dev server processes
running_processes: Dict[str, subprocess.Popen] = {}
