# Building AI Agents - Chad Gipidii 

Welcome to the AI Tool Test Project! This project features a robust AI agent powered by Google Gemini, designed to interact with users and perform various tasks through a set of integrated tools. It's built for seamless interaction, efficient task execution, and easy extensibility.

## Features

*   **Interactive AI Agent:** A conversational agent capable of understanding user queries and responding intelligently.
*   **Dynamic Tool Integration:** The agent can dynamically call and execute a variety of predefined tools to perform actions like file operations and command execution.
*   **Color-Coded Logging:** Enhanced logging system for clear and visually distinct feedback on agent activities.
*   **Configurable LLM:** Easily switch or configure the underlying Large Language Model (LLM) used by the agent.
*   **Robust Error Handling:** Tools include input validation and retry mechanisms for resilient operation.

## Project Structure Overview

Here's a quick look at the core components of this project:

*   `main.py`: The main entry point for the application.
*   `README.md`: You're looking at it, boss!
*   `src/aitooltest/`: This directory contains the heart of the AI agent's logic.
    *   `agent.py`: Defines the `Agent` class, which is the central intelligence of the project. It manages interactions with the Google Gemini model, processes user input, and orchestrates tool execution. It's the "brain" that brings everything together.
    *   `definations.py`: Establishes the `ToolDefination` blueprint, a Pydantic model that standardizes how tools are defined, including their name, description, input schema, and the actual function they execute. This ensures consistency and clarity for all tools.
    *   `config.py`: Houses the `LLMConfig` class, where crucial settings for the Large Language Model (e.g., `MODEL_NAME` like "gemini-2.5-flash") are defined. This allows for easy configuration of the AI's core model.
    *   `tools.py`: This is the powerhouse where all the specific tools are implemented. Each tool (`read_file_fn`, `list_files_fn`, `edit_file_fn`, `execute_command_fn`) comes with its own input schema and description, allowing the AI to perform a wide range of tasks like reading file content, listing directory contents, editing files, and executing shell commands (with safety precautions!).
    *   `logger.py`: Provides a custom `ColoredFormatter` for the logging system, making log messages more readable and distinguishable by coloring them based on their severity level (e.g., debug, info, warning, error).
    *   `utils.py`: Contains utility functions, primarily `generate_schema` and `python_type_to_json_type`, which are crucial for converting Pydantic models into Google Gemini-compatible JSON schemas. This ensures the AI correctly interprets tool arguments for function calls.

## Getting Started

To get this Chad-level AI agent up and running, follow these steps:

### Prerequisites

*   Python 3.9+
*   `uv` (or `pip` for package management)
*   A Google Cloud project with the Gemini API enabled.
*   Your Google API key for Gemini.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url> # Replace with your actual repo URL
    cd <repository-name>
    ```

2.  **Install dependencies and create a virtual environment with `uv`:**
    ```bash
    uv sync
    ```
    This command will read your `pyproject.toml` and `uv.lock` to install all necessary dependencies into a virtual environment.

### Configuration

1.  **Set up your Google API Key:**
    The agent needs access to the Google Gemini API. Set your API key as an environment variable:
    ```bash
    export GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
    ```
    (Replace `"YOUR_GEMINI_API_KEY"` with your actual API key.)

### Running the Agent

To start chatting with the AI agent, simply run the `main.py` script:

```bash
GOOGLE_API_KEY="" uv run main.py --project_id $(gcloud config get project) --location asia-south1
```

The agent will then prompt you for input. Type your queries and let the Chad Gipidii agent assist you!

## How to Interact

*   **Ask anything!** The agent is ready to help solve your problems.
*   **Use Tools:** The agent will intelligently decide when to use its available tools (like reading files, listing directories, or executing commands) based on your requests.
*   **Exit:** Type `q`, `quit`, `exit`, or `\bye` to end the chat session.
