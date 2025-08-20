"""
Tests for the Reddit client functionality.
"""

import pytest
from unittest.mock import Mock, patch

from redditbot.settings import Settings
from redditbot.reddit_client import get_reddit_instance, fetch_posts


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    settings = Mock(spec=Settings)
    settings.reddit_client_id = "test_client_id"
    settings.reddit_client_secret = Mock()
    settings.reddit_client_secret.get_secret_value.return_value = "test_secret"
    settings.reddit_user_agent = "test_user_agent"
    settings.reddit_subreddits = ["python", "programming"]
    settings.reddit_default_limit = 5
    return settings


@pytest.fixture
def mock_reddit():
    """Create mock Reddit instance for testing."""
    reddit = Mock()
    
    # Mock subreddit
    subreddit = Mock()
    reddit.subreddit.return_value = subreddit
    
    # Mock posts
    mock_post = Mock()
    mock_post.id = "test_id"
    mock_post.title = "Test Post"
    mock_post.score = 100
    mock_post.url = "https://example.com"
    mock_post.permalink = "/r/python/comments/test"
    mock_post.created_utc = 1234567890.0
    mock_post.num_comments = 25
    
    subreddit.hot.return_value = [mock_post]
    
    return reddit


def test_get_reddit_instance(mock_settings, mock_reddit):
    """Test creating Reddit instance with settings."""
    with patch('redditbot.reddit_client.praw.Reddit', return_value=mock_reddit):
        result = get_reddit_instance(mock_settings)
        
        assert result == mock_reddit
        # Verify praw.Reddit was called with correct parameters
        from redditbot.reddit_client import praw
        praw.Reddit.assert_called_once_with(
            client_id="test_client_id",
            client_secret="test_secret",
            user_agent="test_user_agent"
        )


def test_fetch_posts(mock_settings, mock_reddit):
    """Test fetching posts from subreddits."""
    with patch('redditbot.reddit_client.get_reddit_instance', return_value=mock_reddit):
        result = fetch_posts(mock_settings, limit=3)
        
        assert "python" in result
        assert "programming" in result
        
        # Check that posts were fetched for each subreddit
        assert len(result["python"]) == 1
        assert len(result["programming"]) == 1
        
        # Check post structure
        post = result["python"][0]
        assert post["id"] == "test_id"
        assert post["title"] == "Test Post"
        assert post["score"] == 100
        assert post["url"] == "https://example.com"
        assert post["permalink"] == "https://reddit.com/r/python/comments/test"
        assert post["created_utc"] == 1234567890.0
        assert post["num_comments"] == 25


def test_fetch_posts_with_default_limit(mock_settings, mock_reddit):
    """Test fetching posts with default limit from settings."""
    with patch('redditbot.reddit_client.get_reddit_instance', return_value=mock_reddit):
        result = fetch_posts(mock_settings)  # No limit specified
        
        # Should use default limit from settings
        assert len(result["python"]) == 1
        assert len(result["programming"]) == 1


def test_fetch_posts_with_custom_limit(mock_settings, mock_reddit):
    """Test fetching posts with custom limit."""
    with patch('redditbot.reddit_client.get_reddit_instance', return_value=mock_reddit):
        result = fetch_posts(mock_settings, limit=10)
        
        # Should use custom limit
        assert len(result["python"]) == 1
        assert len(result["programming"]) == 1
