"""
Chat&Talk GPT - SQLite Database Module
Provides async SQLite database connection and schema management
"""
import aiosqlite
import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("Database")

# Database configuration
DATABASE_DIR = Path("data")
DATABASE_PATH = DATABASE_DIR / "chat_talk.db"
BACKUP_DIR = DATABASE_DIR / "backups"


class Database:
    """Async SQLite database manager with connection pooling and schema management"""
    
    _instance: Optional['Database'] = None
    _connection: Optional[aiosqlite.Connection] = None
    
    def __new__(cls):
        """Singleton pattern for database instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize database paths and ensure directories exist"""
        if not hasattr(self, '_initialized'):
            DATABASE_DIR.mkdir(parents=True, exist_ok=True)
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)
            self._initialized = True
            logger.info(f"Database initialized at: {DATABASE_PATH}")
    
    async def connect(self) -> aiosqlite.Connection:
        """Get or create database connection"""
        if self._connection is None:
            self._connection = await aiosqlite.connect(str(DATABASE_PATH))
            self._connection.row_factory = aiosqlite.Row
            # Enable foreign keys
            await self._connection.execute("PRAGMA foreign_keys = ON")
            logger.info("Database connection established")
        return self._connection
    
    async def disconnect(self):
        """Close database connection"""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.info("Database connection closed")
    
    async def initialize_schema(self):
        """Create all database tables"""
        conn = await self.connect()
        
        # Users table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT,
                settings TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Chat history table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Notes table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                title TEXT NOT NULL,
                content TEXT,
                tags TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Alarms table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS alarms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                time TEXT NOT NULL,
                label TEXT DEFAULT '',
                enabled INTEGER DEFAULT 1,
                days TEXT DEFAULT '[]',
                sound TEXT DEFAULT 'default',
                snoozed_until TIMESTAMP,
                snooze_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Calendar events table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS calendar_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                title TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                event_type TEXT DEFAULT 'general',
                reminder INTEGER,
                completed INTEGER DEFAULT 0,
                location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Flashcards - Decks table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS flashcard_decks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT DEFAULT 'general',
                last_studied TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Flashcards - Cards table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                deck_id INTEGER NOT NULL,
                front TEXT NOT NULL,
                back TEXT NOT NULL,
                known INTEGER DEFAULT 0,
                times_reviewed INTEGER DEFAULT 0,
                last_reviewed TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (deck_id) REFERENCES flashcard_decks(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Reminders table (general reminders)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                type TEXT NOT NULL,
                message TEXT NOT NULL,
                scheduled_time TIMESTAMP NOT NULL,
                enabled INTEGER DEFAULT 1,
                last_triggered TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Webhooks table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS webhooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                events TEXT DEFAULT '[]',
                enabled INTEGER DEFAULT 1,
                secret_key TEXT,
                retry_attempts INTEGER DEFAULT 3,
                timeout INTEGER DEFAULT 30,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_triggered_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Usage stats table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS usage_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                feature TEXT NOT NULL,
                count INTEGER DEFAULT 1,
                date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes for better query performance
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_chat_history_user ON chat_history(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_notes_user ON notes(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_alarms_user ON alarms(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_calendar_user ON calendar_events(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_flashcards_deck ON flashcards(deck_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_reminders_user ON reminders(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_stats_user ON usage_stats(user_id)")
        
        await conn.commit()
        logger.info("Database schema initialized")
    
    async def execute(self, query: str, parameters: tuple = ()) -> aiosqlite.Cursor:
        """Execute a query and return cursor"""
        conn = await self.connect()
        cursor = await conn.execute(query, parameters)
        await conn.commit()
        return cursor
    
    async def execute_many(self, query: str, parameters: list) -> aiosqlite.Cursor:
        """Execute a query with multiple parameter sets"""
        conn = await self.connect()
        cursor = await conn.executemany(query, parameters)
        await conn.commit()
        return cursor
    
    async def fetch_one(self, query: str, parameters: tuple = ()) -> Optional[Dict[str, Any]]:
        """Fetch a single row"""
        conn = await self.connect()
        cursor = await conn.execute(query, parameters)
        row = await cursor.fetchone()
        return dict(row) if row else None
    
    async def fetch_all(self, query: str, parameters: tuple = ()) -> List[Dict[str, Any]]:
        """Fetch all rows"""
        conn = await self.connect()
        cursor = await conn.execute(query, parameters)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def create_backup(self, backup_name: str = None) -> Path:
        """Create a database backup"""
        if backup_name is None:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        backup_path = BACKUP_DIR / backup_name
        
        # Close connection before backup
        if self._connection:
            await self.disconnect()
        
        # Copy database file
        shutil.copy2(DATABASE_PATH, backup_path)
        
        # Reconnect
        await self.connect()
        
        logger.info(f"Database backup created: {backup_path}")
        return backup_path
    
    async def restore_backup(self, backup_name: str) -> bool:
        """Restore database from backup"""
        backup_path = BACKUP_DIR / backup_name
        
        if not backup_path.exists():
            logger.error(f"Backup not found: {backup_name}")
            return False
        
        # Close connection
        await self.disconnect()
        
        # Restore backup
        shutil.copy2(backup_path, DATABASE_PATH)
        
        # Reconnect
        await self.connect()
        
        logger.info(f"Database restored from: {backup_name}")
        return True
    
    async def get_backup_list(self) -> List[Dict[str, str]]:
        """Get list of available backups"""
        backups = []
        for file in BACKUP_DIR.glob("*.db"):
            stat = file.stat()
            backups.append({
                "name": file.name,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
            })
        return sorted(backups, key=lambda x: x["created"], reverse=True)
    
    async def vacuum(self):
        """Optimize database (run periodically)"""
        conn = await self.connect()
        await conn.execute("VACUUM")
        logger.info("Database optimized")


# Singleton instance
database = Database()


# Helper functions for common operations
async def init_database():
    """Initialize database connection and schema"""
    await database.connect()
    await database.initialize_schema()


async def close_database():
    """Close database connection"""
    await database.disconnect()


# Notes operations
async def create_note(user_id: int, title: str, content: str, tags: List[str] = None) -> Dict[str, Any]:
    """Create a new note"""
    tags_json = json.dumps(tags or [])
    cursor = await database.execute(
        "INSERT INTO notes (user_id, title, content, tags) VALUES (?, ?, ?, ?)",
        (user_id, title, content, tags_json)
    )
    note_id = cursor.lastrowid
    return await get_note_by_id(note_id)


async def get_notes(user_id: int, limit: int = None) -> List[Dict[str, Any]]:
    """Get all notes for a user"""
    query = "SELECT * FROM notes WHERE user_id = ? ORDER BY updated_at DESC"
    if limit:
        query += f" LIMIT {limit}"
    notes = await database.fetch_all(query, (user_id,))
    for note in notes:
        note['tags'] = json.loads(note.get('tags', '[]'))
    return notes


async def get_note_by_id(note_id: int) -> Optional[Dict[str, Any]]:
    """Get a note by ID"""
    note = await database.fetch_one("SELECT * FROM notes WHERE id = ?", (note_id,))
    if note:
        note['tags'] = json.loads(note.get('tags', '[]'))
    return note


async def update_note(note_id: int, title: str = None, content: str = None, 
                     tags: List[str] = None) -> Optional[Dict[str, Any]]:
    """Update a note"""
    updates = []
    params = []
    
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if content is not None:
        updates.append("content = ?")
        params.append(content)
    if tags is not None:
        updates.append("tags = ?")
        params.append(json.dumps(tags))
    
    if not updates:
        return await get_note_by_id(note_id)
    
    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(note_id)
    
    await database.execute(
        f"UPDATE notes SET {', '.join(updates)} WHERE id = ?",
        tuple(params)
    )
    return await get_note_by_id(note_id)


async def delete_note(note_id: int) -> bool:
    """Delete a note"""
    cursor = await database.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    return cursor.rowcount > 0


async def search_notes(user_id: int, query: str) -> List[Dict[str, Any]]:
    """Search notes by title or content"""
    search_term = f"%{query}%"
    notes = await database.fetch_all(
        "SELECT * FROM notes WHERE user_id = ? AND (title LIKE ? OR content LIKE ?) ORDER BY updated_at DESC",
        (user_id, search_term, search_term)
    )
    for note in notes:
        note['tags'] = json.loads(note.get('tags', '[]'))
    return notes


# Alarm operations
async def create_alarm(user_id: int, time: str, label: str = '', days: List[str] = None, 
                       sound: str = 'default') -> Dict[str, Any]:
    """Create a new alarm"""
    days_json = json.dumps(days or [])
    cursor = await database.execute(
        "INSERT INTO alarms (user_id, time, label, days, sound) VALUES (?, ?, ?, ?, ?)",
        (user_id, time, label, days_json, sound)
    )
    alarm_id = cursor.lastrowid
    return await get_alarm_by_id(alarm_id)


async def get_alarms(user_id: int, enabled_only: bool = False) -> List[Dict[str, Any]]:
    """Get all alarms for a user"""
    query = "SELECT * FROM alarms WHERE user_id = ?"
    if enabled_only:
        query += " AND enabled = 1"
    query += " ORDER BY time"
    
    alarms = await database.fetch_all(query, (user_id,))
    for alarm in alarms:
        alarm['days'] = json.loads(alarm.get('days', '[]'))
        alarm['enabled'] = bool(alarm['enabled'])
    return alarms


async def get_alarm_by_id(alarm_id: int) -> Optional[Dict[str, Any]]:
    """Get an alarm by ID"""
    alarm = await database.fetch_one("SELECT * FROM alarms WHERE id = ?", (alarm_id,))
    if alarm:
        alarm['days'] = json.loads(alarm.get('days', '[]'))
        alarm['enabled'] = bool(alarm['enabled'])
    return alarm


async def update_alarm(alarm_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """Update an alarm"""
    updates = []
    params = []
    
    allowed_fields = ['time', 'label', 'enabled', 'days', 'sound', 'snoozed_until', 'snooze_count']
    
    for key, value in kwargs.items():
        if key in allowed_fields:
            updates.append(f"{key} = ?")
            if key == 'days' and value is not None:
                params.append(json.dumps(value))
            elif key == 'enabled':
                params.append(1 if value else 0)
            else:
                params.append(value)
    
    if not updates:
        return await get_alarm_by_id(alarm_id)
    
    params.append(alarm_id)
    await database.execute(
        f"UPDATE alarms SET {', '.join(updates)} WHERE id = ?",
        tuple(params)
    )
    return await get_alarm_by_id(alarm_id)


async def delete_alarm(alarm_id: int) -> bool:
    """Delete an alarm"""
    cursor = await database.execute("DELETE FROM alarms WHERE id = ?", (alarm_id,))
    return cursor.rowcount > 0


# Calendar operations
async def create_calendar_event(user_id: int, title: str, description: str, date: str, 
                                time: str, event_type: str = 'general', 
                                reminder: int = None, location: str = None) -> Dict[str, Any]:
    """Create a new calendar event"""
    cursor = await database.execute(
        """INSERT INTO calendar_events (user_id, title, description, date, time, event_type, reminder, location)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, title, description, date, time, event_type, reminder, location)
    )
    event_id = cursor.lastrowid
    return await get_calendar_event_by_id(event_id)


async def get_calendar_events(user_id: int, date: str = None, upcoming: int = 7) -> List[Dict[str, Any]]:
    """Get calendar events"""
    if date:
        events = await database.fetch_all(
            "SELECT * FROM calendar_events WHERE user_id = ? AND date = ? ORDER BY time",
            (user_id, date)
        )
    else:
        today = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + __import__('datetime').timedelta(days=upcoming)).strftime('%Y-%m-%d')
        events = await database.fetch_all(
            """SELECT * FROM calendar_events WHERE user_id = ? AND date >= ? AND date <= ? 
               ORDER BY date, time""",
            (user_id, today, end_date)
        )
    
    for event in events:
        event['completed'] = bool(event['completed'])
    return events


async def get_calendar_event_by_id(event_id: int) -> Optional[Dict[str, Any]]:
    """Get a calendar event by ID"""
    event = await database.fetch_one("SELECT * FROM calendar_events WHERE id = ?", (event_id,))
    if event:
        event['completed'] = bool(event['completed'])
    return event


async def update_calendar_event(event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """Update a calendar event"""
    updates = []
    params = []
    
    allowed_fields = ['title', 'description', 'date', 'time', 'event_type', 'reminder', 'completed', 'location']
    
    for key, value in kwargs.items():
        if key in allowed_fields:
            updates.append(f"{key} = ?")
            if key == 'completed':
                params.append(1 if value else 0)
            else:
                params.append(value)
    
    if not updates:
        return await get_calendar_event_by_id(event_id)
    
    params.append(event_id)
    await database.execute(
        f"UPDATE calendar_events SET {', '.join(updates)} WHERE id = ?",
        tuple(params)
    )
    return await get_calendar_event_by_id(event_id)


async def delete_calendar_event(event_id: int) -> bool:
    """Delete a calendar event"""
    cursor = await database.execute("DELETE FROM calendar_events WHERE id = ?", (event_id,))
    return cursor.rowcount > 0


# Flashcard operations
async def create_flashcard_deck(user_id: int, name: str, description: str = '', 
                                  category: str = 'general') -> Dict[str, Any]:
    """Create a new flashcard deck"""
    cursor = await database.execute(
        "INSERT INTO flashcard_decks (user_id, name, description, category) VALUES (?, ?, ?, ?)",
        (user_id, name, description, category)
    )
    deck_id = cursor.lastrowid
    return await get_flashcard_deck_by_id(deck_id)


async def get_flashcard_decks(user_id: int) -> List[Dict[str, Any]]:
    """Get all flashcard decks for a user"""
    decks = await database.fetch_all(
        """SELECT d.*, COUNT(c.id) as card_count 
           FROM flashcard_decks d 
           LEFT JOIN flashcards c ON d.id = c.deck_id 
           WHERE d.user_id = ? 
           GROUP BY d.id 
           ORDER BY d.created_at DESC""",
        (user_id,)
    )
    return decks


async def get_flashcard_deck_by_id(deck_id: int) -> Optional[Dict[str, Any]]:
    """Get a flashcard deck by ID"""
    deck = await database.fetch_one(
        """SELECT d.*, COUNT(c.id) as card_count 
           FROM flashcard_decks d 
           LEFT JOIN flashcards c ON d.id = c.deck_id 
           WHERE d.id = ? 
           GROUP BY d.id""",
        (deck_id,)
    )
    return deck


async def delete_flashcard_deck(deck_id: int) -> bool:
    """Delete a flashcard deck"""
    cursor = await database.execute("DELETE FROM flashcard_decks WHERE id = ?", (deck_id,))
    return cursor.rowcount > 0


async def create_flashcard(user_id: int, deck_id: int, front: str, back: str) -> Dict[str, Any]:
    """Create a new flashcard"""
    cursor = await database.execute(
        "INSERT INTO flashcards (user_id, deck_id, front, back) VALUES (?, ?, ?, ?)",
        (user_id, deck_id, front, back)
    )
    card_id = cursor.lastrowid
    return await get_flashcard_by_id(card_id)


async def get_flashcards_by_deck(deck_id: int) -> List[Dict[str, Any]]:
    """Get all flashcards in a deck"""
    cards = await database.fetch_all(
        "SELECT * FROM flashcards WHERE deck_id = ? ORDER BY created_at",
        (deck_id,)
    )
    for card in cards:
        card['known'] = bool(card['known'])
    return cards


async def get_flashcard_by_id(card_id: int) -> Optional[Dict[str, Any]]:
    """Get a flashcard by ID"""
    card = await database.fetch_one("SELECT * FROM flashcards WHERE id = ?", (card_id,))
    if card:
        card['known'] = bool(card['known'])
    return card


async def update_flashcard(card_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """Update a flashcard"""
    updates = []
    params = []
    
    allowed_fields = ['front', 'back', 'known', 'times_reviewed', 'last_reviewed']
    
    for key, value in kwargs.items():
        if key in allowed_fields:
            updates.append(f"{key} = ?")
            if key == 'known':
                params.append(1 if value else 0)
            else:
                params.append(value)
    
    if not updates:
        return await get_flashcard_by_id(card_id)
    
    params.append(card_id)
    await database.execute(
        f"UPDATE flashcards SET {', '.join(updates)} WHERE id = ?",
        tuple(params)
    )
    return await get_flashcard_by_id(card_id)


async def delete_flashcard(card_id: int) -> bool:
    """Delete a flashcard"""
    cursor = await database.execute("DELETE FROM flashcards WHERE id = ?", (card_id,))
    return cursor.rowcount > 0


# Chat history operations
async def add_chat_message(user_id: int, role: str, content: str) -> Dict[str, Any]:
    """Add a chat message"""
    cursor = await database.execute(
        "INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)",
        (user_id, role, content)
    )
    message_id = cursor.lastrowid
    return await get_chat_message_by_id(message_id)


async def get_chat_history(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """Get chat history for a user"""
    return await database.fetch_all(
        "SELECT * FROM chat_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
        (user_id, limit)
    )


async def get_chat_message_by_id(message_id: int) -> Optional[Dict[str, Any]]:
    """Get a chat message by ID"""
    return await database.fetch_one("SELECT * FROM chat_history WHERE id = ?", (message_id,))


async def clear_chat_history(user_id: int) -> bool:
    """Clear chat history for a user"""
    await database.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
    return True


# Reminder operations
async def create_reminder(user_id: int, reminder_type: str, message: str, 
                         scheduled_time: str, enabled: bool = True) -> Dict[str, Any]:
    """Create a new reminder"""
    cursor = await database.execute(
        "INSERT INTO reminders (user_id, type, message, scheduled_time, enabled) VALUES (?, ?, ?, ?, ?)",
        (user_id, reminder_type, message, scheduled_time, 1 if enabled else 0)
    )
    reminder_id = cursor.lastrowid
    return await get_reminder_by_id(reminder_id)


async def get_reminders(user_id: int, enabled_only: bool = False) -> List[Dict[str, Any]]:
    """Get all reminders for a user"""
    query = "SELECT * FROM reminders WHERE user_id = ?"
    if enabled_only:
        query += " AND enabled = 1"
    query += " ORDER BY scheduled_time"
    
    reminders = await database.fetch_all(query, (user_id,))
    for reminder in reminders:
        reminder['enabled'] = bool(reminder['enabled'])
    return reminders


async def get_reminder_by_id(reminder_id: int) -> Optional[Dict[str, Any]]:
    """Get a reminder by ID"""
    reminder = await database.fetch_one("SELECT * FROM reminders WHERE id = ?", (reminder_id,))
    if reminder:
        reminder['enabled'] = bool(reminder['enabled'])
    return reminder


async def update_reminder(reminder_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """Update a reminder"""
    updates = []
    params = []
    
    allowed_fields = ['type', 'message', 'scheduled_time', 'enabled', 'last_triggered']
    
    for key, value in kwargs.items():
        if key in allowed_fields:
            updates.append(f"{key} = ?")
            if key == 'enabled':
                params.append(1 if value else 0)
            else:
                params.append(value)
    
    if not updates:
        return await get_reminder_by_id(reminder_id)
    
    params.append(reminder_id)
    await database.execute(
        f"UPDATE reminders SET {', '.join(updates)} WHERE id = ?",
        tuple(params)
    )
    return await get_reminder_by_id(reminder_id)


async def delete_reminder(reminder_id: int) -> bool:
    """Delete a reminder"""
    cursor = await database.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
    return cursor.rowcount > 0


# Usage stats operations
async def record_usage(user_id: int, feature: str, date: str = None) -> Dict[str, Any]:
    """Record usage of a feature"""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    # Check if entry exists for today
    existing = await database.fetch_one(
        "SELECT * FROM usage_stats WHERE user_id = ? AND feature = ? AND date = ?",
        (user_id, feature, date)
    )
    
    if existing:
        # Update count
        await database.execute(
            "UPDATE usage_stats SET count = count + 1 WHERE id = ?",
            (existing['id'],)
        )
    else:
        # Create new entry
        await database.execute(
            "INSERT INTO usage_stats (user_id, feature, date) VALUES (?, ?, ?)",
            (user_id, feature, date)
        )
    
    return {"success": True}


async def get_usage_stats(user_id: int, feature: str = None, days: int = 30) -> List[Dict[str, Any]]:
    """Get usage statistics"""
    start_date = (datetime.now() - __import__('datetime').timedelta(days=days)).strftime('%Y-%m-%d')
    
    if feature:
        return await database.fetch_all(
            """SELECT * FROM usage_stats 
               WHERE user_id = ? AND feature = ? AND date >= ? 
               ORDER BY date DESC""",
            (user_id, feature, start_date)
        )
    else:
        return await database.fetch_all(
            """SELECT * FROM usage_stats 
               WHERE user_id = ? AND date >= ? 
               ORDER BY date DESC""",
            (user_id, start_date)
        )
