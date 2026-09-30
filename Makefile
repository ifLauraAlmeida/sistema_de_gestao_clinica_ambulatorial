# Comandos do projeto. Todos executam dentro dos containers do Docker Compose.
COMPOSE ?= docker compose
BACKEND_RUN = $(COMPOSE) run --rm -T backend
FRONTEND_RUN = $(COMPOSE) run --rm -T --no-deps frontend

.PHONY: up down logs migrate makemigrations createsuperuser seed seed-history \
	test test-backend test-frontend lint lint-backend lint-frontend format build-frontend check

up: ## Sobe postgres, redis, backend e frontend
	$(COMPOSE) up --build

down: ## Para os serviços (os dados do postgres são mantidos no volume)
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f backend frontend

migrate:
	$(BACKEND_RUN) python manage.py migrate

makemigrations:
	$(BACKEND_RUN) python manage.py makemigrations

createsuperuser: ## Cria usuário gestor com acesso ao /admin
	$(COMPOSE) run --rm backend python manage.py createsuperuser

seed: migrate ## Cria dados FICTÍCIOS (exige DEMO_USERS_PASSWORD no ambiente ou no .env)
	$(BACKEND_RUN) python manage.py seed_demo_data

seed-history: seed ## Dados fictícios + histórico de 4 meses e agenda das próximas 2 semanas
	$(BACKEND_RUN) python manage.py seed_demo_history

test: test-backend test-frontend ## Executa todos os testes

test-backend:
	$(BACKEND_RUN) pytest

test-frontend:
	$(FRONTEND_RUN) npm test

lint: lint-backend lint-frontend ## Lint, formatação e tipagem

lint-backend:
	$(BACKEND_RUN) sh -c "ruff check . && ruff format --check . && mypy . && python manage.py makemigrations --check --dry-run"

lint-frontend:
	$(FRONTEND_RUN) sh -c "npm run lint && npm run format:check && npm run typecheck"

format:
	$(BACKEND_RUN) sh -c "ruff check --fix . && ruff format ."
	$(FRONTEND_RUN) npm run format

build-frontend:
	$(FRONTEND_RUN) npm run build

check: lint test build-frontend ## Tudo o que precisa passar antes de um commit
