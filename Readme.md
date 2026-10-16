# Autonomous Coding Agent Studio

A full-stack workspace for generating, checking, and running Python code with an LLM. It includes a FastAPI service, a React frontend, PostgreSQL persistence, a LangGraph workflow, a Docker-based execution sandbox, and an AST flow visualizer.

> **Security note:** Generated code is untrusted. The AST checks are one layer of defense, not a complete security boundary. Execution depends on Docker isolation. The deployed backend receives access to the Docker daemon through its socket; expose the application only behind appropriate network controls and TLS, and do not treat the backend host as isolated from a backend compromise.

## What it does

- Accepts coding prompts through an authenticated web workspace.
- Uses a LangGraph pipeline to screen input, plan, generate code, inspect generated code, request approval for selected tasks, execute code, retry failures, and format the result.
- Runs generated Python in a separate Docker container with configurable memory, CPU, process, timeout, network, and filesystem restrictions.
- Optionally uses a project directory as context when a local path is supplied to the API.
- Stores users, chat history, approvals, execution output, optimization metrics, and flow-graph data in PostgreSQL.
- Converts Python source into an AST-derived graph for display in the frontend.
- Reports token and estimated-cost usage and attempts a separate code optimization pass after successful execution.

## Architecture

```text
Browser (React/Vite or Nginx)
          |
          | /api/*
          v
FastAPI API ---- PostgreSQL
    |
    +---- LangGraph workflow ---- Groq-compatible LLM API
    |
    +---- Docker daemon ---- ephemeral Python sandbox
```

The staging Nginx container serves the frontend and proxies `/api/` requests to the backend. The backend's readiness endpoint checks PostgreSQL and Docker connectivity.

## Technology

- **Backend:** Python 3.11+, FastAPI, Pydantic, SQLAlchemy, Alembic
- **Agent:** LangGraph, LangChain Core, OpenAI-compatible client configured for Groq
- **Database:** PostgreSQL 16+
- **Sandbox:** Docker SDK and `Dockerfile.sandbox`
- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS, React Flow
- **Tests and tooling:** pytest, pytest-asyncio, Ruff, ESLint, TypeScript

The current LLM client connects to Groq and requires `GROQ_API_KEY`. Set `LLM_MODEL` to a model identifier available to your Groq account. Although an `OPENAI_API_KEY` setting exists, the current client does not use it as a provider.

## Repository layout

```text
.
├── alembic/                 # Database migration revisions
├── Dockerfile.backend       # API container image
├── Dockerfile.sandbox       # Restricted code-execution image
├── docker-compose.yml       # Local PostgreSQL service
├── docker-compose.staging.yml # PostgreSQL, API, and frontend deployment
├── scripts/
│   ├── entrypoint.sh        # Applies migrations and starts Uvicorn
│   └── inspect_db.py        # Database inspection helper
├── src/agent/
│   ├── api/                 # FastAPI routes, auth, schemas, and database
│   ├── brain/               # LLM client, planner, and code generation
│   ├── context/             # Project file ingestion and context building
│   ├── guardrails/          # Input, AST, and output checks
│   ├── orchestrator/        # LangGraph state, nodes, and workflow
│   ├── sandbox/             # Docker execution and resource limits
│   └── visualization/      # Python AST graph generation
├── tests/                   # API, orchestration, guardrail, sandbox, and unit tests
└── frontend/                # React application and Nginx configuration
```

## Configuration

Copy the example file and replace every placeholder with a value appropriate to your environment:

```powershell
Copy-Item .env.example .env
```

At minimum, configure:

| Variable | Purpose |
| --- | --- |
| `GROQ_API_KEY` | Required key for LLM requests. |
| `LLM_MODEL` | Model identifier supported by Groq. |
| `JWT_SECRET_KEY` | Secret used to sign access tokens. Use a unique, random value of at least 32 characters. |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Local PostgreSQL credentials and database name. |
| `DATABASE_URL` | Optional explicit SQLAlchemy URL; otherwise composed from the PostgreSQL variables. |
| `ALLOWED_ORIGINS` | Comma-separated allowed browser origins. |
| `SANDBOX_*` | Optional sandbox image and execution resource limits. |

