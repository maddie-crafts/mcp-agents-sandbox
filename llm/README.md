# LLM Client for Clinical Trials Data

A natural language interface for querying structured clinical trial data via ClinicalTrials.gov using the MCP protocol.

## Features

- Natural language queries to real-time clinical trial metadata
- Integration with ClinicalTrials.gov API through the MCP protocol
- Two interface options:
  - Modern web UI (Chainlit)
  - Terminal-based interface

## Prerequisites

- Python 3.11+
- Docker and Docker Compose
- NVIDIA GPU (recommended) for Ollama or other LLM inference

## Quick Start

1. Set environment variables in `.env`:
```bash
OLLAMA_HOST=localhost
OLLAMA_PORT=11435
CLINICAL_TRIALS_MCP_HOST=localhost
CLINICAL_TRIALS_MCP_PORT=8081
```

2. Install dependencies:
```bash
uv sync
```

3. Start the services:
```bash
docker compose up -d
```

## Usage

### Web Interface

Start the Chainlit UI:
```bash
make run-chainlit
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

### Terminal Interface

Run the command-line interface:
```bash
make run-client
```

## Configuration

Edit `conf/config.yaml` to configure:
- LLM model settings (e.g., Ollama model and endpoint)
- MCP server connection (ClinicalTrials.gov MCP)
- Tool registration and usage rules