"""
Test Reddit API integration.
Run: python3 backend/test_reddit_api.py
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.live_feeds.reddit_api import RedditAPI
import config

def test_reddit_api():
    """Test Reddit API connection."""
    print("=" * 60)
    print("REDDIT API TEST")
    print("=" * 60)
    
    # Check if credentials are set
    if not config.REDDIT_API_ENABLED:
        print("\n❌ Reddit API not enabled!")
        print("\nTo enable:")
        print("1. Go to https://www.reddit.com/prefs/apps")
        print("2. Click 'create app' or 'create another app'")
        print("3. Choose 'script' type")
        print("4. Fill in name and redirect URI (can be http://localhost)")
        print("5. Copy the client_id (under the app name)")
        print("6. Copy the secret (under 'secret')")
        print("\nThen set environment variables:")
        print("export REDDIT_CLIENT_ID=your_client_id")
        print("export REDDIT_CLIENT_SECRET=your_secret")
        print("export REDDIT_USER_AGENT='aiDAPTIV-Demo/1.0'")
        return
    
    print(f"\nClient ID: {config.REDDIT_CLIENT_ID[:10]}...")
    print(f"User Agent: {config.REDDIT_USER_AGENT}")
    print()
    
    # Create client
    client = RedditAPI(
        client_id=config.REDDIT_CLIENT_ID,
        client_secret=config.REDDIT_CLIENT_SECRET,
        user_agent=config.REDDIT_USER_AGENT
    )
    
    # Test fetching posts
    print("Fetching posts from r/LocalLLaMA...")
    posts = client.fetch_posts("LocalLLaMA", limit=5)
    
    if posts:
        print(f"\n✅ Success! Fetched {len(posts)} posts")
        print("\nSample post:")
        print("-" * 60)
        post = posts[0]
        print(f"Title: {post['name']}")
        print(f"Upvotes: {post['metadata']['upvotes']}")
        print(f"Comments: {post['metadata']['comments']}")
        print(f"Preview: {post['content'][:200]}...")
        print("-" * 60)
    else:
        print("\n❌ Failed to fetch posts")
        print("Check your credentials and network connection")

if __name__ == "__main__":
    test_reddit_api()
