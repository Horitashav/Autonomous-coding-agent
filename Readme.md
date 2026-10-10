# Autonomous Coding Agent Studio

An enterprise-grade, full-stack autonomous coding pipeline and visual developer workspace. The platform pairs a **LangGraph state machine** featuring automated cyclical self-healing and standard-library code optimization with an isolated **Docker sandbox**, multi-layer security guardrails, Human-in-the-Loop (HITL) authorization gates, PostgreSQL state persistence, an AST visualizer powered by **React Flow**, and a **Deep Berry & Vanilla Cloud** user interface.

---

## Architecture Overview

```
                                      +------------------------------------+
                                      |         React 19 + Vite SPA        |
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
                        +----------------------+                  +----------------------+
                        v                                                                v
+-----------------------------+                                            +-----------------------------+
|    PostgreSQL Relational    |                                            |    LangGraph Orchestrator   |
| (JSONB Flow Graphs & Tel.)  |                                            | (10-Node Cyclical Workflow) |
+-----------------------------+                                            +--------------+--------------+
                                                                                          |
                                 +--------------------------------------------------------+
                                 |
                                 v
   [Input Guard] -> [Planner] -> [HITL Gate] -> [Code Generator] -> [AST Safety Check]
                                                                            |
                                                                   [Docker Sandbox]
                                                                     /           \
                                                              (Success)        (Error)
                                                                 /                 \
                                              [Optimizer Node]              [Repair Node]
                                                     |                              |
                                              [Format Output]               (Max Retries: 3)
                                                     |                              |
                                                   [END]                            v
                                                                             [Format Failure]

```

---

## Core Features

* **Cyclical Self-Healing Workflow:** A multi-step LangGraph state machine that generates, sandbox-tests, inspects runtime diagnostics (`stdout`/`stderr`), and iteratively patches execution errors across up to 3 repair cycles.


* **Idiomatic Optimization & Telemetry Engine:** An automated refactoring node that transforms verbose imperative loops into concise, idiomatic Python standard library constructs (`collections`, `itertools`, `functools`, `pathlib`). Generates live AST node count and lines-of-code (LOC) reduction metrics exposed via an interactive "Show Baseline" vs. "Show Optimized" toggle.
* **Defense-in-Depth Security Guardrails:**
* *Input Guard:* Regex-based injection barrier detecting prompt overrides, role hijacking, and delimiters.


* *AST Static Safety Scanner:* Python Abstract Syntax Tree analysis blocking malicious imports (`os`, `subprocess`, `socket`, `requests`, `shutil`) and dangerous primitives (`eval`, `exec`, `__import__`) prior to execution.


* *Output Guard:* Post-processing redaction engine removing leaked PII (emails, phone numbers, SSNs, API tokens, IP addresses).




* **Human-in-the-Loop (HITL) Authorization:** Safety checkpoint intercepting destructive, file-modifying, or complex tasks for explicit user confirmation before executing inside the runtime container.


* **Ephemeral Docker Sandbox Execution:** Hardware-enforced isolation running untrusted code inside a non-root `python:3.11-slim` container configured with cgroup boundaries (512MB RAM, 1 CPU core, 64 PID cap, `network_mode="none"`, read-only root with 64MB `/tmp` tmpfs).


* **Multi-File Project Context Ingestion:** Token-budgeted file ingester and context builder leveraging `tiktoken` to scan project repositories, prune build artifacts, rank relevant source files, and inject multi-file context into generation prompts.


* **AST Flow Graph Extraction & Visual Canvas:** Dynamic AST parser compiling Python syntax trees into interactive, zoomable React Flow DAGs stored directly as queryable PostgreSQL `JSONB` structures.


* **Dual-Tone Visual Design:** Split-panel authentication interface and dual-tone workspace combining deep berry surfaces (`#24071B`) with warm vanilla cloud parchment (`#FAF6F0`).

---

## Tech Stack

### Backend

* **Framework:** FastAPI (Python 3.11+)


* **Agent Orchestration:** LangGraph, LangChain Core


* **Inference Providers:** Groq API (`langchain-groq`), OpenAI (`gpt-4o-mini`)


* **Database & Persistence:** PostgreSQL 16+, SQLAlchemy 2.0, Alembic


* **Database Driver:** `psycopg2-binary`
* **Sandbox Infrastructure:** Docker SDK for Python (`docker>=7.0.0`)


* **Token Management:** `tiktoken`

* **Observability:** LangSmith (native tracing)


* **Security & Authentication:** `passlib[bcrypt]`, `python-jose[cryptography]` (JWT)


* **Validation:** Pydantic v2 (`pydantic[email]`)


* **Testing:** `pytest`, `pytest-asyncio`, `ruff`


### Frontend

* **Framework:** React 19 / Vite SPA


* **Language:** TypeScript (`verbatimModuleSyntax` compliant)
* **Styling:** Tailwind CSS


* **Interactive Graph Canvas:** `@xyflow/react` (React Flow)


