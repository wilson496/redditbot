"""
Configuration management for RedditBot.
"""

import os
from pathlib import Path
from typing import Union

import dotenv
import yaml

from .settings import Settings


def _default_config_path() -> Path:
    """Get the default path for the configuration file."""
    # src/redditbot/config.py -> repo root is parents[2]
    return Path(__file__).resolve().parents[2] / "config" / "config.yaml"


def _default_env_path() -> Path:
    """Get the default path for the environment file."""
    return Path(__file__).resolve().parents[2] / ".env"


def load_config(path: Union[str, os.PathLike, None] = None) -> dict:
    """Load configuration from YAML file."""
    cfg_path = Path(path) if path else _default_config_path()
    with cfg_path.open("r") as f:
        return yaml.safe_load(f)


def load_env(path: Union[str, os.PathLike, None] = None) -> dict:
    """Load environment variables from .env file."""
    env_path = Path(path) if path else _default_env_path()
    return dotenv.load_dotenv(env_path)


def load_settings(path: Union[str, os.PathLike, None] = None) -> Settings:
    """Load and validate application settings from config files and environment."""
    # Load .env into environment first
    env_path = Path(path) if path else _default_env_path()
    load_env(env_path)

    # Read YAML for non-secret defaults
    try:
        cfg = load_config()
    except FileNotFoundError:
        cfg = {}
        print(f"⚠️  Config file not found at {_default_config_path()}, using environment variables only")
    except Exception as e:
        cfg = {}
        print(f"⚠️  Error loading config file: {e}, using environment variables only")

    defaults: dict = {
        "reddit": {
            "subreddits": cfg.get("reddit", {}).get("subreddits", []),
            "fetch": {"limit": cfg.get("fetch", {}).get("limit", 10)},
            "client_id": cfg.get("reddit", {}).get("client_id"),
            "client_secret": cfg.get("reddit", {}).get("client_secret"),
            "user_agent": cfg.get("reddit", {}).get("user_agent"),
        }
    }

    # Override with env vars when present
    if os.getenv("REDDIT_CLIENT_ID"):
        defaults["reddit"]["client_id"] = os.getenv("REDDIT_CLIENT_ID")
    if os.getenv("REDDIT_CLIENT_SECRET"):
        defaults["reddit"]["client_secret"] = os.getenv("REDDIT_CLIENT_SECRET")
    if os.getenv("REDDIT_USER_AGENT"):
        defaults["reddit"]["user_agent"] = os.getenv("REDDIT_USER_AGENT")
    if os.getenv("FETCH_LIMIT"):
        try:
            defaults["reddit"]["fetch"]["limit"] = int(os.getenv("FETCH_LIMIT", ""))
        except ValueError:
            pass
    if os.getenv("REDDIT_SUBREDDITS"):
        defaults["reddit"]["subreddits"] = [
            s.strip() for s in os.getenv("REDDIT_SUBREDDITS", "").split(",") if s.strip()
        ]

    # Pre-validation checks for missing required values
    missing_fields = []

    if not defaults["reddit"]["client_id"] or defaults["reddit"]["client_id"] is None:
        missing_fields.append("REDDIT_CLIENT_ID")
    if not defaults["reddit"]["client_secret"] or defaults["reddit"]["client_secret"] is None:
        missing_fields.append("REDDIT_CLIENT_SECRET")
    if not defaults["reddit"]["user_agent"] or defaults["reddit"]["user_agent"] is None:
        missing_fields.append("REDDIT_USER_AGENT")
    if not defaults["reddit"]["subreddits"] or defaults["reddit"]["subreddits"] is None:
        missing_fields.append("REDDIT_SUBREDDITS")

    if missing_fields:
        raise ValueError(
            f"Missing required settings: {', '.join(missing_fields)}. "
            f"Please set these values in your config file or environment variables."
        )

    # Validate and return settings
    return Settings.model_validate(defaults)


def validate_settings(path: Union[str, os.PathLike, None] = None) -> tuple[bool, str, Union[Settings, None]]:
    """
    Validate settings without raising exceptions.

    Returns:
        tuple: (is_valid, message, settings_or_none)
    """
    try:
        settings = load_settings(path)
        return True, "Settings are valid", settings
    except Exception as e:
        return False, f"Settings validation failed: {str(e)}", None
