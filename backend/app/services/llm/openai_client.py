from __future__ import annotations

from typing import Any

import httpx

from app.core.config import get_settings
from app.services.llm.base import BaseLLMClient


class OpenAICompatibleClient(BaseLLMClient):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = (self.settings.openai_base_url or "https://api.openai.com/v1").rstrip("/")

    async def generate_text(self, prompt: str, *, system_prompt: str | None = None) -> str:
        payload = await self._request(prompt, system_prompt=system_prompt)
        return payload["choices"][0]["message"]["content"]

    async def generate_json(self, prompt: str, *, system_prompt: str | None = None) -> dict[str, Any]:
        content = await self.generate_text(prompt, system_prompt=system_prompt)
        return {"content": content}

    async def _request(self, prompt: str, *, system_prompt: str | None = None) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json={"model": self.settings.openai_model, "messages": messages},
            )
            response.raise_for_status()
        return response.json()
