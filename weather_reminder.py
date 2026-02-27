"""
Chat&Talk GPT - Weather Reminder for Aakansha
Personalized weather reminder system with location-based alerts and SQLite storage
"""
import json
import logging
import asyncio
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

from database import (
    init_database,
    create_reminder as db_create_reminder,
    get_reminders as db_get_reminders,
    get_reminder_by_id as db_get_reminder_by_id,
    update_reminder as db_update_reminder,
    delete_reminder as db_delete_reminder
)

logger = logging.getLogger("WeatherReminder")

# Import webhook manager for triggering webhooks on reminder events
try:
    from webhook_manager import trigger_webhook
except ImportError:
    trigger_webhook = None
    logger.warning("Webhook manager not available - reminder webhooks disabled")

# Weather condition codes from wttr.in
WEATHER_CODES = {
    "sunny": ["sunny", "clear"],
    "cloudy": ["cloudy", "overcast", "mist", "fog"],
    "rainy": ["rain", "drizzle", "shower"],
    "stormy": ["thunderstorm", "storm", "thunder"],
    "snowy": ["snow", "sleet", "ice"],
    "windy": ["wind", "breezy"]
}


class WeatherReminder:
    """
    Weather reminder system specifically for Aakansha
    Features:
    - Set weather-based reminders
    - Check current weather conditions
    - Store personalized reminders in SQLite
    - Location-based alerts
    """
    
    _db_initialized = False
    
    def __init__(self, reminder_file: str = None):
        self.reminder_file = Path(reminder_file) if reminder_file else None
        self.reminders = self._load_reminders()
        self._ensure_db_initialized()
        
        # Aakansha's default location (can be customized)
        self.default_location = "Kathmandu"  # Default to Nepal
        self.user_name = "Aakansha"
        
        logger.info(f"WeatherReminder initialized for {self.user_name}")
        logger.info(f"Loaded {len(self.reminders)} weather reminders")
    
    def _ensure_db_initialized(self):
        """Ensure database is initialized"""
        if not WeatherReminder._db_initialized:
            try:
                loop = asyncio.get_event_loop()
                if not loop.is_running():
                    loop.run_until_complete(init_database())
            except:
                pass
            WeatherReminder._db_initialized = True
    
    def _load_reminders(self) -> Dict[str, Any]:
        """Load weather reminders from file or database"""
        # Try file first
        try:
            if self.reminder_file and self.reminder_file.exists():
                with open(self.reminder_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    logger.info("Weather reminders loaded from file")
                    return data
        except Exception as e:
            logger.warning(f"Could not load weather reminders from file: {e}")
        
        # Default structure
        return {
            "reminders": [],
            "locations": {
                "home": "Kathmandu",
                "school": "Kathmandu",
                "office": "Kathmandu"
            },
            "settings": {
                "notifications_enabled": True,
                "default_reminder_time": "08:00",
                "weather_check_interval": 180  # minutes
            }
        }
    
    def _save_reminders(self):
        """Save weather reminders to file"""
        try:
            if self.reminder_file:
                self.reminder_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.reminder_file, "w", encoding="utf-8") as f:
                    json.dump(self.reminders, f, indent=2, ensure_ascii=False)
            logger.info("Weather reminders saved")
        except Exception as e:
            logger.error(f"Error saving weather reminders: {e}")
    
    async def get_current_weather(self, location: str = None) -> Dict[str, Any]:
        """Fetch current weather for a location"""
        loc = location or self.default_location
        
        try:
            # Using wttr.in - free weather API
            url = f"https://wttr.in/{loc}?format=j1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                current = data.get("current_condition", [{}])[0]
                
                weather_info = {
                    "location": loc,
                    "temperature": current.get("temp_C", "N/A"),
                    "feels_like": current.get("FeelsLikeC", "N/A"),
                    "humidity": current.get("humidity", "N/A"),
                    "weather_desc": current.get("weatherDesc", [{}])[0].get("value", "Unknown"),
                    "wind_speed": current.get("windspeedKmph", "N/A"),
                    "uv_index": current.get("UVIndex", "N/A"),
                    "visibility": current.get("visibility", "N/A"),
                    "pressure": current.get("pressure", "N/A"),
                    "last_updated": current.get("localObsDateTime", "")
                }
                
                logger.info(f"Weather fetched for {loc}: {weather_info['weather_desc']}, {weather_info['temperature']}°C")
                return {"success": True, "weather": weather_info}
            else:
                return {"success": False, "error": "Could not fetch weather data"}
                
        except Exception as e:
            logger.error(f"Weather fetch error: {e}")
            return {"success": False, "error": str(e)}
    
    def add_reminder(self, reminder_type: str, condition: str, message: str, 
                     time: str = None, location: str = None) -> Dict[str, Any]:
        """Add a weather reminder for Aakansha"""
        import asyncio
        
        reminder = {
            "id": len(self.reminders["reminders"]) + 1,
            "type": reminder_type,
            "condition": condition.lower(),
            "message": message,
            "time": time or self.reminders["settings"]["default_reminder_time"],
            "location": location or self.default_location,
            "created_at": datetime.now().isoformat(),
            "active": True,
            "last_triggered": None,
            "trigger_count": 0
        }
        
        # Save to file
        self.reminders["reminders"].append(reminder)
        self._save_reminders()
        
        # Also save to database
        try:
            loop = asyncio.get_event_loop()
            scheduled_time = f"{datetime.now().strftime('%Y-%m-%d')} {time or self.reminders['settings']['default_reminder_time']}:00"
            
            if loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    db_create_reminder(1, "weather", message, scheduled_time, True),
                    loop
                )
            else:
                loop.run_until_complete(
                    db_create_reminder(1, "weather", message, scheduled_time, True)
                )
        except Exception as e:
            logger.warning(f"Could not save reminder to database: {e}")
        
        logger.info(f"Added weather reminder for {self.user_name}: {condition} - {message}")
        
        return {
            "success": True,
            "message": f"Weather reminder added! I'll remind you when it's {condition}.",
            "reminder_id": reminder["id"]
        }
    
    def remove_reminder(self, reminder_id: int) -> Dict[str, Any]:
        """Remove a weather reminder by ID"""
        for i, reminder in enumerate(self.reminders["reminders"]):
            if reminder["id"] == reminder_id:
                removed = self.reminders["reminders"].pop(i)
                self._save_reminders()
                
                # Also delete from database
                try:
                    import asyncio
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.run_coroutine_threadsafe(db_delete_reminder(reminder_id), loop)
                    else:
                        loop.run_until_complete(db_delete_reminder(reminder_id))
                except Exception as e:
                    logger.warning(f"Could not delete reminder from database: {e}")
                
                logger.info(f"Removed weather reminder {reminder_id}")
                return {
                    "success": True,
                    "message": f"Removed reminder: {removed['message']}"
                }
        
        return {"success": False, "message": "Reminder not found"}
    
    def get_reminders(self) -> List[Dict[str, Any]]:
        """Get all weather reminders for Aakansha"""
        return self.reminders["reminders"]
    
    def update_location(self, location_name: str, location_type: str = "home") -> Dict[str, Any]:
        """Update Aakansha's saved locations"""
        if location_type in self.reminders["locations"]:
            self.reminders["locations"][location_type] = location_name
            self._save_reminders()
            
            logger.info(f"Updated {location_type} location to {location_name}")
            
            return {
                "success": True,
                "message": f"Updated {location_type} location to {location_name}"
            }
        
        return {"success": False, "message": "Invalid location type"}
    
    async def check_weather_conditions(self, location: str = None) -> Dict[str, Any]:
        """Check current weather and return condition category"""
        result = await self.get_current_weather(location)
        
        if not result.get("success"):
            return result
        
        weather = result["weather"]
        desc = weather["weather_desc"].lower()
        temp = int(weather["temperature"]) if weather["temperature"] != "N/A" else 20
        
        # Determine condition category
        condition = "moderate"
        
        for cat, keywords in WEATHER_CODES.items():
            if any(kw in desc for kw in keywords):
                condition = cat
                break
        
        # Check for extreme temperatures
        if temp >= 35:
            condition = "hot"
        elif temp <= 5:
            condition = "cold"
        
        return {
            "success": True,
            "condition": condition,
            "weather": weather,
            "description": desc
        }
    
    async def check_and_trigger_reminders(self) -> List[Dict[str, Any]]:
        """Check weather and trigger any matching reminders"""
        triggered = []
        
        for reminder in self.reminders["reminders"]:
            if not reminder.get("active", True):
                continue
            
            # Get weather for reminder's location
            result = await self.check_weather_conditions(reminder.get("location"))
            
            if not result.get("success"):
                continue
            
            # Check if condition matches
            if result["condition"] == reminder["condition"]:
                reminder["last_triggered"] = datetime.now().isoformat()
                reminder["trigger_count"] = reminder.get("trigger_count", 0) + 1
                
                triggered.append({
                    "reminder": reminder,
                    "weather": result["weather"],
                    "message": reminder["message"]
                })
                
                logger.info(f"Triggered reminder {reminder['id']}: {reminder['message']}")
                
                # Trigger webhook for reminder
                await self._trigger_reminder_webhook(reminder, result["weather"])
        
        if triggered:
            self._save_reminders()
        
        return triggered
    
    async def _trigger_reminder_webhook(self, reminder: Dict[str, Any], weather: Dict[str, Any], user_id: int = 1):
        """Trigger webhooks when a reminder fires"""
        if not trigger_webhook:
            return
        
        webhook_data = {
            "reminder_id": reminder.get("id"),
            "condition": reminder.get("condition"),
            "location": reminder.get("location"),
            "message": reminder.get("message"),
            "weather": weather,
            "triggered_at": datetime.now().isoformat()
        }
        
        try:
            # Trigger weather alert webhook
            await trigger_webhook("weather.alert", webhook_data, user_id)
            # Also trigger reminder webhook
            await trigger_webhook("reminder.triggered", webhook_data, user_id)
            logger.info(f"Reminder webhooks triggered for {reminder.get('id')}")
        except Exception as e:
            logger.error(f"Error triggering reminder webhook: {e}")
    
    def get_weather_advice(self, weather_data: Dict[str, Any]) -> str:
        """Generate personalized weather advice for Aakansha"""
        temp = weather_data.get("temperature", 20)
        desc = weather_data.get("weather_desc", "").lower()
        humidity = weather_data.get("humidity", 50)
        
        advice = []
        
        # Temperature-based advice
        if int(temp) >= 35:
            advice.append("🌡️ It's very hot today! Stay hydrated and avoid direct sunlight.")
        elif int(temp) >= 30:
            advice.append("☀️ It's warm today. Don't forget sunscreen!")
        elif int(temp) >= 20:
            advice.append("😊 Pleasant weather today!")
        elif int(temp) >= 10:
            advice.append("🧥 A bit cool today. Bring a jacket!")
        elif int(temp) <= 5:
            advice.append("🥶 It's cold! Bundle up and stay warm!")
        
        # Weather condition advice
        if "rain" in desc or "drizzle" in desc:
            advice.append("🌧️ Don't forget your umbrella!")
        elif "thunder" in desc or "storm" in desc:
            advice.append("⛈️ There might be a storm. Stay indoors and be safe!")
        elif "snow" in desc:
            advice.append("❄️ Snow expected! Dress warmly and be careful on roads.")
        elif "fog" in desc or "mist" in desc:
            advice.append("🌫️ Foggy conditions. Drive carefully!")
        elif "cloud" in desc:
            advice.append("☁️ Cloudy skies today.")
        elif "sun" in desc:
            advice.append("☀️ Sunny day! Great for outdoor activities!")
        
        # Humidity advice
        if int(humidity) >= 80:
            advice.append("💧 High humidity today. Stay comfortable!")
        
        return " ".join(advice)
    
    def get_default_reminders(self) -> List[Dict[str, Any]]:
        """Get default weather reminders for Aakansha"""
        return [
            {
                "id": 0,
                "type": "recurring",
                "condition": "rainy",
                "message": "Don't forget your umbrella, Aakansha! 🌧️",
                "time": "07:00",
                "location": self.default_location,
                "active": True
            },
            {
                "id": 1,
                "type": "recurring",
                "condition": "sunny",
                "message": "Beautiful sunny day, Aakansha! Don't forget sunscreen! ☀️",
                "time": "08:00",
                "location": self.default_location,
                "active": True
            },
            {
                "id": 2,
                "type": "recurring",
                "condition": "hot",
                "message": "It's going to be hot today, Aakansha! Stay hydrated! 🌡️",
                "time": "07:30",
                "location": self.default_location,
                "active": True
            }
        ]
    
    def setup_default_reminders(self) -> Dict[str, Any]:
        """Setup default weather reminders for Aakansha"""
        defaults = self.get_default_reminders()
        
        for default in defaults:
            # Check if similar reminder exists
            exists = any(
                r["condition"] == default["condition"] and r["type"] == default["type"]
                for r in self.reminders["reminders"]
            )
            
            if not exists:
                default["id"] = len(self.reminders["reminders"]) + 1
                default["created_at"] = datetime.now().isoformat()
                default["last_triggered"] = None
                default["trigger_count"] = 0
                self.reminders["reminders"].append(default)
        
        self._save_reminders()
        
        return {
            "success": True,
            "message": f"Setup {len(defaults)} default weather reminders for {self.user_name}"
        }


# Initialize weather reminder for Aakansha
aakansha_weather_reminder = WeatherReminder()
