
import types
from redditbot.reddit_client import fetch_posts
from redditbot.settings import Settings, RedditSettings, FetchSettings
from pydantic import SecretStr

class DummySubreddit:
    def __init__(self, name): 
        self.name = name
    
    def hot(self, limit=5):
        # Minimal stub posts
        class Post:
            def __init__(self, subreddit_name, i): 
                self.id = f"{subreddit_name}_{i}"
                self.title = f"Post {i} in {subreddit_name}"
                self.score = i * 10
                self.url = f"https://example.com/{subreddit_name}/{i}"
                self.permalink = f"/r/{subreddit_name}/comments/{subreddit_name}_{i}/"
                self.created_utc = 0
                self.num_comments = i
        return [Post(self.name, i) for i in range(1, limit + 1)]

class DummyReddit:
    def subreddit(self, name): 
        s = DummySubreddit(name)
        s.name = name
        return s

def test_fetch_posts_monkeypatch(monkeypatch, tmp_path):
    # Create a dummy reddit instance
    dummy_reddit = DummyReddit()
    
    # Monkeypatch get_reddit_instance to return our dummy
    def mock_get_reddit_instance(settings):
        return dummy_reddit
    
    monkeypatch.setattr("redditbot.reddit_client.get_reddit_instance", mock_get_reddit_instance)

    # Create fake settings
    fake_settings = Settings(
        reddit=RedditSettings(
            subreddits=["a", "b"],
            fetch=FetchSettings(limit=2),
            client_id="test_client_id",  # Use valid test values
            client_secret=SecretStr("test_client_secret"),
            user_agent="test_user_agent",  # Use valid test values
        )
    )

    data = fetch_posts(fake_settings)
    assert set(data.keys()) == {"a", "b"}
    assert len(data["a"]) == 2
    assert all("title" in p and "score" in p for p in data["a"]) 
