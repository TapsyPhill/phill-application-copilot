"""Gemini API client."""

from __future__ import annotations

from backend.app.config.settings import get_settings


class GeminiClient:
    name = "gemini"

    def is_available(self) -> bool:
        return bool(get_settings().gemini_api_key)

    def complete_json(self, prompt: str) -> str:
        import google.generativeai as genai

        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(
            prompt + "\n\nRespond with valid JSON only.",
            generation_config={"response_mime_type": "application/json"},
        )
        return response.text or "{}"
