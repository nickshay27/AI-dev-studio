import os
import json
from pathlib import Path
from typing import Tuple, Dict, Any, List

from ..agents.product_manager import create_plan, Plan
from ..agents.frontend_dev import implement_frontend_skeleton
from ..agents.backend_dev import implement_backend_skeleton
from ..agents.qa_tester import generate_test_notes
from ..tools.fs_tools import write_file


async def run_generic_builder(project_name: str, idea: str) -> Tuple[Dict[str, Any], List[str]]:
    """
    Main builder pipeline:
    1. Create project folder
    2. Generate AI plan (validated)
    3. Save plan.json
    4. Generate README.md
    5. Create frontend skeleton
    6. Create backend skeleton
    7. Generate QA notes

    Returns (plan_dict, list_of_created_files)
    """

    # Root: backend/ -> projects/
    backend_root = Path(__file__).resolve().parents[2]
    projects_root = backend_root / "projects"
    projects_root.mkdir(exist_ok=True)

    project_dir = projects_root / project_name
    project_dir.mkdir(exist_ok=True)

    created_files: List[str] = []

    # -----------------------------------------------------------
    # 1. GENERATE AI PLAN
    # -----------------------------------------------------------
    try:
        plan: Plan = await create_plan(project_name, idea)

        plan_path = project_dir / "plan.json"
        plan_path.write_text(json.dumps(plan.model_dump(), indent=2), encoding="utf-8")
        created_files.append(str(plan_path))

    except Exception as e:
        # Bubble error to /generate_project (FastAPI)
        raise RuntimeError(f"❌ ERROR creating plan: {e}")

    # -----------------------------------------------------------
    # 2. GENERATE README.md
    # -----------------------------------------------------------
    readme_text = f"""# {plan.project_name}

## Project Idea
{idea}

## Summary (AI Generated)
{plan.summary}

## Tech Stack
- {("\n- ").join(plan.tech_stack)}

---

This is an **AI-generated project skeleton** created by the AI Dev Team.
"""

    readme_path = project_dir / "README.md"
    write_file(str(readme_path), readme_text)
    created_files.append(str(readme_path))

    # -----------------------------------------------------------
    # 3. FRONTEND SKELETON
    # -----------------------------------------------------------
    try:
        frontend_files = implement_frontend_skeleton(plan, str(project_dir))
        if isinstance(frontend_files, list):
            created_files.extend(frontend_files)
    except Exception as e:
        raise RuntimeError(f"❌ ERROR generating frontend skeleton: {e}")

    # -----------------------------------------------------------
    # 4. BACKEND SKELETON
    # -----------------------------------------------------------
    try:
        backend_files = implement_backend_skeleton(plan, str(project_dir))
        if isinstance(backend_files, list):
            created_files.extend(backend_files)
    except Exception as e:
        raise RuntimeError(f"❌ ERROR generating backend skeleton: {e}")

    # -----------------------------------------------------------
    # 5. QA NOTES
    # -----------------------------------------------------------
    try:
        qa_files = generate_test_notes(plan, str(project_dir))
        if isinstance(qa_files, list):
            created_files.extend(qa_files)
    except Exception as e:
        raise RuntimeError(f"❌ ERROR generating QA notes: {e}")

    # -----------------------------------------------------------
    # RETURN TO API
    # -----------------------------------------------------------
    return plan.model_dump(), created_files
