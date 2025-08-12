"""
Tests for environment variable precedence over YAML configuration.
"""

from redditbot.config import load_settings


def test_yaml_defaults_used_when_no_env(monkeypatch):
    """Test that YAML defaults are used when no environment variables are set."""
    # Ensure env is clean
    for key in [
        "REDDIT_CLIENT_ID",
        "REDDIT_CLIENT_SECRET",
        "REDDIT_USER_AGENT",
        "REDDIT_SUBREDDITS",
        "FETCH_LIMIT",
    ]:
        monkeypatch.delenv(key, raising=False)

    # Avoid reading a real .env file
    monkeypatch.setattr("redditbot.config.load_env", lambda *args, **kwargs: None)

    # Provide YAML defaults
    yaml_cfg = {
        "reddit": {
            "subreddits": ["devops", "python"],
            "client_id": "yaml-client-id",
            "client_secret": "yaml-secret",
            "user_agent": "yaml-agent",
        },
        "fetch": {"limit": 7},
    }
    monkeypatch.setattr("redditbot.config.load_config", lambda *args, **kwargs: yaml_cfg)

    s = load_settings()
    assert s.reddit.subreddits == ["devops", "python"]
    assert s.reddit.fetch.limit == 7
    assert s.reddit.client_id == "yaml-client-id"
    assert s.reddit.client_secret.get_secret_value() == "yaml-secret"
    assert s.reddit.user_agent == "yaml-agent"


def test_env_overrides_yaml(monkeypatch):
    """Test that environment variables override YAML configuration."""
    # Provide YAML defaults
    yaml_cfg = {
        "reddit": {
            "subreddits": ["devops", "python"],
            "client_id": "yaml-client-id",
            "client_secret": "yaml-secret",
            "user_agent": "yaml-agent",
        },
        "fetch": {"limit": 7},
    }
    monkeypatch.setattr("redditbot.config.load_config", lambda *args, **kwargs: yaml_cfg)

    # Avoid reading a real .env file
    monkeypatch.setattr("redditbot.config.load_env", lambda *args, **kwargs: None)

    # Set env overrides
    monkeypatch.setenv("REDDIT_CLIENT_ID", "env-client-id")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "env-secret")
    monkeypatch.setenv("REDDIT_USER_AGENT", "env-agent")
    monkeypatch.setenv("REDDIT_SUBREDDITS", "learnpython, python")
    monkeypatch.setenv("FETCH_LIMIT", "12")

    s = load_settings()
    assert s.reddit.client_id == "env-client-id"
    assert s.reddit.client_secret.get_secret_value() == "env-secret"
    assert s.reddit.user_agent == "env-agent"
    assert s.reddit.subreddits == ["learnpython", "python"]
    assert s.reddit.fetch.limit == 12



