<div align="center">

# OpenCoder

**Enterprise-Grade Agentic Coding Tool**

*AI-Powered Code Generation, Refactoring & Debugging with Aider + OpenGPU Relay*

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

[![GitHub Stars](https://img.shields.io/github/stars/Asphyksia/OpenCoder?style=social)](https://github.com/Asphyksia/OpenCoder/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/Asphyksia/OpenCoder)](https://github.com/Asphyksia/OpenCoder/issues)
[![GitHub Forks](https://img.shields.io/github/forks/Asphyksia/OpenCoder?style=social)](https://github.com/Asphyksia/OpenCoder/network/members)

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-api-reference">API</a> •
  <a href="#-supported-models">Models</a> •
  <a href="#-troubleshooting">Troubleshooting</a>
</p>

<!-- TODO: Add actual screenshot when available -->
<!-- <img src="docs/screenshot.png" alt="OpenCoder Dashboard" width="80%"> -->

</div>

---

## 📖 Overview

OpenCoder is an **enterprise-grade agentic coding tool** that combines the power of [Aider](https://aider.chat) with [OpenGPU Relay](https://relay.opengpu.network) to provide AI-powered code generation, refactoring, and debugging capabilities. It offers both a RESTful API and a modern web interface for seamless integration into your development workflow.

### Why OpenCoder?

| Traditional AI Coding Tools | OpenCoder |
|:---------------------------:|:---------:|
| ❌ Expensive API costs | ✅ Cost-effective GPU relay |
| ❌ Limited model choices | ✅ 50+ open-source models |
| ❌ No local control | ✅ Self-hosted, full control |
| ❌ Complex setup | ✅ One-command installation |
| ❌ No IDE integration | ✅ REST API for any IDE |

---

## ✨ Features

### 🤖 Agentic Coding Capabilities

| Capability | Description |
|------------|-------------|
| **Code Generation** | Create new files, functions, classes, and entire modules from natural language descriptions |
| **Refactoring** | Improve code quality, optimize performance, and modernize legacy code |
| **Bug Fixing** | Identify and fix bugs with detailed explanations and tests |
| **Code Review** | Get comprehensive code reviews with actionable suggestions |
| **Documentation** | Generate and update documentation automatically |
| **Testing** | Create unit tests, integration tests, and test fixtures |

### 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         OpenCoder Architecture                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐                              │
│  │   Frontend   │    │  REST API    │                              │
│  │   Next.js    │◄──►│   FastAPI    │                              │
│  │   Port 3000  │    │   Port 8001  │                              │
│  └──────────────┘    └──────┬───────┘                              │
│                             │                                        │
│                    ┌────────▼────────┐                              │
│                    │  AiderBridge    │                              │
│                    │  Agent Engine   │                              │
│                    └────────┬────────┘                              │
│                             │                                        │
│              ┌──────────────┼──────────────┐                        │
│              ▼              ▼              ▼                        │
│     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│     │   OpenGPU    │ │   LiteLLM    │ │    Git       │             │
│     │    Relay     │ │    Patch     │ │  Integration │             │
│     └──────────────┘ └──────────────┘ └──────────────┘             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 🔧 Technical Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend API** | FastAPI + Uvicorn | RESTful API with OpenAPI docs |
| **Agent Engine** | Aider + LiteLLM | AI-powered code manipulation |
| **OpenGPU Adapter** | OpenAI-compatible client | Connect to GPU relay network |
| **Frontend** | Next.js 15 + React 19 | Modern web interface |
| **State Management** | Zustand + React Query | Efficient client state |
| **UI Components** | Radix UI + Tailwind CSS | Accessible, beautiful UI |

---

## 🚀 Quick Start

### Option 1: One-Line Installation (Recommended)

```bash
# Clone and install everything automatically
git clone https://github.com/Asphyksia/OpenCoder.git && cd OpenCoder && chmod +x install.sh && ./install.sh
```

### Option 2: Docker (Production-Ready)

```bash
# Using Docker Compose
export OPENGPU_API_KEY=relay_sk_your_key
git clone https://github.com/Asphyksia/OpenCoder.git && cd OpenCoder
docker-compose up -d
```

### After Installation

```bash
# Start OpenCoder
./start.sh

# Access the application
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000
# API Docs:  http://localhost:8000/docs
```

---

## 📦 Installation

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10-3.12 | ⚠️ Python 3.13+ is NOT supported (Aider limitation) |
| Node.js | 18+ | 20+ recommended |
| Git | Any recent version | Required for version control features |
| Docker | 20+ | Optional, for containerized deployment |

### Method 1: Native Installation

```bash
# 1. Clone the repository
git clone https://github.com/Asphyksia/OpenCoder.git
cd OpenCoder

# 2. Run the automated installer
chmod +x install.sh
./install.sh

# 3. Configure your API key
# Get your key from: https://relay.opengpu.network
nano .env  # Add: OPENGPU_API_KEY=relay_sk_your_key

# 4. Start the application
./start.sh
```

### Method 2: Docker Installation

```bash
# 1. Clone the repository
git clone https://github.com/Asphyksia/OpenCoder.git
cd OpenCoder

# 2. Set your API key
export OPENGPU_API_KEY=relay_sk_your_key

# 3. Build and run with Docker Compose
docker-compose up -d

# 4. View logs
docker-compose logs -f
```

### Method 3: Manual Installation

```bash
# 1. Create Python virtual environment
python3.12 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 2. Install Python dependencies
pip install -r requirements.txt
pip install 'aider-chat[all]'

# 3. Install frontend dependencies
cd frontend && npm install && cd ..

# 4. Configure environment
cp .env.example .env
# Edit .env with your API key

# 5. Start services
# Terminal 1: Backend
uvicorn opencoder.api.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

---

## 🔑 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required: Your OpenGPU API key
OPENGPU_API_KEY=relay_sk_your_api_key_here

# Optional: API base URL (default shown)
OPENGPU_BASE_URL=https://relaygpu.com/backend/openai/v1

# Optional: Default model for coding tasks
OPENGPU_MODEL=Qwen/Qwen3-Coder
```

### Getting an API Key

1. Visit [OpenGPU Relay](https://relay.opengpu.network)
2. Create a free account
3. Navigate to API Keys section
4. Generate a new key (starts with `relay_sk_`)
5. Add the key to your `.env` file

---

## 📚 API Reference

### Base URL

```
http://localhost:8000
```

### Endpoints

#### `POST /chat`

Send a message to the coding agent.

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a Python function that calculates fibonacci numbers",
    "model": "Qwen/Qwen3-Coder",
    "read_only": false
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Command executed successfully",
  "events": [...],
  "file_changes": [...],
  "diffs": "diff --git a/...",
  "error": null
}
```

#### `GET /models`

List available models from OpenGPU Relay.

```bash
curl http://localhost:8000/models
```

#### `GET /pricing`

Get pricing information for all models.

```bash
curl http://localhost:8000/pricing
```

#### `GET /status`

Get current workspace status.

```bash
curl http://localhost:8000/status
```

#### `GET /health`

Health check endpoint.

```bash
curl http://localhost:8000/health
```

### OpenAPI Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🎯 Supported Models

### Recommended Models for Coding

| Model | Best For | Context | Speed |
|-------|----------|---------|-------|
| `Qwen/Qwen3-Coder` | General coding (Recommended) | 32K | ⚡⚡⚡ |
| `deepseek-ai/DeepSeek-V3.1` | Complex reasoning | 64K | ⚡⚡ |
| `Qwen/Qwen2.5-72B-Instruct` | General purpose | 32K | ⚡⚡ |
| `meta-llama/Llama-3.3-70B-Instruct` | Chat & code | 8K | ⚡⚡⚡ |

### Model Name Normalization

OpenCoder automatically normalizes model names:

| Input | Normalized |
|-------|------------|
| `openai/Qwen/Qwen3-Coder` | `Qwen/Qwen3-Coder` |
| `anthropic/claude-3-opus` | `claude-3-opus` |
| `Qwen/Qwen3-Coder` | `Qwen/Qwen3-Coder` (unchanged) |

---

## 🛠️ Troubleshooting

### Common Issues

<details>
<summary><strong>❌ Python 3.13 detected</strong></summary>

**Problem:** Aider requires Python 3.10-3.12. Python 3.13 is not supported.

**Solution:**
```bash
# Linux
sudo apt install python3.12 python3.12-venv
python3.12 -m venv venv

# macOS
brew install python@3.12
python3.12 -m venv venv

# Windows: Download from python.org
```
</details>

<details>
<summary><strong>❌ "litellm blocked by OpenGPU" error</strong></summary>

**Problem:** LiteLLM's provider detection conflicts with OpenGPU Relay.

**Solution:** This is automatically handled by our patch. If you see this error, ensure you're using the latest version:
```bash
pip install -U -r requirements.txt
```
</details>

<details>
<summary><strong>❌ Aider cannot connect to OpenGPU</strong></summary>

**Problem:** Environment variables not configured correctly.

**Solution:**
```bash
# Verify your .env file contains:
cat .env | grep OPENGPU

# Test the connection:
curl https://relaygpu.com/backend/openai/v1/models \
  -H "Authorization: Bearer relay_sk_your_key"
```
</details>

<details>
<summary><strong>❌ Port 8000 or 3000 already in use</strong></summary>

**Problem:** Another service is using the default ports.

**Solution:**
```bash
# Use different ports
# Backend:
uvicorn opencoder.api.main:app --port 8001

# Frontend:
PORT=3001 npm run dev
```
</details>

<details>
<summary><strong>❌ Docker container fails to start</strong></summary>

**Problem:** Missing API key or Docker configuration issue.

**Solution:**
```bash
# Ensure API key is set
export OPENGPU_API_KEY=relay_sk_your_key

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check logs
docker-compose logs -f
```
</details>

---

## 📁 Project Structure

```
OpenCoder/
├── opencoder/                 # Backend Python package
│   ├── api/
│   │   └── main.py           # FastAPI application
│   ├── core/
│   │   ├── aider_bridge.py   # Aider CLI integration
│   │   ├── litellm_patch.py  # OpenGPU compatibility patch
│   │   ├── opengpu_adapter.py # OpenGPU client
│   │   └── agent_engine.py   # Agent orchestration
│   └── models/
│       └── schemas.py        # Pydantic models
│
├── frontend/                  # Next.js frontend
│   ├── src/
│   │   ├── app/              # App router pages
│   │   ├── components/       # React components
│   │   ├── hooks/            # Custom hooks
│   │   ├── lib/              # Utilities
│   │   └── store/            # Zustand store
│   └── package.json
│
├── scripts/                   # Helper scripts
│   ├── aider_wrapper.py      # Multi-platform Aider wrapper
│   └── aider_with_patch.py   # Aider with LiteLLM patch
│
├── tests/                     # Test suite
│   └── test_model_normalization.py
│
├── Dockerfile                 # Docker image definition
├── docker-compose.yml         # Docker Compose config
├── install.sh                 # Linux/macOS installer
├── install-docker.sh          # Docker installer
├── start.sh                   # Application starter
├── requirements.txt           # Python dependencies
└── .env.example               # Environment template
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/OpenCoder.git
cd OpenCoder

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio

# Run tests
pytest tests/ -v

# Start development server
./start.sh
```

### Code Style

- Python: Follow PEP 8, use `black` for formatting
- TypeScript/React: Use ESLint and Prettier
- Commits: Follow [Conventional Commits](https://conventionalcommits.org/)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Aider](https://aider.chat) - AI pair programming tool
- [OpenGPU Relay](https://relay.opengpu.network) - GPU compute network
- [FastAPI](https://fastapi.tiangolo.com) - Modern Python web framework
- [Next.js](https://nextjs.org) - React framework
- [Radix UI](https://radix-ui.com) - Accessible UI components

---

## 📞 Support

- **Documentation:** [Wiki](https://github.com/Asphyksia/OpenCoder/wiki)
- **Issues:** [GitHub Issues](https://github.com/Asphyksia/OpenCoder/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Asphyksia/OpenCoder/discussions)

---

<div align="center">

**[⬆ Back to Top](#opencoder)**

Made with ❤️ by the OpenCoder Team

</div>
