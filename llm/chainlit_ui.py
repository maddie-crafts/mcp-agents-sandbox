import chainlit as cl
import logging

from dotenv import find_dotenv, load_dotenv
from hydra import compose, initialize
from client import OllamaClient, MCPClient

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv(find_dotenv())
initialize(config_path="conf")
cfg = compose(config_name="config")

llm = OllamaClient(model=cfg.ollama.model, base_url=cfg.ollama.base_url)
client = MCPClient(llm)


@cl.set_chat_profiles
async def chat_profile(current_user: cl.User):
    return [
        cl.ChatProfile(
            name="Clinical Trials",
            icon="🩺",
            markdown_description="Query clinical trials data such as trial conditions, locations, eligibility, and more.",
            starters=[
                cl.Starter(
                    label="Trials by Condition",
                    message="What clinical trials are recruiting for breast cancer?",
                ),
                cl.Starter(
                    label="Trials by Location",
                    message="List trials in the UK related to diabetes.",
                ),
                cl.Starter(
                    label="Eligibility Criteria",
                    message="What are the eligibility criteria for trial NCT04280705?",
                ),
            ],
        )
    ]


@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [
            {
                "role": "system",
                "content": "You are a helpful assistant that performs API calls on clinical trials databases such as ClinicalTrials.gov.",
            }
        ],
    )


@cl.on_message
async def main(message: cl.Message):
    await client.connect_to_servers(cfg.mcp.servers)

    message_history = cl.user_session.get("message_history", [])
    message_history.append({"role": "user", "content": message.content})
    msg = cl.Message(content="")

    max_history_length = 10
    stream = await client.process_query(message.content, history=message_history[-max_history_length:])

    async for part in stream:
        if token := part["message"]["content"] or "":
            await msg.stream_token(token)

    message_history.append({"role": "assistant", "content": msg.content})
    await msg.update()