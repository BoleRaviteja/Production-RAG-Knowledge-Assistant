.PHONY: up down test lint tf-validate helm-lint
up:        ; cp -n .env.example .env; docker compose up --build -d
down:      ; docker compose down
test:      ; docker compose up -d db && pip install -q -r requirements-dev.txt && pytest -v
lint:      ; ruff check app tests
tf-validate: ; cd terraform && terraform init -backend=false && terraform validate
helm-lint: ; helm lint helm/rag-assistant
