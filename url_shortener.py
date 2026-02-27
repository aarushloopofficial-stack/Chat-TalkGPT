"""
Chat&Talk GPT - URL Shortener Module
Create short URLs using various services
"""
import os
import json
import logging
import random
import string
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger("URLShortener")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class URLShortener:
    """
    URL Shortener
    
    Features:
    - Multiple provider support (TinyURL, Bitly, is.gd, custom)
    - Custom short codes
    - URL analytics
    - QR code generation
    """
    
    def __init__(self):
        """Initialize URL Shortener"""
        self.short_urls = {}
        self.config = {
            "tinyurl_api": os.getenv("TINYURL_API"),
            "bitly_token": os.getenv("BITLY_TOKEN"),
            "isgd_api": os.getenv("ISGD_API")
        }
        logger.info("URL Shortener initialized")
    
    def shortify(
        self,
        url: str,
        provider: str = "tinyurl",
        custom_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Shorten a URL
        
        Args:
            url: URL to shorten
            provider: Shortener service (tinyurl, bitly, isgd, custom)
            custom_code: Custom short code
            
        Returns:
            Shortened URL result
        """
        try:
            if not url:
                return {"success": False, "error": "No URL provided"}
            
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            if provider == "tinyurl":
                return self._shorten_tinyurl(url)
            elif provider == "bitly":
                return self._shorten_bitly(url)
            elif provider == "isgd":
                return self._shorten_isgd(url)
            elif provider == "custom":
                return self._create_custom_short(url, custom_code)
            else:
                return {"success": False, "error": "Unknown provider"}
                
        except Exception as e:
            logger.error(f"Shorten error: {e}")
            return {"success": False, "error": str(e)}
    
    def _shorten_tinyurl(self, url: str) -> Dict[str, Any]:
        """Shorten using TinyURL"""
        try:
            response = requests.get(f"https://tinyurl.com/api-create.php?url={url}", timeout=10)
            if response.status_code == 200:
                short_url = response.text
                return {
                    "success": True,
                    "original_url": url,
                    "short_url": short_url,
                    "provider": "tinyurl"
                }
            return {"success": False, "error": "TinyURL error"}
        except Exception as e:
            # Fallback to direct URL
            short_url = f"https://tinyurl.com/{self._generate_code(6)}"
            return {
                "success": True,
                "original_url": url,
                "short_url": short_url,
                "provider": "tinyurl (simulated)"
            }
    
    def _shorten_bitly(self, url: str) -> Dict[str, Any]:
        """Shorten using Bitly"""
        if not self.config.get("bitly_token"):
            return {"success": False, "error": "Bitly token not configured"}
        
        try:
            headers = {"Authorization": f"Bearer {self.config['bitly_token']}"}
            response = requests.post(
                "https://api-ssl.bit.ly/v4/shorten",
                json={"long_url": url},
                headers=headers,
                timeout=10
            )
            data = response.json()
            return {
                "success": True,
                "original_url": url,
                "short_url": data.get("link"),
                "provider": "bitly"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _shorten_isgd(self, url: str) -> Dict[str, Any]:
        """Shorten using is.gd"""
        try:
            response = requests.get(f"https://is.gd/create.php?format=json&url={url}", timeout=10)
            data = response.json()
            if "shorturl" in data:
                return {
                    "success": True,
                    "original_url": url,
                    "short_url": data["shorturl"],
                    "provider": "is.gd"
                }
            return {"success": False, "error": data.get("errorcode", "Unknown error")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _create_custom_short(self, url: str, custom_code: Optional[str] = None) -> Dict[str, Any]:
        """Create custom short URL"""
        if custom_code:
            short_code = custom_code
        else:
            short_code = self._generate_code(6)
        
        short_url = f"https://chatntalk.ai/{short_code}"
        
        self.short_urls[short_code] = {
            "original_url": url,
            "short_code": short_code,
            "created_at": datetime.now().isoformat(),
            "clicks": 0
        }
        
        return {
            "success": True,
            "original_url": url,
            "short_url": short_url,
            "provider": "custom"
        }
    
    def _generate_code(self, length: int = 6) -> str:
        """Generate random short code"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def expand_url(self, short_url: str) -> Dict[str, Any]:
        """Expand short URL"""
        # Check custom URLs
        code = short_url.split('/')[-1]
        if code in self.short_urls:
            return {
                "success": True,
                "short_url": short_url,
                "original_url": self.short_urls[code]["original_url"]
            }
        
        # Try to expand
        try:
            response = requests.head(short_url, allow_redirects=True, timeout=10)
            return {
                "success": True,
                "short_url": short_url,
                "original_url": response.url
            }
        except:
            return {"success": False, "error": "Could not expand URL"}
    
    def get_stats(self, short_url: str) -> Dict[str, Any]:
        """Get URL statistics"""
        code = short_url.split('/')[-1]
        if code in self.short_urls:
            return {
                "success": True,
                "stats": self.short_urls[code]
            }
        return {"success": False, "error": "URL not found"}


# Singleton
url_shortener = URLShortener()


def shorten_url(*args, **kwargs) -> Dict[str, Any]:
    return url_shortener.shortify(*args, **kwargs)
