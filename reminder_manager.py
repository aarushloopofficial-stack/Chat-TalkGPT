"""
Chat&Talk GPT - General Reminder Manager
Comprehensive reminder system with multiple reminder types, recurrence patterns, and snooze functionality.
"""
import json
import logging
import asyncio
from datetime import datetime, timedelta, time
from typing import Dict, Any, List, Optional
from enum import Enum

from database import (
    init_database,
    database,
    create_reminder as db_create_reminder,
    get_reminders as db_get_reminders,
    get_reminder_by_id as db_get_reminder_by_id,
    update_reminder as db_update_reminder,
    delete_reminder as db_delete_reminder
)

logger = logging.getLogger("ReminderManager")

# Import webhook manager for triggering webhooks on reminder events
try:
    from webhook_manager import trigger_webhook
except ImportError:
    trigger_webhook = None
    logger.warning("Webhook manager not available - reminder webhooks disabled")


# Enums for reminder types and priorities
class ReminderType(str, Enum):
    """Types of reminders supported"""
    TIME_BASED = "time_based"
    RECURRING = "recurring"
    LOCATION_BASED = "location_based"
    EVENT_BASED = "event_based"
    CUSTOM = "custom"
    WEATHER = "weather"  # Integration with weather_reminder.py


class RecurrencePattern(str, Enum):
    """Recurrence patterns for recurring reminders"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM_DAYS = "custom_days"
    WEEKDAYS = "weekdays"
    WEEKENDS = "weekends"


class Priority(str, Enum):
    """Priority levels for reminders"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class SnoozeDuration(str, Enum):
    """Snooze duration options"""
    FIVE_MIN = "5min"
    FIFTEEN_MIN = "15min"
    THIRTY_MIN = "30min"
    ONE_HOUR = "1hr"
    TWO_HOURS = "2hr"
    CUSTOM = "custom"


# Reminder templates for common use cases
REMINDER_TEMPLATES = [
    {
        "id": "daily_medication",
        "name": "Daily Medication",
        "title": "Take Medication",
        "message": "Don't forget to take your medication! 💊",
        "reminder_type": RecurrencePattern.WEEKDAYS,
        "priority": Priority.HIGH,
        "category": "health"
    },
    {
        "id": "weekly_exercise",
        "name": "Weekly Exercise",
        "title": "Exercise Time",
        "message": "Time for your weekly workout! 🏃",
        "reminder_type": RecurrencePattern.WEEKLY,
        "priority": Priority.MEDIUM,
        "category": "fitness"
    },
    {
        "id": "birthday_reminder",
        "name": "Birthday Reminder",
        "title": "Birthday",
        "message": "Wish them a happy birthday! 🎂",
        "reminder_type": RecurrencePattern.YEARLY,
        "priority": Priority.HIGH,
        "category": "personal"
    },
    {
        "id": "bill_payment",
        "name": "Bill Payment",
        "title": "Pay Bill",
        "message": "Reminder to pay your bill 💳",
        "reminder_type": RecurrencePattern.MONTHLY,
        "priority": Priority.HIGH,
        "category": "finance"
    },
    {
        "id": "daily_standup",
        "name": "Daily Standup",
        "title": "Team Standup",
        "message": "Time for daily standup meeting! 📋",
        "reminder_type": RecurrencePattern.WEEKDAYS,
        "priority": Priority.MEDIUM,
        "category": "work"
    },
    {
        "id": "water_reminder",
        "name": "Drink Water",
        "title": "Hydration Reminder",
        "message": "Time to drink some water! 💧",
        "reminder_type": RecurrencePattern.DAILY,
        "priority": Priority.LOW,
        "category": "health"
    },
    {
        "id": "study_session",
        "name": "Study Session",
        "title": "Study Time",
        "message": "Time to study! 📚",
        "reminder_type": RecurrencePattern.CUSTOM_DAYS,
        "priority": Priority.MEDIUM,
        "category": "education"
    },
    {
        "id": "sleep_reminder",
        "name": "Bedtime Reminder",
        "title": "Bedtime",
        "message": "Time to get some rest! 😴",
        "reminder_type": RecurrencePattern.DAILY,
        "priority": Priority.MEDIUM,
        "category": "health"
    }
]


