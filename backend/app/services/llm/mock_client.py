from __future__ import annotations

from typing import Any

from app.services.llm.base import BaseLLMClient


class MockLLMClient(BaseLLMClient):
    async def generate_text(self, prompt: str, *, system_prompt: str | None = None) -> str:
        return (
            "Mock LLM mode is enabled. This response should be reviewed by a pharmacist "
            "before clinical, dispensing, substitution, or patient-specific action.\n\n"
            f"Prompt summary: {prompt[:280]}"
        )

    async def generate_json(self, prompt: str, *, system_prompt: str | None = None) -> dict[str, Any]:
        return {
            "mode": "mock",
            "system_prompt": system_prompt,
            "prompt_excerpt": prompt[:280],
        }
