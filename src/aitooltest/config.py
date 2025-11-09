from pydantic import BaseModel


class LLMConfig(BaseModel):
    MODEL_NAME: str = "gemini-2.5-flash"
    THINKING_BUDGET: int = 0
