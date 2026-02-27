"""
Chat&Talk GPT - Flashcards Module
Provides flashcard deck management and study functionality with SQLite storage
"""
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from database import (
    init_database,
    create_flashcard_deck as db_create_deck,
    get_flashcard_decks as db_get_decks,
    get_flashcard_deck_by_id as db_get_deck_by_id,
    delete_flashcard_deck as db_delete_deck,
    create_flashcard as db_create_card,
    get_flashcards_by_deck as db_get_cards,
    get_flashcard_by_id as db_get_card_by_id,
    update_flashcard as db_update_card,
    delete_flashcard as db_delete_card
)

logger = logging.getLogger("FlashcardManager")

# Valid categories for flashcard decks
VALID_CATEGORIES = ["language", "science", "math", "history", "general"]


class FlashcardManager:
    """Manages flashcard decks and cards for learning and review with SQLite storage"""
    
    _db_initialized = False
    
    def __init__(self, storage_path: str = None):
        """Initialize the flashcard manager"""
        self.storage_path = Path(storage_path) if storage_path else None
        self._use_database = True
        self._ensure_db_initialized()
        
        logger.info("FlashcardManager initialized with SQLite database")
    
    def _ensure_db_initialized(self):
        """Ensure database is initialized"""
        if not FlashcardManager._db_initialized:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if not loop.is_running():
                    loop.run_until_complete(init_database())
            except:
                pass
            FlashcardManager._db_initialized = True
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.now().isoformat()
    
    def create_deck(self, name: str, description: str = "", category: str = "general") -> Dict:
        """Create a new flashcard deck"""
        import asyncio
        
        if category not in VALID_CATEGORIES:
            logger.warning(f"Invalid category '{category}', using 'general'")
            category = "general"
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_create_deck(1, name, description, category), loop
                )
                deck = future.result(timeout=10)
            else:
                deck = loop.run_until_complete(db_create_deck(1, name, description, category))
            
            logger.info(f"Created flashcard deck: {name} (ID: {deck['id']})")
            return {"success": True, "deck": deck, "message": f"Deck '{name}' created successfully"}
        except Exception as e:
            logger.error(f"Error creating deck in database: {e}")
            return {"success": False, "error": str(e)}
    
    def add_card(self, deck_id: int, front: str, back: str) -> Dict:
        """Add a card to a deck"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_create_card(1, deck_id, front, back), loop
                )
                card = future.result(timeout=10)
            else:
                card = loop.run_until_complete(db_create_card(1, deck_id, front, back))
            
            logger.info(f"Added card to deck {deck_id}: {front[:30]}...")
            return {"success": True, "card": card, "message": "Card added successfully"}
        except Exception as e:
            logger.error(f"Error adding card to database: {e}")
            return {"success": False, "error": str(e)}
    
    def get_deck(self, deck_id: int) -> Dict:
        """Get a deck with all its cards"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(db_get_deck_by_id(deck_id), loop)
                deck = future.result(timeout=10)
            else:
                deck = loop.run_until_complete(db_get_deck_by_id(deck_id))
            
            if deck:
                # Get cards for this deck
                if loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(db_get_cards(deck_id), loop)
                    cards = future.result(timeout=10)
                else:
                    cards = loop.run_until_complete(db_get_cards(deck_id))
                deck['cards'] = cards
            
            return {"success": True, "deck": deck} if deck else {"success": False, "error": "Deck not found"}
        except Exception as e:
            logger.error(f"Error getting deck from database: {e}")
            return {"success": False, "error": str(e)}
    
    def get_all_decks(self) -> List[Dict]:
        """Get all decks (without card details for performance)"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(db_get_decks(1), loop)
                decks = future.result(timeout=10)
            else:
                decks = loop.run_until_complete(db_get_decks(1))
            
            return {"success": True, "decks": decks, "count": len(decks)}
        except Exception as e:
            logger.error(f"Error getting decks from database: {e}")
            return {"success": True, "decks": [], "count": 0}
    
    def delete_deck(self, deck_id: int) -> bool:
        """Delete a deck and all its cards"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(db_delete_deck(deck_id), loop)
                result = future.result(timeout=10)
            else:
                result = loop.run_until_complete(db_delete_deck(deck_id))
            
            logger.info(f"Deleted deck: {deck_id}")
            return result
        except Exception as e:
            logger.error(f"Error deleting deck from database: {e}")
            return False
    
    def delete_card(self, deck_id: int, card_id: int) -> bool:
        """Delete a card from a deck"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(db_delete_card(card_id), loop)
                result = future.result(timeout=10)
            else:
                result = loop.run_until_complete(db_delete_card(card_id))
            
            logger.info(f"Deleted card {card_id} from deck {deck_id}")
            return result
        except Exception as e:
            logger.error(f"Error deleting card from database: {e}")
            return False
    
    def study_deck(self, deck_id: int, limit: int = 10) -> Dict:
        """Get cards from a deck for studying"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(db_get_cards(deck_id), loop)
                cards = future.result(timeout=10)
            else:
                cards = loop.run_until_complete(db_get_cards(deck_id))
            
            if not cards:
                return {"success": True, "cards": [], "message": "No cards in this deck"}
            
            # Update last studied
            if loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    db_update_card(cards[0]['id'], last_reviewed=self._get_timestamp()), loop
                )
            else:
                loop.run_until_complete(
                    db_update_card(cards[0]['id'], last_reviewed=self._get_timestamp())
                )
            
            # Sort: unknown cards first (known=False), then by review count
            sorted_cards = sorted(
                cards,
                key=lambda c: (c.get("known", False), c.get("times_reviewed", 0))
            )
            
            study_cards = sorted_cards[:limit]
            
            study_output = []
            for card in study_cards:
                study_output.append({
                    "id": card["id"],
                    "front": card["front"],
                    "back": card["back"],
                    "times_reviewed": card.get("times_reviewed", 0)
                })
            
            logger.info(f"Studying deck {deck_id}: {len(study_cards)} cards")
            return {
                "success": True,
                "deck_id": deck_id,
                "cards": study_output,
                "total_cards": len(cards),
                "message": f"Showing {len(study_cards)} cards for study"
            }
        except Exception as e:
            logger.error(f"Error studying deck: {e}")
            return {"success": False, "error": str(e)}
    
    def mark_known(self, deck_id: int, card_id: int) -> bool:
        """Mark a card as known (reviewed correctly)"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_update_card(card_id, known=True, times_reviewed=1), loop
                )
                result = future.result(timeout=10)
            else:
                result = loop.run_until_complete(
                    db_update_card(card_id, known=True, times_reviewed=1)
                )
            
            logger.info(f"Marked card {card_id} as known in deck {deck_id}")
            return result is not None
        except Exception as e:
            logger.error(f"Error marking card known: {e}")
            return False
    
    def mark_unknown(self, deck_id: int, card_id: int) -> bool:
        """Mark a card as unknown (needs more practice)"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_update_card(card_id, known=False, times_reviewed=1), loop
                )
                result = future.result(timeout=10)
            else:
                result = loop.run_until_complete(
                    db_update_card(card_id, known=False, times_reviewed=1)
                )
            
            logger.info(f"Marked card {card_id} as unknown in deck {deck_id}")
            return result is not None
        except Exception as e:
            logger.error(f"Error marking card unknown: {e}")
            return False
    
    def search_decks(self, query: str) -> List[Dict]:
        """Search decks by name, description, or category"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(db_get_decks(1), loop)
                decks = future.result(timeout=10)
            else:
                decks = loop.run_until_complete(db_get_decks(1))
            
            query_lower = query.lower()
            results = []
            
            for deck in decks:
                if (query_lower in deck.get("name", "").lower() or
                    query_lower in deck.get("description", "").lower() or
                    query_lower in deck.get("category", "").lower()):
                    results.append(deck)
            
            logger.info(f"Search for '{query}' found {len(results)} results")
            return {"success": True, "results": results, "count": len(results)}
        except Exception as e:
            logger.error(f"Error searching decks: {e}")
            return {"success": True, "results": [], "count": 0}
    
    def get_deck_stats(self, deck_id: int) -> Dict:
        """Get statistics for a deck"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future_deck = asyncio.run_coroutine_threadsafe(db_get_deck_by_id(deck_id), loop)
                deck = future_deck.result(timeout=10)
                future_cards = asyncio.run_coroutine_threadsafe(db_get_cards(deck_id), loop)
                cards = future_cards.result(timeout=10)
            else:
                deck = loop.run_until_complete(db_get_deck_by_id(deck_id))
                cards = loop.run_until_complete(db_get_cards(deck_id))
            
            if not deck:
                return {"success": False, "error": f"Deck with ID {deck_id} not found"}
            
            known_count = sum(1 for c in cards if c.get("known", False))
            unknown_count = len(cards) - known_count
            total_reviews = sum(c.get("times_reviewed", 0) for c in cards)
            
            return {
                "success": True,
                "deck_id": deck_id,
                "deck_name": deck.get("name"),
                "total_cards": len(cards),
                "known_cards": known_count,
                "unknown_cards": unknown_count,
                "total_reviews": total_reviews,
                "last_studied": deck.get("last_studied")
            }
        except Exception as e:
            logger.error(f"Error getting deck stats: {e}")
            return {"success": False, "error": str(e)}
    
    def update_card(self, deck_id: int, card_id: int, front: str = None, back: str = None) -> Dict:
        """Update a card's content"""
        import asyncio
        
        kwargs = {}
        if front is not None:
            kwargs['front'] = front
        if back is not None:
            kwargs['back'] = back
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    db_update_card(card_id, **kwargs), loop
                )
                card = future.result(timeout=10)
            else:
                card = loop.run_until_complete(db_update_card(card_id, **kwargs))
            
            if card:
                logger.info(f"Updated card {card_id} in deck {deck_id}")
                return {"success": True, "card": card, "message": "Card updated successfully"}
            
            return {"success": False, "error": "Card not found"}
        except Exception as e:
            logger.error(f"Error updating card: {e}")
            return {"success": False, "error": str(e)}
    
    def get_categories(self) -> List[str]:
        """Get list of valid categories"""
        return VALID_CATEGORIES.copy()


# Create global instance for easy import
flashcard_manager = FlashcardManager()
