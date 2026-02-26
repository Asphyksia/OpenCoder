# OpenCoder

Agentic Coding Tool powered by Aider and OpenGPU Relay.

## ⚠️ Important: Python Version Requirement

**This project requires Python 3.10 - 3.12** (not Python 3.13+)

Python 3.13 is too new and many dependencies (including Aider) don't support it yet.

## Local Setup (Recommended)

```bash
# 1. Ensure you have Python 3.12
python3.12 --version

# 2. Create virtual environment
python3.12 -m venv venv

# 3. Activate
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 4. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 5. Install Aider
pip install aider-chat

# 6. Set API key
export OPENGPU_API_KEY="your-api-key-here"

# 7. Run server
uvicorn opencoder.api.main:app --port 8000
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root info |
| `/health` | GET | Health check |
| `/models` | GET | List available models |
| `/status` | GET | Get repo status |
| `/chat` | POST | Send message to agent |
| `/session/{id}` | DELETE | Close session |

## Example Usage

```bash
# Chat with the agent
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a hello.py file that prints Hello World", "model": "gpt-4o"}'
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENGPU_API_KEY` | - | OpenGPU Relay API key (required) |
| `OPENGPU_BASE_URL` | https://api.opengpu.network/relay/v1 | API base URL |
| `OPENGPU_MODEL` | gpt-4o | Default model |
| `OPENCODER_REPO_PATH` | ./workspace | Working directory |

## Project Structure

```
opencoder/
├── api/
│   └── main.py          # FastAPI application
├── core/
│   ├── agent_engine.py  # Aider wrapper
│   └── opengpu_adapter.py # OpenGPU adapter
├── models/
│   └── schemas.py       # Pydantic models
└── __init__.py
```

## Development

The code uses:
- **FastAPI** for the REST API
- **Aider** as the code editing engine (imported as library)
- **OpenGPU Relay** for model access (OpenAI-compatible API)
- **Pydantic** for data validation

All endpoints return JSON for easy frontend integration.
