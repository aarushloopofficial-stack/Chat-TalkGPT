"""
Chat&Talk GPT - YouTube Manager
YouTube video search and information retrieval
Supports YouTube Data API v3 with fallback to web scraping
"""
import json
import logging
import os
import re
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("YouTubeManager")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests library not available, YouTube features limited")


class YouTubeManager:
    """
    YouTube video management system
    Features:
    - Search videos using YouTube Data API v3
    - Get detailed video information
    - Fetch trending videos (with fallback scraping)
    - Async-compatible methods
    """
    
    # YouTube API endpoints
    SEARCH_API_URL = "https://www.googleapis.com/youtube/v3/search"
    VIDEOS_API_URL = "https://www.googleapis.com/youtube/v3/videos"
    
    # Valid day values
    VALID_DAYS = [" sunday","monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    
    def __init__(self):
        """Initialize YouTube manager with API key"""
        # Get API key from environment
        self.api_key = os.getenv("YOUTUBE_API_KEY", "")
        self.api_enabled = bool(self.api_key)
        
        if self.api_enabled:
            logger.info("YouTube API integration enabled")
        else:
            logger.info("YouTube API key not found, using fallback scraping mode")
        
        # Cache for trending videos
        self._trending_cache: List[Dict[str, Any]] = []
        self._trending_cache_time: Optional[datetime] = None
        self._cache_duration_minutes = 15
    
    def _is_cache_valid(self) -> bool:
        """Check if trending cache is still valid"""
        if not self._trending_cache or not self._trending_cache_time:
            return False
        elapsed = (datetime.now() - self._trending_cache_time).total_seconds() / 60
        return elapsed < self._cache_duration_minutes
    
    async def search_videos(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for videos on YouTube
        
        Args:
            query: Search query string
            limit: Maximum number of results (default: 10)
        
        Returns:
            List of video dictionaries with basic info
        """
        if not REQUESTS_AVAILABLE:
            logger.error("requests library not available")
            return []
        
        try:
            if self.api_enabled:
                return await self._search_videos_api(query, limit)
            else:
                return await self._search_videos_fallback(query, limit)
        except Exception as e:
            logger.error(f"Error searching videos: {e}")
            return []
    
    async def _search_videos_api(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search videos using YouTube Data API v3"""
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": min(limit, 50),
            "key": self.api_key
        }
        
        try:
            response = requests.get(self.SEARCH_API_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            videos = []
            for item in data.get("items", []):
                video = {
                    "id": item["id"].get("videoId", ""),
                    "title": item["snippet"].get("title", ""),
                    "description": item["snippet"].get("description", ""),
                    "channel_title": item["snippet"].get("channelTitle", ""),
                    "published_at": item["snippet"].get("publishedAt", ""),
                    "thumbnail": item["snippet"]["thumbnails"].get("medium", {}).get("url", "")
                }
                videos.append(video)
            
            logger.info(f"Found {len(videos)} videos for query: {query}")
            return videos
        
        except requests.exceptions.RequestException as e:
            logger.error(f"YouTube API request failed: {e}")
            # Fallback to scraping
            return await self._search_videos_fallback(query, limit)
    
    async def _search_videos_fallback(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Fallback search using web scraping (simulated)"""
        logger.info(f"Using fallback search for: {query}")
        
        # Since we can't easily scrape YouTube, return a placeholder
        # In use production, you might a YouTube scraper library
        return [{
            "id": "",
            "title": f"Search results for: {query}",
            "description": "YouTube API key required for full search functionality",
            "channel_title": "N/A",
            "published_at": "",
            "thumbnail": "",
            "note": "Configure YOUTUBE_API_KEY environment variable for full functionality"
        }]
    
    async def get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific video
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            Dictionary with video details or None if not found
        """
        if not REQUESTS_AVAILABLE:
            logger.error("requests library not available")
            return None
        
        if not video_id:
            logger.warning("Empty video ID provided")
            return None
        
        try:
            if self.api_enabled:
                return await self._get_video_info_api(video_id)
            else:
                return await self._get_video_info_fallback(video_id)
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return None
    
    async def _get_video_info_api(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get video info using YouTube Data API v3"""
        params = {
            "part": "snippet,statistics,contentDetails",
            "id": video_id,
            "key": self.api_key
        }
        
        try:
            response = requests.get(self.VIDEOS_API_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            items = data.get("items", [])
            if not items:
                logger.warning(f"Video not found: {video_id}")
                return None
            
            item = items[0]
            snippet = item.get("snippet", {})
            statistics = item.get("statistics", {})
            content_details = item.get("contentDetails", {})
            
            video = {
                "id": video_id,
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "channel_id": snippet.get("channelId", ""),
                "published_at": snippet.get("publishedAt", ""),
                "thumbnail": snippet["thumbnails"].get("high", {}).get("url", ""),
                "tags": snippet.get("tags", []),
                "category_id": snippet.get("categoryId", ""),
                "view_count": statistics.get("viewCount", "0"),
                "like_count": statistics.get("likeCount", "0"),
                "comment_count": statistics.get("commentCount", "0"),
                "duration": content_details.get("duration", ""),
                "dimension": content_details.get("dimension", ""),
                "definition": content_details.get("definition", ""),
                "url": f"https://www.youtube.com/watch?v={video_id}"
            }
            
            logger.info(f"Retrieved info for video: {video_id}")
            return video
        
        except requests.exceptions.RequestException as e:
            logger.error(f"YouTube API request failed: {e}")
            return await self._get_video_info_fallback(video_id)
    
    async def _get_video_info_fallback(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Fallback for getting video info"""
        return {
            "id": video_id,
            "title": f"Video: {video_id}",
            "description": "YouTube API key required for full video details",
            "channel_title": "N/A",
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "note": "Configure YOUTUBE_API_KEY environment variable for full functionality"
        }
    
    async def get_trending(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get trending videos from YouTube
        
        Args:
            limit: Maximum number of results (default: 10)
        
        Returns:
            List of trending video dictionaries
        """
        # Check cache first
        if self._is_cache_valid() and self._trending_cache:
            logger.info("Returning cached trending videos")
            return self._trending_cache[:limit]
        
        if not REQUESTS_AVAILABLE:
            logger.error("requests library not available")
            return []
        
        try:
            if self.api_enabled:
                videos = await self._get_trending_api(limit)
            else:
                videos = await self._get_trending_fallback(limit)
            
            # Update cache
            self._trending_cache = videos
            self._trending_cache_time = datetime.now()
            
            return videos
        
        except Exception as e:
            logger.error(f"Error getting trending videos: {e}")
            return self._trending_cache[:limit] if self._trending_cache else []
    
    async def _get_trending_api(self, limit: int) -> List[Dict[str, Any]]:
        """Get trending videos using YouTube Data API v3"""
        params = {
            "part": "snippet",
            "chart": "mostPopular",
            "regionCode": "US",
            "maxResults": min(limit, 50),
            "key": self.api_key
        }
        
        try:
            response = requests.get(self.VIDEOS_API_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            videos = []
            for item in data.get("items", []):
                snippet = item.get("snippet", {})
                video = {
                    "id": item.get("id", ""),
                    "title": snippet.get("title", ""),
                    "description": snippet.get("description", ""),
                    "channel_title": snippet.get("channelTitle", ""),
                    "channel_id": snippet.get("channelId", ""),
                    "published_at": snippet.get("publishedAt", ""),
                    "thumbnail": snippet["thumbnails"].get("medium", {}).get("url", ""),
                    "category": snippet.get("tags", [])[0] if snippet.get("tags") else "N/A",
                    "url": f"https://www.youtube.com/watch?v={item.get('id', '')}"
                }
                videos.append(video)
            
            logger.info(f"Retrieved {len(videos)} trending videos")
            return videos
        
        except requests.exceptions.RequestException as e:
            logger.error(f"YouTube API request failed: {e}")
            return await self._get_trending_fallback(limit)
    
    async def _get_trending_fallback(self, limit: int) -> List[Dict[str, Any]]:
        """Fallback for getting trending videos using web scraping"""
        logger.info("Using fallback trending method")
        
        # Try to scrape YouTube trending page
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(
                "https://www.youtube.com/feed/trending",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                # Parse HTML to extract video IDs
                video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', response.text)
                video_ids = list(dict.fromkeys(video_ids))[:limit]  # Remove duplicates
                
                # Get details for each video
                videos = []
                for vid in video_ids:
                    video_info = await self.get_video_info(vid)
                    if video_info:
                        videos.append(video_info)
                
                if videos:
                    return videos
        
        except Exception as e:
            logger.warning(f"Fallback scraping failed: {e}")
        
        # Return sample data if everything fails
        return [{
            "id": "dQw4w9WgXcQ",
            "title": "Sample Video - Configure API Key",
            "description": "Set YOUTUBE_API_KEY in your .env file for full YouTube functionality",
            "channel_title": "Chat&Talk GPT",
            "thumbnail": "",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }]
    
    def parse_duration(self, duration: str) -> str:
        """
        Parse ISO 8601 duration to human readable format
        
        Args:
            duration: ISO 8601 duration string (e.g., "PT1H30M45S")
        
        Returns:
            Human readable duration (e.g., "1:30:45")
        """
        if not duration:
            return "0:00"
        
        # Parse ISO 8601 duration
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return "0:00"
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    def format_view_count(self, count: str) -> str:
        """
        Format view count to human readable format
        
        Args:
            count: View count as string
        
        Returns:
            Formatted view count (e.g., "1.5M views")
        """
        try:
            num = int(count)
            if num >= 1_000_000:
                return f"{num / 1_000_000:.1f}M views"
            elif num >= 1_000:
                return f"{num / 1_000:.1f}K views"
            else:
                return f"{num} views"
        except (ValueError, TypeError):
            return "0 views"


# Singleton instance
_youtube_manager: Optional[YouTubeManager] = None


def get_youtube_manager() -> YouTubeManager:
    """Get or create YouTube manager singleton"""
    global _youtube_manager
    if _youtube_manager is None:
        _youtube_manager = YouTubeManager()
    return _youtube_manager