Generate a JWT secret in PowerShell with:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Do not use the example JWT value, local Compose credentials, or any sample key in a public or production deployment. Keep `.env` files out of source control.

## Local development

### Prerequisites

- Python 3.11+
- Node.js 20+ and npm
- Docker Desktop or another Docker daemon, running in Linux-container mode
- A Groq API key and a model identifier enabled for that account

### Start PostgreSQL and build the sandbox image

From the repository root:

```powershell
docker compose up -d postgres
docker build -f Dockerfile.sandbox -t agent-sandbox .
```

The sandbox image must be available to the Docker daemon used by the backend. The staging Compose configuration mounts the host Docker socket; building the image on a different daemon will not make it available to the deployed backend.

### Start the backend

After creating and editing `.env` as described above:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

$env:PYTHONPATH = "src"
alembic upgrade head
uvicorn agent.api.main:app --reload --port 8000
```

API documentation is available at `http://127.0.0.1:8000/docs`. Liveness is reported at `/api/health`; readiness is reported at `/api/health/ready` and requires database and Docker connectivity.

### Start the frontend

In another terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open the URL printed by Vite (normally `http://localhost:5173`). The Vite development server proxies `/api` requests to `http://127.0.0.1:8000`.

## Agent workflow

The graph in `src/agent/orchestrator/graph.py` processes a request through the following stages:

1. Check the prompt with the input guard.
2. Plan the task and identify work that requires approval or is not feasible in the sandbox.
3. Generate Python, optionally using supplied project context.
4. Inspect generated code with the AST safety checker.
5. Pause for approval when required.
6. Run approved code in the Docker sandbox.
7. Ask the model to repair execution failures within the configured retry limit, rechecking repaired code before execution.
8. On success, request an optimization pass and collect line/AST metrics.
9. Format successful output and apply the output redactor.

The sandbox defaults are defined in `src/agent/sandbox/resource_limits.py`; most can be overridden through the `SANDBOX_*` settings. Actual isolation also depends on the host's Docker configuration.

## API overview

