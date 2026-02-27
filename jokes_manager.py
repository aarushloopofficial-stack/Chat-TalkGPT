"""
Chat&Talk GPT - Jokes Manager
Joke fetching system using Official Joke API
"""
import json
import logging
import urllib.request
import urllib.parse
import urllib.error
import random
from typing import Dict, Any, List, Optional

logger = logging.getLogger("JokesManager")

# Official Joke API base URL
JOKE_API_BASE = "https://official-joke-api.appspot.com"


class JokesManager:
    """
    Jokes manager using Official Joke API
    Features:
    - Get random jokes
    - Get multiple jokes
    - Get jokes by type (general, programming, knock-knock)
    """
    
    # API endpoints
    API_RANDOM_JOKE = f"{JOKE_API_BASE}/random_joke"
    API_RANDOM_TEN = f"{JOKE_API_BASE}/random_ten"
    API_JOKES_BY_TYPE = f"{JOKE_API_BASE}/jokes/{{type}}/ten"
    
    # Valid joke types
    VALID_TYPES = ["general", "programming", "knock_knock"]
    
    def __init__(self):
        """Initialize jokes manager"""
        self._joke_cache = []
        logger.info("JokesManager initialized")
    
    def _make_request(self, url: str) -> Optional[Any]:
        """
        Make HTTP request to API
        
        Args:
            url: Full URL to request
        
        Returns:
            JSON response
        """
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data
        except urllib.error.URLError as e:
            logger.error(f"API request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse API response: {e}")
            return None
    
    def _format_joke(self, joke_data: Dict[str, Any], joke_type: str = "general") -> Dict[str, Any]:
        """
        Format joke data into consistent structure
        
        Args:
            joke_data: Raw joke from API
            joke_type: Type of joke
        
        Returns:
            Formatted joke
        """
        # Handle different response formats
        if "setup" in joke_data and "punchline" in joke_data:
            # Standard joke format
            return {
                "id": joke_data.get("id"),
                "type": joke_type,
                "setup": joke_data.get("setup", ""),
                "punchline": joke_data.get("punchline", ""),
                "format": "two_part"
            }
        elif "joke" in joke_data:
            # Single line joke
            return {
                "id": joke_data.get("id"),
                "type": joke_type,
                "joke": joke_data.get("joke", ""),
                "format": "single"
            }
        else:
            # Fallback
            return {
                "id": joke_data.get("id", random.randint(1000, 9999)),
                "type": joke_type,
                "joke": str(joke_data),
                "format": "unknown"
            }
    
    def get_random_joke(self) -> Dict[str, Any]:
        """
        Get one random joke
        
        Returns:
            Dictionary with joke data
        """
        data = self._make_request(self.API_RANDOM_JOKE)
        
        if data:
            joke = self._format_joke(data, "general")
            logger.info(f"Retrieved random joke (ID: {joke['id']})")
            return {
                "success": True,
                "joke": joke
            }
        
        # Fallback jokes
        fallback = self._get_fallback_joke()
        return {
            "success": True,
            "joke": fallback,
            "fallback": True
        }
    
    def get_jokes(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get multiple random jokes
        
        Args:
            limit: Number of jokes to retrieve
        
        Returns:
            Dictionary with jokes array
        """
        # The API returns 10 jokes max
        limit = min(max(1, limit), 10)
        
        data = self._make_request(self.API_RANDOM_TEN)
        
        if data and isinstance(data, list):
            jokes = [self._format_joke(j, "general") for j in data[:limit]]
            logger.info(f"Retrieved {len(jokes)} random jokes")
            
            return {
                "success": True,
                "jokes": jokes,
                "count": len(jokes)
            }
        
        # Fallback
        fallbacks = self._get_fallback_jokes(limit)
        return {
            "success": True,
            "jokes": fallbacks,
            "count": len(fallbacks),
            "fallback": True
        }
    
    def get_jokes_by_type(self, joke_type: str = "general") -> Dict[str, Any]:
        """
        Get jokes by type
        
        Args:
            joke_type: "general", "programming", or "knock_knock"
        
        Returns:
            Dictionary with jokes array
        """
        # Normalize type name
        type_map = {
            "general": "general",
            "programming": "programming",
            "knock-knock": "knock_knock",
            "knock_knock": "knock_knock"
        }
        
        normalized_type = type_map.get(joke_type.lower(), "general")
        
        if normalized_type not in self.VALID_TYPES:
            return {
                "success": False,
                "error": f"Invalid type. Valid types: {self.VALID_TYPES}",
                "jokes": []
            }
        
        # Use the correct API endpoint
        url = f"{JOKE_API_BASE}/jokes/{normalized_type}/ten"
        data = self._make_request(url)
        
        if data and isinstance(data, list):
            jokes = [self._format_joke(j, normalized_type) for j in data]
            logger.info(f"Retrieved {len(jokes)} {normalized_type} jokes")
            
            return {
                "success": True,
                "jokes": jokes,
                "type": normalized_type,
                "count": len(jokes)
            }
        
        # Fallback
        fallbacks = self._get_fallback_jokes_by_type(normalized_type)
        return {
            "success": True,
            "jokes": fallbacks,
            "type": normalized_type,
            "count": len(fallbacks),
            "fallback": True
        }
    
    def _get_fallback_joke(self) -> Dict[str, Any]:
        """Get a fallback joke when API is unavailable"""
        fallback_jokes = [
            {"id": 1, "type": "general", "setup": "Why don't scientists trust atoms?", "punchline": "Because they make up everything!", "format": "two_part"},
            {"id": 2, "type": "general", "setup": "What do you call a fake noodle?", "punchline": "An impasta!", "format": "two_part"},
            {"id": 3, "type": "general", "setup": "Why did the scarecrow win an award?", "punchline": "Because he was outstanding in his field!", "format": "two_part"},
            {"id": 4, "type": "general", "setup": "What do you call a bear with no teeth?", "punchline": "A gummy bear!", "format": "two_part"},
            {"id": 5, "type": "programming", "setup": "Why do programmers prefer dark mode?", "punchline": "Because light attracts bugs!", "format": "two_part"},
            {"id": 6, "type": "programming", "setup": "How many programmers does it take to change a light bulb?", "punchline": "None, that's a hardware problem!", "format": "two_part"},
            {"id": 7, "type": "knock_knock", "setup": "Knock knock. Who's there?", "punchline": "Interrupting cow. Interrupting co-", "format": "two_part"},
            {"id": 8, "type": "knock_knock", "setup": "Knock knock. Who's there?", "punchline": "Lettuce. Lettuce who?", "format": "two_part"}
        ]
        return random.choice(fallback_jokes)
    
    def _get_fallback_jokes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get fallback jokes when API is unavailable"""
        fallback = [
            {"id": 1, "type": "general", "setup": "Why don't scientists trust atoms?", "punchline": "Because they make up everything!", "format": "two_part"},
            {"id": 2, "type": "general", "setup": "What do you call a fake noodle?", "punchline": "An impasta!", "format": "two_part"},
            {"id": 3, "type": "general", "setup": "Why did the scarecrow win an award?", "punchline": "Because he was outstanding in his field!", "format": "two_part"},
            {"id": 4, "type": "general", "setup": "What do you call a bear with no teeth?", "punchline": "A gummy bear!", "format": "two_part"},
            {"id": 5, "type": "general", "setup": "What do you call a sleeping dinosaur?", "punchline": "A dino-snore!", "format": "two_part"},
            {"id": 6, "type": "programming", "setup": "Why do programmers prefer dark mode?", "punchline": "Because light attracts bugs!", "format": "two_part"},
            {"id": 7, "type": "programming", "setup": "How many programmers does it take to change a light bulb?", "punchline": "None, that's a hardware problem!", "format": "two_part"},
            {"id": 8, "type": "programming", "setup": "Why was the JavaScript developer sad?", "punchline": "Because he didn't Node how to Express himself!", "format": "two_part"},
            {"id": 9, "type": "knock_knock", "setup": "Knock knock. Who's there?", "punchline": "Interrupting cow. Interrupting co-", "format": "two_part"},
            {"id": 10, "type": "knock_knock", "setup": "Knock knock. Who's there?", "punchline": "Lettuce. Lettuce who?", "format": "two_part"}
        ]
        return fallback[:limit]
    
    def _get_fallback_jokes_by_type(self, joke_type: str) -> List[Dict[str, Any]]:
        """Get fallback jokes by type"""
        fallbacks = {
            "general": [
                {"id": 1, "type": "general", "setup": "Why don't scientists trust atoms?", "punchline": "Because they make up everything!", "format": "two_part"},
                {"id": 2, "type": "general", "setup": "What do you call a fake noodle?", "punchline": "An impasta!", "format": "two_part"},
                {"id": 3, "type": "general", "setup": "Why did the scarecrow win an award?", "punchline": "Because he was outstanding in his field!", "format": "two_part"}
            ],
            "programming": [
                {"id": 1, "type": "programming", "setup": "Why do programmers prefer dark mode?", "punchline": "Because light attracts bugs!", "format": "two_part"},
                {"id": 2, "type": "programming", "setup": "How many programmers does it take to change a light bulb?", "punchline": "None, that's a hardware problem!", "format": "two_part"},
                {"id": 3, "type": "programming", "setup": "Why was the JavaScript developer sad?", "punchline": "Because he didn't Node how to Express himself!", "format": "two_part"}
            ],
            "knock_knock": [
                {"id": 1, "type": "knock_knock", "setup": "Knock knock. Who's there?", "punchline": "Interrupting cow. Interrupting co-", "format": "two_part"},
                {"id": 2, "type": "knock_knock", "setup": "Knock knock. Who's there?", "punchline": "Lettuce. Lettuce who?", "format": "two_part"},
                {"id": 3, "type": "knock_knock", "setup": "Knock knock. Who's there?", "punchline": "Boo. Boo who?", "format": "two_part"}
            ]
        }
        return fallbacks.get(joke_type, fallbacks["general"])


# For testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    jokes = JokesManager()
    
    # Test getting random joke
    print("Getting random joke...")
    result = jokes.get_random_joke()
    if result.get("success"):
        joke = result["joke"]
        if joke.get("format") == "two_part":
            print(f"Q: {joke['setup']}")
            print(f"A: {joke['punchline']}")
        else:
            print(f"Joke: {joke.get('joke', 'N/A')}")
    
    # Test getting multiple jokes
    print("\nGetting 3 jokes...")
    result = jokes.get_jokes(3)
    if result.get("success"):
        for j in result["jokes"]:
            print(f"  - {j.get('setup', j.get('joke', ''))[:50]}...")
    
    # Test getting jokes by type
    print("\nGetting programming jokes...")
    result = jokes.get_jokes_by_type("programming")
    if result.get("success"):
        for j in result["jokes"][:2]:
            print(f"  - {j.get('setup')[:40]}...")
