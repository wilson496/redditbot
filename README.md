
# RedditBot

An intelligent Reddit monitoring and analytics bot.

## Features
- Fetch posts from multiple subreddits
- Summarize top posts
- REST API with FastAPI
- Dockerized for easy deployment

## Quickstart

### 1) Create a Reddit app
Go to https://www.reddit.com/prefs/apps and create a script app. Copy the client ID and secret.

### 2) Configure credentials
Copy `.env.example` to `.env` and fill in your values.
You can also adjust subreddits and defaults in `config/config.yaml`.

### 3) Run it
```bash
# Local
pip install -r requirements.txt
python src/main.py

# Docker
docker-compose up --build
```

### 4) Try the API
- `GET http://localhost:8000/posts?limit=5`
- `GET http://localhost:8000/summary?limit=5`

## Notes
- Read-only by default. No posting or voting is performed.
- Safe to run locally without elevated permissions.
