from openai import AsyncOpenAI
from app.providers.base_provider import BaseProvider
from app.config import settings


class OpenAIProvider(BaseProvider):
    def __init__(self, model: str = "gpt-4o"):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = model

    async def complete(self, system_prompt: str, user_message: str, max_tokens: int = 1024, temperature: float = 0.2) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content
