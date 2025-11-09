from .tools import ReadFileToolDefination
from pydantic import BaseModel
from typing import Any, Callable, Dict, List
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
        """runs the inference mode into a isolated runtime contexts \
        and manages the resource clean ups"""
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
        stopping_sequences = set(["q", "quit", "exit", "\\bye"])
        logging.info("Chat with Google Gemini (use '(ctrl-c)' to quit)")
        try:
            with self.run_as_chat_inference() as chat_mode:
                while True:
                    print("\u001b[94mYou\u001b[0m: ", end="")
                    user_input = self.get_user_message()
                    if len(user_input) == 0 or user_input in stopping_sequences: break
                    response = chat_mode.send_message(user_input)

                    # Process the responses from LLM AI
                    part_responses = response.candidates[0].content.parts
                    logging.debug("part_responses: %s", part_responses)

                    ai_response: str | Any = ""

                    for part in part_responses:
                        if getattr(part, 'text'):
                            ai_response = part.text
                        elif getattr(part, 'function_call'):
                            # Force logging of each of function calls requested from single call
                            logging.debug("forced function calling")
                            for fn in response.function_calls:
                                # Try to Execute the tool func with params
                                func_out = self.execute_tool_call(chat_mode, fn.name, input_args=dict(fn.args))
                                logging.info("Tool: %s", f"Result of func call: {fn.name}({fn.args.items()}) = {func_out}")
                                response = chat_mode.send_message(f"Result of func call: {fn.name}({fn.args.items()}) = {func_out}")
                                ai_response = response.text if getattr(response, 'text') else "Thinking on it..."

                    logging.info("Gemini: %s", str(ai_response))

        except Exception as e:
            error_message = {
                "error_code": e.__class__.__name__,
                "error_message": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            logging.error("an error occured: %s", error_message, exc_info=e)
            raise e


    def execute_tool_call(self, chat_mode: genai.chats.Chat, name: str, input_args: Dict[str, Any]) -> Any:
        """Tries to run the tool function and return the output. Handles invalid schema gracefully, with retries and user prompt."""
        from collections import Counter

        logging.debug("\u001b[92mtool\u001b[0m: %s(%s)", name, input_args)
        tool: ToolDefination | None = next((tool for tool in self.tools if tool.name == name), None)
        if not tool:
            error_msg = f"Tool {name} not found"
            print(error_msg)
            chat_mode.send_message(error_msg)
            return None

        # Counter for function tools called (visible to user)
        if not hasattr(self, "_tool_call_counter"):
            self._tool_call_counter = Counter()
        self._tool_call_counter[name] += 1
        print(f"[Tool Call {self._tool_call_counter[name]}] {name}({input_args})")

        max_attempts = 2
        attempts = 0
        tool_input = None

        # Try at least 2 times to validate input schema
        while attempts < max_attempts:
            try:
                tool_input = tool.input_schema.model_validate(input_args)
                break
            except Exception as ex:
                attempts += 1
                error_message = f"Input validation failed for tool '{name}' (attempt {attempts}): {ex}"
                print(error_message)
                chat_mode.send_message(error_message)
                logging.error(error_message, exc_info=ex)
                if attempts < max_attempts:
                    print("Please check/fix the tool arguments. Re-enter input arguments as a dictionary (e.g., {'key': 'value'}):")
                    user_input_str = input("> ")
                    try:
                        input_args = eval(user_input_str) if user_input_str.strip() else input_args
                    except Exception as inner_ex:
                        print(f"Could not parse input. Using old input. Error: {inner_ex}")

        if tool_input is None:
            error_message = f"Failed to validate input for tool '{name}' after {max_attempts} attempts."
            print(error_message)
            chat_mode.send_message(error_message)
            return None

        # Now try function execution, and let user see and retry if error occurs
        attempts = 0
        while attempts < max_attempts:
            try:
                tool_output = tool.function(tool_input)
                break
            except Exception as ex:
                attempts += 1
                error_message = f"Execution failed for tool '{name}' (attempt {attempts}): {ex}"
                print(error_message)
                chat_mode.send_message(error_message)
                logging.error(error_message, exc_info=ex)
                if attempts < max_attempts:
                    print("You may fix input and try again. Re-enter input arguments as a dictionary or press enter for the previous one:")
                    user_input_str = input("> ")
                    try:
                        input_args = eval(user_input_str) if user_input_str.strip() else input_args
                        try:
                            tool_input = tool.input_schema.model_validate(input_args)
                        except Exception as v_ex:
                            print(f"Input not valid: {v_ex}")
                            chat_mode.send_message(f"Input not valid: {v_ex}")
                            continue
                    except Exception as inner_ex:
                        print(f"Could not parse input. Using old input. Error: {inner_ex}")
        else:
            tool_output = None

        if tool_output is None:
            error_message = f"Failed to execute tool '{name}' after {max_attempts} attempts."
            print(error_message)
            chat_mode.send_message(error_message)
            return None

        return {"result": tool_output, "tool_name": name, "input_args": input_args}
