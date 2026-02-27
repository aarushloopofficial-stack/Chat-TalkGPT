"""
Chat&Talk GPT - Calendar Manager
Event scheduling and calendar management with SQLite database storage
Supports optional Google Calendar integration for advanced users
"""
import json
import logging
import os
import re
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

from database import (
    init_database,
    create_calendar_event as db_create_event,
    get_calendar_events as db_get_events,
    get_calendar_event_by_id as db_get_event_by_id,
    update_calendar_event as db_update_event,
    delete_calendar_event as db_delete_event
)

logger = logging.getLogger("CalendarManager")

# Import webhook manager for triggering webhooks on calendar events
try:
    from webhook_manager import trigger_webhook
except ImportError:
    trigger_webhook = None
    logger.warning("Webhook manager not available - calendar webhooks disabled")

# Event types
EVENT_TYPES = ["exam", "assignment", "reminder", "general"]

# Default reminder times (in minutes)
DEFAULT_REMINDER_MINUTES = 30


class CalendarManager:
    """
    Calendar management system with SQLite database storage
    Features:
    - SQLite database storage (primary, always works)
    - Optional Google Calendar API integration
    - Event categorization (exam, assignment, reminder, general)
    - Reminder system
    - Mark events as completed
    - Upcoming events list
    """
    
    _db_initialized = False
    
    def __init__(self, calendar_file: str = None):
        """Initialize calendar manager"""
        self.calendar_file = Path(calendar_file) if calendar_file else None
        self._use_database = True
        self._ensure_db_initialized()
        
        # Google Calendar configuration (optional)
        self.google_enabled = os.getenv("GOOGLE_CALENDAR_ENABLED", "false").lower() == "true"
        self.google_calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "")
        
        logger.info("CalendarManager initialized with SQLite database")
        if self.google_enabled:
            logger.info("Google Calendar integration enabled")
    
    def _ensure_db_initialized(self):
        """Ensure database is initialized"""
        if not CalendarManager._db_initialized:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if not loop.is_running():
                    loop.run_until_complete(init_database())
            except:
                pass
            CalendarManager._db_initialized = True
    
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
    
    def add_event(self, title: str, description: str, date: str, 
                  time: str, event_type: str = "general") -> Dict[str, Any]:
        """Add a new event to calendar"""
        import asyncio
        
        if event_type not in EVENT_TYPES:
            logger.warning(f"Invalid event type '{event_type}', using 'general'")
            event_type = "general"
        
        parsed_time = self._parse_time(time)
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_create_event(1, title.strip(), description.strip() if description else "", 
                                   date.strip(), parsed_time, event_type),
                    loop
                )
                event = future.result(timeout=10)
            else:
                event = loop.run_until_complete(
                    db_create_event(1, title.strip(), description.strip() if description else "", 
                                   date.strip(), parsed_time, event_type)
                )
        except Exception as e:
            logger.error(f"Error creating event in database: {e}")
            event = self._add_event_json(title, description, date, parsed_time, event_type)
        
        logger.info(f"Event added: {title} on {date} at {parsed_time} ({event_type})")
        return event
    
    def _add_event_json(self, title: str, description: str, date: str, 
                        time: str, event_type: str) -> Dict[str, Any]:
        """Fallback JSON storage"""
        if self.calendar_file:
            self.calendar_file.parent.mkdir(parents=True, exist_ok=True)
            try:
                with open(self.calendar_file, "r", encoding="utf-8") as f:
                    events = json.load(f)
            except:
                events = []
            
            event_id = max([e.get("id", 0) for e in events], default=0) + 1
            
            event = {
                "id": event_id,
                "title": title,
                "description": description,
                "date": date,
                "time": time,
                "event_type": event_type,
                "reminder": None,
                "completed": False,
                "created_at": datetime.now().isoformat()
            }
            
            events.append(event)
            with open(self.calendar_file, "w", encoding="utf-8") as f:
                json.dump(events, f, indent=2, ensure_ascii=False)
            
            return event
        return {}
    
    def get_events(self, date: str = None, upcoming: int = 7) -> List[Dict[str, Any]]:
        """Get events for a specific date or upcoming days"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_get_events(1, date, upcoming), loop
                )
                events = future.result(timeout=10)
            else:
                events = loop.run_until_complete(db_get_events(1, date, upcoming))
        except Exception as e:
            logger.error(f"Error getting events from database: {e}")
            events = self._get_events_json(date, upcoming)
        
        return events
    
    def _get_events_json(self, date: str = None, upcoming: int = 7) -> List[Dict[str, Any]]:
        """Fallback JSON storage"""
        if self.calendar_file and self.calendar_file.exists():
            try:
                with open(self.calendar_file, "r", encoding="utf-8") as f:
                    events = json.load(f)
                
                if date:
                    filtered_events = [e for e in events if e.get("date") == date]
                else:
                    today = datetime.now().date()
                    end_date = today + timedelta(days=upcoming)
                    
                    filtered_events = []
                    for event in events:
                        try:
                            event_date = datetime.strptime(event.get("date", ""), "%Y-%m-%d").date()
                            if today <= event_date <= end_date:
                                filtered_events.append(event)
                        except ValueError:
                            continue
                
                filtered_events.sort(key=lambda x: (x.get("date", ""), x.get("time", "")))
                return filtered_events
            except:
                pass
        return []
    
    def get_today_events(self) -> List[Dict[str, Any]]:
        """Get today's events"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.get_events(date=today)
    
    def delete_event(self, event_id: int) -> bool:
        """Delete an event by ID"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_delete_event(event_id), loop
                )
                result = future.result(timeout=10)
            else:
                result = loop.run_until_complete(db_delete_event(event_id))
            
            logger.info(f"Event deleted: ID {event_id}")
            return result
        except Exception as e:
            logger.error(f"Error deleting event from database: {e}")
            return self._delete_event_json(event_id)
    
    def _delete_event_json(self, event_id: int) -> bool:
        """Fallback JSON storage"""
        if self.calendar_file and self.calendar_file.exists():
            try:
                with open(self.calendar_file, "r", encoding="utf-8") as f:
                    events = json.load(f)
                
                for i, event in enumerate(events):
                    if event.get("id") == event_id:
                        events.pop(i)
                        with open(self.calendar_file, "w", encoding="utf-8") as f:
                            json.dump(events, f, indent=2, ensure_ascii=False)
                        return True
            except:
                pass
        return False
    
    def set_reminder(self, event_id: int, minutes_before: int) -> bool:
        """Set reminder for an event"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_update_event(event_id, reminder=minutes_before), loop
                )
                result = future.result(timeout=10)
            else:
                result = loop.run_until_complete(db_update_event(event_id, reminder=minutes_before))
            
            logger.info(f"Reminder set for event ID {event_id}: {minutes_before} minutes before")
            return result is not None
        except Exception as e:
            logger.error(f"Error setting reminder: {e}")
            return self._update_event_json(event_id, reminder=minutes_before) is not None
    
    def mark_completed(self, event_id: int) -> bool:
        """Mark an event as completed"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_update_event(event_id, completed=True), loop
                )
                result = future.result(timeout=10)
            else:
                result = loop.run_until_complete(db_update_event(event_id, completed=True))
            
            logger.info(f"Event marked as completed: ID {event_id}")
            return result is not None
        except Exception as e:
            logger.error(f"Error marking event completed: {e}")
            return self._update_event_json(event_id, completed=True) is not None
    
    def get_event_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific event by ID"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_get_event_by_id(event_id), loop
                )
                event = future.result(timeout=10)
            else:
                event = loop.run_until_complete(db_get_event_by_id(event_id))
            return event
        except Exception as e:
            logger.error(f"Error getting event from database: {e}")
            return self._get_event_json(event_id)
    
    def _get_event_json(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Fallback JSON storage"""
        if self.calendar_file and self.calendar_file.exists():
            try:
                with open(self.calendar_file, "r", encoding="utf-8") as f:
                    events = json.load(f)
                for event in events:
                    if event.get("id") == event_id:
                        return event
            except:
                pass
        return None
    
    def _update_event_json(self, event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """Fallback JSON storage"""
        if self.calendar_file and self.calendar_file.exists():
            try:
                with open(self.calendar_file, "r", encoding="utf-8") as f:
                    events = json.load(f)
                
                for event in events:
                    if event.get("id") == event_id:
                        for key, value in kwargs.items():
                            event[key] = value
                        with open(self.calendar_file, "w", encoding="utf-8") as f:
                            json.dump(events, f, indent=2, ensure_ascii=False)
                        return event
            except:
                pass
        return None
    
    def get_events_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """Get all events of a specific type"""
        events = self.get_events()
        return [e for e in events if e.get("event_type") == event_type]
    
    def get_upcoming_events(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get upcoming events (excluding past events)"""
        events = self.get_events(upcoming=days)
        today = datetime.now().date()
        
        upcoming = []
        for event in events:
            try:
                event_date = datetime.strptime(event.get("date", ""), "%Y-%m-%d").date()
                if event_date >= today and not event.get("completed", False):
                    upcoming.append(event)
            except ValueError:
                continue
        
        upcoming.sort(key=lambda x: (x.get("date", ""), x.get("time", "")))
        return upcoming[:days * 5]
    
    def get_pending_reminders(self) -> List[Dict[str, Any]]:
        """Get events that have reminders set but are not completed"""
        now = datetime.now()
        events = self.get_events()
        
        pending = []
        for event in events:
            if event.get("reminder") and not event.get("completed", False):
                try:
                    event_datetime = datetime.strptime(
                        f"{event.get('date')} {event.get('time')}", 
                        "%Y-%m-%d %H:%M"
                    )
                    
                    reminder_time = event_datetime - timedelta(minutes=event["reminder"])
                    
                    if now >= reminder_time and now < event_datetime:
                        pending.append({
                            **event,
                            "reminder_time": reminder_time.isoformat(),
                            "event_time": event_datetime.isoformat()
                        })
                except ValueError:
                    continue
        
        return pending
    
    def update_event(self, event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """Update an event's properties"""
        import asyncio
        
        if 'time' in kwargs and kwargs['time']:
            kwargs['time'] = self._parse_time(kwargs['time'])
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_update_event(event_id, **kwargs), loop
                )
                event = future.result(timeout=10)
            else:
                event = loop.run_until_complete(db_update_event(event_id, **kwargs))
            
            logger.info(f"Event updated: ID {event_id}")
            return event
        except Exception as e:
            logger.error(f"Error updating event: {e}")
            return self._update_event_json(event_id, **kwargs)
    
    def get_calendar_summary(self) -> Dict[str, Any]:
        """Get a summary of the calendar"""
        events = self.get_events()
        today = datetime.now().date()
        
        total_events = len(events)
        completed_events = len([e for e in events if e.get("completed", False)])
        pending_events = total_events - completed_events
        
        events_by_type = {}
        for et in EVENT_TYPES:
            events_by_type[et] = len([e for e in events if e.get("event_type") == et])
        
        today_str = today.strftime("%Y-%m-%d")
        today_events = len([e for e in events if e.get("date") == today_str])
        
        week_end = today + timedelta(days=7)
        upcoming_this_week = len([
            e for e in events 
            if not e.get("completed", False) 
            and today <= datetime.strptime(e.get("date", ""), "%Y-%m-%d").date() <= week_end
        ])
        
        return {
            "total_events": total_events,
            "completed_events": completed_events,
            "pending_events": pending_events,
            "events_by_type": events_by_type,
            "today_events": today_events,
            "upcoming_this_week": upcoming_this_week
        }
    
    async def trigger_calendar_event_webhook(self, event_id: int, user_id: int = 1) -> Dict[str, Any]:
        """
        Trigger webhooks when a calendar event is about to start.
        This should be called when checking for pending reminders.
        """
        if not trigger_webhook:
            logger.warning("Webhook trigger not available")
            return {"success": False, "error": "Webhook system not available"}
        
        # DEBUG: Log that we're trying to get the event
        logger.info(f"DEBUG: Looking for event with ID {event_id}")
        
        # Get the event - using correct method name get_event_by_id
        event = self.get_event_by_id(event_id)
        logger.info(f"DEBUG: Retrieved event: {event}")
        if not event:
            return {"success": False, "error": "Event not found"}
        
        # Prepare webhook payload
        webhook_data = {
            "event_id": event_id,
            "title": event.get("title", ""),
            "description": event.get("description", ""),
            "date": event.get("date", ""),
            "time": event.get("time", ""),
            "event_type": event.get("event_type", "general"),
            "reminder": event.get("reminder"),
            "triggered_at": datetime.now().isoformat()
        }
        
        try:
            await trigger_webhook("calendar.event.starting", webhook_data, user_id)
            logger.info(f"Calendar event webhook triggered for event {event_id}")
            return {"success": True, "event": "calendar.event.starting", "data": webhook_data}
        except Exception as e:
            logger.error(f"Error triggering calendar webhook: {e}")
            return {"success": False, "error": str(e)}


# Global calendar manager instance
calendar_manager = CalendarManager()
