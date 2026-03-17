from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):
    @abstractmethod
    async def complete(self, system_prompt: str, user_message: str, max_tokens: int = 1024, temperature: float = 0.2) -> str:
        pass
