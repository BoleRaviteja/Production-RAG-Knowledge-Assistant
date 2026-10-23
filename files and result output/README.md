# Demo Files and Results

This folder contains the fictional Acme Tech sample documents and screenshots from the RAG demo.

## Run the Project on Windows

Open PowerShell in the project root (`D:\rag-assistant\rag-assistant`). The `.env` file should already exist. If it does not, create it from the example:

```powershell
Copy-Item .env.example .env
```

Build and start the API and pgvector database:

```powershell
docker compose up --build
```

Wait until both containers are healthy, then open [http://localhost:8000](http://localhost:8000). Swagger API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

The Makefile has an `up` target for Bash/WSL (`make up`). On Windows PowerShell, use `docker compose up --build` directly because the Makefile recipe uses the Bash `cp -n` command.

## Make Commands

Run these from the project root in Bash/WSL. Docker is required for the app and database commands; Terraform and Helm are required for their respective validation commands.

| Command | What it does |
|---|---|
| `make up` | Creates `.env` from `.env.example` if needed, then builds and starts the stack in the background. |
| `make down` | Stops the stack and preserves the database volume. |
| `make test` | Starts the database, installs development requirements, and runs pytest. |
| `make lint` | Runs Ruff on `app` and `tests`. |
| `make tf-validate` | Initializes Terraform without a backend and validates the configuration. |
| `make helm-lint` | Lints the Helm chart. |

For PowerShell, use `docker compose up --build` and `docker compose down` for app startup and shutdown. Tests use a separate `rag_test` database because the API test fixture truncates its tables. Create it once in the running PostgreSQL container (skip this command if it already exists), then run pytest against it:

```powershell
docker compose up -d db
docker exec rag-assistant-db-1 psql -U rag -d postgres -c "CREATE DATABASE rag_test OWNER rag;"
$env:DATABASE_URL = "postgresql+psycopg://rag:rag@localhost:5432/rag_test"
D:/PYTHON/python.exe -m pytest -v
```

## Try the Demo

1. Register a user and log in. The first registered user becomes an admin.
2. Upload these files one at a time using **Choose File** and **Upload**:
   - `leave-policy.pdf`
   - `deployment-runbook.txt`
   - `onboarding-guide.txt`
3. Wait for each file's status to show `ready`.
4. Ask a question and inspect the answer and its source list.

Questions tested with these files:

| Question | Expected source |
|---|---|
| How many casual leaves do I get in a year? | `leave-policy.pdf`, page 1 |
| How long is maternity leave? | `leave-policy.pdf`, page 2 |
| How do I apply for work from home? | `leave-policy.pdf`, page 3 |
| What is the rollback process if production fails? | `deployment-runbook.txt` |
| Quasar luminosity redshift threshold 731 | No-match response in the local demo configuration |

`View_outputs.png` shows example answer and source output. `view_inputs.png` and `login.png` are local screenshots and are excluded from this repository because they show the signed-in email.

## Embedding Note

The default local demo uses fake hashing embeddings and a mock LLM, so it runs without API keys. Fake embeddings are not semantic: shared words or hash collisions may retrieve unrelated passages. The local `.env` uses `MIN_SIMILARITY=0.01` to reject zero-score results; this is a demo workaround, not a production setting. Real semantic retrieval requires real embeddings and API credentials.

## Stop the Project

To stop and remove the containers while preserving the uploaded documents in the database volume:

```powershell
docker compose down
```

Do not add `-v` unless you intend to delete the database volume and all uploaded documents.
