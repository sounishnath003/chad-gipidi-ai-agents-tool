from .tools import ReadFileToolDefination
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
        chat_model = self.client.chats.create(
            model=self.llm_config.MODEL_NAME,
            config=genai.types.GenerateContentConfig(
                tools=[
                    genai.types.Tool(function_declarations=[ReadFileToolDefination().to_json()])
                ],
                automatic_function_calling=genai.types.AutomaticFunctionCallingConfig(disable=True),
                tool_config=genai.types.ToolConfig(function_calling_config=genai.types.FunctionCallingConfig(mode="AUTO")), # ANY forces:: :-\
            )
        )
        yield chat_model
        logging.debug("closing the chat inference endpoint...")
        # Maybe you want to do some operations
        for msg in chat_model.get_history():
            logging.debug("Role: %s, Message: %s", msg.role, msg.parts[0].text)
        logging.debug("clearing off the resource contexts...")


    def run(self):
        logging.info("Chat with Google Gemini (use 'ctrl-c' to quit)")
        try:
            with self.run_as_chat_inference() as chat_mode:
                while True:
                    print("\u001b[94mYou\u001b[0m: ", end="")
                    user_input = self.get_user_message()
                    if len(user_input) == 0 or user_input in set(["q", "quit", "exit"]): break
                    response = chat_mode.send_message(user_input)
                    logging.info("Gemini: %s", vars(response))


                    # Force logging of each of function calls requested from single call
                    if getattr(response, 'function_calls', False):
                        logging.debug("forced function calling")
                        for fn in response.function_calls:
                            args = ", ".join(f"{key}={val}" for key, val in fn.args.items())
                            logging.debug("fn.name: %s, args: %s", fn.name, args)

        except Exception as e:
            error_message = {
                "error_code": e.__class__.__name__,
                "error_message": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            logging.error("an error occured: %s", error_message, exc_info=e)
            raise e
