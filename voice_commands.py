"""
Chat&Talk GPT - Voice Command System
Enhanced voice commands like Alexa/Google Assistant with Dynamic App Opening
"""
import re
import json
import logging
import subprocess
import webbrowser
import urllib.parse
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

logger = logging.getLogger("VoiceCommands")

# Comprehensive app list with website URLs and Play Store package names
DYNAMIC_APPS = {
    # AI & Chatbots
    "perplexity": {
        "name": "Perplexity",
        "website": "https://www.perplexity.ai",
        "playstore": "https://play.google.com/store/apps/details?id=ai.perplexity.app",
        "package": "ai.perplexity.app",
        "keywords": ["perplexity", "perplexity ai"]
    },
    "gemini": {
        "name": "Google Gemini",
        "website": "https://gemini.google.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.google.ai",
        "package": "com.google.ai",
        "keywords": ["gemini", "google gemini", "bard", "google bard"]
    },
    "claude": {
        "name": "Claude",
        "website": "https://claude.ai",
        "playstore": "https://play.google.com/store/apps/details?id=ai.anthropic.claude",
        "package": "ai.anthropic.claude",
        "keywords": ["claude", "claude ai", "anthropic"]
    },
    "chatgpt": {
        "name": "ChatGPT",
        "website": "https://chat.openai.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.openai.chatgpt",
        "package": "com.openai.chatgpt",
        "keywords": ["chatgpt", "chat gpt", "gpt", "openai"]
    },
    "higgsfield": {
        "name": "Higgsfield AI",
        "website": "https://higgsfield.ai",
        "playstore": "https://play.google.com/store/apps/details?id=ai.higgsfield.app",
        "package": "ai.higgsfield.app",
        "keywords": ["higgsfield", "higgsfield ai", "video generator"]
    },
    "deepseek": {
        "name": "DeepSeek",
        "website": "https://www.deepseek.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.deepseek.chat",
        "package": "com.deepseek.chat",
        "keywords": ["deepseek", "deep seek", "deepseek ai"]
    },
    
    # Search & Browsers
    "google": {
        "name": "Google",
        "website": "https://www.google.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.google.android.googlequicksearchbox",
        "package": "com.google.android.googlequicksearchbox",
        "keywords": ["google", "search"]
    },
    "brave": {
        "name": "Brave",
        "website": "https://brave.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.brave.browser",
        "package": "com.brave.browser",
        "keywords": ["brave", "brave browser"]
    },
    "chrome": {
        "name": "Chrome",
        "website": "https://www.google.com/chrome",
        "playstore": "https://play.google.com/store/apps/details?id=com.android.chrome",
        "package": "com.android.chrome",
        "keywords": ["chrome", "google chrome", "browser"]
    },
    
    # Social Media
    "facebook": {
        "name": "Facebook",
        "website": "https://www.facebook.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.facebook.katana",
        "package": "com.facebook.katana",
        "keywords": ["facebook", "fb"]
    },
    "messenger": {
        "name": "Messenger",
        "website": "https://www.messenger.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.facebook.orca",
        "package": "com.facebook.orca",
        "keywords": ["messenger", "facebook messenger", "dm"]
    },
    "meta ai": {
        "name": "Meta AI",
        "website": "https://www.meta.ai",
        "playstore": "https://play.google.com/store/apps/details?id=com.meta.ai",
        "package": "com.meta.ai",
        "keywords": ["meta ai", "meta"]
    },
    "instagram": {
        "name": "Instagram",
        "website": "https://www.instagram.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.instagram.android",
        "package": "com.instagram.android",
        "keywords": ["instagram", "insta"]
    },
    "whatsapp": {
        "name": "WhatsApp",
        "website": "https://www.whatsapp.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.whatsapp",
        "package": "com.whatsapp",
        "keywords": ["whatsapp", "wa"]
    },
    "twitter": {
        "name": "Twitter/X",
        "website": "https://twitter.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.twitter.android",
        "package": "com.twitter.android",
        "keywords": ["twitter", "x", "tweet"]
    },
    "reddit": {
        "name": "Reddit",
        "website": "https://www.reddit.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.reddit.frontpage",
        "package": "com.reddit.frontpage",
        "keywords": ["reddit"]
    },
    "telegram": {
        "name": "Telegram",
        "website": "https://telegram.org",
        "playstore": "https://play.google.com/store/apps/details?id=org.telegram.messenger",
        "package": "org.telegram.messenger",
        "keywords": ["telegram", "tg"]
    },
    "discord": {
        "name": "Discord",
        "website": "https://discord.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.discord",
        "package": "com.discord",
        "keywords": ["discord"]
    },
    "linkedin": {
        "name": "LinkedIn",
        "website": "https://www.linkedin.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.linkedin.android",
        "package": "com.linkedin.android",
        "keywords": ["linkedin"]
    },
    
    # Video & Streaming
    "youtube": {
        "name": "YouTube",
        "website": "https://www.youtube.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.google.android.youtube",
        "package": "com.google.android.youtube",
        "keywords": ["youtube", "yt"]
    },
    "youtube music": {
        "name": "YouTube Music",
        "website": "https://music.youtube.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.google.android.apps.youtube.music",
        "package": "com.google.android.apps.youtube.music",
        "keywords": ["youtube music", "yt music"]
    },
    "netflix": {
        "name": "Netflix",
        "website": "https://www.netflix.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.netflix.mediaclient",
        "package": "com.netflix.mediaclient",
        "keywords": ["netflix"]
    },
    "spotify": {
        "name": "Spotify",
        "website": "https://open.spotify.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.spotify.music",
        "package": "com.spotify.music",
        "keywords": ["spotify", "music"]
    },
    
    # Food & Delivery
    "zomato": {
        "name": "Zomato",
        "website": "https://www.zomato.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.application.zomato",
        "package": "com.application.zomato",
        "keywords": ["zomato", "food"]
    },
    "swiggy": {
        "name": "Swiggy",
        "website": "https://www.swiggy.com",
        "playstore": "https://play.google.com/store/apps/details?id=in.swiggy.android",
        "package": "in.swiggy.android",
        "keywords": ["swiggy", "food delivery"]
    },
    "blinkit": {
        "name": "Blinkit",
        "website": "https://www.blinkit.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.blinkit.app",
        "package": "com.blinkit.app",
        "keywords": ["blinkit", "quick commerce", "groceries"]
    },
    "zepto": {
        "name": "Zepto",
        "website": "https://www.zepto.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.zepto.app",
        "package": "com.zepto.app",
        "keywords": ["zepto", "quick delivery"]
    },
    "magicpin": {
        "name": "Magicpin",
        "website": "https://www.magicpin.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.magicpin.app",
        "package": "com.magicpin.app",
        "keywords": ["magicpin", "deals", "offers"]
    },
    "instamart": {
        "name": "Instamart",
        "website": "https://www.instamart.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.swiggy.instamart",
        "package": "com.swiggy.instamart",
        "keywords": ["instamart", "swiggy instamart"]
    },
    "flipkart": {
        "name": "Flipkart",
        "website": "https://www.flipkart.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.flipkart.android",
        "package": "com.flipkart.android",
        "keywords": ["flipkart", "shopping"]
    },
    "amazon": {
        "name": "Amazon",
        "website": "https://www.amazon.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.amazon.mShop.android.shopping",
        "package": "com.amazon.mShop.android.shopping",
        "keywords": ["amazon", "shopping"]
    },
    "daraz": {
        "name": "Daraz",
        "website": "https://www.daraz.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.daraz.android",
        "package": "com.daraz.android",
        "keywords": ["daraz", "shopping"]
    },
    
    # Video Editing
    "capcut": {
        "name": "CapCut",
        "website": "https://www.capcut.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.lemon.lvcc",
        "package": "com.lemon.lvcc",
        "keywords": ["capcut", "video editor", "video editing"]
    },
    "alight motion": {
        "name": "Alight Motion",
        "website": "https://alight.motion",
        "playstore": "https://play.google.com/store/apps/details?id=com.alight.motion",
        "package": "com.alight.motion",
        "keywords": ["alight motion", "motion graphics", "animation"]
    },
    "vn": {
        "name": "VN Video Editor",
        "website": "https://vnvideoeditor.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.vlog.video.editor",
        "package": "com.vlog.video.editor",
        "keywords": ["vn", "video editor", "vlog"]
    },
    "filmora": {
        "name": "Filmora",
        "website": "https://filmora.wondershare.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.wondershare.filmorago",
        "package": "com.wondershare.filmorago",
        "keywords": ["filmora", "video editor"]
    },
    "剪映": {
        "name": "CapCut China",
        "website": "https://www.capcut.cn",
        "playstore": "https://play.google.com/store/apps/details?id=com.lemon.clipv",
        "package": "com.lemon.clipv",
        "keywords": ["剪映", "capcut china"]
    },
    
    # Other Popular Apps
    "zoom": {
        "name": "Zoom",
        "website": "https://zoom.us",
        "playstore": "https://play.google.com/store/apps/details?id=us.zoom.videomeetings",
        "package": "us.zoom.videomeetings",
        "keywords": ["zoom", "video call", "meeting"]
    },
    "whatsapp business": {
        "name": "WhatsApp Business",
        "website": "https://www.whatsapp.com/business",
        "playstore": "https://play.google.com/store/apps/details?id=com.whatsapp.w4b",
        "package": "com.whatsapp.w4b",
        "keywords": ["whatsapp business", "wa business"]
    },
    "slack": {
        "name": "Slack",
        "website": "https://slack.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.Slack",
        "package": "com.Slack",
        "keywords": ["slack", "workspace"]
    },
    "notion": {
        "name": "Notion",
        "website": "https://www.notion.so",
        "playstore": "https://play.google.com/store/apps/details?id=notion.id",
        "package": "notion.id",
        "keywords": ["notion", "notes", "productivity"]
    },
    "canva": {
        "name": "Canva",
        "website": "https://www.canva.com",
        "playstore": "https://play.google.com/store/apps/details?id=com.canva.editor",
        "package": "com.canva.editor",
        "keywords": ["canva", "design", "graphic"]
    },
}


