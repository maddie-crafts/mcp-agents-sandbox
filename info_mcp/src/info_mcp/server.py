import os
import logging
from dotenv import load_dotenv, find_dotenv
from mcp.server import FastMCP

from clinical_trials_agent import (
    get_trials_by_condition,
    get_trials_by_id,
)

load_dotenv(find_dotenv())

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize MCP server with Clinical Trials env vars
mcp_server = FastMCP(
    host=os.environ["CLINICAL_TRIALS_MCP_HOST"],
    port=os.environ["CLINICAL_TRIALS_MCP_PORT"]
)

tools = [
    get_trials_by_condition,
    get_trials_by_id,
]

for tool in tools:
    mcp_server.tool()(tool)