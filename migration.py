"""
Chat&Talk GPT - Database Migration Utilities
Handles importing data from JSON files to SQLite and schema migrations
"""
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from database import database, init_database

logger = logging.getLogger("Migration")


class DataMigration:
    """Handles migration of data from JSON files to SQLite database"""
    
    def __init__(self):
        self.memory_dir = Path("memory")
        self.migrated_count = 0
    
    async def migrate_all(self) -> Dict[str, Any]:
        """Migrate all data from JSON files to SQLite"""
        results = {
            "notes": await self.migrate_notes(),
            "alarms": await self.migrate_alarms(),
            "calendar_events": await self.migrate_calendar_events(),
            "flashcards": await self.migrate_flashcards(),
            "chat_history": await self.migrate_chat_history(),
            "weather_reminders": await self.migrate_weather_reminders()
        }
        
        logger.info(f"Migration complete. Total items migrated: {self.migrated_count}")
        return results
    
    async def migrate_notes(self) -> Dict[str, Any]:
        """Migrate notes from JSON to SQLite"""
        notes_file = self.memory_dir / "notes.json"
        
        if not notes_file.exists():
            logger.warning(f"Notes file not found: {notes_file}")
            return {"success": False, "message": "File not found", "count": 0}
        
        try:
            with open(notes_file, 'r', encoding='utf-8') as f:
                notes = json.load(f)
            
            if not notes:
                return {"success": True, "message": "No notes to migrate", "count": 0}
            
            from database import create_note
            
            for note in notes:
                await create_note(
                    user_id=1,
                    title=note.get('title', 'Untitled'),
                    content=note.get('content', ''),
                    tags=note.get('tags', [])
                )
                self.migrated_count += 1
            
            logger.info(f"Migrated {len(notes)} notes")
            return {"success": True, "message": f"Migrated {len(notes)} notes", "count": len(notes)}
        
        except Exception as e:
            logger.error(f"Error migrating notes: {e}")
            return {"success": False, "message": str(e), "count": 0}
    
    async def migrate_alarms(self) -> Dict[str, Any]:
        """Migrate alarms from JSON to SQLite"""
        alarms_file = self.memory_dir / "alarms.json"
        
        if not alarms_file.exists():
            logger.warning(f"Alarms file not found: {alarms_file}")
            return {"success": False, "message": "File not found", "count": 0}
        
        try:
            with open(alarms_file, 'r', encoding='utf-8') as f:
                alarms = json.load(f)
            
            if not alarms:
                return {"success": True, "message": "No alarms to migrate", "count": 0}
            
            from database import create_alarm
            
            for alarm in alarms:
                await create_alarm(
                    user_id=1,
                    time=alarm.get('time', '00:00'),
                    label=alarm.get('label', ''),
                    days=alarm.get('days', []),
                    sound=alarm.get('sound', 'default')
                )
                self.migrated_count += 1
            
            logger.info(f"Migrated {len(alarms)} alarms")
            return {"success": True, "message": f"Migrated {len(alarms)} alarms", "count": len(alarms)}
        
        except Exception as e:
            logger.error(f"Error migrating alarms: {e}")
            return {"success": False, "message": str(e), "count": 0}
    
    async def migrate_calendar_events(self) -> Dict[str, Any]:
        """Migrate calendar events from JSON to SQLite"""
        events_file = self.memory_dir / "calendar_events.json"
        
        if not events_file.exists():
            logger.warning(f"Calendar events file not found: {events_file}")
            return {"success": False, "message": "File not found", "count": 0}
        
        try:
            with open(events_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            if not events:
                return {"success": True, "message": "No events to migrate", "count": 0}
            
            from database import create_calendar_event
            
            for event in events:
                await create_calendar_event(
                    user_id=1,
                    title=event.get('title', ''),
                    description=event.get('description', ''),
                    date=event.get('date', ''),
                    time=event.get('time', '00:00'),
                    event_type=event.get('event_type', 'general'),
                    reminder=event.get('reminder'),
                    location=event.get('location')
                )
                self.migrated_count += 1
            
            logger.info(f"Migrated {len(events)} calendar events")
            return {"success": True, "message": f"Migrated {len(events)} events", "count": len(events)}
        
        except Exception as e:
            logger.error(f"Error migrating calendar events: {e}")
            return {"success": False, "message": str(e), "count": 0}
    
    async def migrate_flashcards(self) -> Dict[str, Any]:
        """Migrate flashcards from JSON to SQLite"""
        flashcards_file = self.memory_dir / "flashcards.json"
        
        if not flashcards_file.exists():
            logger.warning(f"Flashcards file not found: {flashcards_file}")
            return {"success": False, "message": "File not found", "count": 0}
        
        try:
            with open(flashcards_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            decks = data.get('decks', [])
            if not decks:
                return {"success": True, "message": "No flashcards to migrate", "count": 0}
            
            from database import create_flashcard_deck, create_flashcard
            
            total_cards = 0
            for deck in decks:
                # Create deck
                deck_result = await create_flashcard_deck(
                    user_id=1,
                    name=deck.get('name', 'Untitled Deck'),
                    description=deck.get('description', ''),
                    category=deck.get('category', 'general')
                )
                
                # Get deck ID from result
                deck_id = deck_result.get('id')
                
                # Add cards
                cards = deck.get('cards', [])
                for card in cards:
                    await create_flashcard(
                        user_id=1,
                        deck_id=deck_id,
                        front=card.get('front', ''),
                        back=card.get('back', '')
                    )
                    total_cards += 1
                    self.migrated_count += 1
            
            logger.info(f"Migrated {len(decks)} decks with {total_cards} cards")
            return {"success": True, "message": f"Migrated {len(decks)} decks with {total_cards} cards", "count": len(decks)}
        
        except Exception as e:
            logger.error(f"Error migrating flashcards: {e}")
            return {"success": False, "message": str(e), "count": 0}
    
    async def migrate_chat_history(self) -> Dict[str, Any]:
        """Migrate chat history from JSON to SQLite"""
        chat_file = self.memory_dir / "chat_history.json"
        
        if not chat_file.exists():
            logger.warning(f"Chat history file not found: {chat_file}")
            return {"success": False, "message": "File not found", "count": 0}
        
        try:
            with open(chat_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            messages = data.get('messages', [])
            if not messages:
                return {"success": True, "message": "No chat messages to migrate", "count": 0}
            
            from database import add_chat_message
            
            for msg in messages:
                await add_chat_message(
                    user_id=1,
                    role=msg.get('role', 'user'),
                    content=msg.get('content', '')
                )
                self.migrated_count += 1
            
            logger.info(f"Migrated {len(messages)} chat messages")
            return {"success": True, "message": f"Migrated {len(messages)} messages", "count": len(messages)}
        
        except Exception as e:
            logger.error(f"Error migrating chat history: {e}")
            return {"success": False, "message": str(e), "count": 0}
    
    async def migrate_weather_reminders(self) -> Dict[str, Any]:
        """Migrate weather reminders from JSON to SQLite"""
        weather_file = self.memory_dir / "aakansha_weather_reminders.json"
        
        if not weather_file.exists():
            # Check alternative location
            weather_file = Path("backend/memory/aakansha_weather_reminders.json")
        
        if not weather_file.exists():
            logger.warning(f"Weather reminders file not found")
            return {"success": False, "message": "File not found", "count": 0}
        
        try:
            with open(weather_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            reminders = data.get('reminders', [])
            if not reminders:
                return {"success": True, "message": "No weather reminders to migrate", "count": 0}
            
            from database import create_reminder
            
            for reminder in reminders:
                # Convert weather reminder to general reminder
                scheduled_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                await create_reminder(
                    user_id=1,
                    reminder_type='weather',
                    message=reminder.get('message', ''),
                    scheduled_time=scheduled_time,
                    enabled=reminder.get('active', True)
                )
                self.migrated_count += 1
            
            logger.info(f"Migrated {len(reminders)} weather reminders")
            return {"success": True, "message": f"Migrated {len(reminders)} reminders", "count": len(reminders)}
        
        except Exception as e:
            logger.error(f"Error migrating weather reminders: {e}")
            return {"success": False, "message": str(e), "count": 0}


async def run_migration():
    """Run the complete migration process"""
    # Initialize database
    await init_database()
    
    # Create migration instance
    migration = DataMigration()
    
    # Run migration
    results = await migration.migrate_all()
    
    # Create backup after migration
    await database.create_backup(f"pre_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    
    return results


# Schema migration utilities
class SchemaMigration:
    """Handles database schema migrations"""
    
    def __init__(self):
        self.version = 1
    
    async def get_schema_version(self) -> int:
        """Get current schema version"""
        try:
            result = await database.fetch_one("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
            return result['version'] if result else 0
        except:
            return 0
    
    async def create_version_table(self):
        """Create schema version tracking table"""
        await database.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        """)
    
    async def apply_migrations(self):
        """Apply any pending schema migrations"""
        await self.create_version_table()
        
        current_version = await self.get_schema_version()
        
        # Future migrations can be added here
        # if current_version < 2:
        #     await self.migration_002()
        
        logger.info(f"Schema version: {current_version}")


# Run migration on module import if requested
if __name__ == "__main__":
    import asyncio
    
    async def main():
        results = await run_migration()
        print("Migration Results:")
        for key, value in results.items():
            print(f"  {key}: {value}")
    
    asyncio.run(main())
