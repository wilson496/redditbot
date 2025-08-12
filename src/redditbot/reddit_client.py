
import os
import praw
from redditbot.config import load_settings
from redditbot.settings import Settings

def get_reddit_instance(settings: Settings):
    reddit = praw.Reddit(
        client_id=settings.reddit.client_id,
        client_secret=settings.reddit.client_secret.get_secret_value(),
        user_agent=settings.reddit.user_agent,
    )
    return reddit

def fetch_posts(settings: Settings, limit: int | None = None) -> dict:
    reddit = get_reddit_instance(settings)
    fetch_limit = limit or settings.reddit.fetch.limit
    results: dict[str, list[dict]] = {}
    for sub in settings.reddit.subreddits:
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

# Keep backward compatibility for external usage
def fetch_posts_with_defaults(limit: int | None = None) -> dict:
    """Legacy function that loads settings internally - use fetch_posts(settings, limit) for better performance"""
    settings = load_settings()
    return fetch_posts(settings, limit)
