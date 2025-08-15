# RedditBot

A Reddit bot for fetching and analyzing posts with a clean, typed configuration layer and fail-fast validation.

## Features

- **Clean Configuration**: Typed settings with pydantic-settings v2
- **12-Factor App**: Environment variables override .env files
- **Fail-Fast Validation**: App crashes on startup if required settings are missing
- **Dependency Injection**: FastAPI routes use injected settings for easy testing
- **Matrix Testing**: CI runs on Python 3.10, 3.11, and 3.12

## Configuration & Environment Variables

### Environment Precedence (Highest to Lowest)

1. **Environment Variables** (highest priority)
2. **`.env` file** (loaded automatically)
3. **Default values** (hardcoded in Settings class)

### Required Environment Variables

```bash
# Reddit API Credentials (REQUIRED)
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
REDDIT_USER_AGENT=RedditBot/1.0 (by /u/your_username)
```

### Optional Environment Variables

```bash
# Reddit Configuration (OPTIONAL - has defaults)
REDDIT_SUBREDDITS=python,programming,learnpython
REDDIT_DEFAULT_LIMIT=10
```

### Setup

1. **Copy the example file**: `cp env.example .env`
2. **Fill in your values**: Edit `.env` with your Reddit API credentials
3. **Never commit `.env`**: It's already in `.gitignore`

## Local Development

### Environment Setup

```bash
# Create conda environment
conda env create -f environment.yml
conda activate redditbot

# Install pre-commit hooks
pre-commit install
pre-commit run -a
```

### Running the Application

```bash
# Install dependencies
pip install -e .

# Run the FastAPI server
uvicorn src.redditbot.api:app --reload
```

### Code Quality

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Lint
pylint $(git ls-files '*.py')

# Tests + coverage
pytest --cov=src --cov-report=term-missing
```

## API Endpoints

- `GET /` - Redirects to API documentation
- `GET /posts` - Fetch Reddit posts from configured subreddits
- `GET /summary` - Get summary of posts
- `GET /healthz` - Health check
- `GET /settings` - View current settings
- `GET /settings/validate` - Validate settings

## CI/CD

- **`.github/workflows/ci.yml`** runs lint and tests across Python matrix
- **Coverage** uploaded to Codecov
- **Pre-commit hooks** run locally (not in CI)

## Architecture

### Settings Management

- **`src/redditbot/settings.py`**: Pydantic Settings class with environment variable support
- **`get_settings()`**: Cached singleton accessor function
- **Fail-fast validation**: App crashes on startup if required settings missing

### Dependency Injection

- **FastAPI routes** use `Depends(get_app_settings)` for clean testing
- **Settings cached** in app state during startup
- **No direct config file reading** in routes

## Notes

- **12-Factor App**: Secrets and deploy-specific config in environment, not hardcoded
- **Fail-Fast**: Better to crash on boot than at 3:00 AM
- **Type Safety**: Full Pydantic validation with proper error messages
- **Environment Precedence**: Clear hierarchy for configuration values
