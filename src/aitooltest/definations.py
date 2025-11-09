from typing import Callable, List
from pydantic import BaseModel
from google import genai

class ToolDefination(BaseModel):
    name: str
    description: str
    input_schema: str
    funciton: Callable[[RawMessage, [...], [string, Error]]


class Agent(BaseModel):
    client: genai.Client
    get_user_message: Callable[[...], [str, bool]]
    tools: List[ToolDefination]
