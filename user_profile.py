"""
Chat&Talk GPT - User Profile Manager
Handles user information including name for personalized responses with SQLite storage
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from database import init_database, database

logger = logging.getLogger("UserProfile")


class UserProfile:
    """Manages user profile and preferences with SQLite storage"""
    
    _db_initialized = False
    
    def __init__(self, profile_file: str = "memory/user_profile.json"):
        self.profile_file = Path(profile_file)
        self.profile = self._load_profile()
        self._ensure_db_initialized()
        
        logger.info(f"UserProfile initialized for: {self.get_name()}")
    
    def _ensure_db_initialized(self):
        """Ensure database is initialized"""
        if not UserProfile._db_initialized:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if not loop.is_running():
                    loop.run_until_complete(init_database())
            except:
                pass
            UserProfile._db_initialized = True
    
    def _load_profile(self) -> Dict[str, Any]:
        """Load user profile from database or file"""
        # Try to load from database first
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            
            if loop.is_running():
                # Can't await here, use file fallback
                return self._load_from_file()
            else:
                # Try database
                profile = loop.run_until_complete(
                    database.fetch_one("SELECT * FROM users WHERE id = 1")
                )
                if profile:
                    settings = json.loads(profile.get('settings', '{}'))
                    return {
                        "name": profile.get('name', ''),
                        "email": profile.get('email', ''),
                        "first_use": profile.get('created_at', ''),
                        "last_use": profile.get('updated_at', ''),
                        "total_chats": 0,
                        "preferred_voice": settings.get('preferred_voice', 'abinash'),
                        "preferred_language": settings.get('preferred_language', 'english'),
                        "theme": settings.get('theme', 'dark'),
                        "academic_interests": settings.get('academic_interests', []),
                        "weak_subjects": settings.get('weak_subjects', []),
                        "learning_memories": settings.get('learning_memories', {})
                    }
        except Exception as e:
            logger.warning(f"Could not load profile from database: {e}")
        
        # Fallback to file
        return self._load_from_file()
    
    def _load_from_file(self) -> Dict[str, Any]:
        """Load from JSON file"""
        try:
            if self.profile_file.exists():
                with open(self.profile_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    logger.info("User profile loaded from file")
                    return data
        except Exception as e:
            logger.warning(f"Could not load profile: {e}")
        
        return {
            "name": "",
            "email": "",
            "first_use": datetime.now().isoformat(),
            "last_use": datetime.now().isoformat(),
            "total_chats": 0,
            "preferred_voice": "edge_en_us_guy",
            "preferred_language": "english",
            "theme": "dark",
            "academic_interests": [],
            "weak_subjects": [],
            "learning_memories": {},
            # Voice preferences
            "voice_settings": {
                "speed": 1.0,
                "pitch": 1.0
            },
            "voice_profiles": {
                "default": "edge_en_us_guy",
                "casual": "edge_en_us_jenny",
                "professional": "edge_en_us_guy",
                "storytelling": "edge_en_us_aria"
            },
            # Webhook configuration
            "webhooks_enabled": False,
            "webhook_retry_attempts": 3,
            "webhook_timeout": 30
        }
    
    def add_memory(self, key: str, value: Any):
        """Add a key fact to user's learning memory"""
        self.profile["learning_memories"][key] = value
        self._save_profile()

    def get_memories_summary(self) -> str:
        """Get a summary of what the AI knows about the student's learning progress"""
        memories = self.profile.get("learning_memories", {})
        if not memories:
            return ""
        
        summary = "\nKnown about student:"
        for k, v in memories.items():
            summary += f"\n- {k}: {v}"
        return summary
    
    def _save_profile(self):
        """Save user profile to database and file"""
        # Save to file as backup
        try:
            self.profile["last_use"] = datetime.now().isoformat()
            self.profile_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.profile_file, "w", encoding="utf-8") as f:
                json.dump(self.profile, f, indent=2, ensure_ascii=False)
            logger.info("User profile saved to file")
        except Exception as e:
            logger.error(f"Error saving profile to file: {e}")
        
        # Also save to database
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            
            voice_settings = self.profile.get("voice_settings", {"speed": 1.0, "pitch": 1.0})
            voice_profiles = self.profile.get("voice_profiles", {
                "default": "edge_en_us_guy",
                "casual": "edge_en_us_jenny",
                "professional": "edge_en_us_guy",
                "storytelling": "edge_en_us_aria"
            })
            
            settings = json.dumps({
                "preferred_voice": self.profile.get("preferred_voice", "edge_en_us_guy"),
                "preferred_language": self.profile.get("preferred_language", "english"),
                "theme": self.profile.get("theme", "dark"),
                "academic_interests": self.profile.get("academic_interests", []),
                "weak_subjects": self.profile.get("weak_subjects", []),
                "learning_memories": self.profile.get("learning_memories", {}),
                "voice_settings": voice_settings,
                "voice_profiles": voice_profiles
            })
            
            if loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    database.execute(
                        """INSERT OR REPLACE INTO users (id, name, settings, updated_at)
                           VALUES (1, ?, ?, CURRENT_TIMESTAMP)""",
                        (self.profile.get("name", ""), settings)
                    ),
                    loop
                )
            else:
                loop.run_until_complete(
                    database.execute(
                        """INSERT OR REPLACE INTO users (id, name, settings, updated_at)
                           VALUES (1, ?, ?, CURRENT_TIMESTAMP)""",
                        (self.profile.get("name", ""), settings)
                    )
                )
        except Exception as e:
            logger.warning(f"Could not save profile to database: {e}")
    
    def get_voice_preferences(self) -> Dict[str, Any]:
        """Get user's voice preferences"""
        return {
            "preferred_voice": self.profile.get("preferred_voice", "edge_en_us_guy"),
            "preferred_language": self.profile.get("preferred_language", "english"),
            "voice_settings": self.profile.get("voice_settings", {"speed": 1.0, "pitch": 1.0}),
            "voice_profiles": self.profile.get("voice_profiles", {
                "default": "edge_en_us_guy",
                "casual": "edge_en_us_jenny",
                "professional": "edge_en_us_guy",
                "storytelling": "edge_en_us_aria"
            })
        }
    
    def set_voice_preferences(
        self, 
        voice_id: str = None, 
        language: str = None,
        speed: float = None, 
        pitch: float = None,
        voice_profiles: Dict[str, str] = None
    ):
        """Set user's voice preferences"""
        if voice_id:
            self.profile["preferred_voice"] = voice_id
        if language:
            self.profile["preferred_language"] = language
        
        # Update voice settings
        voice_settings = self.profile.get("voice_settings", {"speed": 1.0, "pitch": 1.0})
        if speed is not None:
            voice_settings["speed"] = speed
        if pitch is not None:
            voice_settings["pitch"] = pitch
        self.profile["voice_settings"] = voice_settings
        
        # Update voice profiles
        if voice_profiles:
            current_profiles = self.profile.get("voice_profiles", {})
            current_profiles.update(voice_profiles)
            self.profile["voice_profiles"] = current_profiles
        
        self._save_profile()
        logger.info("Voice preferences updated")
    
    def get_name(self) -> str:
        """Get user's name"""
        return self.profile.get("name", "")
    
    def set_name(self, name: str):
        """Set user's name"""
        if name.strip():
            self.profile["name"] = name.strip()
            self._save_profile()
            logger.info(f"User name set to: {name}")
    
    def has_name(self) -> bool:
        """Check if user has set their name"""
        return bool(self.profile.get("name", "").strip())
    
    def get_theme(self) -> str:
        """Get user's theme preference"""
        return self.profile.get("theme", "dark")
    
    def set_theme(self, theme: str):
        """Set user's theme preference"""
        if theme in ["light", "dark", "system"]:
            self.profile["theme"] = theme
            self._save_profile()
            logger.info(f"User theme set to: {theme}")
    
    def increment_chats(self):
        """Increment chat counter"""
        self.profile["total_chats"] = self.profile.get("total_chats", 0) + 1
        self._save_profile()
    
    def get_fallback_message(self) -> str:
        """Get personalized fallback message with user's name"""
        user_name = self.get_name()
        
        if user_name:
            return f"Sorry {user_name} 🙏 I am not able to answer this question but I suggest you go to this website and gives you good answer or feedback."
        else:
            return "Sorry 🙏 I am not able to answer this question but I suggest you go to this website and gives you good answer or feedback."
    
    def get_fallback_suggestions(self) -> list:
        """Get suggested websites for fallback"""
        return [
            {"name": "Google", "url": "https://www.google.com"},
            {"name": "Wikipedia", "url": "https://www.wikipedia.org"},
            {"name": "ChatGPT", "url": "https://chat.openai.com"},
            {"name": "YouTube", "url": "https://www.youtube.com"}
        ]


# Initialize global user profile
user_profile = UserProfile()
