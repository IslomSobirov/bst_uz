# API Tests

Comprehensive API tests for the Boosty Uzbekistan Django REST Framework API.

## Test Structure

- `conftest.py` - Pytest fixtures for test data setup
- `test_auth.py` - Authentication endpoints (register, login)
- `test_profiles.py` - User profile endpoints (CRUD, subscribe, unsubscribe, creators list)
- `test_posts.py` - Post endpoints (CRUD, publish, archive, feed, my_posts)
- `test_categories.py` - Category endpoints (CRUD)
- `test_comments.py` - Comment endpoints (CRUD)
- `test_subscriptions.py` - Subscription endpoints (CRUD)

## Running Tests

### Run all tests:
```bash
pytest
```

### Run with coverage:
```bash
pytest --cov=boosty_app --cov-report=html
```

### Run specific test file:
```bash
pytest tests/test_auth.py
```

### Run specific test:
```bash
pytest tests/test_auth.py::TestAuthRegistration::test_register_success
```

### Run tests in Docker (recommended):

**Using Makefile (simplest):**
```bash
make test                    # Run all tests
make test-verbose           # Run with verbose output
make test-coverage          # Run with coverage report
make test-file FILE=tests/test_auth.py
make test-specific TEST=tests/test_auth.py::TestAuthRegistration::test_register_success

# Run tests for specific features
make test-auth
make test-profiles
make test-posts
make help                   # Show all available commands
```

**Or using the helper script:**
```bash
./run_tests.sh
```

**Or directly with docker-compose:**
```bash
docker-compose exec backend python -m pytest
```

### Run tests with verbose output:
```bash
pytest -v
```

## Test Coverage

Tests cover:
- ✅ Positive cases (successful operations)
- ✅ Negative cases (errors, validation failures)
- ✅ Authentication and authorization
- ✅ CRUD operations
- ✅ Edge cases and boundary conditions

## Fixtures

Common fixtures available in `conftest.py`:
- `api_client` - Unauthenticated API client
- `user` - Regular user
- `creator` - Creator user
- `authenticated_client` - API client authenticated as regular user
- `creator_client` - API client authenticated as creator
- `category` - Test category
- `published_post` - Published post
- `draft_post` - Draft post
- `comment` - Test comment
- `subscription` - Test subscription

## Running Tests in Docker Container

### Quick Start:
```bash
# Simple way - use the helper script
./run_tests.sh

# Or directly with docker-compose
docker-compose exec backend python -m pytest
```

### Prerequisites:
1. Make sure Docker containers are running:
   ```bash
   docker-compose up -d db backend
   ```

2. The test script will auto-start containers if needed:
   ```bash
   ./run_tests.sh  # Will start containers if not running
   ```

### Common Test Commands (using Makefile):

```bash
# Run all tests
make test

# Run with verbose output
make test-verbose

# Run with coverage report (HTML output in htmlcov/)
make test-coverage

# Run specific test file
make test-file FILE=tests/test_auth.py

# Run specific test
make test-specific TEST=tests/test_auth.py::TestAuthRegistration::test_register_success

# Run only failed tests from last run
make test-failed

# Run tests for specific feature
make test-auth           # Authentication tests
make test-profiles       # Profile tests
make test-posts          # Post tests
make test-categories     # Category tests
make test-comments       # Comment tests
make test-subscriptions  # Subscription tests

# Show all available commands
make help
```

### Alternative: Direct docker-compose commands

```bash
# Run all tests
docker-compose exec backend python -m pytest

# Run with coverage
docker-compose exec backend python -m pytest --cov=boosty_app --cov-report=html

# Run specific test file
docker-compose exec backend python -m pytest tests/test_auth.py -v

# Run specific test
docker-compose exec backend python -m pytest tests/test_auth.py::TestAuthRegistration::test_register_success -v

# Run only failed tests
docker-compose exec backend python -m pytest --lf

# Run tests and stop at first failure
docker-compose exec backend python -m pytest -x
```

### Using the Helper Script:

The `run_tests.sh` script accepts all pytest arguments:

```bash
# All tests
./run_tests.sh

# Specific file
./run_tests.sh tests/test_auth.py

# With coverage
./run_tests.sh --cov=boosty_app --cov-report=html

# Verbose with specific test
./run_tests.sh tests/test_auth.py::TestAuthRegistration::test_register_success -v
```

### View Coverage Report:

After running with coverage:
```bash
# Coverage HTML report is generated in htmlcov/ directory
# Open it in your browser or view in container:
docker-compose exec backend ls -la htmlcov/
```

### Troubleshooting:

**If you get database connection errors:**
```bash
# Make sure database container is running
docker-compose up -d db

# Check database connection
docker-compose exec backend python manage.py dbshell
```

**If tests fail with import errors:**
```bash
# Rebuild the container to install dependencies
docker-compose build backend
docker-compose up -d backend
```

**If you need a fresh test database:**
```bash
# Remove the test database and re-create
docker-compose exec backend python -m pytest --create-db
```

## Notes

- Tests use pytest-django for Django integration
- Database is automatically rolled back after each test
- Tests use separate test database (configured via pytest.ini)
- All API endpoints are tested with both authenticated and unauthenticated requests
- Tests run in the same Docker container as your backend, ensuring consistent environment
