from typing import List, Literal
from pydantic import BaseModel
from ..model_router import call_llm
import json

Priority = Literal["high", "medium", "low"]
Area = Literal["frontend", "backend", "db", "infra", "qa", "docs"]


class Feature(BaseModel):
    id: int
    title: str
    description: str
    priority: Priority
    area: Area


class Plan(BaseModel):
    project_name: str
    summary: str
    tech_stack: List[str]
    features: List[Feature]


async def create_plan(project_name: str, idea: str) -> Plan:
    system = (
        "You are an expert product manager.\n"
        "You MUST output **VALID JSON ONLY**.\n\n"
        "JSON SCHEMA:\n"
        "{\n"
        '  \"project_name\": \"string\",\n'
        '  \"summary\": \"string (not empty)\",\n'
        '  \"tech_stack\": [\"string\", ... minimum 3 items],\n'
        '  \"features\": [\n'
        "     {\n"
        '       \"id\": number,\n'
        '       \"title\": \"string\",\n'
        '       \"description\": \"string\",\n'
        '       \"priority\": \"high\" | \"medium\" | \"low\",\n'
        '       \"area\": \"frontend\" | \"backend\" | \"db\" | \"infra\" | \"qa\" | \"docs\"\n'
        "     }\n"
        "  ]\n"
        "}\n\n"
        "STRICT RULES:\n"
        "- NO missing fields\n"
        "- NO extra keys\n"
        "- summary MUST NOT be empty\n"
        "- tech_stack MUST have 3+ items\n"
        "- features MUST contain 6–10 items\n"
        "- priority MUST be lowercase\n"
        "- ONLY output JSON\n"
    )

    user = f"Project name: {project_name}\nIdea: {idea}"

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    import asyncio
    raw = await asyncio.to_thread(call_llm, messages, json_mode=True)
    cleaned = raw.strip()

    # Remove ``` wrappers
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned.split("\n", 1)[1]

    # ---- JSON REPAIR STEP ----
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        # If model returns invalid JSON, fix by forcing braces
        first = cleaned.find("{")
        last = cleaned.rfind("}")
        cleaned = cleaned[first:last + 1]
        parsed = json.loads(cleaned)

    # ---- FINAL VALIDATION ----
    return Plan(**parsed)
