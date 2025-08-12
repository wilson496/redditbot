"""
Test settings validation with various scenarios.
"""

import os
import pytest
from redditbot.config import validate_settings, load_settings


def test_no_environment_variables(monkeypatch):
    """Test validation with no environment variables set"""
    # Clear any existing env vars
    for var in ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USER_AGENT", "REDDIT_SUBREDDITS"]:
        monkeypatch.delenv(var, raising=False)
    
    # Mock config loading to return empty config
    monkeypatch.setattr("redditbot.config.load_config", lambda *args, **kwargs: {})
    
    # Test validation
    is_valid, message, settings = validate_settings()
    assert not is_valid
    assert "Missing required settings" in message


def test_partial_environment_variables(monkeypatch):
    """Test validation with partial environment variables"""
    # Set only some required variables
    monkeypatch.setenv("REDDIT_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("REDDIT_USER_AGENT", "test_user_agent")
    
    # Clear others
    for var in ["REDDIT_CLIENT_SECRET", "REDDIT_SUBREDDITS"]:
        monkeypatch.delenv(var, raising=False)
    
    # Mock config loading to return empty config
    monkeypatch.setattr("redditbot.config.load_config", lambda *args, **kwargs: {})
    
    is_valid, message, settings = validate_settings()
    assert not is_valid
    assert "Missing required settings" in message


def test_all_required_environment_variables(monkeypatch):
    """Test validation with all required environment variables"""
    # Set all required variables
    monkeypatch.setenv("REDDIT_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "test_client_secret")
    monkeypatch.setenv("REDDIT_USER_AGENT", "test_user_agent")
    monkeypatch.setenv("REDDIT_SUBREDDITS", "python,programming")
    
    # Mock config loading to return empty config
    monkeypatch.setattr("redditbot.config.load_config", lambda *args, **kwargs: {})
    
    is_valid, message, settings = validate_settings()
    assert is_valid
    assert settings is not None
    assert len(settings.reddit.subreddits) == 2
    assert settings.reddit.fetch.limit == 10  # Default value


def test_invalid_values(monkeypatch):
    """Test validation with invalid values"""
    # Set all required variables but with invalid values
    monkeypatch.setenv("REDDIT_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "test_client_secret")
    monkeypatch.setenv("REDDIT_USER_AGENT", "test_user_agent")
    monkeypatch.setenv("REDDIT_SUBREDDITS", "")  # Empty subreddits
    monkeypatch.setenv("FETCH_LIMIT", "0")  # Invalid fetch limit
    
    # Mock config loading to return empty config
    monkeypatch.setattr("redditbot.config.load_config", lambda *args, **kwargs: {})
    
    # This should fail validation
    with pytest.raises(ValueError):
        load_settings()


def test_successful_settings_load(monkeypatch):
    """Test successful settings loading"""
    # Set all required variables with valid values
    monkeypatch.setenv("REDDIT_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "test_client_secret")
    monkeypatch.setenv("REDDIT_USER_AGENT", "test_user_agent")
    monkeypatch.setenv("REDDIT_SUBREDDITS", "python,programming")
    monkeypatch.setenv("FETCH_LIMIT", "15")
    
    # Mock config loading to return empty config
    monkeypatch.setattr("redditbot.config.load_config", lambda *args, **kwargs: {})
    
    settings = load_settings()
    assert settings.reddit.client_id == "test_client_id"
    assert settings.reddit.subreddits == ["python", "programming"]
    assert settings.reddit.fetch.limit == 15
