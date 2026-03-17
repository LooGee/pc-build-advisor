import anthropic
from app.providers.base_provider import BaseProvider
from app.config import settings


class ClaudeProvider(BaseProvider):
    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = model

    async def complete(self, system_prompt: str, user_message: str, max_tokens: int = 1024, temperature: float = 0.2) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return message.content[0].text
