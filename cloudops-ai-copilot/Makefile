# ============================================================
# CloudOps AI Copilot — Makefile
# ============================================================

.PHONY: help dev dev-backend dev-frontend dev-db test lint build deploy clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ----- Local Development -----

dev: ## Start full stack (backend + frontend + database)
	docker compose -f docker/docker-compose.yml up --build

dev-backend: ## Start backend only
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start frontend only
	cd frontend && npm run dev

dev-db: ## Start database only
	docker compose -f docker/docker-compose.yml up db -d

# ----- Testing -----

test: ## Run all tests
	cd backend && python -m pytest tests/ -v --cov=app --cov-report=term-missing

test-watch: ## Run tests in watch mode
	cd backend && python -m pytest tests/ -v --watch

# ----- Linting -----

lint: ## Run all linters
	cd backend && ruff check app/ && ruff format --check app/
	cd frontend && npx eslint src/ --ext .ts,.tsx

lint-fix: ## Fix lint issues
	cd backend && ruff check app/ --fix && ruff format app/
	cd frontend && npx eslint src/ --ext .ts,.tsx --fix

# ----- Build -----

build: ## Build Docker images
	docker compose -f docker/docker-compose.yml build

build-frontend: ## Build frontend for production
	cd frontend && npm run build

# ----- Database -----

db-migrate: ## Run database migrations
	cd backend && alembic upgrade head

db-rollback: ## Rollback last migration
	cd backend && alembic downgrade -1

db-revision: ## Create a new migration (usage: make db-revision msg="add users table")
	cd backend && alembic revision --autogenerate -m "$(msg)"

# ----- Deployment -----

deploy-plan: ## Terraform plan (dev)
	cd terraform/environments/dev && terraform plan

deploy-apply: ## Terraform apply (dev)
	cd terraform/environments/dev && terraform apply

# ----- Cleanup -----

clean: ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .next -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/dist backend/build frontend/out
