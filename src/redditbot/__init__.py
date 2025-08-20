"""
RedditBot - A Reddit bot for fetching and analyzing posts
"""

__version__ = "0.1.0"
__author__ = "Cam Wilson"

# Import only the main classes to avoid circular imports
from .settings import Settings

__all__ = [
    "Settings",
]
