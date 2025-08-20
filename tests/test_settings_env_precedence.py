"""
Tests for environment variable precedence in settings.
"""

from unittest.mock import patch
import pytest

from redditbot.settings import Settings


def test_environment_variables_override_defaults():
    """Test that environment variables override default values."""
    with patch.dict('os.environ', {
        'REDDIT_CLIENT_ID': 'env_client_id',
        'REDDIT_CLIENT_SECRET': 'env_client_secret',
        'REDDIT_USER_AGENT': 'env_user_agent',
        'REDDIT_SUBREDDITS': 'python,fastapi,django',
        'REDDIT_DEFAULT_LIMIT': '25'
    }):
        settings = Settings()

        # Environment variables should override defaults
        assert settings.reddit_client_id == 'env_client_id'
        assert str(settings.reddit_client_secret) == 'env_client_secret'
        assert settings.reddit_user_agent == 'env_user_agent'
        assert settings.reddit_subreddits == ['python', 'fastapi', 'django']
        assert settings.reddit_default_limit == 25


def test_default_values_when_env_vars_not_set():
    """Test that default values are used when environment variables are not set."""
    with patch.dict('os.environ', {
        'REDDIT_CLIENT_ID': 'env_client_id',
        'REDDIT_CLIENT_SECRET': 'env_client_secret',
        'REDDIT_USER_AGENT': 'env_user_agent'
        # REDDIT_SUBREDDITS and REDDIT_DEFAULT_LIMIT not set
    }):
        settings = Settings()

        # Should use defaults for optional fields
        assert settings.reddit_subreddits == ['python', 'programming']  # default
        assert settings.reddit_default_limit == 10  # default


def test_comma_separated_subreddits_parsing():
    """Test that comma-separated subreddits are properly parsed."""
    with patch.dict('os.environ', {
        'REDDIT_CLIENT_ID': 'env_client_id',
        'REDDIT_CLIENT_SECRET': 'env_client_secret',
        'REDDIT_USER_AGENT': 'env_user_agent',
        'REDDIT_SUBREDDITS': 'python, fastapi , django,  flask'  # with spaces
    }):
        settings = Settings()

        # Should parse comma-separated values and strip whitespace
        assert settings.reddit_subreddits == ['python', 'fastapi', 'django', 'flask']


def test_single_subreddit_parsing():
    """Test that single subreddit is properly handled."""
    with patch.dict('os.environ', {
        'REDDIT_CLIENT_ID': 'env_client_id',
        'REDDIT_CLIENT_SECRET': 'env_client_secret',
        'REDDIT_USER_AGENT': 'env_user_agent',
        'REDDIT_SUBREDDITS': 'python'  # single value
    }):
        settings = Settings()

        # Should create list with single item
        assert settings.reddit_subreddits == ['python']


def test_empty_subreddits_handling():
    """Test that empty subreddits string is handled properly."""
    with patch.dict('os.environ', {
        'REDDIT_CLIENT_ID': 'env_client_id',
        'REDDIT_CLIENT_SECRET': 'env_client_secret',
        'REDDIT_USER_AGENT': 'env_user_agent',
        'REDDIT_SUBREDDITS': ''  # empty string
    }):
        # Should raise validation error
        with pytest.raises(ValueError) as exc_info:
            Settings()

        error_msg = str(exc_info.value)
        assert 'At least one subreddit must be specified' in error_msg


def test_limit_validation():
    """Test that limit values are properly validated."""
    with patch.dict('os.environ', {
        'REDDIT_CLIENT_ID': 'env_client_id',
        'REDDIT_CLIENT_SECRET': 'env_client_secret',
        'REDDIT_USER_AGENT': 'env_user_agent',
        'REDDIT_DEFAULT_LIMIT': '50'  # valid value
    }):
        settings = Settings()
        assert settings.reddit_default_limit == 50


def test_limit_validation_out_of_range():
    """Test that out-of-range limit values are rejected."""
    with patch.dict('os.environ', {
        'REDDIT_CLIENT_ID': 'env_client_id',
        'REDDIT_CLIENT_SECRET': 'env_client_secret',
        'REDDIT_USER_AGENT': 'env_user_agent',
        'REDDIT_DEFAULT_LIMIT': '150'  # too high
    }):
        with pytest.raises(ValueError) as exc_info:
            Settings()

        error_msg = str(exc_info.value)
        assert 'cannot exceed 100' in error_msg


def test_limit_validation_zero():
    """Test that zero limit values are rejected."""
    with patch.dict('os.environ', {
        'REDDIT_CLIENT_ID': 'env_client_id',
        'REDDIT_CLIENT_SECRET': 'env_client_secret',
        'REDDIT_USER_AGENT': 'env_user_agent',
        'REDDIT_DEFAULT_LIMIT': '0'  # too low
    }):
        with pytest.raises(ValueError) as exc_info:
            Settings()

        error_msg = str(exc_info.value)
        assert 'greater than 0' in error_msg


def test_environment_variable_case_insensitivity():
    """Test that environment variable names are case-insensitive."""
    with patch.dict('os.environ', {
        'reddit_client_id': 'lowercase_client_id',  # lowercase
        'REDDIT_CLIENT_SECRET': 'env_client_secret',
        'REDDIT_USER_AGENT': 'env_user_agent'
    }):
        settings = Settings()

        # Should still work due to case-insensitive config
        assert settings.reddit_client_id == 'lowercase_client_id'
