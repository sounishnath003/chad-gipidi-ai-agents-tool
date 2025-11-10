# Building AI Agents - Chad Gipidii

Welcome to the AI Tool Test Project! This project features a robust AI agent powered by Google Gemini, designed to interact with users and perform various tasks through a set of integrated tools. It's built for seamless interaction, efficient task execution, and easy extensibility.

## Features

*   **Interactive AI Agent:** A conversational agent capable of understanding user queries and responding intelligently.
*   **Dynamic Tool Integration with `@tool` Decorator:** Tools are now dynamically registered and discovered using a powerful `@tool` decorator, simplifying their definition and enhancing flexibility.
*   **Multi-step Tool Execution:** The agent can intelligently execute multiple tool calls in sequence, processing intermediate results to tackle complex problems and achieve sophisticated outcomes.
*   **Color-Coded Logging:** Enhanced logging system for clear and visually distinct feedback on agent activities.
*   **Configurable LLM:** Easily switch or configure the underlying Large Language Model (LLM) used by the agent.
*   **Robust Error Handling:** Tools include input validation, retry mechanisms, and structured `STDOUT`/`STDERR` for command execution results, ensuring resilient and clear operation.

## Project Structure Overview

Here's a quick look at the core components of this project:

*   `main.py`: The main entry point for the application.
*   `README.md`: You're looking at it, boss!
*   `src/aitooltest/`: This directory contains the heart of the AI agent's logic.
    *   `agent.py`: Defines the `Agent` class, which is the central intelligence of the project. It manages interactions with the Google Gemini model, processes user input, and **orchestrates multi-step tool execution by dynamically retrieving registered tools**. It's the "brain" that brings everything together.
    *   `definations.py`: Establishes the `ToolDefination` blueprint, a Pydantic model that standardizes how tools are defined, including their name, description, and input schema (`Type[BaseModel]`). This ensures consistency and clarity for all tools within the `tool_registry`.
    *   `config.py`: Houses the `LLMConfig` class, where crucial settings for the Large Language Model (e.g., `MODEL_NAME` like "gemini-2.5-flash") are defined. This allows for easy configuration of the AI's core model.
    *   `tool_registry.py`: **NEW!** This is the central hub for managing and discovering all tools. It provides the `@tool` decorator to easily register functions as callable tools and offers `get_tools()` to retrieve a list of all registered tools for the agent to use.
    *   `tools.py`: This is the powerhouse where all the specific tools are implemented. Each function here is transformed into a powerful tool using the `@tool` decorator, allowing the AI to perform a wide range of tasks like `read_file`, `list_files`, `edit_file`, and `execute_command`. Notably, `execute_command` now returns structured `STDOUT` and `STDERR` for clearer output.
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
*   **Use Tools:** The agent will intelligently decide when to use its available tools (like reading files, listing directories, or executing commands) based on your requests. With **multi-step execution**, it can chain tool calls to achieve complex tasks!
*   **Exit:** Type `q`, `quit`, `exit`, or `\bye` to end the chat session.
