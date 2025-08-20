"""
Reddit API client for fetching posts from subreddits.
"""



import praw

from .settings import Settings, get_settings


def get_reddit_instance(settings: Settings):
    """Create and return a Reddit API instance."""
    reddit = praw.Reddit(
        client_id=settings.reddit_client_id,
        client_secret=settings.reddit_client_secret.get_secret_value(),
        user_agent=settings.reddit_user_agent,
    )
    return reddit


def fetch_posts(settings: Settings, limit: int | None = None) -> dict:
    """Fetch posts from configured subreddits."""
    reddit = get_reddit_instance(settings)
    fetch_limit = limit or settings.reddit_default_limit
    results: dict[str, list[dict]] = {}

    for sub in settings.reddit_subreddits:
        subreddit = reddit.subreddit(sub)
        posts = [
            {
                "id": post.id,
                "title": post.title,
                "score": int(post.score),
                "url": str(post.url),
                "permalink": f"https://reddit.com{post.permalink}",
                "created_utc": float(post.created_utc),
                "num_comments": int(getattr(post, "num_comments", 0)),
            }
            for post in subreddit.hot(limit=fetch_limit)
        ]
        results[sub] = posts

    return results


def fetch_posts_with_defaults(limit: int | None = None) -> dict:
    """Fetch posts using the default settings."""
    settings = get_settings()
    return fetch_posts(settings, limit)
