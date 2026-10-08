# Autonomous Coding Agent Studio

An enterprise-grade, full-stack autonomous coding pipeline and visual developer workspace. The platform pairs a **LangGraph-driven agentic state machine** with an isolated **Docker sandbox**, PostgreSQL state persistence, an AST visualizer powered by **React Flow**, and a **Deep Berry & Vanilla Cloud** interface.

---

## Architecture Overview

```
                                      +------------------------------------+
                                      |         React 18 + Vite SPA        |
                                      | (Tailwind CSS, React Flow, Axios)  |
                                      +-----------------+------------------+
                                                        |
                                                  JWT REST API
                                                        |
                                                        v
                                      +------------------------------------+
                                      |          FastAPI Gateway           |
                                      |      (Pydantic, SQLAlchemy 2)      |
                                      +--------+------------------+--------+
                                               |                  |
                       +-----------------------+                  +-----------------------+
                       v                                                                  v
+-----------------------------+                                            +-----------------------------+
|    PostgreSQL Relational    |                                            |    LangGraph Orchestrator   |
|   (JSONB AST, Chats, Users) |                                            |   (Coder, Tester, Repair)   |
+-----------------------------+                                            +--------------+--------------+
                                                                                          |
                                                                             Subprocess / Docker IPC
                                                                                          |
                                                                                          v
                                                                           +-----------------------------+
                                                                           |    Isolated Python Runner   |
                                                                           | (Resource Caps, Zero-Trust) |
                                                                           +-----------------------------+

```

---

## Core Features

* **Agentic Generation & Self-Correction:** Multi-step cyclical code repair powered by LangGraph state graphs that generate, test, inspect errors (`stdout`/`stderr`), and iteratively patch software solutions.
* **AST Flow Graph Extraction:** Python Abstract Syntax Tree parser converting code control flow (`FunctionDef`, `If`, `For`, `Return`, `Raise`) into hierarchical directed graphs.
* **Interactive Visual Canvas:** Custom React Flow workspace rendering interactive, zoomable, draggable node graphs of generated scripts with built-in minimap and controls.
* **Isolated Sandbox Execution:** Security-conscious code execution environment with hard memory ceilings, execution timeouts, and sandboxed runtimes.
* **Relational Session & Graph Storage:** PostgreSQL backend utilizing native `JSONB` columns to store full visual graph nodes, edge structures, execution outputs, and token/cost telemetry.
* **Dual-Tone Visual Design:** Split-panel authentication interface and dual-tone workspace combining deep berry surfaces (`#24071B`) with warm vanilla cloud parchment (`#FAF6F0`).

---

## Tech Stack

### Backend

* **Framework:** FastAPI (Python 3.11+)
* **Agent Orchestration:** LangGraph, LangChain Core
* **Database & ORM:** PostgreSQL 16+, SQLAlchemy 2.0, Alembic
* **Driver:** `psycopg2-binary`
* **Authentication:** Native `bcrypt` password hashing, python-jose (JWT)
* **Validation:** Pydantic v2 (`pydantic[email]`)
* **Testing:** `pytest`, HTTPX

### Frontend

* **Framework:** React 19 / Vite 8
* **Language:** TypeScript (`verbatimModuleSyntax` compliant)
* **Styling:** Tailwind CSS v4 (`@tailwindcss/vite`)
* **Graph Engine:** `@xyflow/react` (React Flow)
* **Icons:** `lucide-react`
* **HTTP Client:** Axios with auto-bearer token interceptors

---

## Repository Structure

