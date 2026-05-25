"""Local Ollama client — low-cost first pass."""

from __future__ import annotations

import httpx

from backend.app.config.settings import get_settings


class OllamaClient:
    name = "ollama"

    def is_available(self) -> bool:
        settings = get_settings()
        if not settings.ollama_enabled:
            return False
        try:
            r = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=2.0)
            return r.status_code == 200
        except Exception:
            return False

    def complete_json(self, prompt: str) -> str:
        settings = get_settings()
        resp = httpx.post(
            f"{settings.ollama_base_url}/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt + "\n\nRespond with valid JSON only.",
                "stream": False,
            },
            timeout=120.0,
        )
        resp.raise_for_status()
        return resp.json().get("response", "{}")
