"""
Chat&Talk GPT - Sarvam.ai TTS Integration
Provides Indian language text-to-speech with high-quality neural r
"""
import os
import logging
import base64
import asyncio
import json
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger("SarvamTTS")

# Try importing required libraries
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests library not available for Sarvam TTS")


class SarvamTTSProvider:
    """
    Sarvam.ai Text-to-Speech Provider
    Supports 10+ Indian languages with high-quality neural r
    """
    
    # API Configuration
    BASE_URL = "https://api.sarvam.ai"
    
    # Supported languages and their codes
    SUPPORTED_LANGUAGES = {
        "hi": "Hindi",
        "ta": "Tamil", 
        "te": "Telugu",
        "kn": "Kannada",
        "ml": "Malayalam",
        "bn": "Bengali",
        "mr": "Marathi",
        "gu": "Gujarati",
        "pa": "Punjabi",
        "or": "Odia",
        "en": "English",
        "ne": "Nepali"
    }
    
    # Voice IDs available in Sarvam
    VOICES = {
        # Hindi r
        "hi-male-1": {"id": "hi-male-1", "name": "Hindi Male 1", "language": "hi", "gender": "male"},
        "hi-female-1": {"id": "hi-female-1", "name": "Hindi Female 1", "language": "hi", "gender": "female"},
        # Tamil r
        "ta-male-1": {"id": "ta-male-1", "name": "Tamil Male 1", "language": "ta", "gender": "male"},
        "ta-female-1": {"id": "ta-female-1", "name": "Tamil Female 1", "language": "ta", "gender": "female"},
        # Telugu r
        "te-male-1": {"id": "te-male-1", "name": "Telugu Male 1", "language": "te", "gender": "male"},
        "te-female-1": {"id": "te-female-1", "name": "Telugu Female 1", "language": "te", "gender": "female"},
        # Kannada r
        "kn-male-1": {"id": "kn-male-1", "name": "Kannada Male 1", "language": "kn", "gender": "male"},
        "kn-female-1": {"id": "kn-female-1", "name": "Kannada Female 1", "language": "kn", "gender": "female"},
        # Malayalam r
        "ml-male-1": {"id": "ml-male-1", "name": "Malayalam Male 1", "language": "ml", "gender": "male"},
        "ml-female-1": {"id": "ml-female-1", "name": "Malayalam Female 1", "language": "ml", "gender": "female"},
        # Bengali r
        "bn-male-1": {"id": "bn-male-1", "name": "Bengali Male 1", "language": "bn", "gender": "male"},
        "bn-female-1": {"id": "bn-female-1", "name": "Bengali Female 1", "language": "bn", "gender": "female"},
        # Marathi r
        "mr-male-1": {"id": "mr-male-1", "name": "Marathi Male 1", "language": "mr", "gender": "male"},
        "mr-female-1": {"id": "mr-female-1", "name": "Marathi Female 1", "language": "mr", "gender": "female"},
        # Gujarati r
        "gu-male-1": {"id": "gu-male-1", "name": "Gujarati Male 1", "language": "gu", "gender": "male"},
        "gu-female-1": {"id": "gu-female-1", "name": "Gujarati Female 1", "language": "gu", "gender": "female"},
        # Punjabi r
        "pa-male-1": {"id": "pa-male-1", "name": "Punjabi Male 1", "language": "pa", "gender": "male"},
        "pa-female-1": {"id": "pa-female-1", "name": "Punjabi Female 1", "language": "pa", "gender": "female"},
        # Odia r
        "or-male-1": {"id": "or-male-1", "name": "Odia Male 1", "language": "or", "gender": "male"},
        "or-female-1": {"id": "or-female-1", "name": "Odia Female 1", "language": "or", "gender": "female"},
        # English (Indian accent)
        "en-male-1": {"id": "en-male-1", "name": "English Male (IN)", "language": "en", "gender": "male"},
        "en-female-1": {"id": "en-female-1", "name": "English Female (IN)", "language": "en", "gender": "female"},
        # Nepali
        "ne-male-1": {"id": "ne-male-1", "name": "Nepali Male 1", "language": "ne", "gender": "male"},
        "ne-female-1": {"id": "ne-female-1", "name": "Nepali Female 1", "language": "ne", "gender": "female"},
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Sarvam TTS provider"""
        self.api_key = api_key or os.getenv("SARVAM_API_KEY")
        self.is_available = bool(self.api_key and REQUESTS_AVAILABLE)
        
        if not self.is_available:
            if not self.api_key:
                logger.warning("Sarvam API key not provided")
            if not REQUESTS_AVAILABLE:
                logger.warning("requests library not available")
        else:
            logger.info("Sarvam TTS provider initialized successfully")
    
    def is_configured(self) -> bool:
        """Check if Sarvam is properly configured"""
        return self.is_available
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available Sarvam r"""
        return list(self.VOICES.values())
    
    def get_voices_by_language(self, language: str) -> List[Dict[str, Any]]:
        """Get r for a specific language"""
        return [v for v in self.VOICES.values() if v["language"] == language.lower()]
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported languages"""
        return [
            {"code": code, "name": name}
            for code, name in self.SUPPORTED_LANGUAGES.items()
        ]
    
    async def synthesize(
        self,
        text: str,
        voice_id: str = "hi-female-1",
        language: str = "hi",
        speed: float = 1.0,
        pitch: float = 1.0,
        output_format: str = "mp3"
    ) -> Optional[Dict[str, Any]]:
        """
        Synthesize speech from text using Sarvam API
        
        Args:
            text: Text to synthesize
            voice_id: Voice identifier
            language: Language code (hi, ta, te, etc.)
            speed: Speech speed (0.5 - 2.0)
            pitch: Speech pitch (0.5 - 2.0)
            output_format: Audio format (mp3, wav, etc.)
            
        Returns:
            Dict with audio_data (base64) or error
        """
        if not self.is_available:
            logger.error("Sarvam TTS not available - API key missing")
            return {"error": "Sarvam API key not configured"}
        
        try:
            # Prepare API request
            url = f"{self.BASE_URL}/text-to-speech"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": text,
                "voice_id": voice_id,
                "language": language,
                "speed": speed,
                "pitch": pitch,
                "output_format": output_format
            }
            
            # Make synchronous request in executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(url, json=payload, headers=headers, timeout=30)
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle base64 audio response
                audio_data = result.get("audio")
                if audio_data:
                    logger.info(f"Successfully synthesized text with Sarvam ({len(text)} chars)")
                    return {
                        "success": True,
                        "audio_data": audio_data,
                        "format": output_format,
                        "provider": "sarvam",
                        "voice_id": voice_id,
                        "language": language
                    }
                else:
                    logger.warning("No audio data in Sarvam response")
                    return {"error": "No audio data in response"}
            else:
                error_msg = f"Sarvam API error: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text[:100]}"
                logger.error(error_msg)
                return {"error": error_msg}
                
        except asyncio.TimeoutError:
            logger.error("Sarvam TTS request timed out")
            return {"error": "Request timed out"}
        except Exception as e:
            logger.error(f"Sarvam TTS error: {str(e)}")
            return {"error": str(e)}
    
    async def synthesize_batch(
        self,
        texts: List[str],
        voice_id: str = "hi-female-1",
        language: str = "hi"
    ) -> List[Optional[Dict[str, Any]]]:
        """Synthesize multiple texts"""
        tasks = [
            self.synthesize(text, voice_id, language)
            for text in texts
        ]
        return await asyncio.gather(*tasks)


class SarvamTranslationProvider:
    """
    Sarvam.ai Translation API Provider
    Translation between Indian languages
    """
    
    BASE_URL = "https://api.sarvam.ai"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Sarvam translation provider"""
        self.api_key = api_key or os.getenv("SARVAM_API_KEY")
        self.is_available = bool(self.api_key and REQUESTS_AVAILABLE)
        
        if self.is_available:
            logger.info("Sarvam Translation provider initialized")
    
    def is_configured(self) -> bool:
        """Check if translation is properly configured"""
        return self.is_available
    
    async def translate(
        self,
        text: str,
        source_language: str = "auto",
        target_language: str = "en"
    ) -> Optional[Dict[str, Any]]:
        """
        Translate text between languages
        
        Args:
            text: Text to translate
            source_language: Source language code (auto for detection)
            target_language: Target language code
            
        Returns:
            Dict with translated text or error
        """
        if not self.is_available:
            return {"error": "Sarvam API key not configured"}
        
        try:
            url = f"{self.BASE_URL}/translate"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": text,
                "source_language": source_language,
                "target_language": target_language
            }
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(url, json=payload, headers=headers, timeout=30)
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "translated_text": result.get("translated_text", ""),
                    "detected_language": result.get("detected_language", ""),
                    "provider": "sarvam"
                }
            else:
                return {"error": f"API error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Sarvam translation error: {str(e)}")
            return {"error": str(e)}


# Singleton instance
_sarvam_tts: Optional[SarvamTTSProvider] = None
_sarvam_translation: Optional[SarvamTranslationProvider] = None


def get_sarvam_tts() -> SarvamTTSProvider:
    """Get or create Sarvam TTS singleton"""
    global _sarvam_tts
    if _sarvam_tts is None:
        _sarvam_tts = SarvamTTSProvider()
    return _sarvam_tts


def get_sarvam_translation() -> SarvamTranslationProvider:
    """Get or create Sarvam translation singleton"""
    global _sarvam_translation
    if _sarvam_translation is None:
        _sarvam_translation = SarvamTranslationProvider()
    return _sarvam_translation


async def speak_with_sarvam(
    text: str,
    voice_id: str = "hi-female-1",
    language: str = "hi"
) -> Optional[str]:
    """
    Convenience function to synthesize speech with Sarvam
    Returns base64 audio or None on failure
    """
    provider = get_sarvam_tts()
    if not provider.is_configured():
        logger.warning("Sarvam TTS not configured")
        return None
    
    result = await provider.synthesize(text, voice_id, language)
    if result and result.get("success"):
        return result.get("audio_data")
    return None
