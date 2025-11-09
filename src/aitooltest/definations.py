import logging
import json
from typing import Callable
from pydantic import BaseModel
from .config import LLMConfig
from typing import Any, Callable, Dict
from .utils import generate_schema


class ToolDefination(BaseModel):
    name: str
    description: str
    input_schema: BaseModel
    function: Callable[[...], [Any,...]]

    llm_config: LLMConfig = LLMConfig()


    def to_json(self) -> Dict[str, Any]:
        json_dict = {
            "name": self.name,
            "description": self.description,
            "parameters": generate_schema(self.input_schema)
        }
        logging.info("to_json: %s", json_dict)

        return json_dict
