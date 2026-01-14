"""
Simple Reddit client using public JSON endpoints (no OAuth required).
This works for read-only access without needing to create a Reddit app.
"""

import logging
import requests
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class RedditSimple:
    """Simple Reddit client using public JSON endpoints (no auth needed)."""
    
    def __init__(self, user_agent: str = "aiDAPTIV-Demo/1.0"):
        """
        Initialize simple Reddit client.
        
        Args:
            user_agent: User agent string (Reddit requires this)
        """
        self.user_agent = user_agent
        self.base_url = "https://www.reddit.com"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
    
    def fetch_posts(self, subreddit: str, limit: int = 25, sort: str = "hot") -> List[Dict]:
        """
        Fetch posts from a subreddit using public JSON endpoint.
        
        Args:
            subreddit: Subreddit name (without r/)
            limit: Number of posts to fetch (max 100)
            sort: Sort order (hot, new, top, rising)
        
        Returns:
            List of post dictionaries
        """
        try:
            url = f"{self.base_url}/r/{subreddit}/{sort}.json"
            params = {"limit": min(limit, 100)}
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                posts = []
                
                for child in data.get("data", {}).get("children", []):
                    post_data = child.get("data", {})
                    
                    # Filter out bot/administrative accounts
                    author = post_data.get("author", "").lower()
                    if author in ["automoderator", "[deleted]", "reddit"]:
                        continue
                    
                    # Extract post content
                    title = post_data.get("title", "")
                    selftext = post_data.get("selftext", "")
                    url_link = post_data.get("url", "")
                    permalink = f"https://reddit.com{post_data.get('permalink', '')}"
                    
                    # Filter out administrative/meta posts
                    title_lower = title.lower()
                    selftext_lower = selftext.lower()
                    admin_keywords = [
                        "self-promotion thread",
                        "weekly discussion",
                        "monthly discussion",
                        "megathread",
                        "meta thread",
                        "announcement",
                        "rules reminder",
                        "moderator announcement"
                    ]
                    if any(kw in title_lower or kw in selftext_lower for kw in admin_keywords):
                        continue
                    
                    # Combine title and content
                    content = title
                    if selftext:
                        content += f"\n\n{selftext}"
                    if url_link and url_link != permalink:
                        content += f"\n\nLink: {url_link}"
                    
                    # Metadata
                    upvotes = post_data.get("ups", 0)
                    comments = post_data.get("num_comments", 0)
                    created_utc = post_data.get("created_utc", 0)
                    post_id = post_data.get("id", "")
                    
                    posts.append({
                        "name": f"reddit_{subreddit}_{post_id}.txt",
                        "category": "social",
                        "content": f"""Reddit Discussion - r/{subreddit}

User: u/{post_data.get('author', 'unknown')}
Date: {datetime.fromtimestamp(created_utc).strftime('%B %d, %Y') if created_utc else 'Unknown'}
Upvotes: {upvotes}
Comments: {comments}

POST:
{content}

PERMALINK: {permalink}

ANALYSIS:
Social signal from r/{subreddit}. {upvotes} upvotes, {comments} comments. {'High engagement' if upvotes > 100 else 'Moderate engagement'} indicates community interest.""",
                        "size_kb": len(content) / 1024,
                        "source": "reddit",
                        "timestamp": datetime.fromtimestamp(created_utc).isoformat() if created_utc else datetime.now().isoformat(),
                        "url": permalink,
                        "metadata": {
                            "subreddit": subreddit,
                            "upvotes": upvotes,
                            "comments": comments,
                            "author": post_data.get("author", "unknown")
                        }
                    })
                
                logger.info(f"RedditSimple: Fetched {len(posts)} posts from r/{subreddit}")
                return posts
            elif response.status_code == 429:
                logger.warning(f"RedditSimple: Rate limited (429). Try again later.")
                return []
            else:
                logger.warning(f"RedditSimple: Failed to fetch posts: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"RedditSimple: Error fetching posts: {e}")
            return []
    
    def fetch_multiple_subreddits(self, subreddits: List[str], limit_per_sub: int = 10) -> List[Dict]:
        """
        Fetch posts from multiple subreddits.
        
        Args:
            subreddits: List of subreddit names
            limit_per_sub: Posts per subreddit
        
        Returns:
            Combined list of posts
        """
        all_posts = []
        for subreddit in subreddits:
            posts = self.fetch_posts(subreddit, limit=limit_per_sub)
            all_posts.extend(posts)
            # Small delay to avoid rate limiting
            import time
            time.sleep(1.0)
        return all_posts


def create_reddit_simple_client() -> RedditSimple:
    """Create simple Reddit client (no auth needed)."""
    import config
    return RedditSimple(user_agent=config.REDDIT_USER_AGENT)
