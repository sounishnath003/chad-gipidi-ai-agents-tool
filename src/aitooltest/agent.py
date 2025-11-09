from pydantic import BaseModel
from typing import Callable, List
from google import genai
from .definations import ToolDefination
from .config import LLMConfig
from datetime import datetime
from contextlib import contextmanager
import logging

class Agent(BaseModel):
    client: genai.Client
    get_user_message: Callable[[...], [str]]
    tools: List[ToolDefination]

    llm_config: LLMConfig = LLMConfig()

    model_config = {
        "arbitrary_types_allowed": True
    }

    @contextmanager
    def run_as_chat_inference(self):
        logging.debug("initializing chat inference endpoint...")
        chat_model = self.client.chats.create(model=self.llm_config.MODEL_NAME)
        yield chat_model
        logging.debug("closing the chat inference endpoint...")
        # Maybe you want to do some operations
        logging.debug("clearing off the resource contexts...")

    def run(self):
        logging.info("Chat with Google Gemini (use 'ctrl-c' to quit)")
        try:
            with self.run_as_chat_inference() as chat_mode:
                while True:
                    print("\u001b[94mYou\u001b[0m: ", end="")
                    user_input = self.get_user_message()
                    if len(user_input) == 0: break
                    response = chat_mode.send_message(user_input)
                    logging.info("Gemini: %s", str(response.text))
        except Exception as e:
            error_message = {
                "error_code": e.__class__.__name__,
                "error_message": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            logging.error("an error occured: %s", error_message, exc_info=e)
            raise e
