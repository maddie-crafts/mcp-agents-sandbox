import json
import aiohttp
import asyncio
import logging
from contextlib import AsyncExitStack
from typing import List, Optional, Dict

from dotenv import find_dotenv, load_dotenv
from hydra import compose, initialize
from mcp import ClientSession
from mcp.client.sse import sse_client

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv(find_dotenv())


class OllamaClient:
    def __init__(self, model: str, base_url: str):
        self.model = model
        self.base_url = base_url

    async def send_message(
        self, messages: List[str], tools: Optional[list] = None, stream: bool = False
    ):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "tools": tools,
                    "stream": stream,
                },
            ) as response:
                if stream:
                    async for line in response.content:
                        if line:
                            yield json.loads(line)
                else:
                    result = await response.json()
                    yield result


def ollama_tool_conversion(tool):
    return {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["input_schema"],
        },
    }


class MCPClient:
    def __init__(self, llm: OllamaClient):
        self.llm = llm
        self.exit_stack = AsyncExitStack()
        self.sessions = {}
        self.available_tools = []

    async def connect_to_servers(self, servers_config: dict):
        for server_name, config in servers_config.items():
            host = config["host"]
            port = config["port"]
            url = f"http://{host}:{port}/sse"

            sse_transport = await self.exit_stack.enter_async_context(sse_client(url))
            reader, writer = sse_transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(reader, writer)
            )

            await session.initialize()
            self.sessions[server_name] = session

            response = await session.list_tools()
            server_tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                }
                for tool in response.tools
            ]
            self.available_tools.extend(server_tools)

    async def call_tools(self, messages: List[Dict[str, str]]):
        tools = [ollama_tool_conversion(tool) for tool in self.available_tools]
        async for call in self.llm.send_message(messages, tools=tools):
            response = call

        message = response["message"]
        if "tool_calls" in message:
            for tool_call in message["tool_calls"]:
                function = tool_call["function"]
                tool_name = function["name"]
                tool_args = function["arguments"]

                # Try each session until we find one that has the tool
                for session_name, session in self.sessions.items():
                    try:
                        logger.info(
                            f"Session: {session_name}, Tool: {tool_name}, Args: {tool_args}"
                        )
                        result = await session.call_tool(tool_name, tool_args)
                        messages.extend(
                            [
                                {
                                    "role": "system",
                                    "content": f"Calling tool {tool_name}, Args: {tool_args}"
                                },
                                {
                                    "role": "system",
                                    "content": result.content[0].text[:10000],
                                }
                            ]
                        )
                    except Exception as e:
                        logger.error(
                            f"Error calling Session: {session_name}, Tool: {tool_name}, Error: {e}"
                        )

        return messages

    async def process_query(self, query: str, history: List[str] = []) -> str:
        messages = [
            {
                "role": "system",
                "content": '''
                    You are a Clinical Trials Assistant designed to help users query and explore data from ClinicalTrials.gov using structured API tools. Your primary responsibility is to assist with accurate, up-to-date, and relevant information about clinical trials.

                    Your tools allow you to:
                    - Retrieve trials based on condition, location, or trial phase
                    - Fetch detailed metadata about a trial using its NCT ID (e.g., NCT04280705)
                    - Summarize eligibility criteria, recruitment status, or sponsor details

                    Guardrails and safety rules:
                    - **Do not hallucinate**: Only use information retrieved through the provided tools
                    - **Do not fabricate trial IDs** or eligibility information
                    - **Never provide medical advice** or interpretation beyond what is returned by the API
                    - If a query cannot be fulfilled due to missing details (e.g., no NCT ID or vague condition), **ask for clarification or return a helpful fallback message**
                    - Avoid unsupported queries (e.g., treatment recommendations, drug efficacy claims)

                    Tool usage guidance:
                    - Prefer direct tool use when the user asks about a known trial ID or condition
                    - If the user provides only partial input, fill in common fields with default values (e.g., fetch the top 5 results or assume "United States" as a location when omitted)
                    - Respond in a concise, professional tone, citing trial IDs and fields clearly

                    Reminder:
                    You are a helpful assistant acting as an interface to a real dataset. Your purpose is to make clinical trials more accessible — not to interpret, prescribe, or speculate.
                    '''
            },
        ]

        for message in history:
            messages.append(
                {"role": message["role"], "content": message["content"]}
            )

        # Remove duplicate original system prompt if present
        messages = list({(m["role"], m["content"]): m for m in messages}.values())

        messages.append(
            {
                "role": "user",
                "content": query,
            }
        )

        extra_prompt = {
            "role": "system",
            "content": "Using the above conversation and available tools, answer the query appropriately.",
        }

        tool_responses = await self.call_tools(messages)
        logger.info(f"Tool responses: {json.dumps(tool_responses + [extra_prompt], indent=2)}")
        response = self.llm.send_message(tool_responses, stream=True)
        return response

    async def chat_loop(self):
        while True:
            try:
                query = input("Enter a query: ").strip()

                if query.lower() == "quit":
                    break

                response = await self.process_query(query)
                print(response)

            except Exception as e:
                print(f"\nAn error occurred: {e}")

    async def cleanup(self):
        await self.exit_stack.aclose()


async def main():
    initialize(config_path="conf")
    cfg = compose(config_name="config")

    llm = OllamaClient(model=cfg.ollama.model, base_url=cfg.ollama.base_url)
    client = MCPClient(llm)

    await client.connect_to_servers(cfg.mcp.servers)
    await client.chat_loop()
    await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
