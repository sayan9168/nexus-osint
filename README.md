<div align="center">

# 🌐 NEXUS-OSINT

### AI-Native OSINT & 3D Link Analysis Platform

**A next-generation, open-source alternative to Maltego — powered by AI agents, real-time 3D graph visualization, and autonomous investigation workflows.**

[![License](https://img.shields.io/badge/License-Sayanox%20v1.1-cyan)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org)
[![Memgraph](https://img.shields.io/badge/Memgraph-2.18-orange)](https://memgraph.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent-purple)](https://github.com/langchain-ai/langgraph)

[Report Bug](https://github.com/sayan9168/nexus-osint/issues) · [Request Feature](https://github.com/sayan9168/nexus-osint/issues) · [Documentation](https://github.com/sayan9168/nexus-osint/wiki)

</div>

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [API Reference](#-api-reference)
- [AI Agent](#-ai-recon-agent)
- [3D Graph UI](#-3d-graph-ui)
- [Transforms](#-transforms)
- [Configuration](#-configuration)
- [Development](#-development)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

---

## 🔍 Overview

**NEXUS-OSINT** is a production-grade, AI-native Open Source Intelligence (OSINT) and 3D Link Analysis platform. It enables security researchers, threat analysts, and investigators to:

- **Autonomously investigate** targets using AI-driven OSINT workflows
- **Visualize complex relationships** in an interactive 3D WebGL graph (100,000+ nodes)
- **Discover hidden correlations** between entities using semantic vector search
- **Execute OSINT transforms** (DNS, WHOIS, VirusTotal, and custom) asynchronously
- **Receive real-time updates** via WebSocket as the AI agent discovers new entities

> ⚡ Built as a modern, open-source alternative to Maltego with first-class AI integration.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **Autonomous AI Agent** | LangGraph-powered agent that decides which OSINT transforms to run based on graph context |
| 🌐 **3D Graph Visualization** | WebGL-powered force-directed graph rendering 100K+ nodes at 60 FPS |
| ⚡ **Real-Time Streaming** | WebSocket-based live graph updates as entities are discovered |
| 🔗 **Semantic Correlation** | Vector embeddings (Qdrant) to find hidden links between unrelated entity types |
| 🔄 **Async Transform Engine** | Celery + Redis task queue for non-blocking OSINT data collection |
| 📊 **In-Memory Graph DB** | Memgraph (Cypher) for ultra-fast node/relationship queries |
| 🛡️ **Threat Intelligence** | VirusTotal integration for reputation checks and IOC discovery |
| 🏗️ **Production-Grade** | Docker orchestration, rate limiting, retry logic, structured logging |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        NEXUS-OSINT Platform                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐    WebSocket     ┌──────────────────────────────┐  │
│  │  Next.js 3D  │◄────────────────►│     FastAPI Backend           │  │
│  │  Frontend    │    REST API      │  ┌────────────────────────┐  │  │
│  │  (WebGL)     │◄────────────────►│  │  /api/v1/graph         │  │  │
│  │  Port:3001   │                  │  │  /api/v1/entities      │  │  │
│  └──────────────┘                  │  │  /api/v1/transforms    │  │  │
│                                    │  │  /api/v1/agent         │  │  │
│                                    │  │  /ws/graph (WebSocket) │  │  │
│                                    │  └────────────────────────┘  │  │
│                                    └──────┬───────────┬───────────┘  │
│                                           │           │              │
│                              ┌────────────┘           └────────┐     │
│                              ▼                                  ▼     │
│  ┌──────────────────────────────────┐  ┌─────────────────────┐      │
│  │     Memgraph (Graph DB)          │  │   Qdrant (Vector)   │      │
│  │     In-Memory Cypher             │  │   Semantic Search    │      │
│  │     Port: 7687                   │  │   Port: 6333         │      │
│  └──────────────────────────────────┘  └─────────────────────┘      │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │              Celery Workers + Redis Broker                     │    │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────────┐   │    │
│  │  │DNS      │  │WHOIS    │  │VirusTotal│  │  Custom      │   │    │
│  │  │Transform│  │Transform│  │Transform │  │  Transforms  │   │    │
│  │  └─────────┘  └─────────┘  └─────────┘  └──────────────┘   │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │              AI Recon Agent (LangGraph)                        │    │
│  │  Plan (LLM) → Execute Tools → Correlate (Vector) → Report    │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11+, FastAPI (AsyncIO), Pydantic v2 |
| **Graph Database** | Memgraph 2.18 (In-Memory Cypher) |
| **Vector Database** | Qdrant 1.9 (Semantic Search & Identity Matching) |
| **Task Queue** | Celery 5.4 + Redis 7.2 |
| **AI Agent** | LangGraph + LangChain + LLM (Qwen / Claude) |
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS |
| **3D Rendering** | 3d-force-graph (WebGL / Three.js) |
| **State Management** | Zustand |
| **Orchestration** | Docker & Docker Compose |
| **Logging** | structlog (structured JSON logging) |

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose v2.20+
- 8GB+ RAM (Memgraph is in-memory)
- (Optional) Ollama for local LLM inference

### 1. Clone the Repository

```bash
git clone https://github.com/sayan9168/nexus-osint.git
cd nexus-osint
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
VIRUSTOTAL_API_KEY=your_vt_key_here
LLM_API_KEY=your_llm_key_here
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen2.5:72b
```

### 3. Build & Launch

```bash
# Build all containers
docker compose build --no-cache

# Start all services
docker compose up -d
```

### 4. Access the Platform

| Service | URL |
|---------|-----|
| 🌐 **3D Graph Dashboard** | http://localhost:3001 |
| 🔌 **Backend API** | http://localhost:8000 |
| 📖 **API Docs (Swagger)** | http://localhost:8000/docs |
| 🤖 **AI Agent Service** | http://localhost:8001 |
| 🗄️ **Memgraph Lab** | http://localhost:3000 |
| 📐 **Qdrant Dashboard** | http://localhost:6333/dashboard |

### 5. Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Run a DNS transform
curl -X POST http://localhost:8000/api/v1/transforms/execute \
  -H "Content-Type: application/json" \
  -d '{"transform_name": "dns_resolution", "entity_type": "Domain", "entity_value": "example.com"}'

# Trigger AI investigation
curl -X POST http://localhost:8000/api/v1/agent/investigate \
  -H "Content-Type: application/json" \
  -d '{"target": "suspicious-domain.com", "goal": "Identify all associated infrastructure"}'
```

---

## 📁 Project Structure

```
nexus-osint/
├── docker-compose.yml          # Service orchestration
├── .env.example                # Environment template
├── Makefile                    # Build/run shortcuts
├── README.md
├── LICENSE
├── .gitignore
│
├── backend/                    # FastAPI + Transforms + Workers
│   ├── main.py                 # App entry point
│   ├── config.py               # Centralized settings
│   ├── db/                     # Memgraph + Qdrant clients
│   ├── transforms/             # OSINT transform engine
│   ├── api/                    # REST + WebSocket routes
│   └── workers/                # Celery task definitions
│
├── agent/                      # AI Recon Agent (LangGraph)
│   ├── recon_agent.py          # Main agent workflow
│   ├── tools.py                # LLM tool definitions
│   ├── state.py                # LangGraph state schema
│   ├── correlation.py          # Semantic correlation engine
│   └── prompts.py              # System prompts
│
├── frontend/                   # Next.js 3D Dashboard
│   └── src/
│       ├── components/         # Graph3D, Sidebar, AgentPanel
│       ├── hooks/              # useWebSocket, useGraphData
│       ├── store/              # Zustand state
│       └── lib/                # API client, types
│
└── docker/                     # Init scripts & configs
    ├── memgraph/init.cypher
    ├── redis/redis.conf
    └── nginx/nginx.conf
```

---

## 📡 API Reference

### Graph Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/graph/full` | Retrieve full graph (nodes + edges) |
| `GET` | `/api/v1/graph/neighbors` | Get entity neighbors by depth |
| `GET` | `/api/v1/graph/summary` | Graph statistics summary |
| `POST` | `/api/v1/graph/nodes` | Create a new node |
| `POST` | `/api/v1/graph/edges` | Create a new edge |
| `POST` | `/api/v1/graph/query` | Execute raw Cypher query |
| `POST` | `/api/v1/graph/correlate` | Semantic correlation search |
| `DELETE` | `/api/v1/graph/nodes/{id}` | Delete node + relationships |

### Entity Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/entities/` | List entities (paginated) |
| `GET` | `/api/v1/entities/{id}` | Get single entity |
| `POST` | `/api/v1/entities/` | Create entity |
| `PUT` | `/api/v1/entities/{id}` | Update entity |
| `DELETE` | `/api/v1/entities/{id}` | Delete entity |
| `POST` | `/api/v1/entities/search` | Full-text search |

### Transform Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/transforms/` | List available transforms |
| `POST` | `/api/v1/transforms/execute` | Execute transform (sync/async) |
| `GET` | `/api/v1/transforms/status/{id}` | Check async task status |

### Agent Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/agent/investigate` | Launch AI investigation |
| `GET` | `/api/v1/agent/health` | Agent service health |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `ws://host:8000/ws/graph` | Real-time graph updates stream |

---

## 🤖 AI Recon Agent

The autonomous investigation agent uses **LangGraph** to orchestrate a tool-calling loop:

```
┌────────┐     ┌───────────────┐     ┌─────────────┐     ┌────────┐
│  PLAN  │────►│ EXECUTE TOOLS │────►│  CORRELATE  │────►│ REPORT │
│ (LLM)  │◄────│   (OSINT)     │◄────│  (Vector)   │     │        │
└────────┘     └───────────────┘     └─────────────┘     └────────┘
```

**Available Tools:**
- `run_dns_resolution` — DNS record discovery
- `run_whois_lookup` — Domain ownership intelligence
- `run_virustotal_lookup` — Threat reputation & IOC extraction
- `query_graph_neighbors` — Knowledge graph traversal
- `find_semantic_correlations` — Hidden link discovery via embeddings
- `get_investigation_summary` — Current state overview

---

## 🌐 3D Graph UI

The frontend renders an interactive 3D force-directed graph using **WebGL** (Three.js):

- **100,000+ nodes** rendered at 60 FPS with GPU acceleration
- **Color-coded entities** by type (Domain, IP, Email, Hash, Wallet, Person, etc.)
- **Animated particles** flowing along edges to show relationship direction
- **Click-to-inspect** any node for full metadata
- **Real-time updates** via WebSocket as the AI agent discovers entities
- **Filter panel** to toggle entity type visibility
- **AI Agent panel** to launch investigations and view reports

---

## 🔄 Transforms

| Transform | Input | Output | Description |
|-----------|-------|--------|-------------|
| `dns_resolution` | Domain | IP, Domain, Email | Resolves A, AAAA, MX, NS, TXT records |
| `whois_lookup` | Domain | Domain, Email, Person | Retrieves registration data |
| `virustotal_lookup` | Domain/IP/Hash | IP, Domain, Hash, Email | Threat intelligence & IOCs |

**Custom transforms** can be added by extending `BaseTransform`:

```python
from transforms.base import BaseTransform
from db.schemas import NodeLabel, TransformResult

class MyCustomTransform(BaseTransform):
    name = "my_transform"
    description = "Does something useful"
    input_type = NodeLabel.DOMAIN
    output_types = [NodeLabel.IP]

    async def execute(self, entity_value, parameters=None):
        # Your logic here
        return TransformResult(
            transform_name=self.name,
            status="success",
            new_nodes=[...],
            new_edges=[...],
        )
```

---

## ⚙️ Configuration

All configuration is managed via environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `MEMGRAPH_HOST` | `localhost` | Memgraph server host |
| `MEMGRAPH_PORT` | `7687` | Memgraph Bolt port |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection |
| `QDRANT_HOST` | `localhost` | Qdrant server host |
| `QDRANT_PORT` | `6333` | Qdrant HTTP port |
| `VIRUSTOTAL_API_KEY` | — | VirusTotal API key |
| `LLM_API_KEY` | — | LLM provider API key |
| `LLM_BASE_URL` | `http://localhost:11434/v1` | LLM endpoint |
| `LLM_MODEL` | `qwen2.5:72b` | Model identifier |

---

## 💻 Development

### Local Development (without Docker)

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Celery Worker
celery -A workers.celery_app worker --loglevel=info

# Agent
cd agent
pip install -r requirements.txt
python recon_agent.py

# Frontend
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
cd backend
pytest tests/ -v --cov=.

cd frontend
npm run lint
```

### Makefile Commands

```bash
make up          # Start all services
make down        # Stop all services
make build       # Rebuild containers
make logs        # Tail all logs
make clean       # Full cleanup (volumes + images)
make restart     # Restart all
```

---

## 🗺 Roadmap

- [ ] Shodan / Censys integration transforms
- [ ] Blockchain explorer transforms (Etherscan, Blockchain.com)
- [ ] Dark web forum crawler (Tor-based)
- [ ] Multi-user authentication (JWT + RBAC)
- [ ] Graph export (GraphML, GEXF, JSON)
- [ ] Timeline view for temporal analysis
- [ ] Collaborative investigation sessions
- [ ] Plugin marketplace for community transforms
- [ ] Kubernetes Helm chart for cloud deployment
- [ ] Mobile-responsive graph viewer

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'feat: add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Commit Convention

```
feat:     New feature
fix:      Bug fix
docs:     Documentation update
refactor: Code refactoring
test:     Adding tests
chore:    Maintenance tasks
```

---

## 📜 License

This project is licensed under the **Sayanox License v1.1**.

See the [LICENSE](./LICENSE) file for full terms and conditions.

---

## 👤 Author

<div align="center">

**Sayan**

[![GitHub](https://img.shields.io/badge/GitHub-sayan9168-181717?style=for-the-badge&logo=github)](https://github.com/sayan9168)
[![Twitter](https://img.shields.io/badge/Twitter-notfound__sayan-1DA1F2?style=for-the-badge&logo=twitter)](https://twitter.com/notfound_sayan)
[![Instagram](https://img.shields.io/badge/Instagram-_sayyyyan-E4405F?style=for-the-badge&logo=instagram)](https://instagram.com/_sayyyyan)
[![Gmail](https://img.shields.io/badge/Gmail-sm6881164@gmail.com-D14836?style=for-the-badge&logo=gmail)](mailto:sm6881164@gmail.com)

</div>

---

<div align="center">

**⚡ Built with passion for the OSINT community ⚡**

*If this project helps your research, please consider giving it a ⭐ on GitHub.*

</div>
```

---

