#!/bin/bash
# Script to run tests inside Docker container

set -e

echo "🧪 Running API tests in Docker container..."

# Check if backend container is running
if ! docker-compose ps backend | grep -q "Up"; then
    echo "❌ Backend container is not running. Starting services..."
    docker-compose up -d db backend
    echo "⏳ Waiting for services to be ready..."
    sleep 5
fi

# Run tests inside the backend container
# Pass all arguments to pytest

# Check if pytest is installed, if not, install it
if ! docker-compose exec backend python -m pytest --version > /dev/null 2>&1; then
    echo "⚠️  pytest not found. Installing test dependencies..."
    docker-compose exec backend pip install -q pytest pytest-django pytest-cov pytest-factoryboy factory-boy
    echo "✅ Test dependencies installed"
fi

# Run tests using python -m pytest (works even if pytest executable isn't in PATH)
docker-compose exec backend python -m pytest "$@"