* **Icons:** `lucide-react`
* **HTTP Client:** Axios with bearer-token interceptors



---

## Repository Structure

```text
.
├── alembic/                         # Database migrations
│   ├── versions/
│   │   ├── ..._initial_schema.py
│   │   └── d772756d64b4_add_optimized_code_and_optimization_.py
│   └── env.py
├── alembic.ini                      # Alembic migration configuration
├── docker-compose.yml               # Local infrastructure (PostgreSQL)
├── Dockerfile.sandbox               # Locked-down execution container (cgroups/non-root)
├── pyproject.toml                   # Project metadata and package dependencies
├── src/
│   └── agent/
│       ├── __init__.py
│       ├── config.py                # Central single source of truth configuration
│       ├── main.py                  # Rich-formatted CLI entry point
│       ├── api/                     # Web REST API layer
│       │   ├── auth_utils.py        # bcrypt hashing and JWT encoding/decoding
│       │   ├── database.py          # SQLAlchemy PostgreSQL connection sessions
│       │   ├── main.py              # FastAPI application initialization & CORS
│       │   ├── models.py            # Database tables (User, Chat, Message)
│       │   ├── schemas.py           # Pydantic serialization models
│       │   └── routes/
│       │       ├── agent.py         # Graph execution & AST flow endpoints
│       │       ├── auth.py          # Signup, login, and /me profile routes
│       │       └── chat.py          # Chat session CRUD routes
│       ├── benchmarks/              # Performance benchmarking suite
│       │   ├── humaneval.py         # Standardized test problems
│       │   ├── reporter.py          # Markdown/terminal metrics generator
│       │   └── runner.py            # pass@1 and pass@3 test runner
│       ├── brain/                   # LLM integration & prompting
│       │   ├── code_generator.py    # Code generation and repair orchestrator
│       │   ├── llm_client.py        # OpenAI/Groq API client wrapper
│       │   ├── planner.py           # Task feasibility & complexity analyzer
│       │   └── prompts.py           # Generation, repair, and planning prompts
│       ├── context/                 # Multi-file repository ingestion
│       │   ├── context_builder.py   # Token budget manager and relevance ranker
│       │   ├── file_ingester.py     # Recursive source file crawler
│       │   └── token_counter.py     # tiktoken BPE analyzer
│       ├── guardrails/              # Security defense layers
│       │   ├── ast_checker.py       # AST node visitor blocking dangerous calls
│       │   ├── input_guard.py       # Prompt injection pattern scanner
│       │   └── output_guard.py      # Regex PII redaction engine
│       ├── hitl/                    # Human-in-the-Loop gates
│       │   └── approval.py          # Interactive confirmation routines
│       ├── orchestrator/            # State machine core
│       │   ├── graph.py             # LangGraph state machine assembly
│       │   ├── nodes.py             # 10 pipeline node implementations
│       │   └── state.py             # AgentState TypedDict schema
│       └── visualization/           # AST tree conversion
│           └── flow_analyzer.py     # Python AST to React Flow DAG parser
├── tests/                           # Test suite
│   ├── evals/
│   │   ├── adversarial_suite.py     # 20 penetration tests (injection & escape)
│   │   ├── benchmark_suite.py       # 50 deterministic verification tasks
│   │   └── conftest.py              # Shared fixtures
│   ├── test_brain.py                # LLM client & code generator unit tests
│   ├── test_guardrails.py           # AST and input guard test suite
│   ├── test_orchestrator.py         # LangGraph state and routing tests
│   ├── test_sandbox.py              # Docker sandbox resource limit tests
│   └── test_setup.py                # Baseline environment smoke tests
└── frontend/                        # React 19 Single Page Application
    ├── src/
    │   ├── components/
    │   │   ├── AuthModal.tsx        # Dual-tone authentication modal
    │   │   ├── ChatFeed.tsx         # Message feed, code toggle, and telemetry
    │   │   ├── FlowVisualizerModal.tsx # React Flow AST modal canvas
    │   │   └── Sidebar.tsx          # Workspace threads and user session manager
    │   ├── context/
    │   │   └── AuthContext.tsx      # JWT session management context
    │   ├── types/
    │   │   └── api.ts               # Shared TypeScript schemas
    │   ├── App.tsx                  # Root state container
    │   ├── index.css                # Deep Berry and Vanilla Cloud styling tokens
    │   └── main.tsx
    ├── package.json
    ├── tsconfig.json
    └── vite.config.ts

```

---

## Environment Configuration

Create a `.env` file in the project root:

