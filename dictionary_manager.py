"""
Chat&Talk GPT - Dictionary Manager
Provides word definitions, synonyms, antonyms, and pronunciations using free APIs
"""
import requests
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger("DictionaryManager")

# Free Dictionary API endpoints
DICTIONARY_API_BASE = "https://api.dictionaryapi.dev/api/v2/entries/en"
DATAMUSE_API_BASE = "https://api.datamuse.com/words"


class DictionaryManager:
    """Manages dictionary operations using free APIs"""
    
    def __init__(self, user_agent: str = "ChatAndTalkGPT/1.0 (Educational Assistant)"):
        """
        Initialize the DictionaryManager
        
        Args:
            user_agent: User agent string for API requests
        """
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
        logger.info("DictionaryManager initialized")
    
    async def define(self, word: str) -> Dict[str, Any]:
        """
        Get definition, pronunciation, part of speech, and examples for a word
        
        Args:
            word: The word to look up
            
        Returns:
            Dictionary with word information including definitions
        """
        try:
            url = f"{DICTIONARY_API_BASE}/{word.lower().strip()}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 404:
                return {
                    "success": False,
                    "word": word,
                    "error": f"Word '{word}' not found in dictionary"
                }
            
            response.raise_for_status()
            data = response.json()
            
            if not data or len(data) == 0:
                return {
                    "success": False,
                    "word": word,
                    "error": "No definition found"
                }
            
            # Parse the response
            entry = data[0]
            word = entry.get("word", word)
            
            # Get phonetic
            phonetic = ""
            if "phonetic" in entry:
                phonetic = entry.get("phonetic", "")
            elif "phonetics" in entry:
                for ph in entry.get("phonetics", []):
                    if ph.get("text"):
                        phonetic = ph.get("text", "")
                        break
            
            # Get audio URL if available
            audio_url = ""
            if "phonetics" in entry:
                for ph in entry.get("phonetics", []):
                    if ph.get("audio"):
                        audio_url = ph.get("audio", "")
                        break
            
            # Collect definitions
            definitions = []
            for meaning in entry.get("meanings", []):
                part_of_speech = meaning.get("partOfSpeech", "")
                for def_obj in meaning.get("definitions", []):
                    definition_text = def_obj.get("definition", "")
                    example = def_obj.get("example", "")
                    
                    definitions.append({
                        "part_of_speech": part_of_speech,
                        "definition": definition_text,
                        "example": example
                    })
            
            return {
                "success": True,
                "word": word,
                "phonetic": phonetic,
                "audio_url": audio_url,
                "definitions": definitions
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Dictionary API error for '{word}': {e}")
            return {
                "success": False,
                "word": word,
                "error": "Failed to connect to dictionary service"
            }
        except Exception as e:
            logger.error(f"Error defining word '{word}': {e}")
            return {
                "success": False,
                "word": word,
                "error": str(e)
            }
    
    async def get_synonyms(self, word: str) -> List[str]:
        """
        Get synonyms for a word using Datamuse API
        
        Args:
            word: The word to find synonyms for
            
        Returns:
            List of synonym strings
        """
        try:
            url = f"{DATAMUSE_API_BASE}?rel_syn={word.lower().strip()}&max=20"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            synonyms = [item.get("word", "") for item in data if item.get("word")]
            
            return list(set(synonyms))  # Remove duplicates
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Datamuse API error for synonyms of '{word}': {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting synonyms for '{word}': {e}")
            return []
    
    async def get_antonyms(self, word: str) -> List[str]:
        """
        Get antonyms for a word using Datamuse API
        
        Args:
            word: The word to find antonyms for
            
        Returns:
            List of antonym strings
        """
        try:
            url = f"{DATAMUSE_API_BASE}?rel_ant={word.lower().strip()}&max=20"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            antonyms = [item.get("word", "") for item in data if item.get("word")]
            
            return list(set(antonyms))  # Remove duplicates
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Datamuse API error for antonyms of '{word}': {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting antonyms for '{word}': {e}")
            return []
    
    async def get_word_info(self, word: str) -> Dict[str, Any]:
        """
        Get complete word information including definitions, synonyms, and antonyms
        
        Args:
            word: The word to look up
            
        Returns:
            Dictionary with complete word information
        """
        # Get definition first
        definition_result = await self.define(word)
        
        if not definition_result.get("success", False):
            return definition_result
        
        word_lower = word.lower().strip()
        
        # Get synonyms and antonyms
        synonyms = await self.get_synonyms(word_lower)
        antonyms = await self.get_antonyms(word_lower)
        
        # Build complete response
        result = {
            "success": True,
            "word": definition_result.get("word", word),
            "phonetic": definition_result.get("phonetic", ""),
            "audio_url": definition_result.get("audio_url", ""),
            "definitions": definition_result.get("definitions", []),
            "synonyms": synonyms,
            "antonyms": antonyms
        }
        
        return result
    
    async def search_words(self, prefix: str, limit: int = 10) -> List[str]:
        """
        Search for words starting with a given prefix using Datamuse API
        
        Args:
            prefix: The prefix to search for
            limit: Maximum number of results (default 10)
            
        Returns:
            List of words matching the prefix
        """
        try:
            url = f"{DATAMUSE_API_BASE}?sp={prefix.lower().strip()}*&max={limit}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            words = [item.get("word", "") for item in data if item.get("word")]
            
            return words[:limit]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Datamuse API error for prefix '{prefix}': {e}")
            return []
        except Exception as e:
            logger.error(f"Error searching words for '{prefix}': {e}")
            return []


# Global instance for easy import
dictionary_manager = DictionaryManager()
