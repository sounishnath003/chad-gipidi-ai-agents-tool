import argparse
import logging
from typing import Callable
from google import genai
from src.aitooltest.logger import initialize_logging
from src.aitooltest.agent import Agent


def main():
    """Main entrypoint of the function"""

    def get_user_message():
        """tries to take the user's input from command line"""
        input_text = input()
        return input_text

    parser = argparse.ArgumentParser()
    parser.add_argument("--project_id", required=True, type=str, help="provide gcp project id")
    parser.add_argument("--location", required=True, type=str, help="provide gcp project location")
    parser.add_argument("--model_name", default="gemini-2.5-flash", type=str, help="provide the gen ai model name / id")

    opts, pipeline_opts = parser.parse_known_args()
    logging.debug("opts: %s, unknown_opts: %s", opts, pipeline_opts)

    # If you want to use Vertex AI - Chat Inference mode is not available yet....
    # agent = Agent(client=genai.Client(vertexai=True, project=opts.project_id, location=opts.location), get_user_message=get_user_message, tools=[])

    # Use: Google Gemini AI - API Key instead
    agent = Agent(client=genai.Client(), get_user_message=get_user_message, tools=[])

    # Run the agent
    agent.run()


if __name__ == "__main__":
    initialize_logging()
    main()
