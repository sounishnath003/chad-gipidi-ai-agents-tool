import logging
import pathspec
from pathlib import Path
from typing import Any, Callable, List
from pydantic import Field, BaseModel
from .definations import ToolDefination


# --- Read File Tool --- #
class ReadFileInputSchema(BaseModel):
    path: str = Field(..., description="The relative path of a file in the working directory")

def read_file_fn(args: ReadFileInputSchema) -> str:
    logging.debug("read_file_fn: %s", args)
    return open(args.path, "r").read().strip()

class ReadFileToolDefination(ToolDefination):
    name: str = "read_file_fn"
    description: str = "Read the contents of a given relative file path. when you want to see what's written in the file. Do not use this with directory name"
    input_schema: BaseModel = ReadFileInputSchema
    function: Callable[[Any,...], [str]] = read_file_fn


# --- List File tool --- #
class ListFileInputSchema(BaseModel):
    path: str = Field(..., description="The relative path of a directory in the working directory")


def list_files_fn(args: ListFileInputSchema) -> List[str]:
    """List all files in a directory, skipping those ignored by .gitignore and always skipping .git/."""
    logging.debug("list_files_fn: %s", args)

    def load_gitignore_patterns(gitignore_path: Path):
        """Load patterns from a .gitignore file."""
        if not gitignore_path.exists():
            return pathspec.PathSpec.from_lines("gitwildmatch", [])
        with gitignore_path.open("r") as f:
            patterns = f.readlines()
        return pathspec.PathSpec.from_lines("gitwildmatch", patterns)

    def list_files_skipping_gitignore(base_path: Path):
        """List all files recursively, skipping those ignored by .gitignore and .git folder."""
        gitignore_path = base_path / ".gitignore"
        spec = load_gitignore_patterns(gitignore_path)

        all_files = []
        for p in base_path.rglob("*"):
            # skip .git and its contents always
            if any(part == ".git" for part in p.parts):
                continue
            if p.is_file():
                rel_path = str(p.relative_to(base_path))
                if not spec.match_file(rel_path):
                    all_files.append(rel_path)
        return all_files

    base_dir = Path(args.path).resolve()
    if not base_dir.exists() or not base_dir.is_dir():
        raise ValueError(f"Path '{args.path}' is not a valid directory")

    result = list_files_skipping_gitignore(base_dir)
    return "\n".join(result) if result else "No files or directories found"
    
class ListFileToolDefination(ToolDefination):
    name: str = "list_files_fn"
    description: str = "List files and directories at given path. If no path provided, lists files in the current directory."
    input_schema: BaseModel = ListFileInputSchema
    function: Callable[[Any,...], [str]] = list_files_fn