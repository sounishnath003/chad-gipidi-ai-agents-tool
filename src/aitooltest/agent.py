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
    get_user_message: Callable[[], str]
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
                    genai.types.Tool(function_declarations=[tool.to_json() for tool in self.tools])
                ],
                tool_config=genai.types.ToolConfig(
                    function_calling_config=genai.types.FunctionCallingConfig(mode="AUTO")
                )
            )
        )
        yield chat_model
        logging.debug("closing the chat inference endpoint...")
        for msg in chat_model.get_history():
            logging.debug("Role: %s, Message: %s", msg.role, getattr(msg.parts[0], "text", ""))
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

                    # Improved LLM response processing (do not overwrite content for each part)
                    part_responses = response.candidates[0].content.parts
                    logging.debug("part_responses: %s", part_responses)
                    texts: List[str] = []
                    ai_response: str | Any = ""

                    for part in part_responses:
                        # Ensure that only non-None strings are appended to texts
                        text_val = getattr(part, 'text', None)
                        if text_val is not None:
                            texts.append(str(text_val))
                        elif getattr(part, 'function_call', None):
                            # Force logging of each of function calls requested from single call
                            logging.debug("forced function calling")
                            for fn in getattr(response, "function_calls", []):
                                func_out = self.execute_tool_call(chat_mode, fn.name, input_args=dict(fn.args))
                                logging.info("Tool: %s", f"Result of func call: {fn.name}({fn.args.items()}) = {func_out}")
                                followup = f"Result of func call: {fn.name}({fn.args.items()}) = {func_out}"
                                resp = chat_mode.send_message(followup)
                                # If resp.text exists and is not None, add it; else, add fallback
                                resp_text = getattr(resp, "text", None)
                                if resp_text is not None:
                                    texts.append(str(resp_text))
                                else:
                                    texts.append("Thinking on it...")

                    # Only join actual strings in texts (skip None)
                    ai_response = "\n".join([s for s in texts if isinstance(s, str)]) if texts else "Nothing found..."
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

        # --- CRITICAL SECURITY FIX: Remove use of eval() on user input ---
        def parse_input_dict(s: str, old: dict) -> dict:
            """Safe parsing of input as dictionary from user without using eval."""
            import ast
            try:
                v = ast.literal_eval(s)
                if isinstance(v, dict):
                    return v
                else:
                    print("Input must be a dictionary. Using old input.")
                    return old
            except Exception as ex:
                print(f"Input parsing error: {ex}. Using old input.")
                return old

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
                    if user_input_str.strip():
                        input_args = parse_input_dict(user_input_str, input_args)
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
                    if user_input_str.strip():
                        input_args = parse_input_dict(user_input_str, input_args)
                        try:
                            tool_input = tool.input_schema.model_validate(input_args)
                        except Exception as v_ex:
                            print(f"Input not valid: {v_ex}")
                            chat_mode.send_message(f"Input not valid: {v_ex}")
                            continue
        else:
            tool_output = None

        if tool_output is None:
            error_message = f"Failed to execute tool '{name}' after {max_attempts} attempts."
            print(error_message)
            chat_mode.send_message(error_message)
            return None

        return {"result": tool_output, "tool_name": name}
