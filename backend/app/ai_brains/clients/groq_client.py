"""Groq fast classifier client."""

from __future__ import annotations

from backend.app.config.settings import get_settings


class GroqClient:
    name = "groq"

    def is_available(self) -> bool:
        return bool(get_settings().groq_api_key)

    def complete_json(self, prompt: str) -> str:
        from groq import Groq

        client = Groq(api_key=get_settings().groq_api_key)
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=2048,
            temperature=0.1,
        )
        return chat.choices[0].message.content or "{}"