All endpoints except signup, login, health, and flow-graph generation require a bearer access token.

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/auth/signup` | Create an account and receive an access token. |
| `POST` | `/api/auth/login` | Authenticate and receive an access token. |
| `GET` | `/api/auth/me` | Return the authenticated user's profile. |
| `GET` | `/api/chats/` | List the current user's chats. |
| `POST` | `/api/chats/` | Create a chat. |
| `GET` | `/api/chats/{chat_id}` | Read chat details and message history. |
| `PUT` | `/api/chats/{chat_id}/rename` | Rename a chat. |
| `DELETE` | `/api/chats/{chat_id}` | Delete a chat and its messages. |
| `POST` | `/api/chats/{chat_id}/messages` | Submit a prompt and run the agent workflow. |
| `POST` | `/api/chats/{chat_id}/approvals/{approval_id}?action=approve` | Approve a pending operation. Use `action=reject` to reject it. |
| `POST` | `/api/flow-graph` | Generate an AST flow graph from Python source. |
| `GET` | `/api/health` | Liveness probe. |
| `GET` | `/api/health/ready` | Readiness probe for PostgreSQL and Docker. |

## Current limitations

- **Project context paths are not restricted to a configured workspace root.** The API accepts `project_path` from the request and the backend reads files under that path before sending selected context to the configured LLM provider. Do not enable this for untrusted callers until paths are restricted to explicitly authorized project directories.
- **Human approval is not fully wired to the frontend.** The API creates pending approval records and has an approval-resolution route, but message responses do not include the approval ID and there is no endpoint to list pending approvals.
- **The flow-graph endpoint is unauthenticated and has no request-size limit for source code.** Add authentication, input limits, and rate limiting before exposing it to untrusted traffic.

## Tests and quality checks

The test suite includes API, LLM/client, context, guardrail, orchestration, sandbox, and setup tests. API tests need a dedicated PostgreSQL database that has been migrated. The shared test fixture refuses to run unless the selected database name contains `test` or `ci` and the `public.users` table exists.

Start the local database, then create a dedicated test database once:

```powershell
docker compose exec -T postgres psql -U agent_admin -d postgres -c "CREATE DATABASE agent_test_db;"
```

Set the test connection and apply migrations to that database before running pytest:

```powershell
$env:TEST_DATABASE_URL = "postgresql+psycopg2://agent_admin:agent_secret_password@localhost:5432/agent_test_db"
$env:DATABASE_URL = $env:TEST_DATABASE_URL
$env:PYTHONPATH = "src"
alembic upgrade head
pytest tests/ -v
```

The local Compose credentials above are for local development only. Sandbox tests additionally need Docker and the `agent-sandbox` image; they may skip when Docker is unavailable.

Frontend checks:

```powershell
cd frontend
npm run lint
npm run build
```

## AWS EC2 deployment

The included staging stack is Docker Compose-based and can be run on a Linux EC2 instance with Docker Engine and the Compose v2 plugin installed. The instructions below assume the repository and deployment files are present on the instance.

1. Launch a Linux EC2 instance in a VPC and install Docker Engine plus the Docker Compose v2 plugin using the official instructions for the selected operating system. Assign an Elastic IP if you need a stable public address, then point your DNS record at that address.
2. Configure the instance security group to allow SSH only from your administrator IP. Allow inbound HTTP (`80`) for the application, and HTTPS (`443`) if TLS is terminated on the instance or by a fronting load balancer. Do not expose PostgreSQL (`5432`) or the backend (`8000`) directly to the internet.
3. Connect to the instance using your EC2 key pair. Keep the private key on your local machine; never add it to the repository, an image, or the instance. Clone or update the project on the instance, then follow the Compose deployment steps below.
4. Set `ALLOWED_ORIGINS` to the exact public browser origin, including the scheme and hostname (for example, `https://agent.example.com` once HTTPS is configured). Do not use `*` for an authenticated deployment.
5. Put TLS in front of the current HTTP-only frontend service before making the application publicly accessible. The security group and instance firewall should expose only the required web ports.

The Compose stack stores PostgreSQL data in a Docker volume on the EC2 host. That volume is not a backup and will not protect against instance or volume loss. Configure regular database backups and test restoration. The stack is not configured for AWS RDS, ECS, or a managed load balancer out of the box.

## Docker Compose deployment

The `docker-compose.staging.yml` file starts PostgreSQL, the API, and the Nginx frontend. The frontend is published on host port `80`; the API and database are internal to the Compose network. On EC2, run these commands from the repository directory on the EC2 host.

1. Create a separate staging environment file and set real values. Do not commit it:

   ```powershell
   Copy-Item .env.example .env.staging
   ```

   Set at least `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `JWT_SECRET_KEY`, `GROQ_API_KEY`, `LLM_MODEL`, and `ALLOWED_ORIGINS`. Set `ALLOWED_ORIGINS` to the exact browser origin(s) serving the frontend. Use a unique, random JWT secret of at least 32 characters.

2. Build the sandbox image on the same Docker host/daemon that will run the backend:

   ```powershell
   docker build -f Dockerfile.sandbox -t agent-sandbox .
   ```

3. Build and start the staging stack:

   ```powershell
   docker compose --env-file .env.staging -f docker-compose.staging.yml up --build -d
   ```

4. Check service status and logs:

   ```powershell
   docker compose --env-file .env.staging -f docker-compose.staging.yml ps
   docker compose --env-file .env.staging -f docker-compose.staging.yml logs --tail 100 backend frontend
   ```

   Once healthy, the application is served at `http://<your-host>/`. Confirm the backend readiness endpoint through the frontend proxy at `http://<your-host>/api/health/ready`.

The staging configuration currently publishes plain HTTP on port 80. Put it behind a TLS-terminating reverse proxy or load balancer before exposing it to the public internet. Protect the Docker host and Docker socket, use strong unique database credentials, and arrange database backups and operational monitoring. The named `postgres_staging_data` volume provides persistence, not backups.

## License

This project is licensed under the MIT License.
