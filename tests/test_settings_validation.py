"""
Tests for settings validation functionality.
"""

from unittest.mock import patch
import pytest
from pydantic import ValidationError

from redditbot.settings import Settings, get_settings, validate_settings_on_startup


def test_settings_with_valid_values():
    """Test that Settings can be created with valid values."""
    with patch.dict('os.environ', {
        'REDDIT_CLIENT_ID': 'test_client_id',
        'REDDIT_CLIENT_SECRET': 'test_secret',
        'REDDIT_USER_AGENT': 'test_user_agent'
    }):
        settings = Settings()

        assert settings.reddit_client_id == 'test_client_id'
        assert str(settings.reddit_client_secret) == 'test_secret'
        assert settings.reddit_user_agent == 'test_user_agent'
        assert settings.reddit_subreddits == ['python', 'programming']  # defaults
        assert settings.reddit_default_limit == 10  # default


def test_settings_with_custom_subreddits():
    """Test that subreddits can be overridden via environment variable."""
    with patch.dict('os.environ', {
        'REDDIT_CLIENT_ID': 'test_client_id',
        'REDDIT_CLIENT_SECRET': 'test_secret',
        'REDDIT_USER_AGENT': 'test_user_agent',
        'REDDIT_SUBREDDITS': 'python,fastapi,django'
    }):
        settings = Settings()

        assert settings.reddit_subreddits == ['python', 'fastapi', 'django']


def test_settings_with_custom_limit():
    """Test that default limit can be overridden via environment variable."""
    with patch.dict('os.environ', {
        'REDDIT_CLIENT_ID': 'test_client_id',
        'REDDIT_CLIENT_SECRET': 'test_secret',
        'REDDIT_USER_AGENT': 'test_user_agent',
        'REDDIT_DEFAULT_LIMIT': '25'
    }):
        settings = Settings()

        assert settings.reddit_default_limit == 25


def test_settings_missing_required_fields():
    """Test that Settings raises error when required fields are missing."""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValidationError) as exc_info:
            Settings()

        # Check that the error mentions the missing fields
        error_msg = str(exc_info.value)
        assert 'REDDIT_CLIENT_ID' in error_msg
        assert 'REDDIT_CLIENT_SECRET' in error_msg
        assert 'REDDIT_USER_AGENT' in error_msg


def test_settings_invalid_limit():
    """Test that invalid limit values are rejected."""
    with patch.dict('os.environ', {
        'REDDIT_CLIENT_ID': 'test_client_id',
        'REDDIT_CLIENT_SECRET': 'test_secret',
        'REDDIT_USER_AGENT': 'test_user_agent',
        'REDDIT_DEFAULT_LIMIT': '0'  # Invalid: must be > 0
    }):
        with pytest.raises(ValidationError) as exc_info:
            Settings()

        error_msg = str(exc_info.value)
        assert 'greater than 0' in error_msg


def test_settings_limit_too_high():
    """Test that limit values above 100 are rejected."""
    with patch.dict('os.environ', {
        'REDDIT_CLIENT_ID': 'test_client_id',
        'REDDIT_CLIENT_SECRET': 'test_secret',
        'REDDIT_USER_AGENT': 'test_user_agent',
        'REDDIT_DEFAULT_LIMIT': '101'  # Invalid: must be <= 100
    }):
        with pytest.raises(ValidationError) as exc_info:
            Settings()

        error_msg = str(exc_info.value)
        assert 'cannot exceed 100' in error_msg


def test_settings_empty_subreddits():
    """Test that empty subreddits list is rejected."""
    with patch.dict('os.environ', {
        'REDDIT_CLIENT_ID': 'test_client_id',
        'REDDIT_CLIENT_SECRET': 'test_secret',
        'REDDIT_USER_AGENT': 'test_user_agent',
        'REDDIT_SUBREDDITS': ''  # Empty string
    }):
        with pytest.raises(ValidationError) as exc_info:
            Settings()

        error_msg = str(exc_info.value)
        assert 'At least one subreddit must be specified' in error_msg


def test_get_settings_caching():
    """Test that get_settings returns cached instance."""
    with patch.dict('os.environ', {
        'REDDIT_CLIENT_ID': 'test_client_id',
        'REDDIT_CLIENT_SECRET': 'test_secret',
        'REDDIT_USER_AGENT': 'test_user_agent'
    }):
        settings1 = get_settings()
        settings2 = get_settings()

        # Should be the same instance due to caching
        assert settings1 is settings2


def test_validate_settings_on_startup_success():
    """Test successful settings validation on startup."""
    with patch.dict('os.environ', {
        'REDDIT_CLIENT_ID': 'test_client_id',
        'REDDIT_CLIENT_SECRET': 'test_secret',
        'REDDIT_USER_AGENT': 'test_user_agent'
    }):
        settings = validate_settings_on_startup()

        assert isinstance(settings, Settings)
        assert settings.reddit_client_id == 'test_client_id'


def test_validate_settings_on_startup_failure():
    """Test that startup validation fails with invalid settings."""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(RuntimeError) as exc_info:
            validate_settings_on_startup()

        error_msg = str(exc_info.value)
        assert 'Application cannot start due to invalid settings' in error_msg
