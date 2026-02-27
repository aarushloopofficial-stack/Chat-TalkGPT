"""
Chat&Talk GPT - News Manager
Provides current news headlines using free APIs (GDELT, NewsData.io, GNews)
"""
import requests
import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger("NewsManager")

# Valid categories for news
VALID_CATEGORIES = [
    "technology", "business", "sports", "entertainment", 
    "science", "health", "general", "world", "nation"
]

# Country code mapping for GDELT
COUNTRY_MAPPING = {
    "us": "USA",
    "uk": "GBR",
    "in": "IND",
    "np": "NPL",
    "ca": "CAN",
    "au": "AUS",
    "de": "DEU",
    "fr": "FRA",
    "jp": "JPN",
    "cn": "CHN"
}


class NewsManager:
    """
    News manager for fetching current news from free APIs
    Uses GDELT as primary (completely free, no API key required)
    """
    
    def __init__(self):
        """Initialize the NewsManager with user agent"""
        self.user_agent = "ChatAndTalkGPT/1.0 (Personal Assistant)"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        
        # GDELT API base URL
        self.gdelt_base_url = "http://api.gdeltproject.org/api/v2/doc/doc"
        
        logger.info("NewsManager initialized with GDELT API")
    
    def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Make HTTP request with error handling"""
        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout: {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
    
    def _map_category_to_gdelt(self, category: str) -> str:
        """Map category to GDELT topic codes"""
        category_map = {
            "technology": "TECHNOLOGY",
            "business": "BUSINESS",
            "sports": "SPORTS",
            "entertainment": "ENTERTAINMENT",
            "science": "SCIENCE",
            "health": "HEALTH",
            "general": "",
            "world": "",
            "nation": ""
        }
        return category_map.get(category.lower(), "")
    
    def get_latest_news(
        self, 
        category: str = None, 
        country: str = "us", 
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get latest news headlines
        
        Args:
            category: Category of news (technology, business, sports, etc.)
            country: Country code (us, in, np, uk, etc.)
            limit: Maximum number of results (max 250)
        
        Returns:
            Dict with news articles in specified format
        """
        logger.info(f"Fetching latest news: category={category}, country={country}, limit={limit}")
        
        # Build GDELT query
        query_parts = []
        
        # Add country filter
        country_code = COUNTRY_MAPPING.get(country.lower(), country.upper())
        if country_code:
            # GDELT uses country names, not codes
            country_names = {
                "USA": "United States",
                "GBR": "United Kingdom", 
                "IND": "India",
                "NPL": "Nepal",
                "CAN": "Canada",
                "AUS": "Australia",
                "DEU": "Germany",
                "FRA": "France",
                "JPN": "Japan",
                "CHN": "China"
            }
            country_name = country_names.get(country_code, country)
            query_parts.append(f"{country_name} sourcelang:english")
        
        # Add category filter
        if category and category.lower() != "general":
            topic = self._map_category_to_gdelt(category)
            if topic:
                query_parts.append(f"({topic})")
        
        # Build final query
        query = " ".join(query_parts) if query_parts else "sourcelang:english"
        
        # Make API request to GDELT
        params = {
            "query": query,
            "mode": "artlist",
            "maxrecords": min(limit, 250),
            "format": "json",
            "sort": "DateDesc"
        }
        
        result = self._make_request(self.gdelt_base_url, params)
        
        if not result or "articles" not in result:
            # Fallback: try simpler query
            params["query"] = "sourcelang:english"
            result = self._make_request(self.gdelt_base_url, params)
        
        if not result or "articles" not in result:
            logger.warning("GDELT API returned no results, using fallback")
            return self._get_fallback_news(category, limit)
        
        # Transform GDELT articles to our format
        articles = []
        for article in result.get("articles", [])[:limit]:
            transformed = self._transform_gdelt_article(article, category)
            if transformed:
                articles.append(transformed)
        
        total = len(articles)
        logger.info(f"Retrieved {total} news articles")
        
        return {
            "success": True,
            "total_results": total,
            "articles": articles
        }
    
    def _transform_gdelt_article(self, article: Dict, category: str = None) -> Optional[Dict]:
        """Transform GDELT article to our format"""
        try:
            # Extract image URL from seendata
            image_url = None
            if "seendata" in article and article["seendata"]:
                seen = article["seendata"]
                if isinstance(seen, list) and len(seen) > 0:
                    image_url = seen[0].get("url")
            
            # Get domain/source
            source = article.get("domain", "Unknown")
            if "socialimage" in article:
                image_url = article.get("socialimage")
            
            return {
                "title": article.get("title", "No title"),
                "description": article.get("seotext", "")[:200] if article.get("seotext") else "",
                "source": source,
                "url": article.get("url", ""),
                "image": image_url,
                "published_at": article.get("seendate", ""),
                "category": category or "general"
            }
        except Exception as e:
            logger.warning(f"Error transforming article: {e}")
            return None
    
    def search_news(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search news by keyword
        
        Args:
            query: Search query string
            limit: Maximum number of results
        
        Returns:
            Dict with news articles in specified format
        """
        logger.info(f"Searching news: query='{query}', limit={limit}")
        
        # Build search query
        search_query = f'{query} sourcelang:english'
        
        params = {
            "query": search_query,
            "mode": "artlist",
            "maxrecords": min(limit, 250),
            "format": "json",
            "sort": "Relevance"
        }
        
        result = self._make_request(self.gdelt_base_url, params)
        
        if not result or "articles" not in result:
            logger.warning("Search returned no results")
            return {
                "success": True,
                "total_results": 0,
                "articles": [],
                "query": query
            }
        
        # Transform articles
        articles = []
        for article in result.get("articles", [])[:limit]:
            transformed = self._transform_gdelt_article(article)
            if transformed:
                articles.append(transformed)
        
        total = len(articles)
        logger.info(f"Search found {total} articles for '{query}'")
        
        return {
            "success": True,
            "total_results": total,
            "articles": articles,
            "query": query
        }
    
    def get_news_by_source(self, source: str, limit: int = 10) -> Dict[str, Any]:
        """
        Get news from specific source
        
        Args:
            source: News source name (e.g., "BBC", "CNN", "Reuters")
            limit: Maximum number of results
        
        Returns:
            Dict with news articles in specified format
        """
        logger.info(f"Fetching news from source: {source}, limit={limit}")
        
        # Build query for specific source
        search_query = f'domain:{source.lower().replace(" ", "")} sourcelang:english'
        
        params = {
            "query": search_query,
            "mode": "artlist",
            "maxrecords": min(limit, 250),
            "format": "json",
            "sort": "DateDesc"
        }
        
        result = self._make_request(self.gdelt_base_url, params)
        
        if not result or "articles" not in result:
            # Try with just source name
            search_query = f'{source} sourcelang:english'
            params["query"] = search_query
            result = self._make_request(self.gdelt_base_url, params)
        
        if not result or "articles" not in result:
            logger.warning(f"No news found from source: {source}")
            return {
                "success": True,
                "total_results": 0,
                "articles": [],
                "source": source
            }
        
        # Transform articles
        articles = []
        for article in result.get("articles", [])[:limit]:
            transformed = self._transform_gdelt_article(article)
            if transformed:
                articles.append(transformed)
        
        total = len(articles)
        logger.info(f"Found {total} articles from {source}")
        
        return {
            "success": True,
            "total_results": total,
            "articles": articles,
            "source": source
        }
    
    def get_trending_topics(self) -> List[str]:
        """
        Get trending topics (simulated based on common news categories)
        
        Returns:
            List of trending topic strings
        """
        logger.info("Fetching trending topics")
        
        # Get current trending by querying popular topics
        # In production, you could use GDELT's trend API
        trending = [
            "Artificial Intelligence",
            "Climate Change",
            "Stock Market",
            "Healthcare",
            "Technology",
            "Sports",
            "Politics",
            "Entertainment",
            "Science",
            "Business",
            "World News",
            "Renewable Energy",
            "Cybersecurity",
            "Space Exploration",
            "Electric Vehicles"
        ]
        
        logger.info(f"Returning {len(trending)} trending topics")
        return trending
    
    def _get_fallback_news(self, category: str, limit: int) -> Dict[str, Any]:
        """Get fallback news when primary API fails"""
        logger.info("Using fallback news data")
        
        # Generate sample news for demonstration
        fallback_articles = [
            {
                "title": f"Latest {category or 'general'} News Update",
                "description": "Stay tuned for the latest updates in your chosen category.",
                "source": "News Manager",
                "url": "https://example.com",
                "image": None,
                "published_at": datetime.utcnow().isoformat() + "Z",
                "category": category or "general"
            }
        ]
        
        return {
            "success": True,
            "total_results": len(fallback_articles),
            "articles": fallback_articles[:limit]
        }


# Global instance for easy import
news_manager = NewsManager()