class DynamicAppOpener:
    """Handles dynamic app opening with user preference selection"""
    
    def __init__(self):
        self.pending_app_request = {}  # Store pending requests for user response
    
    def find_app(self, query: str) -> Optional[Dict]:
        """Find an app in the dynamic apps list based on query"""
        query_lower = query.lower().strip()
        
        # Check direct matches and keyword matches
        for app_key, app_info in DYNAMIC_APPS.items():
            # Check if query matches app key
            if app_key in query_lower or query_lower in app_key:
                return app_info
            
            # Check keywords
            for keyword in app_info.get("keywords", []):
                if keyword in query_lower or query_lower in keyword:
                    return app_info
        
        return None
    
    def is_app_installed(self, package_name: str) -> bool:
        """Check if an Android app is installed (Android only)"""
        try:
            # Try to check via adb (Android Debug Bridge)
            result = subprocess.run(
                ["adb", "shell", "pm", "list", "packages", package_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            return package_name in result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            # If adb is not available or check fails, return False
            return False
    
    def check_app_status(self, app_info: Dict) -> Tuple[str, str]:
        """Check if app is installed and return status"""
        package = app_info.get("package", "")
        if package and self.is_app_installed(package):
            return "installed", "App is installed on your device"
        return "not_installed", "App is not installed"
    
    def create_preference_prompt(self, app_info: Dict, user_name: str = "User") -> Dict[str, Any]:
        """Create a prompt for user to choose app or website format"""
        app_name = app_info.get("name", "")
        install_status, status_msg = self.check_app_status(app_info)
        
        # Build the response
        prompt = f"{app_name}, Sir, which form would you like to use - App form or Website form?"
        
        if install_status == "installed":
            prompt += f" {status_msg}, so I can open it directly."
        else:
            prompt += f" {status_msg}."
        
        return {
            "action": "app_preference",
            "app_name": app_name,
            "app_info": app_info,
            "install_status": install_status,
            "prompt": prompt,
            "speak": prompt,
            "options": [
                {
                    "id": "app",
                    "label": "📱 App Form" + (" (Already Installed)" if install_status == "installed" else " (Open Play Store)"),
                    "description": "Open in mobile app" if install_status == "installed" else "Open Play Store to install"
                },
                {
                    "id": "website",
                    "label": "🌐 Website Form",
                    "description": "Open official website"
                }
            ],
            "response": prompt
        }
    
    def open_in_app_form(self, app_info: Dict) -> Dict[str, Any]:
        """Open app in App form - either installed app or Play Store"""
        app_name = app_info.get("name", "")
        install_status, _ = self.check_app_status(app_info)
        
        try:
            if install_status == "installed":
                # Open the installed app
                package = app_info.get("package", "")
                if package:
                    # Try to open via intent
                    intent_url = f"intent://{package}#Intent;scheme=package;end"
                    webbrowser.open(intent_url)
                    
                    response = f"Opening {app_name} app for you."
                    return {
                        "action": "open_app",
                        "app_name": app_name,
                        "format": "app_installed",
                        "response": response,
                        "speak": response
                    }
            
            # If not installed, open Play Store
            playstore_url = app_info.get("playstore", "")
            if playstore_url:
                webbrowser.open(playstore_url)
                
                response = f"Opening {app_name} on Play Store for you to install."
                return {
                    "action": "open_playstore",
                    "app_name": app_name,
                    "format": "playstore",
                    "url": playstore_url,
                    "response": response,
                    "speak": response
                }
            
            # Fallback to website if no Play Store URL
            return self.open_in_website_form(app_info)
            
        except Exception as e:
            logger.error(f"Error opening app form: {e}")
            return {
                "action": "error",
                "response": f"I couldn't open {app_name}. Please try again.",
                "speak": f"I couldn't open {app_name}. Please try again."
            }
    
    def open_in_website_form(self, app_info: Dict) -> Dict[str, Any]:
        """Open app in Website form - Google search for official website"""
        app_name = app_info.get("name", "")
        
        try:
            website_url = app_info.get("website", "")
            
            if website_url:
                # Open direct website
                webbrowser.open(website_url)
                response = f"Opening {app_name} website for you."
                return {
                    "action": "open_website",
                    "app_name": app_name,
                    "format": "website",
                    "url": website_url,
                    "response": response,
                    "speak": response
                }
            else:
                # Fallback to Google search
                search_query = f"{app_name} official website"
                search_url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
                webbrowser.open(search_url)
                
                response = f"Searching for {app_name} official website."
                return {
                    "action": "search_website",
                    "app_name": app_name,
                    "format": "search",
                    "url": search_url,
                    "response": response,
                    "speak": response
                }
                
        except Exception as e:
            logger.error(f"Error opening website form: {e}")
            return {
                "action": "error",
                "response": f"I couldn't open {app_name}. Please try again.",
                "speak": f"I couldn't open {app_name}. Please try again."
            }
    
    def process_user_choice(self, app_info: Dict, choice: str) -> Dict[str, Any]:
        """Process user's choice for app or website format"""
        choice_lower = choice.lower().strip()
        
        if "app" in choice_lower or "application" in choice_lower:
            return self.open_in_app_form(app_info)
        elif "website" in choice_lower or "web" in choice_lower or "site" in choice_lower:
            return self.open_in_website_form(app_info)
        else:
            # Default to website if unclear
            return self.open_in_website_form(app_info)


# Initialize dynamic app opener
dynamic_app_opener = DynamicAppOpener()


# Voice command patterns - like Alexa skills
VOICE_COMMANDS = {
    # App/Website Opening Commands
    "open": {
        "patterns": [
            r"open\s+(.+)",  # "open youtube"
            r"launch\s+(.+)",  # "launch chrome"
            r"start\s+(.+)",   # "start vscode"
            r"go\s+to\s+(.+)", # "go to google"
            r"visit\s+(.+)",    # "visit instagram"
        ],
        "apps": {
            "youtube": "https://www.youtube.com",
            "youtube music": "https://music.youtube.com",
            "instagram": "https://www.instagram.com",
            "whatsapp": "https://web.whatsapp.com",
            "whatsapp web": "https://web.whatsapp.com",
            "facebook": "https://www.facebook.com",
            "twitter": "https://twitter.com",
            "x": "https://twitter.com",
            "telegram": "https://web.telegram.org",
            "discord": "https://discord.com",
            "reddit": "https://www.reddit.com",
            "linkedin": "https://www.linkedin.com",
            "netflix": "https://www.netflix.com",
            "spotify": "https://open.spotify.com",
            "chatgpt": "https://chat.openai.com",
            "gpt": "https://chat.openai.com",
            "google": "https://www.google.com",
            "bing": "https://www.bing.com",
            "amazon": "https://www.amazon.com",
            "wikipedia": "https://www.wikipedia.org",
        },
        "browsers": {
            "chrome": "browser:chrome",
            "google chrome": "browser:chrome",
            "brave": "browser:brave",
            "firefox": "browser:firefox",
            "edge": "browser:edge",
            "microsoft edge": "browser:edge",
        },
        "apps_local": {
            "vscode": "app:vscode",
            "visual studio code": "app:vscode",
            "vs code": "app:vscode",
            "notepad": "app:notepad",
            "calculator": "app:calculator",
            "terminal": "app:terminal",
            "cmd": "app:terminal",
            "powershell": "app:powershell",
            "explorer": "app:explorer",
            "file explorer": "app:explorer",
            "antigravity": "app:antigravity",
        }
    },
    
    # Search Commands
    "search": {
        "patterns": [
            r"search\s+for\s+(.+)",     # "search for weather"
            r"search\s+(.+)",            # "search python tutorial"
            r"find\s+(.+)",              # "find nearest restaurant"
            r"look\s+up\s+(.+)",         # "look up definition"
        ],
    },
    
    # System Control Commands
    "system": {
        "patterns": [
            r"play\s+(.+)",              # "play music"
            r"pause\s+(.+)",             # "pause"
            r"stop\s+(.+)",              # "stop"
            r"resume\s+(.+)",            # "resume"
            r"volume\s+(up|down|mute)", # "volume up"
        ],
    },
    
    # Information Commands
    "info": {
        "patterns": [
            r"what\s+is\s+(.+)",         # "what is AI"
            r"who\s+is\s+(.+)",          # "who is Elon Musk"
            r"tell\s+me\s+about\s+(.+)", # "tell me about Python"
            r"define\s+(.+)",             # "define machine learning"
            r"how\s+do\s+i\s+(.+)",      # "how do I make coffee"
            r"what\s+time\s+is\s+it",    # "what time is it"
            r"what\s+is\s+the\s+date",   # "what is the date"
        ],
    },
    
    # Smart Home Commands (placeholders)
    "smart_home": {
        "patterns": [
            r"turn\s+on\s+(.+)",         # "turn on lights"
            r"turn\s+off\s+(.+)",        # "turn off fan"
            r"set\s+(.+)",               # "set thermostat to 72"
        ],
    },
    
    # Settings Commands
    "settings": {
        "patterns": [
            r"change\s+(voice|language|mode)\s+to\s+(.+)",
            r"set\s+(voice|language|mode)\s+to\s+(.+)",
            r"use\s+(male|female)\s+voice",
        ],
    },
    
    # Conversation Commands
    "conversation": {
        "patterns": [
            r"hello|hi|hey|namaste|नमस्ते",  # Greeting
            r"thank\s+you|thanks",             # Thanks
            r"good\s+morning",                 # Morning
            r"good\s+afternoon",              # Afternoon
            r"good\s+evening",                 # Evening
            r"good\s+night",                   # Night
        ],
    }
}

# App paths for local apps
APP_PATHS = {
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "brave": "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
    "edge": "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    "firefox": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
    "vscode": "C:\\Users\\User\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "terminal": "cmd.exe",
    "powershell": "powershell.exe",
    "explorer": "explorer.exe",
}


class VoiceCommandProcessor:
    """Process voice commands like Alexa/Google Assistant"""
    
    def __init__(self):
        self.last_response = ""
        self.command_history = []
        logger.info("VoiceCommandProcessor initialized")
    
    def process_command(self, text: str) -> Dict[str, Any]:
        """
        Process a voice command and return action + response
        """
        text_lower = text.lower().strip()
        
        logger.info(f"Processing voice command: {text}")
        
        # Add to history
        self.command_history.append({
            "command": text,
            "timestamp": datetime.now().isoformat()
        })
        
        # Check each command category
        result = self._check_open_commands(text_lower)
        if result:
            return result
            
        result = self._check_system_commands(text_lower)
        if result:
            return result
            
        result = self._check_settings_commands(text_lower)
        if result:
            return result
            
        result = self._check_conversation_commands(text_lower)
        if result:
            return result
        
        # If no command matched, return None to use AI
        return None
    
    def _check_open_commands(self, text: str) -> Optional[Dict[str, Any]]:
        """Check for app/website opening commands"""
        
        # First, check for dynamic apps (new system with preference selection)
        app_info = dynamic_app_opener.find_app(text)
        if app_info:
            # Check if this is a user response to our preference question
            if self._is_user_choice_response(text):
                return self._process_choice_response(text)
            
            # Otherwise, ask user for preference
            user_name = self._get_user_name()
            return dynamic_app_opener.create_preference_prompt(app_info, user_name)
        
        # Direct app patterns
        for pattern in VOICE_COMMANDS["open"]["patterns"]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                target = match.group(1).strip()
                
                # Check websites
                websites = VOICE_COMMANDS["open"]["apps"]
                for app_name, url in websites.items():
                    if app_name in target:
                        return self._open_url(url, app_name)
                
                # Check browsers
                browsers = VOICE_COMMANDS["open"]["browsers"]
                for browser_name, browser_cmd in browsers.items():
                    if browser_name in target:
                        return self._open_browser(target.replace(browser_name, "").strip())
                
                # Check local apps
                local_apps = VOICE_COMMANDS["open"]["apps_local"]
                for app_name, app_cmd in local_apps.items():
                    if app_name in target:
                        return self._open_app(app_name)
        
        return None
    
    def _open_url(self, url: str, app_name: str) -> Dict[str, Any]:
        """Open a URL in browser"""
        try:
            webbrowser.open(url)
            response = f"Opening {app_name} now. Is there anything else?"
            self.last_response = response
            return {
                "action": "open_url",
                "target": url,
                "app_name": app_name,
                "response": response,
                "speak": response
            }
        except Exception as e:
            logger.error(f"Error opening URL: {e}")
            return {
                "action": "error",
                "response": f"I couldn't open {app_name}. Please try again.",
                "speak": f"I couldn't open {app_name}. Please try again."
            }
    
    def _is_user_choice_response(self, text: str) -> bool:
        """Check if user is responding to app/website preference question"""
        choice_keywords = ["app", "website", "web", "site", "application", "form", 
                         "open app", "open website", "use app", "use website",
                         "first option", "second option", "option 1", "option 2"]
        return any(keyword in text.lower() for keyword in choice_keywords)
    
    def _process_choice_response(self, text: str) -> Dict[str, Any]:
        """Process user's choice for app or website format"""
        # Check if we have a pending request stored
        if hasattr(self, 'pending_app_request') and self.pending_app_request:
            app_info = self.pending_app_request.get("app_info")
            if app_info:
                self.pending_app_request = {}
                return dynamic_app_opener.process_user_choice(app_info, text)
        
        # Default: try website
        return {
            "action": "error",
            "response": "I'm not sure which format you'd prefer. Please try again.",
            "speak": "I'm not sure which format you'd prefer. Please try again."
        }
    
    def _get_user_name(self) -> str:
        """Get user's name for personalized prompts"""
        # Try to load from user profile file
        try:
            import os
            profile_path = os.path.join(os.path.dirname(__file__), '..', 'memory', 'user_profile.json')
            if os.path.exists(profile_path):
                import json
                with open(profile_path, 'r') as f:
                    user_data = json.load(f)
                    if user_data.get('name'):
                        return user_data['name'].split()[0]
        except:
            pass
        return "User"
    
    def _open_browser(self, url: str = "") -> Dict[str, Any]:
        """Open browser with optional URL"""
        browser = "chrome"  # Default
        
        try:
            if "brave" in url:
                browser = "brave"
            elif "edge" in url:
                browser = "edge"
            elif "firefox" in url:
                browser = "firefox"
            
            # If there's a URL, open it
            if url and "http" not in url:
                url = f"https://www.google.com/search?q={url.replace(' ', '+')}"
            
            subprocess.Popen([APP_PATHS.get(browser, "chrome.exe"), url if url else ""])
            
            response = f"Opening {browser.capitalize()} for you."
            self.last_response = response
            return {
                "action": "open_browser",
                "browser": browser,
                "url": url,
                "response": response,
                "speak": response
            }
        except Exception as e:
            logger.error(f"Error opening browser: {e}")
            return {
                "action": "error",
                "response": "I couldn't open the browser. Please check if it's installed.",
                "speak": "I couldn't open the browser. Please check if it's installed."
            }
    
    def _open_app(self, app_name: str) -> Dict[str, Any]:
        """Open a local application"""
        try:
            # Get app path
            app_path = APP_PATHS.get(app_name, "")
            
            if app_name == "antigravity":
                # Special case for antigravity (VSCode with specific folder)
                subprocess.Popen([
                    APP_PATHS.get("vscode"),
                    "--folder-uri",
                    "https://github.com/ajmnz/antigravity"
                ])
            elif app_path:
                subprocess.Popen([app_path])
            else:
                subprocess.Popen([app_name])
            
            response = f"Launching {app_name} now. Is there anything else?"
            self.last_response = response
            return {
                "action": "open_app",
                "app": app_name,
                "response": response,
                "speak": response
            }
        except Exception as e:
            logger.error(f"Error opening app: {e}")
            return {
                "action": "error",
                "response": f"I couldn't open {app_name}. The application might not be installed.",
                "speak": f"I couldn't open {app_name}. The application might not be installed."
            }
    
    def _check_system_commands(self, text: str) -> Optional[Dict[str, Any]]:
        """Check for system control commands"""
        
        patterns = VOICE_COMMANDS["system"]["patterns"]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                action = match.group(1) if match.groups() else ""
                
                if "volume" in text:
                    if "up" in text:
                        return self._volume_up()
                    elif "down" in text:
                        return self._volume_down()
                    elif "mute" in text:
                        return self._volume_mute()
                
                if "play" in text:
                    return {
                        "action": "play",
                        "target": action,
                        "response": f"Playing {action}.",
                        "speak": f"Playing {action}."
                    }
                
                if "pause" in text or "stop" in text:
                    return {
                        "action": "pause",
                        "response": "Paused.",
                        "speak": "Paused."
                    }
        
        return None
    
    def _volume_up(self) -> Dict[str, Any]:
        """Increase system volume"""
        # This would require platform-specific code
        return {
            "action": "volume_up",
            "response": "Volume increased.",
            "speak": "Volume increased."
        }
    
    def _volume_down(self) -> Dict[str, Any]:
        """Decrease system volume"""
        return {
            "action": "volume_down",
            "response": "Volume decreased.",
            "speak": "Volume decreased."
        }
    
    def _volume_mute(self) -> Dict[str, Any]:
        """Mute system volume"""
        return {
            "action": "volume_mute",
            "response": "Volume muted.",
            "speak": "Volume muted."
        }
    
    def _check_settings_commands(self, text: str) -> Dict[str, Any]:
        """Check for settings change commands"""
        
        patterns = VOICE_COMMANDS["settings"]["patterns"]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                setting = match.group(1) if match.groups() else ""
                value = match.group(2) if len(match.groups()) > 1 else ""
                
                if "voice" in setting:
                    voice = "male" if "male" in value else "female"
                    return {
                        "action": "set_voice",
                        "value": voice,
                        "response": f"Voice changed to {value}.",
                        "speak": f"Voice changed to {value}."
                    }
                
                if "language" in setting:
                    lang_map = {"english": "en", "hindi": "hi", "nepali": "ne"}
                    lang = lang_map.get(value, "en")
                    return {
                        "action": "set_language",
                        "value": lang,
                        "response": f"Language changed to {value}.",
                        "speak": f"Language changed to {value}."
                    }
        
        return None
    
    def _check_conversation_commands(self, text: str) -> Optional[Dict[str, Any]]:
        """Check for conversation commands (greetings, etc.)"""
        
        greetings = ["hello", "hi", "hey", "namaste", "नमस्ते"]
        thanks = ["thank you", "thanks", "धन्यवाद", "धन्यवाद"]
        
        for g in greetings:
            if g in text:
                return {
                    "action": "greeting",
                    "response": "Hello! How can I help you today?",
                    "speak": "Hello! How can I help you today?"
                }
        
        for t in thanks:
            if t in text:
                return {
                    "action": "thanks",
                    "response": "You're welcome! Is there anything else?",
                    "speak": "You're welcome! Is there anything else?"
                }
        
        if "schedule" in text or "calendar" in text:
            import urllib.parse
            # Basic extraction of title from "schedule [title]"
            title = text.split("schedule")[-1].split("on")[0].strip() or "New Study Session"
            cal_url = f"https://www.google.com/calendar/render?action=TEMPLATE&text={urllib.parse.quote(title)}&details=Scheduled+by+ChatAndTalk+GPT"
            webbrowser.open(cal_url)
            return {
                "action": "calendar",
                "response": f"Opening Google Calendar to schedule: {title}",
                "speak": f"I've opened the calendar for you to schedule {title}"
            }
        
        return None
    
    def get_command_history(self) -> List[Dict]:
        """Get command history"""
        return self.command_history
    
    def get_last_response(self) -> str:
        """Get last spoken response"""
        return self.last_response


# Initialize the voice command processor
voice_processor = VoiceCommandProcessor()
