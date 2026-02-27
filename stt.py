"""
Chat&Talk GPT - Speech-to-Text Manager
Handles voice input recognition
"""
import logging
import asyncio
from typing import Optional

logger = logging.getLogger("STTManager")

# Try importing speech recognition libraries
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    logger.warning("SpeechRecognition not availabe")

# Whisper is optional - don't crash if it fails
WHISPER_AVAILABLE = False
try:
    import whisper
    WHISPER_AVAILABLE = True
except Exception as e:
    logger.warning(f"whisper not available: {e}")


class STTManager:
    """Manages speech-to-text recognition"""
    
    def __init__(self):
        self.recognizer = None
        self.microphone = None
        self.use_whisper = WHISPER_AVAILABLE
        self.use_speech_recognition = SPEECH_RECOGNITION_AVAILABLE
        
        # Initialize speech recognition
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                
                # Adjust for ambient noise
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                logger.info("Speech recognition initialized")
            except Exception as e:
                logger.error(f"Failed to init speech recognition: {e}")
                self.recognizer = None
                self.microphone = None
        
        # Load Whisper model if available
        self.whisper_model = None
        if WHISPER_AVAILABLE:
            try:
                self.whisper_model = whisper.load_model("base")
                logger.info("Whisper model loaded (base)")
            except Exception as e:
                logger.error(f"Failed to load Whisper: {e}")
                self.whisper_model = None
        
        logger.info("STT Manager initialized")
    
    async def recognize(self, audio_data: Optional[str] = None) -> str:
        """
        Recognize speech from audio
        Accepts base64 audio or uses microphone
        """
        logger.info("STT recognition request")
        
        # Try Whisper first (better quality)
        if self.whisper_model:
            try:
                result = await self._whisper_recognize(audio_data)
                if result:
                    return result
            except Exception as e:
                logger.error(f"Whisper recognition failed: {e}")
        
        # Try speech_recognition library
        if self.recognizer and self.microphone:
            try:
                result = await self._speech_recognition_mic()
                if result:
                    return result
            except Exception as e:
                logger.error(f"Speech recognition failed: {e}")
        
        # Return empty if all fail
        logger.warning("All STT methods failed")
        return ""
    
    async def _whisper_recognize(self, audio_data: Optional[str]) -> Optional[str]:
        """Recognize using Whisper model"""
        
        import tempfile
        import base64
        import numpy as np
        import torch
        
        if audio_data:
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_data)
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(audio_bytes)
                temp_file = f.name
            
            try:
                # Transcribe
                result = self.whisper_model.transcribe(temp_file)
                text = result["text"].strip()
                
                if text:
                    logger.info(f"Whisper recognized: {text[:50]}...")
                    return text
            finally:
                # Clean up
                import os
                os.remove(temp_file)
        else:
            # Record from microphone
            # This would need proper audio capture in production
            logger.info("Whisper mic recording not implemented")
        
        return None
    
    async def _speech_recognition_mic(self) -> Optional[str]:
        """Recognize using speech_recognition with microphone"""
        
        if not (self.recognizer and self.microphone):
            return None
        
        loop = asyncio.get_event_loop()
        
        # Listen in executor
        def listen():
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            return audio
        
        try:
            audio = await loop.run_in_executor(None, listen)
            
            # Recognize using Google (free, no API key needed)
            def recognize_google():
                return self.recognizer.recognize_google(audio)
            
            text = await loop.run_in_executor(None, recognize_google)
            
            if text:
                logger.info(f"Google STT recognized: {text}")
                return text
            
        except sr.WaitTimeoutError:
            logger.warning("No speech detected (timeout)")
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")
        
        return None
    
    def test_microphone(self) -> bool:
        """Test if microphone is available"""
        try:
            if self.microphone:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                logger.info("Microphone test successful")
                return True
        except Exception as e:
            logger.error(f"Microphone test failed: {e}")
        return False
    
    def get_available_languages(self) -> list:
        """Get list of supported languages"""
        return [
            "en-US (English - US)",
            "en-GB (English - UK)", 
            "hi-IN (Hindi - India)",
            "ne-NP (Nepali - Nepal)"
        ]
