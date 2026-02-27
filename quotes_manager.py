"""
Chat&Talk GPT - Quotes Manager
Motivational quotes using ZenQuotes API
"""
import json
import logging
import urllib.request
import urllib.error
import random
from typing import Dict, Any, List, Optional

logger = logging.getLogger("QuotesManager")

# ZenQuotes API base URL
ZENQUOTES_API_BASE = "https://zenquotes.io/api"


class QuotesManager:
    """
    Motivational quotes manager using ZenQuotes API
    Features:
    - Get random inspirational quotes
    - Get multiple quotes
    - Get today's quote
    """
    
    # API endpoints
    API_RANDOM = f"{ZENQUOTES_API_BASE}/random"
    API_TODAY = f"{ZENQUOTES_API_BASE}/today"
    API_QUOTE = f"{ZENQUOTES_API_BASE}/quote"
    
    def __init__(self):
        """Initialize quotes manager"""
        self._quotes_cache = []
        logger.info("QuotesManager initialized")
    
    def _make_request(self, url: str) -> Optional[Any]:
        """
        Make HTTP request to API
        
        Args:
            url: Full URL to request
        
        Returns:
            JSON response
        """
        try:
            # ZenQuotes requires a User-Agent header
            request = urllib.request.Request(url)
            request.add_header("User-Agent", "Chat&TalkGPT/1.0")
            
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data
        except urllib.error.URLError as e:
            logger.error(f"API request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse API response: {e}")
            return None
    
    def _format_quote(self, quote_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format quote data into consistent structure
        
        Args:
            quote_data: Raw quote from API
        
        Returns:
            Formatted quote
        """
        return {
            "id": quote_data.get("id", random.randint(1000, 9999)),
            "quote": quote_data.get("q", quote_data.get("quote", "")),
            "author": quote_data.get("a", quote_data.get("author", "Unknown")),
            "source": quote_data.get("s", "")
        }
    
    def get_random_quote(self) -> Dict[str, Any]:
        """
        Get one random inspirational quote
        
        Returns:
            Dictionary with quote data
        """
        data = self._make_request(self.API_RANDOM)
        
        if data and isinstance(data, list) and len(data) > 0:
            quote = self._format_quote(data[0])
            logger.info(f"Retrieved random quote by {quote['author']}")
            return {
                "success": True,
                "quote": quote
            }
        
        # Fallback quote
        fallback = self._get_fallback_quote()
        return {
            "success": True,
            "quote": fallback,
            "fallback": True
        }
    
    def get_quotes(self, limit: int = 5) -> Dict[str, Any]:
        """
        Get multiple inspirational quotes
        
        Args:
            limit: Number of quotes to retrieve
        
        Returns:
            Dictionary with quotes array
        """
        # ZenQuotes free API returns 1 quote at a time for random
        # We make multiple requests to get multiple quotes
        limit = min(max(1, limit), 10)
        
        quotes = []
        for _ in range(limit):
            data = self._make_request(self.API_RANDOM)
            if data and isinstance(data, list) and len(data) > 0:
                quote = self._format_quote(data[0])
                quotes.append(quote)
        
        if quotes:
            logger.info(f"Retrieved {len(quotes)} quotes")
            return {
                "success": True,
                "quotes": quotes,
                "count": len(quotes)
            }
        
        # Fallback
        fallbacks = self._get_fallback_quotes(limit)
        return {
            "success": True,
            "quotes": fallbacks,
            "count": len(fallbacks),
            "fallback": True
        }
    
    def get_today_quote(self) -> Dict[str, Any]:
        """
        Get today's inspirational quote
        
        Returns:
            Dictionary with today's quote
        """
        data = self._make_request(self.API_TODAY)
        
        if data and isinstance(data, list) and len(data) > 0:
            quote = self._format_quote(data[0])
            logger.info(f"Retrieved today's quote by {quote['author']}")
            return {
                "success": True,
                "quote": quote,
                "is_today": True
            }
        
        # Fallback to random quote
        return self.get_random_quote()
    
    def _get_fallback_quote(self) -> Dict[str, Any]:
        """Get a fallback quote when API is unavailable"""
        fallback_quotes = [
            {"id": 1, "quote": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
            {"id": 2, "quote": "Innovation distinguishes between a leader and a follower.", "author": "Steve Jobs"},
            {"id": 3, "quote": "Stay hungry, stay foolish.", "author": "Steve Jobs"},
            {"id": 4, "quote": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt"},
            {"id": 5, "quote": "It is during our darkest moments that we must focus to see the light.", "author": "Aristotle"},
            {"id": 6, "quote": "The best time to plant a tree was 20 years ago. The second best time is now.", "author": "Chinese Proverb"},
            {"id": 7, "quote": "Your time is limited, don't waste it living someone else's life.", "author": "Steve Jobs"},
            {"id": 8, "quote": "The only impossible journey is the one you never begin.", "author": "Tony Robbins"},
            {"id": 9, "quote": "Success is not final, failure is not fatal: it is the courage to continue that counts.", "author": "Winston Churchill"},
            {"id": 10, "quote": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
            {"id": 11, "quote": "The greatest glory in living lies not in never falling, but in rising every time we fall.", "author": "Nelson Mandela"},
            {"id": 12, "quote": "Life is what happens when you're busy making other plans.", "author": "John Lennon"},
            {"id": 13, "quote": "The way to get started is to quit talking and begin doing.", "author": "Walt Disney"},
            {"id": 14, "quote": "If life were predictable it would cease to be life, and be without flavor.", "author": "Eleanor Roosevelt"},
            {"id": 15, "quote": "Spread love everywhere you go. Let no one ever come to you without leaving happier.", "author": "Mother Teresa"}
        ]
        return random.choice(fallback_quotes)
    
    def _get_fallback_quotes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get fallback quotes when API is unavailable"""
        fallback_quotes = [
            {"id": 1, "quote": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
            {"id": 2, "quote": "Innovation distinguishes between a leader and a follower.", "author": "Steve Jobs"},
            {"id": 3, "quote": "Stay hungry, stay foolish.", "author": "Steve Jobs"},
            {"id": 4, "quote": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt"},
            {"id": 5, "quote": "It is during our darkest moments that we must focus to see the light.", "author": "Aristotle"},
            {"id": 6, "quote": "The best time to plant a tree was 20 years ago. The second best time is now.", "author": "Chinese Proverb"},
            {"id": 7, "quote": "Your time is limited, don't waste it living someone else's life.", "author": "Steve Jobs"},
            {"id": 8, "quote": "The only impossible journey is the one you never begin.", "author": "Tony Robbins"},
            {"id": 9, "quote": "Success is not final, failure is not fatal: it is the courage to continue that counts.", "author": "Winston Churchill"},
            {"id": 10, "quote": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"}
        ]
        return fallback_quotes[:limit]


# For testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    quotes = QuotesManager()
    
    # Test getting random quote
    print("Getting random quote...")
    result = quotes.get_random_quote()
    if result.get("success"):
        q = result["quote"]
        print(f'"{q["quote"]}"')
        print(f"- {q["author"]}")
    
    # Test getting today's quote
    print("\nGetting today's quote...")
    result = quotes.get_today_quote()
    if result.get("success"):
        q = result["quote"]
        print(f'"{q["quote"]}"')
        print(f"- {q["author"]}")
    
    # Test getting multiple quotes
    print("\nGetting 3 quotes...")
    result = quotes.get_quotes(3)
    if result.get("success"):
        for q in result["quotes"]:
            print(f'  - "{q["quote"][:50]}..." - {q["author"]}')
