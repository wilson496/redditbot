"""
Settings and configuration models for RedditBot.
"""

from pydantic import Field, SecretStr, BaseModel, field_validator
from pydantic_settings import BaseSettings


class FetchSettings(BaseModel):
    """Settings for fetching posts from Reddit."""
    limit: int = Field(..., description="The limit of posts to fetch")

    @field_validator('limit')
    @classmethod
    def validate_limit(cls, v):
        """Validate that the fetch limit is within acceptable bounds."""
        if v <= 0:
            raise ValueError('Fetch limit must be greater than 0')
        if v > 100:
            raise ValueError('Fetch limit cannot exceed 100')
        return v


class RedditSettings(BaseModel):
    """Settings for Reddit API configuration."""
    subreddits: list[str] = Field(..., description="The subreddits to fetch posts from")
    fetch: FetchSettings = Field(..., description="The fetch settings")
    client_id: str = Field(..., description="The client ID for the Reddit API")
    client_secret: SecretStr = Field(..., description="The client secret for the Reddit API")
    user_agent: str = Field(..., description="The user agent for the Reddit API")

    @field_validator('subreddits')
    @classmethod
    def validate_subreddits(cls, v):
        """Validate that subreddits list is not empty and contains valid names."""
        if not v or len(v) == 0:
            raise ValueError('At least one subreddit must be specified')
        if any(not sub.strip() for sub in v):
            raise ValueError('Subreddit names cannot be empty or whitespace only')
        return v

    @field_validator('client_id')
    @classmethod
    def validate_client_id(cls, v):
        """Validate that client ID is not empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError('Client ID cannot be empty or whitespace only')
        return v.strip()

    @field_validator('user_agent')
    @classmethod
    def validate_user_agent(cls, v):
        """Validate that user agent is not empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError('User agent cannot be empty or whitespace only')
        return v.strip()


class Settings(BaseSettings):
    """Main application settings."""
    reddit: RedditSettings = Field(..., description="The Reddit API settings")