class ReminderManager:
    """
    General reminder management system with SQLite database storage
    Features:
    - Multiple reminder types (time_based, recurring, location_based, event_based, custom)
    - Recurrence patterns (daily, weekly, monthly, yearly, custom_days, weekdays, weekends)
    - Snooze functionality (5min, 15min, 30min, 1hr, custom)
    - Priority levels (low, medium, high, urgent)
    - Categories/tags for organization
    - Link to notes, alarms, calendar events
    - Integration with weather_reminder.py
    """
    
    _db_initialized = False
    
    def __init__(self):
        """Initialize reminder manager"""
        self._ensure_db_initialized()
        logger.info("ReminderManager initialized")
    
    def _ensure_db_initialized(self):
        """Ensure database is initialized and schema updated"""
        if not ReminderManager._db_initialized:
            try:
                loop = asyncio.get_event_loop()
                if not loop.is_running():
                    loop.run_until_complete(self._init_schema())
            except Exception as e:
                logger.warning(f"Could not initialize schema: {e}")
            ReminderManager._db_initialized = True
    
    async def _init_schema(self):
        """Initialize database schema with extended reminder fields"""
        await init_database()
        
        conn = await database.connect()
        
        # Check if we need to add new columns to reminders table
        cursor = await conn.execute("PRAGMA table_info(reminders)")
        columns = [row[1] for row in await cursor.fetchall()]
        
        # Add new columns if they don't exist
        new_columns = {
            'title': 'TEXT DEFAULT ""',
            'recurrence_pattern': 'TEXT',
            'recurrence_days': 'TEXT DEFAULT "[]"',
            'completed': 'INTEGER DEFAULT 0',
            'snoozed': 'INTEGER DEFAULT 0',
            'snooze_until': 'TIMESTAMP',
            'priority': 'TEXT DEFAULT "medium"',
            'categories': 'TEXT DEFAULT "[]"',
            'linked_item_id': 'INTEGER',
            'linked_item_type': 'TEXT',
            'trigger_conditions': 'TEXT DEFAULT "{}"',
            'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'last_triggered_at': 'TIMESTAMP',
            'trigger_count': 'INTEGER DEFAULT 0'
        }
        
        for col, col_type in new_columns.items():
            if col not in columns:
                try:
                    await conn.execute(f"ALTER TABLE reminders ADD COLUMN {col} {col_type}")
                    logger.info(f"Added column {col} to reminders table")
                except Exception as e:
                    logger.warning(f"Could not add column {col}: {e}")
        
        await conn.commit()
    
    def _parse_datetime(self, dt_str: str) -> str:
        """Parse datetime string to ISO format"""
        if not dt_str:
            return datetime.now().isoformat()
        
        try:
            # Try parsing as ISO format
            datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return dt_str
        except:
            pass
        
        # Try parsing common formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%d/%m/%Y'
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(dt_str, fmt)
                return dt.isoformat()
            except:
                continue
        
        return datetime.now().isoformat()
    
    def _calculate_next_trigger(self, reminder: Dict[str, Any]) -> Optional[str]:
        """Calculate next trigger time for recurring reminders"""
        pattern = reminder.get('recurrence_pattern')
        if not pattern:
            return None
        
        now = datetime.now()
        trigger_time = reminder.get('trigger_time') or reminder.get('scheduled_time')
        
        if not trigger_time:
            return None
        
        try:
            current_trigger = datetime.fromisoformat(trigger_time.replace('Z', '+00:00'))
        except:
            try:
                current_trigger = datetime.strptime(trigger_time, '%Y-%m-%d %H:%M:%S')
            except:
                return None
        
        if pattern == RecurrencePattern.DAILY:
            next_time = current_trigger + timedelta(days=1)
        elif pattern == RecurrencePattern.WEEKLY:
            next_time = current_trigger + timedelta(weeks=1)
        elif pattern == RecurrencePattern.MONTHLY:
            # Add one month
            month = current_trigger.month + 1
            year = current_trigger.year
            if month > 12:
                month = 1
                year += 1
            try:
                next_time = current_trigger.replace(month=month, year=year)
            except:
                next_time = current_trigger + timedelta(days=30)
        elif pattern == RecurrencePattern.YEARLY:
            try:
                next_time = current_trigger.replace(year=current_trigger.year + 1)
            except:
                next_time = current_trigger + timedelta(days=365)
        elif pattern == RecurrencePattern.CUSTOM_DAYS:
            days = reminder.get('recurrence_days', [])
            if days and isinstance(days, str):
                days = json.loads(days)
            custom_interval = int(days[0]) if days else 1
            next_time = current_trigger + timedelta(days=custom_interval)
        elif pattern == RecurrencePattern.WEEKDAYS:
            # Find next weekday
            next_time = current_trigger + timedelta(days=1)
            while next_time.weekday() >= 5:  # Saturday = 5, Sunday = 6
                next_time += timedelta(days=1)
        elif pattern == RecurrencePattern.WEEKENDS:
            # Find next weekend
            next_time = current_trigger + timedelta(days=1)
            while next_time.weekday() < 5:
                next_time += timedelta(days=1)
        else:
            return None
        
        return next_time.isoformat()
    
    async def create_reminder(
        self,
        user_id: int,
        title: str,
        message: str,
        reminder_type: str = ReminderType.TIME_BASED,
        trigger_time: str = None,
        recurrence_pattern: str = None,
        recurrence_days: List[str] = None,
        priority: str = Priority.MEDIUM,
        categories: List[str] = None,
        linked_item_id: int = None,
        linked_item_type: str = None,
        trigger_conditions: Dict[str, Any] = None,
        enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Create a new reminder
        
        Args:
            user_id: User ID
            title: Reminder title
            message: Reminder message
            reminder_type: Type of reminder (time_based, recurring, etc.)
            trigger_time: When to trigger (ISO format datetime string)
            recurrence_pattern: Recurrence pattern (daily, weekly, etc.)
            recurrence_days: Days for weekly/monthly recurrence
            priority: Priority level (low, medium, high, urgent)
            categories: List of categories/tags
            linked_item_id: ID of linked item (note, alarm, etc.)
            linked_item_type: Type of linked item (note, alarm, calendar_event)
            trigger_conditions: Custom trigger conditions (JSON)
            enabled: Whether reminder is enabled
        
        Returns:
            Created reminder object
        """
        # Parse trigger time
        scheduled_time = self._parse_datetime(trigger_time) if trigger_time else datetime.now().isoformat()
        
        # Create reminder data
        reminder_data = {
            'user_id': user_id,
            'title': title,
            'message': message,
            'type': reminder_type,
            'scheduled_time': scheduled_time,
            'trigger_time': scheduled_time,
            'recurrence_pattern': recurrence_pattern,
            'recurrence_days': json.dumps(recurrence_days or []),
            'priority': priority,
            'categories': json.dumps(categories or []),
            'linked_item_id': linked_item_id,
            'linked_item_type': linked_item_type,
            'trigger_conditions': json.dumps(trigger_conditions or {}),
            'enabled': enabled,
            'completed': False,
            'snoozed': False,
            'trigger_count': 0
        }
        
        cursor = await database.execute(
            """INSERT INTO reminders 
               (user_id, title, message, type, scheduled_time, trigger_time, 
                recurrence_pattern, recurrence_days, priority, categories, 
                linked_item_id, linked_item_type, trigger_conditions, enabled, completed, snoozed, trigger_count)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (reminder_data['user_id'], reminder_data['title'], reminder_data['message'],
             reminder_data['type'], reminder_data['scheduled_time'], reminder_data['trigger_time'],
             reminder_data['recurrence_pattern'], reminder_data['recurrence_days'],
             reminder_data['priority'], reminder_data['categories'], reminder_data['linked_item_id'],
             reminder_data['linked_item_type'], reminder_data['trigger_conditions'],
             1 if enabled else 0, 0, 0, 0)
        )
        
        reminder_id = cursor.lastrowid
        reminder = await self.get_reminder_by_id(reminder_id)
        
        logger.info(f"Created reminder {reminder_id}: {title}")
        
        # Trigger webhook
        await self._trigger_webhook("reminder.created", reminder, user_id)
        
        return reminder
    
    async def get_reminder_by_id(self, reminder_id: int) -> Optional[Dict[str, Any]]:
        """Get a reminder by ID"""
        reminder = await db_get_reminder_by_id(reminder_id)
        if reminder:
            return self._parse_reminder(reminder)
        return None
    
    async def get_reminders(
        self,
        user_id: int,
        enabled_only: bool = False,
        upcoming: bool = False,
        include_completed: bool = True
    ) -> List[Dict[str, Any]]:
        """Get all reminders for a user"""
        reminders = await db_get_reminders(user_id, enabled_only)
        
        parsed_reminders = [self._parse_reminder(r) for r in reminders]
        
        # Filter by upcoming if requested
        if upcoming:
            now = datetime.now()
            parsed_reminders = [
                r for r in parsed_reminders
                if r.get('enabled') and not r.get('completed')
                and datetime.fromisoformat(r.get('trigger_time', r.get('scheduled_time')).replace('Z', '+00:00')) <= now
            ]
        
        # Filter out completed if not requested
        if not include_completed:
            parsed_reminders = [r for r in parsed_reminders if not r.get('completed')]
        
        return parsed_reminders
    
    async def get_due_reminders(self, user_id: int) -> List[Dict[str, Any]]:
        """Get reminders that are due to trigger"""
        now = datetime.now().isoformat()
        
        reminders = await database.fetch_all(
            """SELECT * FROM reminders 
               WHERE user_id = ? AND enabled = 1 AND completed = 0 
               AND (trigger_time IS NULL OR trigger_time <= ?)
               ORDER BY priority DESC, trigger_time""",
            (user_id, now)
        )
        
        return [self._parse_reminder(r) for r in reminders]
    
    async def update_reminder(
        self,
        reminder_id: int,
        title: str = None,
        message: str = None,
        reminder_type: str = None,
        trigger_time: str = None,
        recurrence_pattern: str = None,
        recurrence_days: List[str] = None,
        priority: str = None,
        categories: List[str] = None,
        linked_item_id: int = None,
        linked_item_type: str = None,
        trigger_conditions: Dict[str, Any] = None,
        enabled: bool = None,
        completed: bool = None,
        snoozed: bool = None
    ) -> Optional[Dict[str, Any]]:
        """Update a reminder"""
        updates = []
        params = []
        
        field_map = {
            'title': title,
            'message': message,
            'type': reminder_type,
            'trigger_time': trigger_time,
            'recurrence_pattern': recurrence_pattern,
            'recurrence_days': json.dumps(recurrence_days) if recurrence_days is not None else None,
            'priority': priority,
            'categories': json.dumps(categories) if categories is not None else None,
            'linked_item_id': linked_item_id,
            'linked_item_type': linked_item_type,
            'trigger_conditions': json.dumps(trigger_conditions) if trigger_conditions is not None else None,
            'enabled': 1 if enabled is not None else None,
            'completed': 1 if completed is not None else None,
            'snoozed': 1 if snoozed is not None else None,
            'updated_at': datetime.now().isoformat()
        }
        
        for key, value in field_map.items():
            if value is not None:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if not updates:
            return await self.get_reminder_by_id(reminder_id)
        
        params.append(reminder_id)
        
        await database.execute(
            f"UPDATE reminders SET {', '.join(updates)} WHERE id = ?",
            tuple(params)
        )
        
        reminder = await self.get_reminder_by_id(reminder_id)
        
        # Trigger webhook
        if reminder:
            await self._trigger_webhook("reminder.updated", reminder, reminder.get('user_id'))
        
        return reminder
    
    async def delete_reminder(self, reminder_id: int) -> bool:
        """Delete a reminder"""
        reminder = await self.get_reminder_by_id(reminder_id)
        
        if not reminder:
            return False
        
        result = await db_delete_reminder(reminder_id)
        
        if result:
            # Trigger webhook
            await self._trigger_webhook("reminder.deleted", reminder, reminder.get('user_id'))
        
        return result
    
    async def snooze_reminder(
        self,
        reminder_id: int,
        duration: str = SnoozeDuration.FIFTEEN_MIN,
        custom_minutes: int = None
    ) -> Optional[Dict[str, Any]]:
        """Snooze a reminder"""
        reminder = await self.get_reminder_by_id(reminder_id)
        
        if not reminder:
            return None
        
        # Calculate snooze duration
        if duration == SnoozeDuration.FIVE_MIN:
            snooze_minutes = 5
        elif duration == SnoozeDuration.FIFTEEN_MIN:
            snooze_minutes = 15
        elif duration == SnoozeDuration.THIRTY_MIN:
            snooze_minutes = 30
        elif duration == SnoozeDuration.ONE_HOUR:
            snooze_minutes = 60
        elif duration == SnoozeDuration.TWO_HOURS:
            snooze_minutes = 120
        elif duration == SnoozeDuration.CUSTOM:
            snooze_minutes = custom_minutes or 15
        else:
            snooze_minutes = 15
        
        snooze_until = (datetime.now() + timedelta(minutes=snooze_minutes)).isoformat()
        
        await database.execute(
            "UPDATE reminders SET snoozed = 1, snooze_until = ? WHERE id = ?",
            (snooze_until, reminder_id)
        )
        
        reminder = await self.get_reminder_by_id(reminder_id)
        
        # Trigger webhook
        await self._trigger_webhook("reminder.snoozed", reminder, reminder.get('user_id'))
        
        return reminder
    
    async def complete_reminder(self, reminder_id: int) -> Optional[Dict[str, Any]]:
        """Mark a reminder as completed"""
        reminder = await self.get_reminder_by_id(reminder_id)
        
        if not reminder:
            return None
        
        # Check if it's a recurring reminder
        if reminder.get('recurrence_pattern'):
            # Calculate next trigger time
            next_trigger = self._calculate_next_trigger(reminder)
            
            if next_trigger:
                # Update to next occurrence
                await database.execute(
                    """UPDATE reminders SET completed = 1, trigger_time = ?, 
                       last_triggered_at = ?, trigger_count = trigger_count + 1 
                       WHERE id = ?""",
                    (next_trigger, datetime.now().isoformat(), reminder_id)
                )
            else:
                await database.execute(
                    "UPDATE reminders SET completed = 1 WHERE id = ?",
                    (reminder_id,)
                )
        else:
            await database.execute(
                """UPDATE reminders SET completed = 1, last_triggered_at = ?, 
                   trigger_count = trigger_count + 1 WHERE id = ?""",
                (datetime.now().isoformat(), reminder_id)
            )
        
        reminder = await self.get_reminder_by_id(reminder_id)
        
        # Trigger webhook
        await self._trigger_webhook("reminder.completed", reminder, reminder.get('user_id'))
        
        return reminder
    
    async def trigger_reminder(self, reminder_id: int) -> Optional[Dict[str, Any]]:
        """Manually trigger a reminder"""
        reminder = await self.get_reminder_by_id(reminder_id)
        
        if not reminder:
            return None
        
        # Update last triggered
        await database.execute(
            """UPDATE reminders SET last_triggered_at = ?, 
               trigger_count = trigger_count + 1 WHERE id = ?""",
            (datetime.now().isoformat(), reminder_id)
        )
        
        reminder = await self.get_reminder_by_id(reminder_id)
        
        # Trigger webhook
        await self._trigger_webhook("reminder.triggered", reminder, reminder.get('user_id'))
        
        return reminder
    
    async def get_reminders_by_category(self, user_id: int, category: str) -> List[Dict[str, Any]]:
        """Get reminders by category"""
        reminders = await self.get_reminders(user_id)
        
        return [
            r for r in reminders
            if category.lower() in [c.lower() for c in r.get('categories', [])]
        ]
    
    async def get_reminders_by_priority(self, user_id: int, priority: str) -> List[Dict[str, Any]]:
        """Get reminders by priority"""
        reminders = await self.get_reminders(user_id)
        
        return [r for r in reminders if r.get('priority') == priority.lower()]
    
    async def get_templates(self) -> List[Dict[str, Any]]:
        """Get reminder templates"""
        return REMINDER_TEMPLATES
    
    async def create_from_template(
        self,
        user_id: int,
        template_id: str,
        trigger_time: str,
        custom_message: str = None
    ) -> Optional[Dict[str, Any]]:
        """Create a reminder from a template"""
        template = next((t for t in REMINDER_TEMPLATES if t['id'] == template_id), None)
        
        if not template:
            return None
        
        return await self.create_reminder(
            user_id=user_id,
            title=template['title'],
            message=custom_message or template['message'],
            reminder_type=template.get('reminder_type', ReminderType.RECURRING),
            trigger_time=trigger_time,
            recurrence_pattern=template.get('reminder_type'),
            priority=template.get('priority', Priority.MEDIUM),
            categories=[template.get('category', 'general')]
        )
    
    def _parse_reminder(self, reminder: Dict[str, Any]) -> Dict[str, Any]:
        """Parse reminder database row to proper types"""
        reminder['enabled'] = bool(reminder.get('enabled'))
        reminder['completed'] = bool(reminder.get('completed'))
        reminder['snoozed'] = bool(reminder.get('snoozed'))
        
        # Parse JSON fields
        try:
            reminder['recurrence_days'] = json.loads(reminder.get('recurrence_days', '[]'))
        except:
            reminder['recurrence_days'] = []
        
        try:
            reminder['categories'] = json.loads(reminder.get('categories', '[]'))
        except:
            reminder['categories'] = []
        
        try:
            reminder['trigger_conditions'] = json.loads(reminder.get('trigger_conditions', '{}'))
        except:
            reminder['trigger_conditions'] = {}
        
        return reminder
    
    async def _trigger_webhook(self, event: str, reminder: Dict[str, Any], user_id: int):
        """Trigger webhook for reminder events"""
        if not trigger_webhook:
            return
        
        webhook_data = {
            "event": event,
            "reminder_id": reminder.get('id'),
            "title": reminder.get('title'),
            "message": reminder.get('message'),
            "type": reminder.get('type'),
            "priority": reminder.get('priority'),
            "trigger_time": reminder.get('trigger_time') or reminder.get('scheduled_time'),
            "recurrence_pattern": reminder.get('recurrence_pattern'),
            "completed": reminder.get('completed'),
            "snoozed": reminder.get('snoozed'),
            "triggered_at": datetime.now().isoformat()
        }
        
        try:
            await trigger_webhook(event, webhook_data, user_id)
            logger.info(f"Webhook triggered: {event} for reminder {reminder.get('id')}")
        except Exception as e:
            logger.error(f"Error triggering webhook: {e}")
    
    async def check_and_trigger_due_reminders(self, user_id: int = 1) -> List[Dict[str, Any]]:
        """Check for due reminders and trigger them"""
        due_reminders = await self.get_due_reminders(user_id)
        triggered = []
        
        for reminder in due_reminders:
            # Skip if snoozed
            if reminder.get('snoozed'):
                snooze_until = reminder.get('snooze_until')
                if snooze_until:
                    try:
                        snooze_time = datetime.fromisoformat(snooze_until.replace('Z', '+00:00'))
                        if snooze_time > datetime.now():
                            continue
                        else:
                            # Unsnooze
                            await database.execute(
                                "UPDATE reminders SET snoozed = 0, snooze_until = NULL WHERE id = ?",
                                (reminder['id'],)
                            )
                    except:
                        pass
            
            # Trigger the reminder
            await self.trigger_reminder(reminder['id'])
            
            # For recurring reminders, schedule next occurrence
            if reminder.get('recurrence_pattern'):
                next_trigger = self._calculate_next_trigger(reminder)
                if next_trigger:
                    await database.execute(
                        "UPDATE reminders SET trigger_time = ? WHERE id = ?",
                        (next_trigger, reminder['id'])
                    )
            
            triggered.append(reminder)
            logger.info(f"Triggered reminder {reminder['id']}: {reminder.get('title')}")
        
        return triggered