```env
# ==========================================
# LLM Orchestrator
# ==========================================
GROQ_API_KEY=gsk_your_groq_api_key_here
OPENAI_API_KEY=sk-your_openai_key_here

# ==========================================
# PostgreSQL Database Configuration
# ==========================================
POSTGRES_USER=agent_admin
POSTGRES_PASSWORD=agent_secret_password
POSTGRES_DB=agent_production_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg2://agent_admin:agent_secret_password@localhost:5432/agent_production_db

# ==========================================
# Authentication & Security
# ==========================================
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET_KEY=your_generated_64_character_hex_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# ==========================================
# LangSmith Observability & Tracing (Optional)
# ==========================================
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_your_langsmith_key_here
LANGCHAIN_PROJECT=autonomous-coding-agent-studio
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com

# ==========================================
# Runtime Settings
# ==========================================
ENVIRONMENT=development
PORT=8000

```

---

## Local Development Setup

### 1. Prerequisites

* **Python 3.11+**

* **Node.js 20+** and `npm`
* **Docker Desktop** (running with Linux containers enabled)



### 2. Infrastructure Setup

Start the local PostgreSQL container:

```powershell
docker compose up -d

```

Build the isolated execution sandbox container image:

```powershell
docker build -f Dockerfile.sandbox -t agent-sandbox .

```

### 3. Backend Setup

```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install package and development dependencies
pip install -e ".[dev]"

# Set path and apply database migrations
$env:PYTHONPATH="src"
alembic upgrade head

# Start FastAPI development server
uvicorn agent.api.main:app --reload --port 8000

```

Interactive OpenAPI documentation will be accessible at `[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)`.

### 4. Frontend Setup

Open a separate terminal window:

```powershell
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev

```

Open `http://localhost:5173` in your browser.

---

## LangGraph Node Workflow

The execution graph (`src/agent/orchestrator/graph.py`) processes tasks through a cyclical pipeline:

| Step | Node Name | Operation |
| --- | --- | --- |
| **0** | `check_input` | Inspects prompt against 16 prompt injection patterns; stops malicious inputs.

 |
| **1** | `plan_task` | Analyzes task complexity, dependencies, and network requirements.

 |
| **2** | `human_approval` | Prompts user before running destructive or high-risk actions.

 |
| **3** | `generate_code` | Generates self-contained Python code, incorporating multi-file context if provided.

 |
| **4** | `check_code_safety` | Runs AST visitor to block dangerous modules and system calls.

 |
| **5** | `execute_code` | Runs code inside the isolated Docker sandbox under hardware limits.

 |
| **6** | `repair_code` | Captures tracebacks, requests LLM fixes, and reruns the safety pipeline (up to 3 retries).

 |
| **7** | `optimize_code` | Refactors successful solutions using Python standard libraries and logs AST reduction telemetry. |
| **8** | `format_output` | Redacts sensitive PII (emails, phone numbers, tokens) from execution output.

 |
| **9** | `format_failure` | Produces human-readable error summaries when repair retries are exhausted.

 |

---

## API Reference

### Authentication

| Method | Endpoint | Description | Auth Required |
| --- | --- | --- | --- |
| `POST` | `/api/auth/signup` | Create user profile and return access token

 | No |
| `POST` | `/api/auth/login` | Authenticate credentials and return access token

 | No |
| `GET` | `/api/auth/me` | Fetch active authenticated session details

 | Bearer JWT

 |

### Workspace & Agent Dispatch

| Method | Endpoint | Description | Auth Required |
| --- | --- | --- | --- |
| `GET` | `/api/chats/` | List all user workspaces

 | Bearer JWT

 |
| `POST` | `/api/chats/` | Create a new workspace thread

 | Bearer JWT

 |
| `GET` | `/api/chats/{chat_id}` | Retrieve chat history, execution outputs, and telemetry

 | Bearer JWT

 |
| `PUT` | `/api/chats/{chat_id}/rename` | Rename an existing workspace thread

 | Bearer JWT

 |
| `DELETE` | `/api/chats/{chat_id}` | Delete a workspace and its stored messages

 | Bearer JWT

 |
| `POST` | `/api/chats/{chat_id}/messages` | Submit a prompt to run through the LangGraph pipeline

 | Bearer JWT

 |
| `POST` | `/api/flow-graph` | Convert arbitrary Python code into a React Flow AST graph

 | No |

---

## Automated Evaluation & Benchmark Suite

The repository includes test suites covering unit verification, penetration defense, and runtime benchmarks:

```powershell
# Run baseline unit and smoke tests
pytest tests/test_setup.py tests/test_guardrails.py tests/test_brain.py tests/test_orchestrator.py -v

# Run the 20-case penetration testing suite
pytest tests/evals/adversarial_suite.py -v

# Run the 50-problem deterministic benchmark suite
pytest tests/evals/benchmark_suite.py -v

# Run multi-file context and HumanEval benchmark evaluations
pytest tests/test_context.py tests/test_benchmarks.py -v

```

---

## Production Deployment

### Containerized Multi-Service Deployment

Run the complete backend and database stack via Docker Compose:

```powershell
docker compose up --build -d

```

### Static Asset Build

Compile the React frontend bundle for static hosting:

```powershell
cd frontend
npm run build
# Production distribution files output to frontend/dist/

```

---

## License

This project is licensed under the MIT License.