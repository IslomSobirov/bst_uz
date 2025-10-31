.PHONY: help test test-verbose test-coverage test-file test-specific test-failed test-auth test-profiles test-posts test-categories test-comments test-subscriptions up down restart logs shell migrate clean pre-commit-install pre-commit-run pre-commit-update lint format

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

# Docker commands
up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

logs: ## Show logs from all services
	docker-compose logs -f

shell: ## Open shell in backend container
	docker-compose exec backend /bin/bash

# Pre-commit hooks
pre-commit-install: ## Install pre-commit hooks
	docker-compose exec backend pre-commit install

pre-commit-run: ## Run pre-commit hooks on all files
	docker-compose exec backend pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks
	docker-compose exec backend pre-commit autoupdate

lint: ## Run pylint on all Python files
	docker-compose exec backend pylint boosty_app/ boosty_project/ --load-plugins=pylint_django --django-settings-module=boosty_project.settings || true

format: ## Format code with black and isort
	docker-compose exec backend black boosty_app/ boosty_project/ --line-length=120 --skip-string-normalization
	docker-compose exec backend isort boosty_app/ boosty_project/ --profile black --line-length=120

# Test commands
test: ## Run all tests
	docker-compose exec backend python -m pytest

test-verbose: ## Run all tests with verbose output
	docker-compose exec backend python -m pytest -v

test-coverage: ## Run tests with coverage report
	docker-compose exec backend python -m pytest --cov=boosty_app --cov-report=html --cov-report=term-missing

test-file: ## Run tests from a specific file (usage: make test-file FILE=tests/test_auth.py)
	docker-compose exec backend python -m pytest $(FILE)

test-specific: ## Run a specific test (usage: make test-specific TEST=tests/test_auth.py::TestAuthRegistration::test_register_success)
	docker-compose exec backend python -m pytest $(TEST) -v

test-failed: ## Run only failed tests from last run
	docker-compose exec backend python -m pytest --lf

test-auth: ## Run authentication tests
	docker-compose exec backend python -m pytest tests/test_auth.py -v

test-profiles: ## Run profile tests
	docker-compose exec backend python -m pytest tests/test_profiles.py -v

test-posts: ## Run post tests
	docker-compose exec backend python -m pytest tests/test_posts.py -v

test-categories: ## Run category tests
	docker-compose exec backend python -m pytest tests/test_categories.py -v

test-comments: ## Run comment tests
	docker-compose exec backend python -m pytest tests/test_comments.py -v

test-subscriptions: ## Run subscription tests
	docker-compose exec backend python -m pytest tests/test_subscriptions.py -v

# Django management commands
migrate: ## Run database migrations
	docker-compose exec backend python manage.py migrate

makemigrations: ## Create new migrations
	docker-compose exec backend python manage.py makemigrations

createsuperuser: ## Create Django superuser
	docker-compose exec backend python manage.py createsuperuser

shell-django: ## Open Django shell
	docker-compose exec backend python manage.py shell

# Cleanup
clean: ## Clean test cache and coverage files
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	docker-compose exec backend rm -rf .pytest_cache htmlcov .coverage || true

clean-all: clean ## Clean all including Docker volumes
	docker-compose down -v
