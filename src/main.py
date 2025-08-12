"""
Main entry point for the RedditBot API server.
"""

try:
    import uvicorn
except ImportError:
    print("Error: uvicorn is required to run the server.")
    print("Install it with: pip install uvicorn")
    exit(1)

from redditbot.api import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
