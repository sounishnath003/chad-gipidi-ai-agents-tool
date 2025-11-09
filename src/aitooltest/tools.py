import logging
from typing import Any, Callable
from pydantic import Field, BaseModel
from .definations import ToolDefination


# --- Read File Tool --- #
class ReadFileInputSchema(BaseModel):
    path: str = Field(..., description="The relative path of a file in the working directory")

def read_file_fn(args: ReadFileInputSchema) -> str:
    logging.info("path: %s", args)
    return open(args.path, "r").read().strip() 

class ReadFileToolDefination(ToolDefination):
    name: str = "read_file_fn"
    description: str = "Read the contents of a given relative file path. when you want to see what's written in the file. Do not use this with directory name"
    input_schema: BaseModel = ReadFileInputSchema
    function: Callable[[Any,...], [str]] = read_file_fn

