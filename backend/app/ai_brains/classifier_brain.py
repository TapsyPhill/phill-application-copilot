"""Classifier brain — category and subcategory with evidence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.app.ai_brains.ai_json_validator import parse_and_validate
from backend.app.ai_brains.clients.gemini_client import GeminiClient
from backend.app.ai_brains.clients.groq_client import GroqClient
from backend.app.ai_brains.clients.ollama_client import OllamaClient

PROMPT_PATH = Path(__file__).parent / "prompts" / "classification_prompt.md"


class ClassifierBrain:
    def __init__(self) -> None:
        self._prompt = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else ""
        self._clients = [OllamaClient(), GroqClient(), GeminiClient()]

    def classify(self, cleaned_text: str, profile_context: str = "") -> dict[str, Any]:
        user_prompt = f"{self._prompt}\n\nPROFILE:\n{profile_context}\n\nPOST:\n{cleaned_text[:12000]}"
        outputs = []
        for client in self._clients:
            if not client.is_available():
                continue
            try:
                raw = client.complete_json(user_prompt)
            except Exception:
                continue
            data, err = parse_and_validate(raw)
            if data:
                data["model_name"] = client.name
                outputs.append(data)
            if len(outputs) >= 2:
                break
        return {"outputs": outputs}
