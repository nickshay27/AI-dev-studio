import os
import json
from typing import List, Literal, TypedDict, Optional

import requests

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class ChatMessage(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str


def _call_ollama(messages: List[ChatMessage], model: str) -> str:
    import requests
    url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/api/chat")

    resp = requests.post(
        url,
        json={"model": model, "messages": messages, "stream": False},
        timeout=300,
    )

    resp.raise_for_status()

    # Ollama returns JSON, but sometimes with extra whitespace/newlines
    try:
        data = resp.json()
        return data["message"]["content"]
    except Exception:
        # Fallback for multi-object or invalid JSON formats
        text = resp.text.strip()

        # Try to extract last JSON object if multiple objects are returned
        if "}" in text:
            possible_json = text.splitlines()[-1]
            try:
                parsed = json.loads(possible_json)
                return parsed["message"]["content"]
            except:
                pass

        raise RuntimeError(f"Ollama returned unparsable response: {text}")


def _call_openai(messages: List[ChatMessage], json_mode: bool) -> str:
    if OpenAI is None:
        raise RuntimeError("OpenAI package not installed")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY missing")

    client = OpenAI(api_key=api_key)
    model_name = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    kwargs = {"model": model_name, "messages": messages}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    resp = client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content or ""


def call_llm(messages: List[ChatMessage], *, json_mode=False, task_type=None) -> str:
    provider = os.getenv("MODEL_PROVIDER", "local").lower()

    if provider == "local":
        if task_type == "code":
            model = os.getenv("LOCAL_MODEL_CODER", "deepseek-coder:6.7b")
        else:
            model = os.getenv("LOCAL_MODEL_GENERAL", "llama3.1")
        return _call_ollama(messages, model)

    elif provider == "openai":
        return _call_openai(messages, json_mode)

    else:
        raise ValueError(f"Unknown MODEL_PROVIDER={provider}")
