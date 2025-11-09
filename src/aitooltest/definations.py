from typing import Callable
from pydantic import BaseModel
from .config import LLMConfig


class ToolDefination(BaseModel):
    name: str
    description: str
    input_schema: str
    function: Callable[[...], [str]]

    llm_config: LLMConfig = LLMConfig()
