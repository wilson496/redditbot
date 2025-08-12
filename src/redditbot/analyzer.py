
from collections import defaultdict

def summarize_posts(posts_by_subreddit: dict) -> dict:
    summary = {}
    for subreddit, posts in posts_by_subreddit.items():
        if not posts:
            summary[subreddit] = None
            continue
        top_post = max(posts, key=lambda p: p.get("score", 0))
        summary[subreddit] = {
            "id": top_post["id"],
            "title": top_post["title"],
            "score": top_post["score"],
            "permalink": top_post["permalink"],
        }
    return summary
