"""
Chat&Talk GPT - News Subscription Manager
Comprehensive news aggregation and daily digest delivery system
Supports multiple categories: technology, finance, economics, AI, industry solutions, country-specific
"""
import os
import logging
import asyncio
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid

logger = logging.getLogger("NewsSubscriptionManager")

# Try importing optional dependencies
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests library not available for news fetching")

# Data storage
DATA_DIR = Path("backend/memory")
NEWS_SUBSCRIPTIONS_FILE = DATA_DIR / "news_subscriptions.json"
NEWS_CACHE_FILE = DATA_DIR / "news_cache.json"


class NewsCategory(Enum):
    """News categories"""
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    ECONOMICS = "economics"
    AI = "ai"
    BUSINESS = "business"
    SCIENCE = "science"
    HEALTH = "health"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    WORLD = "world"
    COUNTRY_SPECIFIC = "country_specific"
    INDUSTRY = "industry"
    GENERAL = "general"


class NotificationFrequency(Enum):
    """Notification frequency options"""
    INSTANT = "instant"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class PushPlatform(Enum):
    """Supported push notification platforms"""
    WEB = "web"
    ANDROID = "android"
    IOS = "ios"
    DESKTOP = "desktop"


class NewsSubscriptionManager:
    """
    News subscription and daily digest delivery system
    Features:
    - Multiple news categories
    - User subscriptions to categories
    - Push notification to multiple platforms (web, mobile, desktop)
    - Daily/weekly/monthly digest scheduling
    - Country-specific news
    - Industry-specific solutions
    """

    def __init__(self):
        self.subscriptions = self._load_subscriptions()
        self.news_cache = self._load_news_cache()
        
        # News API configuration (using free APIs)
        self.gnews_api_key = os.getenv("GNEWS_API_KEY", "")
        self.newsapi_key = os.getenv("NEWSAPI_KEY", "")
        
        # Default categories
        self.available_categories = [
            {"id": "technology", "name": "Technology", "icon": "💻", "description": "Tech news, gadgets, software"},
            {"id": "finance", "name": "Finance", "icon": "💰", "description": "Stock market, banking, investments"},
            {"id": "economics", "name": "Economics", "icon": "📈", "description": "Economic indicators, policies, markets"},
            {"id": "ai", "name": "Artificial Intelligence", "icon": "🤖", "description": "AI, machine learning, robotics"},
            {"id": "business", "name": "Business", "icon": "🏢", "description": "Business news, startups, entrepreneurship"},
            {"id": "science", "name": "Science", "icon": "🔬", "description": "Scientific discoveries, research"},
            {"id": "health", "name": "Health", "icon": "🏥", "description": "Healthcare, medical breakthroughs"},
            {"id": "sports", "name": "Sports", "icon": "⚽", "description": "Sports news, events"},
            {"id": "entertainment", "name": "Entertainment", "icon": "🎬", "description": "Movies, music, celebrities"},
            {"id": "world", "name": "World News", "icon": "🌍", "description": "International news"},
            {"id": "nepal", "name": "Nepal", "icon": "🇳🇵", "description": "Nepal-specific news"},
            {"id": "india", "name": "India", "icon": "🇮🇳", "description": "India-specific news"},
            {"id": "usa", "name": "USA", "icon": "🇺🇸", "description": "USA-specific news"},
            {"id": "industry", "name": "Industry Solutions", "icon": "🏭", "description": "Solutions for various industries"},
        ]
        
        logger.info(f"News Subscription Manager initialized with {len(self.subscriptions)} users")

    def _load_subscriptions(self) -> Dict:
        """Load user subscriptions"""
        try:
            if NEWS_SUBSCRIPTIONS_FILE.exists():
                with open(NEWS_SUBSCRIPTIONS_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading subscriptions: {e}")
        return {"users": {}, "categories": {}}

    def _save_subscriptions(self):
        """Save user subscriptions"""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(NEWS_SUBSCRIPTIONS_FILE, 'w') as f:
                json.dump(self.subscriptions, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving subscriptions: {e}")

    def _load_news_cache(self) -> Dict:
        """Load cached news"""
        try:
            if NEWS_CACHE_FILE.exists():
                with open(NEWS_CACHE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading news cache: {e}")
        return {"articles": {}, "last_updated": {}}

    def _save_news_cache(self):
        """Save news cache"""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(NEWS_CACHE_FILE, 'w') as f:
                json.dump(self.news_cache, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving news cache: {e}")

    def register_user(self, user_id: str, email: str, name: str = "") -> Dict:
        """Register a new user for news subscriptions"""
        if "users" not in self.subscriptions:
            self.subscriptions["users"] = {}
        
        if user_id not in self.subscriptions["users"]:
            self.subscriptions["users"][user_id] = {
                "email": email,
                "name": name,
                "subscriptions": [],
                "notification_preferences": {
                    "frequency": "daily",
                    "time": "08:00",
                    "platforms": ["email"],
                    "push_tokens": []
                },
                "country": "us",
                "language": "en",
                "created_at": datetime.now().isoformat()
            }
            self._save_subscriptions()
        
        return self.subscriptions["users"][user_id]

    def update_notification_preferences(
        self, 
        user_id: str, 
        frequency: str = None,
        time: str = None,
        platforms: List[str] = None,
        country: str = None,
        language: str = None
    ) -> Dict:
        """Update notification preferences for a user"""
        if user_id not in self.subscriptions["users"]:
            return {"success": False, "message": "User not registered"}
        
        prefs = self.subscriptions["users"][user_id]["notification_preferences"]
        
        if frequency:
            prefs["frequency"] = frequency
        if time:
            prefs["time"] = time
        if platforms:
            prefs["platforms"] = platforms
        if country:
            self.subscriptions["users"][user_id]["country"] = country
        if language:
            self.subscriptions["users"][user_id]["language"] = language
        
        self._save_subscriptions()
        return {"success": True, "preferences": prefs}

    def subscribe_to_category(self, user_id: str, category: str) -> Dict:
        """Subscribe user to a news category"""
        if user_id not in self.subscriptions["users"]:
            return {"success": False, "message": "User not registered"}
        
        user = self.subscriptions["users"][user_id]
        
        if category not in user["subscriptions"]:
            user["subscriptions"].append(category)
            self._save_subscriptions()
            return {
                "success": True, 
                "message": f"Subscribed to {category}",
                "subscriptions": user["subscriptions"]
            }
        
        return {"success": False, "message": "Already subscribed to this category"}

    def unsubscribe_from_category(self, user_id: str, category: str) -> Dict:
        """Unsubscribe user from a news category"""
        if user_id not in self.subscriptions["users"]:
            return {"success": False, "message": "User not registered"}
        
        user = self.subscriptions["users"][user_id]
        
        if category in user["subscriptions"]:
            user["subscriptions"].remove(category)
            self._save_subscriptions()
            return {
                "success": True, 
                "message": f"Unsubscribed from {category}",
                "subscriptions": user["subscriptions"]
            }
        
        return {"success": False, "message": "Not subscribed to this category"}

    def get_user_subscriptions(self, user_id: str) -> List[str]:
        """Get user's subscribed categories"""
        if user_id in self.subscriptions["users"]:
            return self.subscriptions["users"][user_id].get("subscriptions", [])
        return []

    def add_push_token(self, user_id: str, token: str, platform: str = "web") -> Dict:
        """Add a push notification token for a user"""
        if user_id not in self.subscriptions["users"]:
            return {"success": False, "message": "User not registered"}
        
        tokens = self.subscriptions["users"][user_id]["notification_preferences"].get("push_tokens", [])
        
        # Check if token already exists
        for t in tokens:
            if t.get("token") == token:
                return {"success": False, "message": "Token already registered"}
        
        tokens.append({
            "token": token,
            "platform": platform,
            "added_at": datetime.now().isoformat()
        })
        
        self.subscriptions["users"][user_id]["notification_preferences"]["push_tokens"] = tokens
        
        if platform not in self.subscriptions["users"][user_id]["notification_preferences"]["platforms"]:
            self.subscriptions["users"][user_id]["notification_preferences"]["platforms"].append("push")
        
        self._save_subscriptions()
        return {"success": True, "message": f"Push token added for {platform}"}

    def remove_push_token(self, user_id: str, token: str) -> Dict:
        """Remove a push notification token"""
        if user_id not in self.subscriptions["users"]:
            return {"success": False, "message": "User not registered"}
        
        tokens = self.subscriptions["users"][user_id]["notification_preferences"].get("push_tokens", [])
        tokens = [t for t in tokens if t.get("token") != token]
        
        self.subscriptions["users"][user_id]["notification_preferences"]["push_tokens"] = tokens
        self._save_subscriptions()
        return {"success": True, "message": "Push token removed"}

    async def fetch_news(
        self, 
        category: str = "general", 
        country: str = "us",
        limit: int = 10
    ) -> List[Dict]:
        """Fetch news for a specific category"""
        articles = []
        
        # Check cache first
        cache_key = f"{category}_{country}"
        if cache_key in self.news_cache.get("articles", {}):
            cached = self.news_cache["articles"][cache_key]
            last_updated = datetime.fromisoformat(cached.get("last_updated", "2020-01-01"))
            if (datetime.now() - last_updated).total_seconds() < 3600:  # 1 hour cache
                return cached.get("articles", [])[:limit]

        # Try fetching from free news APIs
        try:
            # Using GNews API (free tier available)
            if self.gnews_api_key:
                url = f"https://gnews.io/api/v4/topics/{category}"
                params = {
                    "lang": "en",
                    "country": country,
                    "max": limit,
                    "apikey": self.gnews_api_key
                }
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    articles = [
                        {
                            "title": article.get("title", ""),
                            "description": article.get("description", ""),
                            "content": article.get("content", ""),
                            "url": article.get("url", ""),
                            "image": article.get("image", ""),
                            "publishedAt": article.get("publishedAt", ""),
                            "source": article.get("source", {}).get("name", "")
                        }
                        for article in data.get("articles", [])
                    ]
            
            # Fallback to NewsAPI if GNews didn't work
            if not articles and self.newsapi_key:
                url = "https://newsapi.org/v2/top-headlines"
                params = {
                    "category": category if category != "general" else "general",
                    "country": country,
                    "pageSize": limit,
                    "apiKey": self.newsapi_key
                }
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    articles = [
                        {
                            "title": article.get("title", ""),
                            "description": article.get("description", ""),
                            "content": article.get("content", ""),
                            "url": article.get("url", ""),
                            "urlToImage": article.get("urlToImage", ""),
                            "publishedAt": article.get("publishedAt", ""),
                            "source": article.get("source", {}).get("name", "")
                        }
                        for article in data.get("articles", [])
                    ]
        except Exception as e:
            logger.error(f"Error fetching news: {e}")

        # If no external API, generate sample news
        if not articles:
            articles = self._generate_sample_news(category, country, limit)

        # Cache the results
        if "articles" not in self.news_cache:
            self.news_cache["articles"] = {}
        
        self.news_cache["articles"][cache_key] = {
            "articles": articles,
            "last_updated": datetime.now().isoformat()
        }
        self._save_news_cache()

        return articles

    def _generate_sample_news(self, category: str, country: str, limit: int) -> List[Dict]:
        """Generate sample news for demo purposes"""
        sample_templates = {
            "technology": [
                {"title": "AI Revolutionizes Healthcare Industry", "description": "New AI systems help doctors diagnose diseases faster and more accurately."},
                {"title": "Quantum Computing Breakthrough", "description": "Scientists achieve major milestone in quantum error correction."},
                {"title": "5G Networks Expand Global Coverage", "description": "Telecom companies announce expanded 5G services in rural areas."},
            ],
            "finance": [
                {"title": "Stock Markets Reach New Highs", "description": "Major indices surge amid positive economic data."},
                {"title": "Cryptocurrency Regulations Updated", "description": "New guidelines for digital asset trading announced."},
                {"title": "Central Bank Interest Rate Decision", "description": "Federal Reserve announces monetary policy update."},
            ],
            "ai": [
                {"title": "GPT-5 Announcement Expected", "description": "AI research labs hint at next generation language models."},
                {"title": "Robotics Industry Growth Accelerates", "description": "Automation adoption increases across manufacturing sectors."},
                {"title": "AI Ethics Guidelines Released", "description": "International body establishes AI development standards."},
            ],
            "nepal": [
                {"title": "Tourism Industry Recovery in Nepal", "description": "Number of international visitors increases significantly."},
                {"title": "Hydropower Projects Progress", "description": "New hydroelectric projects add capacity to national grid."},
                {"title": "Agricultural Innovation in Nepal", "description": "Modern farming techniques help increase crop yields."},
            ],
            "india": [
                {"title": "Digital India Initiative Expands", "description": "More government services now available online."},
                {"title": "Economic Growth Projections", "description": "India's GDP growth exceeds analyst expectations."},
                {"title": "Technology Hub Development", "description": "New startup incubators launch in major cities."},
            ],
        }
        
        country_names = {"us": "USA", "np": "Nepal", "in": "India", "uk": "UK"}
        
        templates = sample_templates.get(category, sample_templates.get("technology", []))
        articles = []
        
        for i, template in enumerate(templates[:limit]):
            articles.append({
                "title": template["title"],
                "description": template["description"],
                "content": template["description"] + f" More details to follow from {country_names.get(country, 'around the world')}.",
                "url": f"https://example.com/news/{category}/{i+1}",
                "image": "",
                "publishedAt": datetime.now().isoformat(),
                "source": f"{country_names.get(country, 'Global')} News"
            })
        
        return articles

    def get_daily_digest(
        self, 
        user_id: str,
        limit_per_category: int = 5
    ) -> Dict:
        """Generate daily digest for a user"""
        if user_id not in self.subscriptions["users"]:
            return {"success": False, "message": "User not registered"}
        
        user = self.subscriptions["users"][user_id]
        subscriptions = user.get("subscriptions", [])
        
        if not subscriptions:
            return {"success": False, "message": "No subscriptions found"}
        
        digest = {
            "user_id": user_id,
            "generated_at": datetime.now().isoformat(),
            "categories": []
        }
        
        country = user.get("country", "us")
        
        for category in subscriptions:
            articles = asyncio.run(self.fetch_news(category, country, limit_per_category))
            digest["categories"].append({
                "category": category,
                "articles": articles
            })
        
        return {"success": True, "digest": digest}

    def get_available_categories(self) -> List[Dict]:
        """Get list of available news categories"""
        return self.available_categories

    def get_all_subscriptions(self) -> Dict:
        """Get all subscriptions (admin)"""
        return self.subscriptions


# Global instance
news_subscription_manager = NewsSubscriptionManager()


def get_news_subscription_manager() -> NewsSubscriptionManager:
    """Get the news subscription manager instance"""
    return news_subscription_manager
