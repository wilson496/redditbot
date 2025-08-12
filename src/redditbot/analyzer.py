"""
Post analysis and summarization functionality.
"""


def summarize_posts(posts_by_subreddit: dict) -> dict:
    """
    Summarize posts by finding the top-scoring post from each subreddit.
    
    Args:
        posts_by_subreddit: Dictionary mapping subreddit names to lists of posts
        
    Returns:
        Dictionary mapping subreddit names to their top post summary
    """
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
