"""
FastAPI application for the RedditBot API.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Dict, List, Any

from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse

from .analyzer import summarize_posts
from .config import load_settings
from .models import HealthCheckResponse, RedditPost
from .reddit_client import fetch_posts
from .settings import Settings


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """Manage application lifecycle and validate settings on startup."""
    fastapi_app.state.start_time = datetime.now(timezone.utc)

    # Validate settings before starting the app
    try:
        settings = load_settings()
        fastapi_app.state.settings = settings
        print("✅ Settings loaded successfully")
        print(f"   - Reddit client configured for {len(settings.reddit.subreddits)} subreddits")
        print(f"   - Fetch limit: {settings.reddit.fetch.limit}")
    except Exception as e:
        print(f"❌ Failed to load settings: {e}")
        raise RuntimeError(f"Application cannot start due to invalid settings: {e}") from e

    yield
    # shutdown logic here if needed


app = FastAPI(title="RedditBot API", lifespan=lifespan)


@app.get("/posts", response_model=List[RedditPost])
def get_posts(limit: int = Query(5, ge=1, le=100)) -> List[Dict]:
    """Fetch Reddit posts from configured subreddits."""
    settings = app.state.settings
    posts_by_subreddit = fetch_posts(settings, limit=limit)
    flat_posts: List[RedditPost] = []
    for posts in posts_by_subreddit.values():
        for p in posts:
            flat_posts.append(
                RedditPost(
                    id=p["id"],
                    title=p["title"],
                    score=p["score"],
                    permalink=p["permalink"],
                )
            )
    return flat_posts


@app.get("/summary")
def get_summary(limit: int = Query(5, ge=1, le=100)) -> Dict[str, Any]:
    """Get a summary of Reddit posts from configured subreddits."""
    settings = app.state.settings
    posts = fetch_posts(settings, limit=limit)
    summary = summarize_posts(posts)
    return summary


@app.get("/")
def root():
    """Redirect root to API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/healthz", response_model=HealthCheckResponse)
def health_check() -> HealthCheckResponse:
    """Health check endpoint."""
    uptime_seconds = (datetime.now(timezone.utc) - app.state.start_time).total_seconds()
    return HealthCheckResponse(status="ok", uptime_seconds=uptime_seconds)


@app.get("/settings", response_model=Settings)
def get_settings() -> Settings:
    """Get current application settings."""
    return Settings()


@app.get("/settings/validate")
def validate_settings() -> Dict[str, Any]:
    """Validate that current settings are properly loaded and accessible."""
    try:
        settings = app.state.settings

        # Detailed validation
        validation_details = {
            "subreddits": {
                "configured": len(settings.reddit.subreddits) > 0,
                "count": len(settings.reddit.subreddits),
                "values": settings.reddit.subreddits,
                "valid": all(sub.strip() for sub in settings.reddit.subreddits)
            },
            "client_id": {
                "configured": bool(settings.reddit.client_id and settings.reddit.client_id.strip()),
                "value": (settings.reddit.client_id[:8] + "..." 
                         if settings.reddit.client_id else None),
                "valid": bool(settings.reddit.client_id and settings.reddit.client_id.strip())
            },
            "client_secret": {
                "configured": bool(settings.reddit.client_secret),
                "valid": bool(settings.reddit.client_secret)
            },
            "user_agent": {
                "configured": bool(settings.reddit.user_agent and settings.reddit.user_agent.strip()),
                "value": (settings.reddit.user_agent[:50] + "..." 
                         if len(settings.reddit.user_agent) > 50 
                         else settings.reddit.user_agent),
                "valid": bool(settings.reddit.user_agent and settings.reddit.user_agent.strip())
            },
            "fetch_limit": {
                "configured": True,
                "value": settings.reddit.fetch.limit,
                "valid": 0 < settings.reddit.fetch.limit <= 100
            }
        }

        # Check if all required fields are valid
        all_valid = all(
            validation_details["subreddits"]["valid"],
            validation_details["client_id"]["valid"],
            validation_details["client_secret"]["valid"],
            validation_details["user_agent"]["valid"],
            validation_details["fetch_limit"]["valid"]
        )

        return {
            "status": "valid" if all_valid else "invalid",
            "message": ("Settings are properly loaded and accessible" if all_valid 
                       else "Some settings are invalid or missing"),
            "validation_details": validation_details,
            "summary": {
                "total_fields": 5,
                "valid_fields": sum(1 for field in validation_details.values() if field["valid"]),
                "missing_fields": [name for name, details in validation_details.items() 
                                 if not details["valid"]]
            }
        }
    except (ValueError, RuntimeError) as e:
        return {
            "status": "error",
            "message": f"Settings validation failed: {str(e)}",
            "error": str(e)
        }