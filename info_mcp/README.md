# Clinical Trials MCP Server

Micro-service for accessing clinical trial data through the MCP protocol. This service provides natural language access to clinical trials metadata including conditions, locations, statuses, and eligibility criteria.

## Features

- Access to [ClinicalTrials.gov](https://clinicaltrials.gov/api/gui) REST API
- Retrieve trials by condition, location, or NCT ID
- Built on FastMCP framework with async/await support
- Ready to integrate with LLM clients for conversational access

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Configure environment variables in `.env`:
```env
CLINICAL_TRIALS_MCP_HOST=localhost
CLINICAL_TRIALS_MCP_PORT=8081
```

## Docker Usage

Run with Docker Compose:
```bash
docker compose up clinical-trials-server
```

The server will be available at `http://localhost:8081`.

## Quick Start

1. Configure environment:
```bash
cp .env.example .env
```

2. Start services:
```bash
make build
make up
```

3. Launch web interface:
```bash
make run-chainlit
```

Visit http://localhost:8000 to start querying clinical trial data.

## Prerequisites

- Docker and Docker Compose
- NVIDIA GPU (recommended) for optimal LLM performance
- Python 3.11+ (for local development)

## Example Queries

Try asking questions like:
- "What clinical trials are recruiting for breast cancer?"
- "Get me trials in the UK related to diabetes"
- "Show eligibility criteria for NCT04280705"

## Development

- Use `make help` to see available commands
- Each service has its own README with detailed documentation
- Configuration files are in the `conf/` directory

## Description

This project contains multiple modules that interact with various services and APIs using the FastMCP framework. Each module is designed to perform specific tasks and can be run independently or together using Docker Compose. The primary focus of this project is on healthcare agents, providing tools and services to interact with structured medical datasets like ClinicalTrials.gov.

## Modules

### LLM Client

The `llm` module provides a client that interacts with a Language Model (LLM) server to process queries and utilize available tools. It is built using the FastMCP framework and supports asynchronous operations with `aiohttp`.

For more details, refer to the [LLM Client README](llm/README.md).

### Clinical Trials Database

The `clinical_trials_mcp` module provides a server that interacts with ClinicalTrials.gov to retrieve metadata such as conditions, eligibility, trial phases, and recruitment status. It is built using the FastMCP framework and the public REST API.

For more details, refer to the [Clinical Trials README](clinical_trials_mcp/README.md).

## Docker

Dockerfiles are provided for each module to build Docker images.

- **Build the Docker image:**
```sh
docker build -t clinical-trials-mcp .
```

- **Run the Docker container:**
```sh
docker run --env-file .env clinical-trials-mcp
```

## Docker Compose

A `docker-compose.yml` file is provided to run all services together.

- **Start all services:**
```sh
docker-compose up -d
```

- **Stop all services:**
```sh
docker-compose down
```

## Makefile

A `Makefile` is provided to simplify common tasks.

- **Available targets:**
  - `setup-env`: Set up the initial environment.
  - `build`: Build all Docker images.
  - `up`: Start all services using docker-compose.
  - `down`: Stop all services using docker-compose.
  - `restart`: Restart all services using docker-compose.
  - `run-chainlit`: Run the Chainlit UI for the LLM client.
  - `run-client`: Run the LLM client in terminal mode.