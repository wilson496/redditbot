"""
Settings and configuration models for RedditBot.

This module provides a clean, typed configuration layer with predictable precedence
and fail-fast validation. Environment variables override .env files, which override
YAML defaults.
"""

from functools import lru_cache
from typing import List, Union
from pydantic import Field, SecretStr, field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Main application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Reddit API credentials (required)
    reddit_client_id: str = Field(
        ...,
        alias="REDDIT_CLIENT_ID",
        description="Reddit API client ID",
    )

    reddit_client_secret: SecretStr = Field(
        ...,
        alias="REDDIT_CLIENT_SECRET",
        description="Reddit API client secret",
    )

    reddit_user_agent: str = Field(
        ...,
        alias="REDDIT_USER_AGENT",
        description="Reddit API user agent string",
    )

    # Reddit configuration (with defaults)
    # Store as string from env, then parse in computed field
    reddit_subreddits_raw: str = Field(
        default="python,programming",
        alias="REDDIT_SUBREDDITS",
        description="Raw comma-separated subreddits string",
    )

    reddit_default_limit: int = Field(
        default=10,
        alias="REDDIT_DEFAULT_LIMIT",
        ge=1,
        le=100,
        description="Default number of posts to fetch per subreddit",
    )

    @computed_field
    @property
    def reddit_subreddits(self) -> List[str]:
        """Parse comma-separated subreddits string into list."""
        if not self.reddit_subreddits_raw:
            return ["python", "programming"]  # fallback defaults
        
        subreddits = [s.strip() for s in self.reddit_subreddits_raw.split(",") if s.strip()]
        if not subreddits:
            raise ValueError("At least one subreddit must be specified")
        return subreddits

    @field_validator("reddit_subreddits_raw")
    @classmethod
    def validate_subreddits_raw(cls, v):
        """Validate that subreddits string is not empty."""
        if isinstance(v, str) and not v.strip():
            raise ValueError("At least one subreddit must be specified")
        return v

    @field_validator("reddit_client_id")
    @classmethod
    def validate_client_id(cls, v):
        """Validate that client ID is not empty."""
        if not v or not v.strip():
            raise ValueError("Client ID cannot be empty")
        return v.strip()

    @field_validator("reddit_user_agent")
    @classmethod
    def validate_user_agent(cls, v):
        """Validate that user agent is not empty."""
        if not v or not v.strip():
            raise ValueError("User agent cannot be empty")
        return v.strip()

    @field_validator("reddit_default_limit")
    @classmethod
    def validate_limit(cls, v):
        """Validate that limit is within acceptable bounds."""
        if v <= 0:
            raise ValueError("Default limit must be greater than 0")
        if v > 100:
            raise ValueError("Default limit cannot exceed 100")
        return v


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    This function returns a singleton Settings instance that is cached
    using LRU cache. The settings are loaded once and reused for
    subsequent calls, improving performance.

    Returns:
        Settings: The application settings instance

    Raises:
        ValidationError: If required settings are missing or invalid
    """
    return Settings()


def validate_settings_on_startup() -> Settings:
    """
    Validate settings on application startup.

    This function is designed to be called during application startup
    to ensure all required settings are present and valid. If validation
    fails, the application should not start.

    Returns:
        Settings: Validated settings instance

    Raises:
        ValidationError: If settings validation fails
    """
    try:
        settings = get_settings()
        print("✅ Settings validated successfully")
        print(
            f"   - Reddit client configured for {len(settings.reddit_subreddits)} subreddits"
        )
        print(f"   - Default fetch limit: {settings.reddit_default_limit}")
        return settings
    except Exception as e:
        print(f"❌ Settings validation failed: {e}")
        raise RuntimeError(
            f"Application cannot start due to invalid settings: {e}"
        ) from e
