"""
Test Reddit simple client (no auth required).
Run: python3 backend/test_reddit_simple.py
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.live_feeds.reddit_simple import RedditSimple
import config

def test_reddit_simple():
    """Test Reddit simple client (no auth)."""
    print("=" * 60)
    print("REDDIT SIMPLE CLIENT TEST (No Auth Required)")
    print("=" * 60)
    print()
    
    # Create client
    client = RedditSimple(user_agent=config.REDDIT_USER_AGENT)
    
    # Test fetching posts
    print("Fetching posts from r/LocalLLaMA...")
    posts = client.fetch_posts("LocalLLaMA", limit=5)
    
    if posts:
        print(f"\n✅ Success! Fetched {len(posts)} posts (no auth required!)")
        print("\nSample post:")
        print("-" * 60)
        post = posts[0]
        print(f"Title: {post['name']}")
        print(f"Upvotes: {post['metadata']['upvotes']}")
        print(f"Comments: {post['metadata']['comments']}")
        print(f"Preview: {post['content'][:200]}...")
        print("-" * 60)
        print("\n✅ Reddit simple client works! No signup needed.")
    else:
        print("\n❌ Failed to fetch posts")
        print("Check your internet connection")

if __name__ == "__main__":
    test_reddit_simple()
