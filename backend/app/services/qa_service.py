import httpx
from backend.app.core.config import settings

class QuestionAnsweringService:
    def __init__(self):
        self.api_url = f"{settings.MODEL_API_URL}/qa"

    async def answer_question(self, question: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, json={"question": question})
            response.raise_for_status()
            return response.json().get("answer", "无法回答该问题")