# Singleton instance
reminder_manager = ReminderManager()


# Helper functions for easy access
async def create_reminder(**kwargs) -> Dict[str, Any]:
    """Create a new reminder"""
    return await reminder_manager.create_reminder(**kwargs)


async def get_reminders(user_id: int, **kwargs) -> List[Dict[str, Any]]:
    """Get all reminders for a user"""
    return await reminder_manager.get_reminders(user_id, **kwargs)


async def get_reminder_by_id(reminder_id: int) -> Optional[Dict[str, Any]]:
    """Get a reminder by ID"""
    return await reminder_manager.get_reminder_by_id(reminder_id)


async def update_reminder(reminder_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """Update a reminder"""
    return await reminder_manager.update_reminder(reminder_id, **kwargs)


async def delete_reminder(reminder_id: int) -> bool:
    """Delete a reminder"""
    return await reminder_manager.delete_reminder(reminder_id)


async def snooze_reminder(reminder_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """Snooze a reminder"""
    return await reminder_manager.snooze_reminder(reminder_id, **kwargs)


async def complete_reminder(reminder_id: int) -> Optional[Dict[str, Any]]:
    """Complete a reminder"""
    return await reminder_manager.complete_reminder(reminder_id)


async def trigger_reminder(reminder_id: int) -> Optional[Dict[str, Any]]:
    """Manually trigger a reminder"""
    return await reminder_manager.trigger_reminder(reminder_id)


async def get_due_reminders(user_id: int) -> List[Dict[str, Any]]:
    """Get due reminders"""
    return await reminder_manager.get_due_reminders(user_id)


async def get_templates() -> List[Dict[str, Any]]:
    """Get reminder templates"""
    return await reminder_manager.get_templates()


async def create_from_template(user_id: int, template_id: str, trigger_time: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Create a reminder from template"""
    return await reminder_manager.create_from_template(user_id, template_id, trigger_time, **kwargs)
