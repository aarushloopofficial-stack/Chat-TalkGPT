"""
Chat&Talk GPT - Notes Manager
Local note-taking system with SQLite database storage
"""
import json
import logging
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from database import (
    init_database, database,
    create_note as db_create_note,
    get_notes as db_get_notes,
    get_note_by_id as db_get_note_by_id,
    update_note as db_update_note,
    delete_note as db_delete_note,
    search_notes as db_search_notes
)

logger = logging.getLogger("NotesManager")


class NotesManager:
    """
    Notes management system with SQLite database storage
    Features:
    - Create, read, update, delete notes
    - Full-text search across notes
    - Note categorization with tags
    - Async-compatible methods
    """
    
    _db_initialized = False
    
    def __init__(self, notes_file: str = None):
        """Initialize notes manager"""
        # Legacy parameter - kept for backward compatibility
        self.notes_file = Path(notes_file) if notes_file else None
        self._use_database = True  # Always use database by default
        self._ensure_db_initialized()
        
        logger.info("NotesManager initialized with SQLite database")
    
    def _ensure_db_initialized(self):
        """Ensure database is initialized"""
        if not NotesManager._db_initialized:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're in an async context, we can't await here
                    # Just mark as initialized, actual init will happen on first use
                    pass
                else:
                    loop.run_until_complete(init_database())
            except:
                pass
            NotesManager._db_initialized = True
    
    def _generate_id(self) -> str:
        """Generate unique note ID"""
        return str(uuid.uuid4())[:8]
    
    async def _async_init(self):
        """Async initialization"""
        await init_database()
    
    def create_note(self, title: str, content: str, tags: List[str] = None) -> Dict[str, Any]:
        """
        Create a new note
        
        Args:
            title: Note title
            content: Note content
            tags: Optional list of tags
        
        Returns:
            Created note dictionary
        """
        import asyncio
        
        if not title:
            title = "Untitled Note"
        
        # Run async database operation in sync context
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Create a new task
                future = asyncio.run_coroutine_threadsafe(
                    db_create_note(1, title.strip(), content.strip(), tags or []),
                    loop
                )
                note = future.result(timeout=10)
            else:
                note = loop.run_until_complete(
                    db_create_note(1, title.strip(), content.strip(), tags or [])
                )
        except Exception as e:
            logger.error(f"Error creating note in database: {e}")
            # Fallback to JSON storage
            note = self._create_note_json(title, content, tags)
        
        logger.info(f"Created note: {note['id']} - {title}")
        return note
    
    def _create_note_json(self, title: str, content: str, tags: List[str] = None) -> Dict[str, Any]:
        """Fallback JSON storage"""
        if self.notes_file:
            self.notes_file.parent.mkdir(parents=True, exist_ok=True)
            try:
                with open(self.notes_file, "r", encoding="utf-8") as f:
                    notes = json.load(f)
            except:
                notes = []
            
            note = {
                "id": self._generate_id(),
                "title": title.strip(),
                "content": content.strip(),
                "tags": tags or [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            notes.insert(0, note)
            
            with open(self.notes_file, "w", encoding="utf-8") as f:
                json.dump(notes, f, indent=2, ensure_ascii=False)
            
            return note
        return {"id": "0", "title": title, "content": content, "tags": tags or []}
    
    def get_notes(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get all notes, optionally limited
        
        Args:
            limit: Maximum number of notes to return
        
        Returns:
            List of note dictionaries
        """
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_get_notes(1, limit), loop
                )
                notes = future.result(timeout=10)
            else:
                notes = loop.run_until_complete(db_get_notes(1, limit))
        except Exception as e:
            logger.error(f"Error getting notes from database: {e}")
            notes = self._get_notes_json(limit)
        
        return notes
    
    def _get_notes_json(self, limit: int = None) -> List[Dict[str, Any]]:
        """Fallback JSON storage"""
        if self.notes_file and self.notes_file.exists():
            try:
                with open(self.notes_file, "r", encoding="utf-8") as f:
                    notes = json.load(f)
                return notes[:limit] if limit else notes
            except:
                pass
        return []
    
    def get_note(self, note_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific note by ID
        
        Args:
            note_id: Note ID
        
        Returns:
            Note dictionary or None if not found
        """
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_get_note_by_id(int(note_id)), loop
                )
                note = future.result(timeout=10)
            else:
                note = loop.run_until_complete(db_get_note_by_id(int(note_id)))
            return note
        except Exception as e:
            logger.error(f"Error getting note from database: {e}")
            return self._get_note_json(note_id)
    
    def _get_note_json(self, note_id: str) -> Optional[Dict[str, Any]]:
        """Fallback JSON storage"""
        if self.notes_file and self.notes_file.exists():
            try:
                with open(self.notes_file, "r", encoding="utf-8") as f:
                    notes = json.load(f)
                for note in notes:
                    if note.get("id") == note_id:
                        return note
            except:
                pass
        return None
    
    def update_note(self, note_id: str, title: str = None, content: str = None, 
                    tags: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Update an existing note
        
        Args:
            note_id: Note ID
            title: New title (optional)
            content: New content (optional)
            tags: New tags (optional)
        
        Returns:
            Updated note dictionary or None if not found
        """
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_update_note(int(note_id), title, content, tags), loop
                )
                note = future.result(timeout=10)
            else:
                note = loop.run_until_complete(
                    db_update_note(int(note_id), title, content, tags)
                )
            if note:
                logger.info(f"Updated note: {note_id}")
            return note
        except Exception as e:
            logger.error(f"Error updating note in database: {e}")
            return self._update_note_json(note_id, title, content, tags)
    
    def _update_note_json(self, note_id: str, title: str = None, content: str = None, 
                          tags: List[str] = None) -> Optional[Dict[str, Any]]:
        """Fallback JSON storage"""
        if self.notes_file and self.notes_file.exists():
            try:
                with open(self.notes_file, "r", encoding="utf-8") as f:
                    notes = json.load(f)
                
                for i, note in enumerate(notes):
                    if note.get("id") == note_id:
                        if title is not None:
                            notes[i]["title"] = title.strip()
                        if content is not None:
                            notes[i]["content"] = content.strip()
                        if tags is not None:
                            notes[i]["tags"] = tags
                        notes[i]["updated_at"] = datetime.now().isoformat()
                        
                        with open(self.notes_file, "w", encoding="utf-8") as f:
                            json.dump(notes, f, indent=2, ensure_ascii=False)
                        
                        return notes[i]
            except:
                pass
        return None
    
    def delete_note(self, note_id: str) -> bool:
        """
        Delete a note
        
        Args:
            note_id: Note ID
        
        Returns:
            True if deleted, False if not found
        """
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_delete_note(int(note_id)), loop
                )
                result = future.result(timeout=10)
            else:
                result = loop.run_until_complete(db_delete_note(int(note_id)))
            
            if result:
                logger.info(f"Deleted note: {note_id}")
            return result
        except Exception as e:
            logger.error(f"Error deleting note from database: {e}")
            return self._delete_note_json(note_id)
    
    def _delete_note_json(self, note_id: str) -> bool:
        """Fallback JSON storage"""
        if self.notes_file and self.notes_file.exists():
            try:
                with open(self.notes_file, "r", encoding="utf-8") as f:
                    notes = json.load(f)
                
                for i, note in enumerate(notes):
                    if note.get("id") == note_id:
                        notes.pop(i)
                        with open(self.notes_file, "w", encoding="utf-8") as f:
                            json.dump(notes, f, indent=2, ensure_ascii=False)
                        return True
            except:
                pass
        return False
    
    def search_notes(self, query: str) -> List[Dict[str, Any]]:
        """
        Search notes by query string
        Searches in title, content, and tags
        
        Args:
            query: Search query string
        
        Returns:
            List of matching note dictionaries
        """
        import asyncio
        
        if not query:
            return self.get_notes()
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_search_notes(1, query), loop
                )
                results = future.result(timeout=10)
            else:
                results = loop.run_until_complete(db_search_notes(1, query))
            
            logger.info(f"Search for '{query}' found {len(results)} notes")
            return results
        except Exception as e:
            logger.error(f"Error searching notes in database: {e}")
            return self._search_notes_json(query)
    
    def _search_notes_json(self, query: str) -> List[Dict[str, Any]]:
        """Fallback JSON search"""
        if self.notes_file and self.notes_file.exists():
            try:
                with open(self.notes_file, "r", encoding="utf-8") as f:
                    notes = json.load(f)
                
                query_lower = query.lower()
                results = []
                
                for note in notes:
                    if query_lower in note.get("title", "").lower():
                        results.append(note)
                    elif query_lower in note.get("content", "").lower():
                        results.append(note)
                    else:
                        for tag in note.get("tags", []):
                            if query_lower in tag.lower():
                                results.append(note)
                                break
                
                return results
            except:
                pass
        return []
    
    def get_notes_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get all notes with a specific tag"""
        all_notes = self.get_notes()
        tag_lower = tag.lower()
        results = []
        
        for note in all_notes:
            for note_tag in note.get("tags", []):
                if tag_lower == note_tag.lower():
                    results.append(note)
                    break
        
        return results
    
    def get_all_tags(self) -> List[str]:
        """Get all unique tags from all notes"""
        tags_set = set()
        all_notes = self.get_notes()
        
        for note in all_notes:
            for tag in note.get("tags", []):
                tags_set.add(tag.lower())
        
        return sorted(list(tags_set))
    
    def add_tag_to_note(self, note_id: str, tag: str) -> Optional[Dict[str, Any]]:
        """Add a tag to a note"""
        note = self.get_note(note_id)
        if note:
            tags = note.get("tags", [])
            if tag.lower() not in [t.lower() for t in tags]:
                tags.append(tag)
                return self.update_note(note_id, tags=tags)
        return None
    
    def remove_tag_from_note(self, note_id: str, tag: str) -> Optional[Dict[str, Any]]:
        """Remove a tag from a note"""
        note = self.get_note(note_id)
        if note:
            tags = [t for t in note.get("tags", []) if t.lower() != tag.lower()]
            return self.update_note(note_id, tags=tags)
        return None
    
    def get_note_count(self) -> int:
        """Get total number of notes"""
        return len(self.get_notes())
    
    def get_recent_notes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most recently updated notes"""
        notes = self.get_notes()
        sorted_notes = sorted(
            notes,
            key=lambda x: x.get("updated_at", ""),
            reverse=True
        )
        return sorted_notes[:limit]
    
    def clear_all_notes(self) -> bool:
        """Delete all notes (use with caution)"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            notes = self.get_notes()
            for note in notes:
                if loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        db_delete_note(note['id']), loop
                    )
                    future.result(timeout=10)
                else:
                    loop.run_until_complete(db_delete_note(note['id']))
            
            logger.warning("Cleared all notes from database")
            return True
        except Exception as e:
            logger.error(f"Error clearing notes: {e}")
            return False


# Singleton instance
_notes_manager: Optional[NotesManager] = None


def get_notes_manager() -> NotesManager:
    """Get or create notes manager singleton"""
    global _notes_manager
    if _notes_manager is None:
        _notes_manager = NotesManager()
    return _notes_manager
