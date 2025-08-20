"""
Data models for the RedditBot API.
"""

from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str
    uptime_seconds: float


class RedditPost(BaseModel):
    """Model representing a Reddit post."""

    id: str
    title: str
    score: int
    permalink: str
