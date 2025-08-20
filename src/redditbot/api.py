"""
FastAPI application for the RedditBot API.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Dict, List, Any

from fastapi import FastAPI, Query, Depends
from fastapi.responses import RedirectResponse

from .analyzer import summarize_posts
from .models import HealthCheckResponse, RedditPost
from .reddit_client import fetch_posts
from .settings import validate_settings_on_startup, Settings


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """Manage application lifecycle and validate settings on startup."""
    fastapi_app.state.start_time = datetime.now(timezone.utc)

    # Validate settings before starting the app
    try:
        settings = validate_settings_on_startup()
        fastapi_app.state.settings = settings
        print("✅ Application started successfully")
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        raise RuntimeError(f"Application cannot start due to invalid settings: {e}") from e

    yield
    # shutdown logic here if needed


app = FastAPI(title="RedditBot API", lifespan=lifespan)


def get_app_settings() -> Settings:
    """Dependency function to get settings for routes."""
    return app.state.settings


@app.get("/posts", response_model=List[RedditPost])
def get_posts(
    limit: int = Query(5, ge=1, le=100),
    settings: Settings = Depends(get_app_settings)
) -> List[RedditPost]:
    """Fetch Reddit posts from configured subreddits."""
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
def get_summary(
    limit: int = Query(5, ge=1, le=100),
    settings: Settings = Depends(get_app_settings)
) -> Dict[str, Any]:
    """Get a summary of Reddit posts from configured subreddits."""
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
def get_current_settings(settings: Settings = Depends(get_app_settings)) -> Settings:
    """Get current application settings."""
    return settings


@app.get("/settings/validate")
def validate_current_settings(settings: Settings = Depends(get_app_settings)) -> Dict[str, Any]:
    """Validate that current settings are properly loaded and accessible."""
    try:
        # Detailed validation
        validation_details = {
            "subreddits": {
                "configured": len(settings.reddit_subreddits) > 0,
                "count": len(settings.reddit_subreddits),
                "values": settings.reddit_subreddits,
            },
            "client_id": {
                "configured": bool(settings.reddit_client_id),
                "length": len(settings.reddit_client_id) if settings.reddit_client_id else 0,
            },
            "client_secret": {
                "configured": bool(settings.reddit_client_secret),
                "is_secret": True,
            },
            "user_agent": {
                "configured": bool(settings.reddit_user_agent),
                "value": settings.reddit_user_agent,
            },
            "default_limit": {
                "configured": True,
                "value": settings.reddit_default_limit,
                "in_range": 1 <= settings.reddit_default_limit <= 100,
            },
        }

        return {
            "valid": True,
            "message": "Settings are valid and accessible",
            "details": validation_details,
        }
    except (ValueError, AttributeError, TypeError) as e:
        return {
            "valid": False,
            "message": f"Settings validation failed: {str(e)}",
            "error": str(e),
        }