```text
.
├── alembic/                       # Database migration versions and environments
│   ├── versions/
│   └── env.py
├── alembic.ini                    # Alembic migration configuration
├── docker-compose.yml             # Local multi-service infrastructure
├── Dockerfile                     # Backend container definition
├── requirements.txt               # Backend Python dependencies
├── src/
│   └── agent/
│       ├── __init__.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── auth_utils.py      # Native bcrypt hashing & JWT token generators
│       │   ├── database.py        # SQLAlchemy engine and declarative sessions
│       │   ├── main.py            # FastAPI entry point and middleware
│       │   ├── models.py          # SQLAlchemy models (User, Chat, Message)
│       │   ├── schemas.py         # Pydantic validation schemas
│       │   └── routes/
│       │       ├── __init__.py
│       │       ├── auth.py        # Sign-up, login, and identity endpoints
│       │       └── chats.py       # Thread lifecycle and agent dispatch endpoints
│       ├── core/                  # LangGraph nodes, state, and test evaluators
│       └── utils/
│           └── ast_parser.py      # Abstract syntax tree to React Flow converter
├── tests/                         # Pytest integration and route tests
│   ├── conftest.py
│   └── test_api.py
└── frontend/                      # Single-page client application
    ├── public/
    ├── src/
    │   ├── components/
    │   │   ├── AuthModal.tsx      # Split-screen Deep Berry & Vanilla auth view
    │   │   ├── ChatFeed.tsx       # Message thread, code actions, and badges
    │   │   ├── FlowVisualizerModal.tsx # React Flow AST modal canvas
    │   │   └── Sidebar.tsx        # Session manager and workspace threads
    │   ├── context/
    │   │   └── AuthContext.tsx    # JWT session provider and user state
    │   ├── lib/
    │   │   └── api.ts             # Axios instance with auth interceptors
    │   ├── types/
    │   │   └── api.ts             # TypeScript definitions for payloads & graphs
    │   ├── App.tsx                # Main dashboard state machine
    │   ├── index.css              # Custom design tokens & Tailwind setup
    │   └── main.tsx
    ├── package.json
    ├── tsconfig.json
    └── vite.config.ts             # Vite server with proxy routing

```

---

## Environment Configuration

Create a `.env` file in the project root:

```env
# Database Credentials
POSTGRES_USER=agent_admin
POSTGRES_PASSWORD=agent_secret_password
POSTGRES_DB=agent_production_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg2://agent_admin:agent_secret_password@localhost:5432/agent_production_db

# Security & Sessions
JWT_SECRET_KEY=generate_a_random_32_byte_hex_string_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# LLM Orchestrator
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

```

---

## Local Development Setup

### 1. Prerequisites

* **Python 3.11+**
* **Node.js 20+** and `npm`
* **PostgreSQL 16+** (local service or Docker)

### 2. Database Initialization

Start PostgreSQL via Docker or your local engine:

```bash
docker run --name agent_postgres -e POSTGRES_USER=agent_admin -e POSTGRES_PASSWORD=agent_secret_password -e POSTGRES_DB=agent_production_db -p 5432:5432 -d postgres:16-alpine

```

### 3. Backend Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install "pydantic[email]"

# Run database migrations
export PYTHONPATH=src            # On Windows PowerShell: $env:PYTHONPATH="src"
alembic upgrade head

# Start API server
uvicorn agent.api.main:app --reload --port 8000

```

Backend API docs will be live at `[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)`.

### 4. Frontend Setup

Open a secondary terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev

```

Open `http://localhost:5173` in your browser.

---

## Database Migrations

When altering models in `src/agent/api/models.py`:

```bash
# Generate revision script
alembic revision --autogenerate -m "Add column to messages"

# Apply pending revisions
alembic upgrade head

# Rollback one revision
alembic downgrade -1

```

---

## API Reference

### Authentication

| Method | Endpoint | Description | Auth Required |
| --- | --- | --- | --- |
| `POST` | `/api/auth/signup` | Register new user profile and issue JWT | No |
| `POST` | `/api/auth/login` | Validate credentials and issue JWT | No |
| `GET` | `/api/auth/me` | Fetch active user context | Bearer JWT |

### Workspace Management

| Method | Endpoint | Description | Auth Required |
| --- | --- | --- | --- |
| `GET` | `/api/chats/` | List all user workspaces | Bearer JWT |
| `POST` | `/api/chats/` | Initialize a new workspace thread | Bearer JWT |
| `GET` | `/api/chats/{chat_id}` | Retrieve messages and telemetry graphs | Bearer JWT |
| `PUT` | `/api/chats/{chat_id}/rename` | Rename existing workspace thread | Bearer JWT |
| `DELETE` | `/api/chats/{chat_id}` | Remove workspace and all associated messages | Bearer JWT |
| `POST` | `/api/chats/{chat_id}/messages` | Dispatch prompt to LangGraph agent | Bearer JWT |

---

## Running the Automated Test Suite

The test suite validates database models, password hashing routines, JWT validation, and chat/message route lifecycles:

```bash
# Execute full test suite
pytest -v -s tests/

```

---

## Production Deployment

### Docker Multi-Stage Deployment

The system can be deployed via `docker-compose.prod.yml`:

```bash
docker compose -f docker-compose.yml up --build -d

```

### Static Asset Build

Compile the frontend bundle for static hosting (Nginx/Cloudflare Pages/Vercel):

```bash
cd frontend
npm run build
# Production assets generated inside frontend/dist/

```

---

## License

This project is licensed under the MIT License. See the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.