import argparse
import logging
from google import genai
from .tools import EditFileToolDefination, ExecuteCommandToolDefination, ListFileToolDefination, ReadFileToolDefination
from .logger import initialize_logging
from .agent import Agent


def run_agent_main_entrypoint():
    """Main entrypoint of the function"""
    initialize_logging()

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
    # agent = Agent(client=genai.Client(vertexai=True, project=opts.project_id,\
    # location=opts.location), get_user_message=get_user_message, tools=[])

    # Use: Google Gemini AI - API Key instead
    agent = Agent(client=genai.Client(), get_user_message=get_user_message,
        tools=[
            ReadFileToolDefination(),
            ListFileToolDefination(),
            EditFileToolDefination(),
            ExecuteCommandToolDefination(),
        ]
    )

    # Run the agent
    agent.run()

