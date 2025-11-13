import logging
import os
import subprocess
import pathspec
import threading
import uuid
from pathlib import Path
from typing import Dict, Optional
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
def apply_patch(path: str, patch_content: str) -> Dict:
    """
    Apply a patch to a file using the diff format.
    Returns a dictionary with the status and details of the operation.
    """
    logging.debug("apply_patch to %s", path)

    # Create the file if it doesn't exist, as `patch` can create new files from patches.
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as f:
            pass  # create empty file

    try:
        result = subprocess.run(
            ['patch', path],
            input=patch_content,
            text=True,
            capture_output=True,
            check=False
        )

        if result.returncode == 0:
            logging.info("Patch applied successfully to %s", path)
            return {"status": "OK"}
        else:
            logging.warning("Failed to apply patch to %s. Return code: %s", path, result.returncode)
            
            # Check for a reject file (.rej)
            rej_path = Path(path + ".rej")
            rej_content = None
            if rej_path.exists():
                try:
                    with open(rej_path, "r") as f:
                        rej_content = f.read()
                    os.remove(rej_path)  # Clean up the reject file
                except Exception as e:
                    logging.error("Error reading or deleting reject file %s: %s", rej_path, e)

            return {
                "status": "FAIL",
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "rejects": rej_content
            }

    except FileNotFoundError:
        error_message = "The 'patch' command is not available on this system. Please install it."
        logging.error(error_message)
        return {"status": "ERROR", "message": error_message}
    except Exception as e:
        logging.error("An unexpected error occurred during apply_patch: %s", e)
        return {"status": "ERROR", "message": str(e)}


# A dictionary to store running processes information
running_commands = {}

def _run_command_in_thread(command: str, command_id: str):
    """Helper function to run a command in a separate thread."""
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        running_commands[command_id]['process'] = process

        # Stream stdout and stderr
        stdout_lines = []
        stderr_lines = []

        for line in iter(process.stdout.readline, ''):
            stdout_lines.append(line)
            running_commands[command_id]['stdout'] = "".join(stdout_lines)
        
        for line in iter(process.stderr.readline, ''):
            stderr_lines.append(line)
            running_commands[command_id]['stderr'] = "".join(stderr_lines)

        process.stdout.close()
        process.stderr.close()
        process.wait()
        
        running_commands[command_id]['returncode'] = process.returncode
        running_commands[command_id]['status'] = 'completed'
    except Exception as e:
        running_commands[command_id]['status'] = 'error'
        running_commands[command_id]['stderr'] = str(e)
        running_commands[command_id]['returncode'] = 1


@tool
def execute_command(command: str, description: Optional[str] = None, wait: bool = False) -> Dict:
    """
    Execute a given command.
    By default, it runs in the background and returns a command_id.
    Set `wait=True` to run it in the foreground and wait for completion.
    """
    logging.debug("execute_command: %s, description=%s, wait=%s", command, description, wait)

    if wait:
        result = subprocess.run(command, shell=True, cwd=os.getcwd(), capture_output=True, text=True)
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        return {"STDOUT": stdout, "STDERR": stderr, "returncode": str(result.returncode)}

    command_id = str(uuid.uuid4())
    thread = threading.Thread(target=_run_command_in_thread, args=(command, command_id))
    
    running_commands[command_id] = {
        'command': command,
        'description': description,
        'status': 'running',
        'stdout': '',
        'stderr': '',
        'returncode': None,
        'thread': thread,
        'process': None,
    }
    
    thread.start()
    
    return {"status": "started", "command_id": command_id}


@tool
def check_command(command_id: str) -> Dict:
    """
    Check the status of a command started with `execute_command`.
    """
    logging.debug("check_command: %s", command_id)
    if command_id not in running_commands:
        return {"status": "error", "message": "Command ID not found."}
    
    info = running_commands[command_id]
    return {
        "command": info['command'],
        "description": info['description'],
        "status": info['status'],
        "stdout": info['stdout'],
        "stderr": info['stderr'],
        "returncode": info['returncode'],
    }


@tool
def list_running_commands() -> Dict[str, Dict]:
    """List all currently running commands."""
    logging.debug("list_running_commands")
    
    serializable_commands = {}
    for cmd_id, info in running_commands.items():
        if info['status'] == 'running':
             serializable_commands[cmd_id] = {
                'command': info['command'],
                'description': info['description'],
                'status': info['status'],
            }
    return serializable_commands


@tool
def generate_or_refactor_code(
    prompt: str,
    existing_code: Optional[str] = None,
    programming_language: str = None,
    file_tree_input: Optional[str] = None,
) -> str:
    """
    Generate or refactor code based on a prompt.

    Args:
        prompt: The instruction for code generation/refactoring.
        existing_code: The code to be refactored, if any.
        programming_language: The language of the code.
        file_tree_input: The file structure of the project.

    Returns:
        The generated or refactored code.
    """
    # This is a placeholder for the actual implementation.
    # In a real scenario, this would call a code generation model.
    logging.debug(
        "generate_or_refactor_code: %s, %s, %s, %s",
        prompt,
        existing_code,
        programming_language,
        file_tree_input,
    )
    return "Generated or refactored code will appear here."
