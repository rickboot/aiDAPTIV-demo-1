"""
Reddit API client for fetching live social signals.
Free tier: 60 requests/minute, no API key needed (just client_id/secret).
"""

import logging
import time
from typing import List, Dict, Optional
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


class RedditAPI:
    """Reddit API client using requests (no PRAW dependency)."""
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """
        Initialize Reddit API client.
        
        Args:
            client_id: Reddit app client ID
            client_secret: Reddit app client secret
            user_agent: User agent string (required by Reddit)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.base_url = "https://www.reddit.com"
        self.oauth_url = "https://oauth.reddit.com"
        self.access_token = None
        self.token_expires_at = 0
        
    def _get_access_token(self) -> bool:
        """Get OAuth access token."""
        try:
            auth = HTTPBasicAuth(self.client_id, self.client_secret)
            data = {"grant_type": "client_credentials"}
            headers = {"User-Agent": self.user_agent}
            
            response = requests.post(
                f"{self.base_url}/api/v1/access_token",
                auth=auth,
                data=data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires_at = time.time() + expires_in - 60  # Refresh 1 min early
                logger.info("Reddit API: Access token obtained")
                return True
            else:
                logger.error(f"Reddit API: Failed to get token: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Reddit API: Error getting token: {e}")
            return False
    
    def _ensure_token(self) -> bool:
        """Ensure we have a valid access token."""
        if not self.access_token or time.time() >= self.token_expires_at:
            return self._get_access_token()
        return True
    
    def fetch_posts(self, subreddit: str, limit: int = 25, sort: str = "hot") -> List[Dict]:
        """
        Fetch posts from a subreddit.
        
        Args:
            subreddit: Subreddit name (without r/)
            limit: Number of posts to fetch (max 100)
            sort: Sort order (hot, new, top, rising)
        
        Returns:
            List of post dictionaries
        """
        if not self._ensure_token():
            logger.warning("Reddit API: Could not get access token")
            return []
        
        try:
            headers = {
                "Authorization": f"bearer {self.access_token}",
                "User-Agent": self.user_agent
            }
            
            url = f"{self.oauth_url}/r/{subreddit}/{sort}.json"
            params = {"limit": min(limit, 100)}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
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
                    url = post_data.get("url", "")
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
                    if url and url != permalink:
                        content += f"\n\nLink: {url}"
                    
                    # Metadata
                    upvotes = post_data.get("ups", 0)
                    comments = post_data.get("num_comments", 0)
                    created_utc = post_data.get("created_utc", time.time())
                    post_id = post_data.get("id", "")
                    
                    posts.append({
                        "name": f"reddit_{subreddit}_{post_id}.txt",
                        "category": "social",
                        "content": f"""Reddit Discussion - r/{subreddit}

User: u/{post_data.get('author', 'unknown')}
Date: {datetime.fromtimestamp(created_utc).strftime('%B %d, %Y')}
Upvotes: {upvotes}
Comments: {comments}

POST:
{content}

PERMALINK: {permalink}

ANALYSIS:
Social signal from r/{subreddit}. {upvotes} upvotes, {comments} comments. {'High engagement' if upvotes > 100 else 'Moderate engagement'} indicates community interest.""",
                        "size_kb": len(content) / 1024,
                        "source": "reddit",
                        "timestamp": datetime.fromtimestamp(created_utc).isoformat(),
                        "url": permalink,
                        "metadata": {
                            "subreddit": subreddit,
                            "upvotes": upvotes,
                            "comments": comments,
                            "author": post_data.get("author", "unknown")
                        }
                    })
                
                logger.info(f"Reddit API: Fetched {len(posts)} posts from r/{subreddit}")
                return posts
            else:
                logger.warning(f"Reddit API: Failed to fetch posts: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Reddit API: Error fetching posts: {e}")
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
            # Rate limit: 60 requests/min = 1 per second, add small delay
            time.sleep(1.1)
        return all_posts


def create_reddit_client() -> Optional[RedditAPI]:
    """Create Reddit API client if credentials are available."""
    try:
        import config
        if config.REDDIT_API_ENABLED:
            return RedditAPI(
                client_id=config.REDDIT_CLIENT_ID,
                client_secret=config.REDDIT_CLIENT_SECRET,
                user_agent=config.REDDIT_USER_AGENT
            )
    except Exception as e:
        logger.warning(f"Could not create Reddit client: {e}")
    return None
