"""
Chat&Talk GPT - Alarm Manager
Alarm and reminder system with SQLite database storage
"""
import json
import logging
import os
import re
import uuid
import asyncio
from datetime import datetime, timedelta, time
from pathlib import Path
from typing import Dict, Any, List, Optional

from database import (
    init_database,
    create_alarm as db_create_alarm,
    get_alarms as db_get_alarms,
    get_alarm_by_id as db_get_alarm_by_id,
    update_alarm as db_update_alarm,
    delete_alarm as db_delete_alarm
)

logger = logging.getLogger("AlarmManager")

# Import webhook manager for triggering webhooks on alarm events
try:
    from webhook_manager import trigger_webhook
except ImportError:
    trigger_webhook = None
    logger.warning("Webhook manager not available - alarm webhooks disabled")


class AlarmManager:
    """
    Alarm management system with SQLite database storage
    Features:
    - Create, read, delete alarms
    - Recurring alarms (daily, weekdays, weekends, specific days)
    - Snooze functionality
    - Enable/disable alarms
    - Async-compatible methods
    """
    
    # Valid day values
    VALID_DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    
    _db_initialized = False
    
    def __init__(self, alarms_file: str = None):
        """Initialize alarm manager"""
        self.alarms_file = Path(alarms_file) if alarms_file else None
        self._use_database = True
        self._ensure_db_initialized()
        
        logger.info("AlarmManager initialized with SQLite database")
    
    def _ensure_db_initialized(self):
        """Ensure database is initialized"""
        if not AlarmManager._db_initialized:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if not loop.is_running():
                    loop.run_until_complete(init_database())
            except:
                pass
            AlarmManager._db_initialized = True
    
    def _parse_time(self, time_str: str) -> str:
        """Parse time string to 24-hour format (HH:MM)"""
        time_str = time_str.strip().upper()
        
        if re.match(r"^\d{2}:\d{2}$", time_str):
            return time_str
        
        match = re.match(r"^(\d{1,2}):(\d{2})\s*(AM|PM)?$", time_str)
        if match:
            hour = int(match.group(1))
            minute = match.group(2)
            period = match.group(3)
            
            if period == "PM" and hour != 12:
                hour += 12
            elif period == "AM" and hour == 12:
                hour = 0
            
            return f"{hour:02d}:{minute}"
        
        return time_str
    
    def _validate_days(self, days: List[str]) -> List[str]:
        """Validate and normalize days list"""
        if not days:
            return []
        
        validated = []
        for day in days:
            day_lower = day.lower()
            if day_lower in self.VALID_DAYS:
                validated.append(day_lower)
        
        return validated
    
    def _normalize_days(self, days: List[str]) -> List[str]:
        """Normalize day shortcuts to full day names"""
        if not days:
            return []
        
        normalized = set()
        for day in days:
            day_lower = day.lower()
            
            if day_lower in self.VALID_DAYS:
                normalized.add(day_lower)
            elif day_lower in ["weekday", "weekdays"]:
                normalized.update(["monday", "tuesday", "wednesday", "thursday", "friday"])
            elif day_lower in ["weekend", "weekends"]:
                normalized.update(["saturday", "sunday"])
            elif day_lower in ["daily", "everyday", "every day"]:
                normalized.update(self.VALID_DAYS)
        
        return sorted(list(normalized), key=lambda d: self.VALID_DAYS.index(d))
    
    def set_alarm(self, time: str, label: str = "", days: List[str] = None) -> Dict[str, Any]:
        """Set a new alarm"""
        import asyncio
        
        time_24h = self._parse_time(time)
        
        if not re.match(r"^\d{2}:\d{2}$", time_24h):
            raise ValueError(f"Invalid time format: {time}. Use HH:MM format.")
        
        normalized_days = self._normalize_days(days) if days else []
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_create_alarm(1, time_24h, label.strip() if label else "", normalized_days),
                    loop
                )
                alarm = future.result(timeout=10)
            else:
                alarm = loop.run_until_complete(
                    db_create_alarm(1, time_24h, label.strip() if label else "", normalized_days)
                )
        except Exception as e:
            logger.error(f"Error creating alarm in database: {e}")
            alarm = self._set_alarm_json(time_24h, label, normalized_days)
        
        logger.info(f"Created alarm: {alarm['id']} at {time_24h}")
        return alarm
    
    def _set_alarm_json(self, time_24h: str, label: str, days: List[str]) -> Dict[str, Any]:
        """Fallback JSON storage"""
        if self.alarms_file:
            self.alarms_file.parent.mkdir(parents=True, exist_ok=True)
            try:
                with open(self.alarms_file, "r", encoding="utf-8") as f:
                    alarms = json.load(f)
            except:
                alarms = []
            
            alarm = {
                "id": str(uuid.uuid4())[:8],
                "time": time_24h,
                "label": label,
                "days": days,
                "enabled": True,
                "snoozed_until": None,
                "snooze_count": 0,
                "created_at": datetime.now().isoformat()
            }
            
            alarms.append(alarm)
            with open(self.alarms_file, "w", encoding="utf-8") as f:
                json.dump(alarms, f, indent=2, ensure_ascii=False)
            
            return alarm
        return {}
    
    def get_alarms(self, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """Get all alarms"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_get_alarms(1, enabled_only), loop
                )
                alarms = future.result(timeout=10)
            else:
                alarms = loop.run_until_complete(db_get_alarms(1, enabled_only))
        except Exception as e:
            logger.error(f"Error getting alarms from database: {e}")
            alarms = self._get_alarms_json(enabled_only)
        
        return alarms
    
    def _get_alarms_json(self, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """Fallback JSON storage"""
        if self.alarms_file and self.alarms_file.exists():
            try:
                with open(self.alarms_file, "r", encoding="utf-8") as f:
                    alarms = json.load(f)
                if enabled_only:
                    return [a for a in alarms if a.get("enabled", True)]
                return alarms
            except:
                pass
        return []
    
    def get_alarm(self, alarm_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific alarm by ID"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_get_alarm_by_id(int(alarm_id)), loop
                )
                alarm = future.result(timeout=10)
            else:
                alarm = loop.run_until_complete(db_get_alarm_by_id(int(alarm_id)))
            return alarm
        except Exception as e:
            logger.error(f"Error getting alarm from database: {e}")
            return self._get_alarm_json(alarm_id)
    
    def _get_alarm_json(self, alarm_id: str) -> Optional[Dict[str, Any]]:
        """Fallback JSON storage"""
        if self.alarms_file and self.alarms_file.exists():
            try:
                with open(self.alarms_file, "r", encoding="utf-8") as f:
                    alarms = json.load(f)
                for alarm in alarms:
                    if alarm.get("id") == alarm_id:
                        return alarm
            except:
                pass
        return None
    
    def delete_alarm(self, alarm_id: str) -> bool:
        """Delete an alarm"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_delete_alarm(int(alarm_id)), loop
                )
                result = future.result(timeout=10)
            else:
                result = loop.run_until_complete(db_delete_alarm(int(alarm_id)))
            
            if result:
                logger.info(f"Deleted alarm: {alarm_id}")
            return result
        except Exception as e:
            logger.error(f"Error deleting alarm from database: {e}")
            return self._delete_alarm_json(alarm_id)
    
    def _delete_alarm_json(self, alarm_id: str) -> bool:
        """Fallback JSON storage"""
        if self.alarms_file and self.alarms_file.exists():
            try:
                with open(self.alarms_file, "r", encoding="utf-8") as f:
                    alarms = json.load(f)
                
                for i, alarm in enumerate(alarms):
                    if alarm.get("id") == alarm_id:
                        alarms.pop(i)
                        with open(self.alarms_file, "w", encoding="utf-8") as f:
                            json.dump(alarms, f, indent=2, ensure_ascii=False)
                        return True
            except:
                pass
        return False
    
    def enable_alarm(self, alarm_id: str) -> Optional[Dict[str, Any]]:
        """Enable an alarm"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_update_alarm(int(alarm_id), enabled=True), loop
                )
                alarm = future.result(timeout=10)
            else:
                alarm = loop.run_until_complete(db_update_alarm(int(alarm_id), enabled=True))
            
            logger.info(f"Enabled alarm: {alarm_id}")
            return alarm
        except Exception as e:
            logger.error(f"Error enabling alarm: {e}")
            return self._update_alarm_json(alarm_id, enabled=True)
    
    def disable_alarm(self, alarm_id: str) -> Optional[Dict[str, Any]]:
        """Disable an alarm"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_update_alarm(int(alarm_id), enabled=False, snoozed_until=None, snooze_count=0), loop
                )
                alarm = future.result(timeout=10)
            else:
                alarm = loop.run_until_complete(
                    db_update_alarm(int(alarm_id), enabled=False, snoozed_until=None, snooze_count=0)
                )
            
            logger.info(f"Disabled alarm: {alarm_id}")
            return alarm
        except Exception as e:
            logger.error(f"Error disabling alarm: {e}")
            return self._update_alarm_json(alarm_id, enabled=False)
    
    def snooze_alarm(self, alarm_id: str, minutes: int = 10) -> Optional[Dict[str, Any]]:
        """Snooze an alarm"""
        import asyncio
        
        snooze_time = datetime.now() + timedelta(minutes=minutes)
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_update_alarm(int(alarm_id), snoozed_until=snooze_time.isoformat()), loop
                )
                alarm = future.result(timeout=10)
            else:
                alarm = loop.run_until_complete(
                    db_update_alarm(int(alarm_id), snoozed_until=snooze_time.isoformat())
                )
            
            logger.info(f"Snoozed alarm {alarm_id} for {minutes} minutes")
            return alarm
        except Exception as e:
            logger.error(f"Error snoozing alarm: {e}")
            return self._update_alarm_json(alarm_id, snoozed_until=snooze_time.isoformat())
    
    def clear_snooze(self, alarm_id: str) -> Optional[Dict[str, Any]]:
        """Clear snooze from an alarm"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_update_alarm(int(alarm_id), snoozed_until=None, snooze_count=0), loop
                )
                alarm = future.result(timeout=10)
            else:
                alarm = loop.run_until_complete(
                    db_update_alarm(int(alarm_id), snoozed_until=None, snooze_count=0)
                )
            
            logger.info(f"Cleared snooze for alarm: {alarm_id}")
            return alarm
        except Exception as e:
            logger.error(f"Error clearing snooze: {e}")
            return self._update_alarm_json(alarm_id, snoozed_until=None, snooze_count=0)
    
    def _update_alarm_json(self, alarm_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Fallback JSON storage"""
        if self.alarms_file and self.alarms_file.exists():
            try:
                with open(self.alarms_file, "r", encoding="utf-8") as f:
                    alarms = json.load(f)
                
                for alarm in alarms:
                    if alarm.get("id") == alarm_id:
                        for key, value in kwargs.items():
                            alarm[key] = value
                        with open(self.alarms_file, "w", encoding="utf-8") as f:
                            json.dump(alarms, f, indent=2, ensure_ascii=False)
                        return alarm
            except:
                pass
        return None
    
    def update_alarm(self, alarm_id: str, time: str = None, label: str = None, 
                     days: List[str] = None) -> Optional[Dict[str, Any]]:
        """Update an existing alarm"""
        import asyncio
        
        kwargs = {}
        if time is not None:
            kwargs['time'] = self._parse_time(time)
        if label is not None:
            kwargs['label'] = label.strip()
        if days is not None:
            kwargs['days'] = self._normalize_days(days)
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_update_alarm(int(alarm_id), **kwargs), loop
                )
                alarm = future.result(timeout=10)
            else:
                alarm = loop.run_until_complete(db_update_alarm(int(alarm_id), **kwargs))
            
            logger.info(f"Updated alarm: {alarm_id}")
            return alarm
        except Exception as e:
            logger.error(f"Error updating alarm: {e}")
            return self._update_alarm_json(alarm_id, **kwargs)
    
    def get_upcoming_alarms(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get upcoming alarms sorted by time"""
        alarms = self.get_alarms(enabled_only=True)
        
        now = datetime.now()
        current_time = now.time()
        current_day = self.VALID_DAYS[now.weekday()]
        
        upcoming = []
        
        for alarm in alarms:
            alarm_time_str = alarm.get("time", "00:00")
            try:
                alarm_time = time.fromisoformat(alarm_time_str)
            except:
                continue
            
            alarm_days = alarm.get("days", [])
            
            should_ring_today = not alarm_days or current_day in alarm_days
            
            if should_ring_today:
                if alarm_time >= current_time:
                    upcoming.append(alarm)
                elif alarm.get("snoozed_until"):
                    snooze_time = datetime.fromisoformat(alarm["snoozed_until"])
                    if snooze_time > now:
                        upcoming.append(alarm)
            else:
                if alarm_days:
                    upcoming.append(alarm)
        
        upcoming.sort(key=lambda a: a.get("time", "23:59"))
        return upcoming[:limit]
    
    def get_alarms_for_day(self, day: str) -> List[Dict[str, Any]]:
        """Get all alarms scheduled for a specific day"""
        day_lower = day.lower()
        
        if day_lower not in self.VALID_DAYS:
            return []
        
        alarms = self.get_alarms(enabled_only=True)
        results = []
        
        for alarm in alarms:
            alarm_days = alarm.get("days", [])
            if not alarm_days or day_lower in alarm_days:
                results.append(alarm)
        
        results.sort(key=lambda a: a.get("time", "23:59"))
        return results
    
    def get_alarm_count(self) -> int:
        """Get total number of alarms"""
        return len(self.get_alarms())
    
    def get_enabled_count(self) -> int:
        """Get number of enabled alarms"""
        return len(self.get_alarms(enabled_only=True))
    
    def clear_all_alarms(self) -> bool:
        """Delete all alarms (use with caution)"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            alarms = self.get_alarms()
            for alarm in alarms:
                if loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        db_delete_alarm(alarm['id']), loop
                    )
                    future.result(timeout=10)
                else:
                    loop.run_until_complete(db_delete_alarm(alarm['id']))
            
            logger.warning("Cleared all alarms from database")
            return True
        except Exception as e:
            logger.error(f"Error clearing alarms: {e}")
            return False
    
    def is_alarm_ringing(self, alarm_id: str) -> bool:
        """Check if an alarm is currently ringing"""
        alarm = self.get_alarm(alarm_id)
        if not alarm or not alarm.get("enabled", True):
            return False
        
        now = datetime.now()
        current_time = now.time()
        current_day = self.VALID_DAYS[now.weekday()]
        
        alarm_time_str = alarm.get("time", "00:00")
        try:
            alarm_time = time.fromisoformat(alarm_time_str)
        except:
            return False
        
        alarm_days = alarm.get("days", [])
        
        if alarm_days and current_day not in alarm_days:
            return False
        
        if alarm.get("snoozed_until"):
            snooze_time = datetime.fromisoformat(alarm["snoozed_until"])
            if snooze_time > now:
                return True
        
        return alarm_time.hour == current_time.hour and alarm_time.minute == current_time.minute

    async def trigger_alarm_webhook(self, alarm_id: str, user_id: int = 1) -> Dict[str, Any]:
        """
        Trigger webhooks when an alarm fires.
        This should be called when an alarm is triggered/activated.
        """
        if not trigger_webhook:
            logger.warning("Webhook trigger not available")
            return {"success": False, "error": "Webhook system not available"}
        
        alarm = self.get_alarm(alarm_id)
        if not alarm:
            return {"success": False, "error": "Alarm not found"}
        
        # Prepare webhook payload
        webhook_data = {
            "alarm_id": alarm_id,
            "time": alarm.get("time", ""),
            "label": alarm.get("label", ""),
            "days": alarm.get("days", []),
            "sound": alarm.get("sound", "default"),
            "enabled": alarm.get("enabled", True),
            "triggered_at": datetime.now().isoformat()
        }
        
        try:
            # Run webhook trigger in background
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If already in async context, create task
                asyncio.create_task(trigger_webhook("alarm.triggered", webhook_data, user_id))
            else:
                # Run synchronously
                loop.run_until_complete(trigger_webhook("alarm.triggered", webhook_data, user_id))
            
            logger.info(f"Alarm webhook triggered for alarm {alarm_id}")
            return {"success": True, "event": "alarm.triggered", "data": webhook_data}
        except Exception as e:
            logger.error(f"Error triggering alarm webhook: {e}")
            return {"success": False, "error": str(e)}


# Singleton instance
_alarm_manager: Optional[AlarmManager] = None


def get_alarm_manager() -> AlarmManager:
    """Get or create alarm manager singleton"""
    global _alarm_manager
    if _alarm_manager is None:
        _alarm_manager = AlarmManager()
    return _alarm_manager
