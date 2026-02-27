"""
Chat&Talk GPT - Wake Word Detector
Handles "Hey GPT", "Hey Jarvis", or custom wake word detection
Supports both text-based and can be extended for audio wake word detection
"""
import logging
import re
from typing import List, Optional, Callable
import threading
import time

logger = logging.getLogger("WakeWord")


class WakeWordDetector:
    """
    Wake word detection system with support for:
    - Multiple wake words (hey gpt, hello gpt, hi gpt, hey jarvis, etc.)
    - Custom wake words
    - Text-based detection
    - Audio-based detection (can be extended with libraries like snowboy/porcupine)
    - Continuous listening mode
    - Callback system for when wake word is detected
    """
    
    def __init__(self, custom_wake_words: List[str] = None):
        # Default wake words
        self.default_wake_words = [
            "hey gpt", "hello gpt", "hi gpt", "hey jarvis", 
            "hey assistant", "okay gpt", "ok gpt", "gpt",
            "hey bot", "hello assistant", "hi assistant"
        ]
        
        # Combine default with custom wake words
        self.wake_words = self.default_wake_words.copy()
        if custom_wake_words:
            self.wake_words.extend([w.lower().strip() for w in custom_wake_words])
        
        # Remove duplicates while preserving order
        seen = set()
        self.wake_words = [x for x in self.wake_words if not (x in seen or seen.add(x))]
        
        self.is_active = False
        self.is_continuous = False
        self._callback: Optional[Callable] = None
        self._stop_event = threading.Event()
        self._listen_thread: Optional[threading.Thread] = None
        
        logger.info(f"WakeWord detector initialized with {len(self.wake_words)} wake words: {self.wake_words}")
    
    def add_wake_word(self, wake_word: str) -> bool:
        """Add a custom wake word"""
        wake_word = wake_word.lower().strip()
        if wake_word and wake_word not in self.wake_words:
            self.wake_words.append(wake_word)
            logger.info(f"Added custom wake word: {wake_word}")
            return True
        return False
    
    def remove_wake_word(self, wake_word: str) -> bool:
        """Remove a wake word"""
        wake_word = wake_word.lower().strip()
        if wake_word in self.wake_words and wake_word not in self.default_wake_words:
            self.wake_words.remove(wake_word)
            logger.info(f"Removed wake word: {wake_word}")
            return True
        return False
    
    def check_for_wake_word(self, text: str) -> bool:
        """Check if the transcribed text contains a wake word"""
        if not text:
            return False
            
        text_lower = text.lower().strip()
        
        for wake_word in self.wake_words:
            # Check for exact match or as a word boundary
            pattern = r'\b' + re.escape(wake_word) + r'\b'
            if re.search(pattern, text_lower):
                logger.info(f"Wake word detected: '{wake_word}' in text: '{text[:50]}...'")
                return True
            
            # Also check if text starts with wake word (for natural speech)
            if text_lower.startswith(wake_word):
                logger.info(f"Wake word detected (start): '{wake_word}' in text: '{text[:50]}...'")
                return True
        
        return False
    
    def extract_command_after_wake_word(self, text: str) -> Optional[str]:
        """Extract the command after the wake word"""
        if not text:
            return None
            
        text_lower = text.lower().strip()
        
        for wake_word in self.wake_words:
            if text_lower.startswith(wake_word):
                command = text[len(wake_word):].strip()
                # Remove common filler words
                command = re.sub(r'^(please|can you|could you|would you|then)?\s*', '', command)
                if command:
                    logger.info(f"Extracted command after wake word: '{command}'")
                    return command
        
        return None
    
    def set_callback(self, callback: Callable[[str], None]):
        """Set callback function to be called when wake word is detected"""
        self._callback = callback
    
    def start_continuous_listening(self, audio_source=None):
        """Start continuous listening for wake words (placeholder for audio-based detection)"""
        if self.is_continuous:
            logger.warning("Already in continuous listening mode")
            return
            
        self.is_continuous = True
        self._stop_event.clear()
        
        def listen_loop():
            logger.info("Started continuous wake word listening")
            while not self._stop_event.is_set():
                # This is a placeholder - in production, you'd use actual audio input
                # For example, using libraries like:
                # - snowboy (https://snowboy.picovoice.ai/)
                # - porcupine (https://picovoice.ai/porcupine/)
                # - pocketsphinx
                time.sleep(0.1)  # Simulate listening
            
            logger.info("Stopped continuous wake word listening")
        
        self._listen_thread = threading.Thread(target=listen_loop, daemon=True)
        self._listen_thread.start()
        logger.info("Continuous listening started")
    
    def stop_continuous_listening(self):
        """Stop continuous listening"""
        if not self.is_continuous:
            return
            
        self._stop_event.set()
        if self._listen_thread:
            self._listen_thread.join(timeout=2)
        
        self.is_continuous = False
        logger.info("Continuous listening stopped")
    
    def get_wake_words(self) -> List[str]:
        """Get list of all wake words"""
        return self.wake_words.copy()
    
    def reset_to_defaults(self):
        """Reset to default wake words only"""
        self.wake_words = self.default_wake_words.copy()
        logger.info("Reset to default wake words")


# Global instance
wake_detector = WakeWordDetector()


# Factory function for creating custom wake word detectors
def create_wake_word_detector(custom_wake_words: List[str] = None) -> WakeWordDetector:
    """Create a new wake word detector with custom wake words"""
    return WakeWordDetector(custom_wake_words)
