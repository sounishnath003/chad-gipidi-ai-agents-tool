import inspect
import logging
from typing import Any, Callable, Dict, List
from pydantic import create_model, Field
from .definations import ToolDefination

_tools: Dict[str, ToolDefination] = {}


def tool(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    A decorator to register a function as a tool.
    """
    # Extract function signature and docstring
    sig = inspect.signature(func)
    doc = inspect.getdoc(func)
    if not doc:
        raise ValueError("Tool function must have a docstring.")

    # Create Pydantic model from function signature
    fields = {
        name: (param.annotation, Field(..., description=f"Description for {name}"))
        for name, param in sig.parameters.items()
    }
    logging.debug(fields)
    input_schema = create_model(f"{func.__name__}InputSchema", **fields)

    # Create ToolDefination
    tool_def = ToolDefination(
        name=func.__name__,
        description=doc.strip(),
        input_schema=input_schema,
        function=func,
    )

    # Register the tool
    _tools[func.__name__] = tool_def
    return func


def get_tools() -> List[ToolDefination]:
    """
    Returns a list of all registered tools.
    """
    return list(_tools.values())
