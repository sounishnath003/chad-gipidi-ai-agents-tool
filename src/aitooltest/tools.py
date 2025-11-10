import logging
import os
import subprocess
import pathspec
from pathlib import Path
from typing import Dict
from .tool_registry import tool


@tool
def read_file(path: str) -> str:
    """Read the contents of a given relative file path."""
    logging.debug("read_file: %s", path)
    with open(path, "r") as f:
        return f.read().strip()


@tool
def list_files(path: str) -> str:
    """List all files in a directory, skipping those ignored by .gitignore and always skipping .git/."""
    logging.debug("list_files: %s", path)

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

    base_dir = Path(path).resolve()
    if not base_dir.exists() or not base_dir.is_dir():
        raise ValueError(f"Path '{path}' is not a valid directory")

    result = list_files_skipping_gitignore(base_dir)
    return "\n".join(result) if result else "No files or directories found"


@tool
def edit_file(path: str, old_str: str, new_str: str) -> str:
    """
    Edit a file by replacing text.
    - Creates file if missing & old_str == "".
    - Raises error if old_str not found.
    - Returns "OK" on success.
    """
    def create_new_file(path: str, content: str) -> str:
        """Helper: create new file (including parent dirs)."""
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return "OK"

    logging.debug("edit_file: %s", (path, old_str, new_str))

    # Validate input
    if not path or old_str == new_str:
        raise ValueError("invalid input parameters")

    # Try to read existing file
    try:
        with open(path, "r", encoding="utf-8") as f:
            old_content = f.read()
    except FileNotFoundError:
        if old_str == "":
            return create_new_file(path, new_str)
        raise FileNotFoundError(f"File not found: {path}")

    # Replace occurrences
    new_content = old_content.replace(old_str, new_str)

    # Detect no match
    if old_content == new_content and old_str != "":
        raise ValueError("old_str not found in file")

    # Write updated content
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return "OK"


@tool
def execute_command(command: str) -> Dict[str, str]:
    """Execute a given command and return its stdout and stderr."""
    logging.debug("execute_command: %s", command)
    result = subprocess.run(command, shell=True, cwd=os.getcwd(), capture_output=True, text=True)
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    
    command_output = {"STDOUT": "", "STDERR": ""}

    if stdout:
        command_output["STDOUT"] = stdout
    if stderr:
        command_output["STDERR"] = stderr

    return command_output
