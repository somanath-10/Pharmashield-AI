from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseLLMClient(ABC):
    @abstractmethod
    async def generate_text(self, prompt: str, *, system_prompt: str | None = None) -> str:
        raise NotImplementedError

    @abstractmethod
    async def generate_json(self, prompt: str, *, system_prompt: str | None = None) -> dict[str, Any]:
        raise NotImplementedError
