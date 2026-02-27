"""
Chat&Talk GPT - Text-to-Speech Manager
Handles voice synthesis with multiple voice options from various TTS providers
"""
import os
import base64
import logging
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger("TTSManager")

# Try importing TTS libraries
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    logger.warning("edge-tts not available")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logger.warning("gTTS not available")

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("pyttsx3 not available")

try:
    from eleven import ElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    logger.warning("elevenlabs not available")

try:
    from sarvam_tts import SarvamTTSProvider
    SARVAM_AVAILABLE = True
except ImportError:
    SARVAM_AVAILABLE = False
    logger.warning("sarvam_tts not available")


@dataclass
class VoiceProfile:
    """Represents a TTS voice profile"""
    voice_id: str
    name: str
    provider: str  # edge, gtts, pyttsx3, elevenlabs
    language: str  # en, hi, ne, etc.
    accent: str  # US, UK, IN, NP, etc.
    gender: str  # male, female, neutral
    quality_rating: int  # 1-5
    sample_url: str = ""
    tags: List[str] = field(default_factory=list)
    description: str = ""
    engine_voice_id: str = ""  # Provider-specific voice ID
    is_premium: bool = False
    is_default: bool = False


class VoiceCatalog:
    """Manages the voice catalog with all available voices"""
    
    # Cache for voice list
    _cache: Dict[str, Any] = {}
    _cache_time: Optional[datetime] = None
    CACHE_TTL = timedelta(hours=1)
    
    @classmethod
    def get_all_voices(cls) -> List[VoiceProfile]:
        """Get all available voices with caching"""
        now = datetime.now()
        if cls._cache and cls._cache_time:
            if now - cls._cache_time < cls.CACHE_TTL:
                return cls._cache.get("voices", [])
        
        voices = cls._build_voice_catalog()
        cls._cache = {"voices": voices}
        cls._cache_time = now
        return voices
    
    @classmethod
    def _build_voice_catalog(cls) -> List[VoiceProfile]:
        """Build the comprehensive voice catalog"""
        voices = []
        
        # === EDGE TTS VOICES ===
        # English (US) - Male
        voices.extend([
            VoiceProfile(
                voice_id="edge_en_us_guy",
                name="Guy",
                provider="edge",
                language="en",
                accent="US",
                gender="male",
                quality_rating=5,
                tags=["natural", "professional", "confident"],
                description="Confident and professional American male voice",
                engine_voice_id="en-US-GuyNeural"
            ),
            VoiceProfile(
                voice_id="edge_en_us_eric",
                name="Eric",
                provider="edge",
                language="en",
                accent="US",
                gender="male",
                quality_rating=5,
                tags=["natural", "deep", "clear"],
                description="Deep and clear American male voice",
                engine_voice_id="en-US-EricNeural"
            ),
            VoiceProfile(
                voice_id="edge_en_us_brian",
                name="Brian",
                provider="edge",
                language="en",
                accent="US",
                gender="male",
                quality_rating=4,
                tags=["natural", "casual", "friendly"],
                description="Casual and friendly American male voice",
                engine_voice_id="en-US-BrianNeural"
            ),
            # English (US) - Female
            VoiceProfile(
                voice_id="edge_en_us_jenny",
                name="Jenny",
                provider="edge",
                language="en",
                accent="US",
                gender="female",
                quality_rating=5,
                tags=["natural", "friendly", "professional"],
                description="Friendly and professional American female voice",
                engine_voice_id="en-US-JennyNeural"
            ),
            VoiceProfile(
                voice_id="edge_en_us_aria",
                name="Aria",
                provider="edge",
                language="en",
                accent="US",
                gender="female",
                quality_rating=5,
                tags=["natural", "emotional", "expressive"],
                description="Expressive and emotional American female voice",
                engine_voice_id="en-US-AriaNeural"
            ),
            VoiceProfile(
                voice_id="edge_en_us_sara",
                name="Sara",
                provider="edge",
                language="en",
                accent="US",
                gender="female",
                quality_rating=4,
                tags=["natural", "calm", "soft"],
                description="Calm and soft American female voice",
                engine_voice_id="en-US-SaraNeural"
            ),
            # English (UK)
            VoiceProfile(
                voice_id="edge_en_gb_ryan",
                name="Ryan",
                provider="edge",
                language="en",
                accent="GB",
                gender="male",
                quality_rating=5,
                tags=["natural", "british", "professional"],
                description="Professional British male voice",
                engine_voice_id="en-GB-RyanNeural"
            ),
            VoiceProfile(
                voice_id="edge_en_gb_sonia",
                name="Sonia",
                provider="edge",
                language="en",
                accent="GB",
                gender="female",
                quality_rating=5,
                tags=["natural", "british", "elegant"],
                description="Elegant British female voice",
                engine_voice_id="en-GB-SoniaNeural"
            ),
            # Hindi - Male
            VoiceProfile(
                voice_id="edge_hi_madhur",
                name="Madhur",
                provider="edge",
                language="hi",
                accent="IN",
                gender="male",
                quality_rating=5,
                tags=["natural", "professional", "confident"],
                description="Professional Hindi male voice",
                engine_voice_id="hi-IN-MadhurNeural"
            ),
            VoiceProfile(
                voice_id="edge_hi_amol",
                name="Amol",
                provider="edge",
                language="hi",
                accent="IN",
                gender="male",
                quality_rating=4,
                tags=["natural", "casual", "friendly"],
                description="Friendly Hindi male voice",
                engine_voice_id="hi-IN-AmolNeural"
            ),
            # Hindi - Female
            VoiceProfile(
                voice_id="edge_hi_swara",
                name="Swara",
                provider="edge",
                language="hi",
                accent="IN",
                gender="female",
                quality_rating=5,
                tags=["natural", "professional", "elegant"],
                description="Elegant Hindi female voice",
                engine_voice_id="hi-IN-SwaraNeural"
            ),
            VoiceProfile(
                voice_id="edge_hi_arya",
                name="Arya",
                provider="edge",
                language="hi",
                accent="IN",
                gender="female",
                quality_rating=4,
                tags=["natural", "young", "friendly"],
                description="Young and friendly Hindi female voice",
                engine_voice_id="hi-IN-AryaNeural"
            ),
            # Nepali
            VoiceProfile(
                voice_id="edge_ne_sagar",
                name="Sagar",
                provider="edge",
                language="ne",
                accent="NP",
                gender="male",
                quality_rating=5,
                tags=["natural", "professional", "confident"],
                description="Professional Nepali male voice",
                engine_voice_id="ne-NP-SagarNeural"
            ),
            VoiceProfile(
                voice_id="edge_ne_sapana",
                name="Sapana",
                provider="edge",
                language="ne",
                accent="NP",
                gender="female",
                quality_rating=4,
                tags=["natural", "friendly", "soft"],
                description="Friendly Nepali female voice",
                engine_voice_id="ne-NP-SapanaNeural"
            ),
        ])
        
        # === G TTS VOICES ===
        voices.extend([
            VoiceProfile(
                voice_id="gtts_en",
                name="Google English",
                provider="gtts",
                language="en",
                accent="US",
                gender="neutral",
                quality_rating=3,
                tags=["fast", "basic"],
                description="Basic Google English TTS voice",
                engine_voice_id="en"
            ),
            VoiceProfile(
                voice_id="gtts_hi",
                name="Google Hindi",
                provider="gtts",
                language="hi",
                accent="IN",
                gender="neutral",
                quality_rating=3,
                tags=["fast", "basic"],
                description="Basic Google Hindi TTS voice",
                engine_voice_id="hi"
            ),
            VoiceProfile(
                voice_id="gtts_ne",
                name="Google Nepali",
                provider="gtts",
                language="ne",
                accent="NP",
                gender="neutral",
                quality_rating=2,
                tags=["fast", "basic", "limited"],
                description="Basic Google Nepali TTS voice (limited)",
                engine_voice_id="ne"
            ),
        ])
        
        # === PYTTSX3 VOICES (System voices) ===
        # These are populated at runtime based on available system voices
        # Added basic structure for offline mode
        voices.extend([
            VoiceProfile(
                voice_id="pyttsx3_male",
                name="System Male",
                provider="pyttsx3",
                language="en",
                accent="US",
                gender="male",
                quality_rating=2,
                tags=["offline", "system"],
                description="System default male voice (offline)",
                engine_voice_id="male"
            ),
            VoiceProfile(
                voice_id="pyttsx3_female",
                name="System Female",
                provider="pyttsx3",
                language="en",
                accent="US",
                gender="female",
                quality_rating=2,
                tags=["offline", "system"],
                description="System default female voice (offline)",
                engine_voice_id="female"
            ),
        ])
        
        # === ELEVENLABS VOICES (Premium) ===
        if ELEVENLABS_AVAILABLE:
            voices.extend([
                VoiceProfile(
                    voice_id="eleven_rachel",
                    name="Rachel",
                    provider="elevenlabs",
                    language="en",
                    accent="US",
                    gender="female",
                    quality_rating=5,
                    tags=["premium", "natural", "calm", "professional"],
                    description="Premium calm and professional female voice",
                    engine_voice_id="21m00Tcm4TlvDq8ikWAM",
                    is_premium=True
                ),
                VoiceProfile(
                    voice_id="eleven_adam",
                    name="Adam",
                    provider="elevenlabs",
                    language="en",
                    accent="US",
                    gender="male",
                    quality_rating=5,
                    tags=["premium", "natural", "confident", "deep"],
                    description="Premium confident male voice",
                    engine_voice_id="pNInz6obpgDQGcFmaJgB",
                    is_premium=True
                ),
                VoiceProfile(
                    voice_id="eleven_sam",
                    name="Sam",
                    provider="elevenlabs",
                    language="en",
                    accent="US",
                gender="male",
                quality_rating=4,
                tags=["premium", "young", "friendly"],
                description="Premium young and friendly male voice",
                engine_voice_id="yoZ06aMxZJJ28mfd3POQ",
                is_premium=True
            ),
        ])
        
        # === SARVAM AI VOICES (Indian Languages) ===
        # High-quality neural voices for Indian languages
        voices.extend([
            # Hindi
            VoiceProfile(
                voice_id="sarvam_hi_male_1",
                name="Hindi Male (Sarvam)",
                provider="sarvam",
                language="hi",
                accent="IN",
                gender="male",
                quality_rating=5,
                tags=["indian", "natural", "professional", "hindi"],
                description="High-quality Hindi male voice",
                engine_voice_id="hi-male-1"
            ),
            VoiceProfile(
                voice_id="sarvam_hi_female_1",
                name="Hindi Female (Sarvam)",
                provider="sarvam",
                language="hi",
                accent="IN",
                gender="female",
                quality_rating=5,
                tags=["indian", "natural", "professional", "hindi"],
                description="High-quality Hindi female voice",
                engine_voice_id="hi-female-1"
            ),
            # Tamil
            VoiceProfile(
                voice_id="sarvam_ta_male_1",
                name="Tamil Male (Sarvam)",
                provider="sarvam",
                language="ta",
                accent="IN",
                gender="male",
                quality_rating=5,
                tags=["indian", "natural", "tamil"],
                description="High-quality Tamil male voice",
                engine_voice_id="ta-male-1"
            ),
            VoiceProfile(
                voice_id="sarvam_ta_female_1",
                name="Tamil Female (Sarvam)",
                provider="sarvam",
                language="ta",
                accent="IN",
                gender="female",
                quality_rating=5,
                tags=["indian", "natural", "tamil"],
                description="High-quality Tamil female voice",
                engine_voice_id="ta-female-1"
            ),
            # Telugu
            VoiceProfile(
                voice_id="sarvam_te_male_1",
                name="Telugu Male (Sarvam)",
                provider="sarvam",
                language="te",
                accent="IN",
                gender="male",
                quality_rating=5,
                tags=["indian", "natural", "telugu"],
                description="High-quality Telugu male voice",
                engine_voice_id="te-male-1"
            ),
            VoiceProfile(
                voice_id="sarvam_te_female_1",
                name="Telugu Female (Sarvam)",
                provider="sarvam",
                language="te",
                accent="IN",
                gender="female",
                quality_rating=5,
                tags=["indian", "natural", "telugu"],
                description="High-quality Telugu female voice",
                engine_voice_id="te-female-1"
            ),
            # Kannada
            VoiceProfile(
                voice_id="sarvam_kn_male_1",
                name="Kannada Male (Sarvam)",
                provider="sarvam",
                language="kn",
                accent="IN",
                gender="male",
                quality_rating=5,
                tags=["indian", "natural", "kannada"],
                description="High-quality Kannada male voice",
                engine_voice_id="kn-male-1"
            ),
            VoiceProfile(
                voice_id="sarvam_kn_female_1",
                name="Kannada Female (Sarvam)",
                provider="sarvam",
                language="kn",
                accent="IN",
                gender="female",
                quality_rating=5,
                tags=["indian", "natural", "kannada"],
                description="High-quality Kannada female voice",
                engine_voice_id="kn-female-1"
            ),
            # Malayalam
            VoiceProfile(
                voice_id="sarvam_ml_male_1",
                name="Malayalam Male (Sarvam)",
                provider="sarvam",
                language="ml",
                accent="IN",
                gender="male",
                quality_rating=5,
                tags=["indian", "natural", "malayalam"],
                description="High-quality Malayalam male voice",
                engine_voice_id="ml-male-1"
            ),
            VoiceProfile(
                voice_id="sarvam_ml_female_1",
                name="Malayalam Female (Sarvam)",
                provider="sarvam",
                language="ml",
                accent="IN",
                gender="female",
                quality_rating=5,
                tags=["indian", "natural", "malayalam"],
                description="High-quality Malayalam female voice",
                engine_voice_id="ml-female-1"
            ),
            # Bengali
            VoiceProfile(
                voice_id="sarvam_bn_male_1",
                name="Bengali Male (Sarvam)",
                provider="sarvam",
                language="bn",
                accent="IN",
                gender="male",
                quality_rating=5,
                tags=["indian", "natural", "bengali"],
                description="High-quality Bengali male voice",
                engine_voice_id="bn-male-1"
            ),
            VoiceProfile(
                voice_id="sarvam_bn_female_1",
                name="Bengali Female (Sarvam)",
                provider="sarvam",
                language="bn",
                accent="IN",
                gender="female",
                quality_rating=5,
                tags=["indian", "natural", "bengali"],
                description="High-quality Bengali female voice",
                engine_voice_id="bn-female-1"
            ),
            # Marathi
            VoiceProfile(
                voice_id="sarvam_mr_male_1",
                name="Marathi Male (Sarvam)",
                provider="sarvam",
                language="mr",
                accent="IN",
                gender="male",
                quality_rating=5,
                tags=["indian", "natural", "marathi"],
                description="High-quality Marathi male voice",
                engine_voice_id="mr-male-1"
            ),
            VoiceProfile(
                voice_id="sarvam_mr_female_1",
                name="Marathi Female (Sarvam)",
                provider="sarvam",
                language="mr",
                accent="IN",
                gender="female",
                quality_rating=5,
                tags=["indian", "natural", "marathi"],
                description="High-quality Marathi female voice",
                engine_voice_id="mr-female-1"
            ),
            # Gujarati
            VoiceProfile(
                voice_id="sarvam_gu_male_1",
                name="Gujarati Male (Sarvam)",
                provider="sarvam",
                language="gu",
                accent="IN",
                gender="male",
                quality_rating=5,
                tags=["indian", "natural", "gujarati"],
                description="High-quality Gujarati male voice",
                engine_voice_id="gu-male-1"
            ),
            VoiceProfile(
                voice_id="sarvam_gu_female_1",
                name="Gujarati Female (Sarvam)",
                provider="sarvam",
                language="gu",
                accent="IN",
                gender="female",
                quality_rating=5,
                tags=["indian", "natural", "gujarati"],
                description="High-quality Gujarati female voice",
                engine_voice_id="gu-female-1"
            ),
            # Punjabi
            VoiceProfile(
                voice_id="sarvam_pa_male_1",
                name="Punjabi Male (Sarvam)",
                provider="sarvam",
                language="pa",
                accent="IN",
                gender="male",
                quality_rating=5,
                tags=["indian", "natural", "punjabi"],
                description="High-quality Punjabi male voice",
                engine_voice_id="pa-male-1"
            ),
            VoiceProfile(
                voice_id="sarvam_pa_female_1",
                name="Punjabi Female (Sarvam)",
                provider="sarvam",
                language="pa",
                accent="IN",
                gender="female",
                quality_rating=5,
                tags=["indian", "natural", "punjabi"],
                description="High-quality Punjabi female voice",
                engine_voice_id="pa-female-1"
            ),
            # Odia
            VoiceProfile(
                voice_id="sarvam_or_male_1",
                name="Odia Male (Sarvam)",
                provider="sarvam",
                language="or",
                accent="IN",
                gender="male",
                quality_rating=5,
                tags=["indian", "natural", "odia"],
                description="High-quality Odia male voice",
                engine_voice_id="or-male-1"
            ),
            VoiceProfile(
                voice_id="sarvam_or_female_1",
                name="Odia Female (Sarvam)",
                provider="sarvam",
                language="or",
                accent="IN",
                gender="female",
                quality_rating=5,
                tags=["indian", "natural", "odia"],
                description="High-quality Odia female voice",
                engine_voice_id="or-female-1"
            ),
            # English (Indian accent)
            VoiceProfile(
                voice_id="sarvam_en_male_1",
                name="English Male (IN) (Sarvam)",
                provider="sarvam",
                language="en",
                accent="IN",
                gender="male",
                quality_rating=5,
                tags=["indian", "natural", "english"],
                description="High-quality English male voice (Indian accent)",
                engine_voice_id="en-male-1"
            ),
            VoiceProfile(
                voice_id="sarvam_en_female_1",
                name="English Female (IN) (Sarvam)",
                provider="sarvam",
                language="en",
                accent="IN",
                gender="female",
                quality_rating=5,
                tags=["indian", "natural", "english"],
                description="High-quality English female voice (Indian accent)",
                engine_voice_id="en-female-1"
            ),
            # Nepali
            VoiceProfile(
                voice_id="sarvam_ne_male_1",
                name="Nepali Male (Sarvam)",
                provider="sarvam",
                language="ne",
                accent="NP",
                gender="male",
                quality_rating=5,
                tags=["indian", "natural", "nepali"],
                description="High-quality Nepali male voice",
                engine_voice_id="ne-male-1"
            ),
            VoiceProfile(
                voice_id="sarvam_ne_female_1",
                name="Nepali Female (Sarvam)",
                provider="sarvam",
                language="ne",
                accent="NP",
                gender="female",
                quality_rating=5,
                tags=["indian", "natural", "nepali"],
                description="High-quality Nepali female voice",
                engine_voice_id="ne-female-1"
            ),
        ])
        
        return voices
    
    @classmethod
    def get_voice_by_id(cls, voice_id: str) -> Optional[VoiceProfile]:
        """Get a specific voice by ID"""
        voices = cls.get_all_voices()
        for voice in voices:
            if voice.voice_id == voice_id:
                return voice
        return None
    
    @classmethod
    def get_voices_by_language(cls, language: str) -> List[VoiceProfile]:
        """Get all voices for a specific language"""
        voices = cls.get_all_voices()
        return [v for v in voices if v.language == language.lower()]
    
    @classmethod
    def get_voices_by_provider(cls, provider: str) -> List[VoiceProfile]:
        """Get all voices for a specific provider"""
        voices = cls.get_all_voices()
        return [v for v in voices if v.provider == provider.lower()]
    
    @classmethod
    def get_voices_by_gender(cls, gender: str) -> List[VoiceProfile]:
        """Get all voices for a specific gender"""
        voices = cls.get_all_voices()
        return [v for v in voices if v.gender == gender.lower()]
    
    @classmethod
    def get_voices_by_tags(cls, tags: List[str]) -> List[VoiceProfile]:
        """Get voices matching any of the given tags"""
        voices = cls.get_all_voices()
        return [v for v in voices if any(tag in v.tags for tag in tags)]
    
    @classmethod
    def get_languages(cls) -> List[Dict[str, str]]:
        """Get list of available languages"""
        voices = cls.get_all_voices()
        languages = {}
        for voice in voices:
            lang_key = voice.language
            if lang_key not in languages:
                lang_names = {
                    "en": "English",
                    "hi": "Hindi", 
                    "ne": "Nepali"
                }
                languages[lang_key] = {
                    "code": lang_key,
                    "name": lang_names.get(lang_key, lang_key.upper())
                }
        return list(languages.values())
    
    @classmethod
    def get_providers(cls) -> List[Dict[str, Any]]:
        """Get list of available providers"""
        voices = cls.get_all_voices()
        providers = {}
        for voice in voices:
            if voice.provider not in providers:
                provider_info = {
                    "name": voice.provider,
                    "display_name": voice.provider.upper(),
                    "quality": "High" if voice.provider in ["edge", "elevenlabs"] else "Medium" if voice.provider == "gtts" else "Low"
                }
                if voice.provider == "edge":
                    provider_info["display_name"] = "Microsoft Edge TTS"
                    provider_info["description"] = "High-quality neural voices, free"
                elif voice.provider == "elevenlabs":
                    provider_info["display_name"] = "ElevenLabs"
                    provider_info["description"] = "Premium AI voices"
                elif voice.provider == "gtts":
                    provider_info["display_name"] = "Google TTS"
                    provider_info["description"] = "Basic free voices"
                elif voice.provider == "pyttsx3":
                    provider_info["display_name"] = "pyttsx3"
                    provider_info["description"] = "Offline system voices"
                elif voice.provider == "sarvam":
                    provider_info["display_name"] = "Sarvam.ai"
                    provider_info["description"] = "High-quality Indian language voices"
                providers[voice.provider] = provider_info
        return list(providers.values())
    
    @classmethod
    def get_recommended_voices(cls, use_case: str) -> List[VoiceProfile]:
        """Get recommended voices for a specific use case"""
        use_case_map = {
            "casual": ["natural", "friendly", "casual"],
            "professional": ["professional", "confident", "clear"],
            "news": ["formal", "authoritative", "clear"],
            "storytelling": ["emotional", "expressive", "natural"],
            "learning": ["clear", "slow", "professional"],
            "presentation": ["professional", "confident", "clear"]
        }
        
        tags = use_case_map.get(use_case.lower(), ["natural"])
        return cls.get_voices_by_tags(tags)
    
    @classmethod
    def clear_cache(cls):
        """Clear the voice cache"""
        cls._cache = {}
        cls._cache_time = None


class VoiceSettings:
    """Custom voice settings (speed, pitch)"""
    
    DEFAULT_SPEED = 1.0  # 0.5 to 2.0
    DEFAULT_PITCH = 1.0  # 0.5 to 2.0
    
    def __init__(self, speed: float = DEFAULT_SPEED, pitch: float = DEFAULT_PITCH):
        self.speed = max(0.5, min(2.0, speed))
        self.pitch = max(0.5, min(2.0, pitch))
    
    def to_dict(self) -> Dict[str, float]:
        return {"speed": self.speed, "pitch": self.pitch}


class TTSManager:
    """Manages text-to-speech synthesis with multiple voice options"""
    
    # Custom voice names (legacy support)
    VOICE_NAMES = {
        "aakansha": {
            "name": "Aakansha", 
            "description": "Sweet, Polite & Confident Female Voice (Sarvam)",
            "gender": "female"
        },
        "abinash": {
            "name": "Abinash", 
            "description": "Confident & Professional Male Voice (Sarvam)",
            "gender": "male"
        }
    }
    
    # Voice mappings for different TTS engines
    VOICE_MAPPINGS = {
        "abinash": {
            "en": "sarvam_en_male_1",
            "hi": "sarvam_hi_male_1",
            "ne": "sarvam_ne_male_1",
        },
        "aankansha": {
            "en": "sarvam_en_female_1",
            "hi": "sarvam_hi_female_1",
            "ne": "sarvam_ne_female_1",
        },
        "aakansha": {
            "en": "sarvam_en_female_1",
            "hi": "sarvam_hi_female_1",
            "ne": "sarvam_ne_female_1",
        }
    }
    
    # Language code mappings
    LANGUAGE_CODES = {
        "english": "en",
        "hindi": "hi",
        "nepali": "ne"
    }
    
    def __init__(self):
        self.use_edge = EDGE_TTS_AVAILABLE
        self.use_gtts = GTTS_AVAILABLE
        self.use_pyttsx3 = PYTTSX3_AVAILABLE
        self.use_elevenlabs = ELEVENLABS_AVAILABLE
        self.use_sarvam = SARVAM_AVAILABLE
        
        # Initialize voice catalog
        self.voice_catalog = VoiceCatalog()
        
        # Initialize ElevenLabs client
        self.elevenlabs_client = None
        if ELEVENLABS_AVAILABLE:
            try:
                api_key = os.getenv("ELEVENLABS_API_KEY")
                if api_key and api_key != "your_elevenlabs_api_key_here":
                    self.elevenlabs_client = ElevenLabs(api_key=api_key)
                    logger.info("ElevenLabs client initialized successfully")
                else:
                    logger.warning("ElevenLabs API key not configured")
            except Exception as e:
                logger.error(f"Failed to initialize ElevenLabs: {e}")
        
        # Initialize Sarvam TTS client
        self.sarvam_client = None
        if SARVAM_AVAILABLE:
            try:
                api_key = os.getenv("SARVAM_API_KEY")
                if api_key and api_key != "your_sarvam_api_key_here":
                    self.sarvam_client = SarvamTTSProvider(api_key=api_key)
                    if self.sarvam_client.is_configured():
                        logger.info("Sarvam TTS client initialized successfully")
                    else:
                        self.sarvam_client = None
                        logger.warning("Sarvam API key not configured")
                else:
                    logger.warning("Sarvam API key not configured")
            except Exception as e:
                logger.error(f"Failed to initialize Sarvam: {e}")
        
        # Initialize pyttsx3 engine if available (offline, local voices)
        self.pyttsx3_engine = None
        self.pyttsx3_voices = []
        if PYTTSX3_AVAILABLE:
            try:
                self.pyttsx3_engine = pyttsx3.init()
                self.pyttsx3_engine.setProperty('rate', 175)
                self.pyttsx3_engine.setProperty('volume', 1.0)
                
                # Get available voices
                self.pyttsx3_voices = self.pyttsx3_engine.getProperty('voices')
                logger.info(f"pyttsx3 found {len(self.pyttsx3_voices)} voices")
            except Exception as e:
                logger.error(f"Failed to init pyttsx3: {e}")
                self.pyttsx3_engine = None
        
        # Default voice settings
        self.voice_settings = VoiceSettings()
        
        logger.info("TTS Manager initialized with voice catalog")
    
    async def synthesize(
        self, 
        text: str, 
        voice: str = "abinash",
        language: str = "en",
        speed: float = None,
        pitch: float = None
    ) -> str:
        """
        Synthesize text to speech
        Returns base64-encoded audio data
        
        Parameters:
        - text: Text to convert to speech
        - voice: Voice ID or legacy voice name
        - language: Language code (en, hi, ne)
        - speed: Speech speed (0.5-2.0)
        - pitch: Speech pitch (0.5-2.0)
        
        Legacy voice names still supported:
        - abinash: Confident & Professional Male
        - aakansha: Sweet, Polite & Confident Female (ElevenLabs)
        """
        logger.info(f"TTS request: voice={voice}, lang={language}, text_len={len(text)}")
        
        # Apply custom settings if provided
        if speed is not None or pitch is not None:
            settings = VoiceSettings(speed or 1.0, pitch or 1.0)
        else:
            settings = self.voice_settings
        
        # Normalize voice name to lowercase
        voice = voice.lower()
        
        # Map old voice names to new voice IDs
        voice_map = {
            "male": "sarvam_en_male_1",
            "female": "sarvam_en_female_1",
            "abinash": "sarvam_en_male_1",
            "abinash_male": "sarvam_en_male_1",
            "aankansha": "sarvam_en_female_1",
            "aakansha": "sarvam_en_female_1",
            "aakansha_female": "sarvam_en_female_1",
            "guy": "sarvam_en_male_1",
            "jenny": "sarvam_en_female_1",
            # Hindi
            "abinash_hi": "sarvam_hi_male_1",
            "aakansha_hi": "sarvam_hi_female_1",
            # Nepali
            "abinash_ne": "sarvam_ne_male_1",
            # Sarvam voices (Indian languages)
            "sarvam_hi_male": "sarvam_hi_male_1",
            "sarvam_hi_female": "sarvam_hi_female_1",
            "sarvam_ta_male": "sarvam_ta_male_1",
            "sarvam_ta_female": "sarvam_ta_female_1",
            "sarvam_te_male": "sarvam_te_male_1",
            "sarvam_te_female": "sarvam_te_female_1",
            "sarvam_kn_male": "sarvam_kn_male_1",
            "sarvam_kn_female": "sarvam_kn_female_1",
            "sarvam_ml_male": "sarvam_ml_male_1",
            "sarvam_ml_female": "sarvam_ml_female_1",
            "sarvam_bn_male": "sarvam_bn_male_1",
            "sarvam_bn_female": "sarvam_bn_female_1",
            "sarvam_mr_male": "sarvam_mr_male_1",
            "sarvam_mr_female": "sarvam_mr_female_1",
            "sarvam_gu_male": "sarvam_gu_male_1",
            "sarvam_gu_female": "sarvam_gu_female_1",
            "sarvam_pa_male": "sarvam_pa_male_1",
            "sarvam_pa_female": "sarvam_pa_female_1",
            "sarvam_or_male": "sarvam_or_male_1",
            "sarvam_or_female": "sarvam_or_female_1",
            "sarvam_en_male": "sarvam_en_male_1",
            "sarvam_en_female": "sarvam_en_female_1",
            "sarvam_ne_male": "sarvam_ne_male_1",
            "sarvam_ne_female": "sarvam_ne_female_1",
        }
        voice_id = voice_map.get(voice, voice)
        
        # Normalize language code
        lang_code = self.LANGUAGE_CODES.get(language, language)
        
        # Try different TTS methods in order of preference
        
        # 1. Try Sarvam (Indian languages with high quality)
        if voice_id.startswith("sarvam_") and self.use_sarvam and self.sarvam_client:
            try:
                audio_base64 = await self._sarvam_tts_synthesize(text, voice_id, lang_code, settings)
                if audio_base64:
                    return audio_base64
            except Exception as e:
                logger.error(f"Sarvam TTS failed: {e}")
        
        # 2. Try ElevenLabs (best quality, for premium voices)
        if "eleven" in voice_id and self.use_elevenlabs and self.elevenlabs_client:
            try:
                audio_base64 = await self._elevenlabs_synthesize(text, voice_id, settings)
                if audio_base64:
                    return audio_base64
            except Exception as e:
                logger.error(f"ElevenLabs TTS failed: {e}")
        
        # 2. Try Edge TTS (best quality, free)
        if self.use_edge:
            try:
                audio_base64 = await self._edge_tts_synthesize(text, voice_id, lang_code, settings)
                if audio_base64:
                    return audio_base64
            except Exception as e:
                logger.error(f"Edge TTS failed: {e}")
        
        # 3. Try gTTS (Google TTS)
        if self.use_gtts:
            try:
                audio_base64 = self._gtts_synthesize(text, lang_code, settings)
                if audio_base64:
                    return audio_base64
            except Exception as e:
                logger.error(f"gTTS failed: {e}")
        
        # 4. Try pyttsx3 (offline)
        if self.pyttsx3_engine:
            try:
                audio_base64 = await self._pyttsx3_synthesize(text, voice_id, settings)
                if audio_base64:
                    return audio_base64
            except Exception as e:
                logger.error(f"pyttsx3 failed: {e}")
        
        # Return placeholder if all fail
        logger.warning("All TTS methods failed, returning placeholder")
        return ""
    
    async def _elevenlabs_synthesize(
        self, 
        text: str, 
        voice_id: str,
        settings: VoiceSettings
    ) -> Optional[str]:
        """Synthesize using ElevenLabs AI"""
        
        # Get voice profile
        voice_profile = self.voice_catalog.get_voice_by_id(voice_id)
        if not voice_profile:
            return None
        
        engine_voice_id = voice_profile.engine_voice_id
        
        try:
            # Adjust stability and similarity based on settings
            stability = 0.5
            similarity_boost = 0.75
            
            audio_generator = self.elevenlabs_client.generate(
                text=text,
                voice_id=engine_voice_id,
                model="eleven_monolingual_v1",
                stability=stability,
                similarity_boost=similarity_boost
            )
            
            audio_bytes = b"".join(audio_generator)
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            
            logger.info("ElevenLabs synthesis successful")
            return audio_base64
            
        except Exception as e:
            logger.error(f"ElevenLabs synthesis error: {e}")
            return None
    
    async def _sarvam_tts_synthesize(
        self,
        text: str,
        voice_id: str,
        lang_code: str,
        settings: VoiceSettings
    ) -> Optional[str]:
        """Synthesize using Sarvam.ai TTS for Indian languages"""
        
        if not self.sarvam_client or not self.sarvam_client.is_configured():
            return None
        
        # Extract language and gender from voice_id
        # e.g., sarvam_hi_male_1 -> language: hi, gender: male
        parts = voice_id.replace("sarvam_", "").split("_")
        if len(parts) >= 2:
            language = parts[0]  # hi, ta, te, kn, etc.
            # Map to Sarvam voice format
            sarvam_voice_id = f"{language}-{parts[1]}-1"  # e.g., hi-male-1
        else:
            # Default to Hindi
            language = lang_code if lang_code in ["hi", "ta", "te", "kn", "ml", "bn", "mr", "gu", "pa", "or", "en", "ne"] else "hi"
            sarvam_voice_id = "hi-female-1"
        
        try:
            result = await self.sarvam_client.synthesize(
                text=text,
                voice_id=sarvam_voice_id,
                language=language,
                speed=settings.speed,
                pitch=settings.pitch,
                output_format="mp3"
            )
            
            if result and result.get("success"):
                logger.info(f"Sarvam synthesis successful: {language}")
                return result.get("audio_data")
            elif result:
                logger.error(f"Sarvam synthesis failed: {result.get('error')}")
            
            return None
            
        except Exception as e:
            logger.error(f"Sarvam synthesis error: {e}")
            return None
    
    async def _edge_tts_synthesize(
        self, 
        text: str, 
        voice_id: str,
        lang_code: str,
        settings: VoiceSettings
    ) -> Optional[str]:
        """Synthesize using Microsoft Edge TTS with custom settings"""
        
        # Get voice profile
        voice_profile = self.voice_catalog.get_voice_by_id(voice_id)
        
        # Determine voice name
        if voice_profile and voice_profile.provider == "edge":
            voice_name = voice_profile.engine_voice_id
        else:
            # Fallback to legacy mappings
            voice_name = self.VOICE_MAPPINGS.get(
                voice_id,
                self.VOICE_MAPPINGS.get("abinash", {}).get(lang_code, "sarvam_en_male_1")
            )
        
        # Create communicate object
        communicate = edge_tts.Communicate(text, voice_name)
        
        # Apply rate and pitch adjustments
        # Edge TTS uses rate like "+10%" or "-10%" and pitch like "+10Hz" or "-10Hz"
        rate_adjustment = int((settings.speed - 1.0) * 100)
        pitch_adjustment = int((settings.pitch - 1.0) * 10)
        
        rate_str = f"{rate_adjustment:+d}%"
        pitch_str = f"{pitch_adjustment:+d}Hz"
        
        # Save to temporary file
        temp_file = f"temp_audio_{int(datetime.now().timestamp())}.mp3"
        
        try:
            await communicate.save(temp_file)
            
            with open(temp_file, "rb") as f:
                audio_data = base64.b64encode(f.read()).decode("utf-8")
            
            # Clean up
            os.remove(temp_file)
            
            logger.info("Edge TTS synthesis successful")
            return audio_data
            
        except Exception as e:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            logger.error(f"Edge TTS synthesis error: {e}")
            return None
    
    def _gtts_synthesize(
        self, 
        text: str, 
        lang_code: str,
        settings: VoiceSettings
    ) -> Optional[str]:
        """Synthesize using Google TTS"""
        
        # Map language codes for gTTS
        gtts_lang = "en" if lang_code == "en" else ("hi" if lang_code == "hi" else "ne")
        
        slow = settings.speed < 0.8
        
        tts = gTTS(text=text, lang=gtts_lang, slow=slow)
        
        temp_file = f"temp_audio_{int(datetime.now().timestamp())}.mp3"
        tts.save(temp_file)
        
        try:
            with open(temp_file, "rb") as f:
                audio_data = base64.b64encode(f.read()).decode("utf-8")
            
            os.remove(temp_file)
            
            logger.info("gTTS synthesis successful")
            return audio_data
            
        except Exception as e:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            logger.error(f"gTTS synthesis error: {e}")
            return None
    
    async def _pyttsx3_synthesize(
        self, 
        text: str, 
        voice_id: str,
        settings: VoiceSettings
    ) -> Optional[str]:
        """Synthesize using pyttsx3 (offline)"""
        
        # Select voice based on voice_id
        selected_voice = None
        
        if voice_id == "pyttsx3_female" or "female" in voice_id.lower():
            for voice in self.pyttsx3_voices:
                if "female" in voice.name.lower() or "zira" in voice.name.lower():
                    selected_voice = voice
                    break
        elif voice_id == "pyttsx3_male" or "male" in voice_id.lower():
            for voice in self.pyttsx3_voices:
                if "male" in voice.name.lower() or "david" in voice.name.lower():
                    selected_voice = voice
                    break
        
        if selected_voice:
            self.pyttsx3_engine.setProperty('voice', selected_voice.id)
        
        # Set rate based on speed
        base_rate = 175
        rate = int(base_rate * settings.speed)
        self.pyttsx3_engine.setProperty('rate', rate)
        
        # Note: pyttsx3 saving is complex, we'll use the say method
        # For actual file saving, we'd need to use the save_to_file method
        temp_file = f"temp_audio_{int(datetime.now().timestamp())}.wav"
        
        try:
            # Use save_to_file for file output
            self.pyttsx3_engine.save_to_file(text, temp_file)
            self.pyttsx3_engine.runAndWait()
            
            if os.path.exists(temp_file):
                with open(temp_file, "rb") as f:
                    audio_data = base64.b64encode(f.read()).decode("utf-8")
                os.remove(temp_file)
                logger.info("pyttsx3 synthesis successful")
                return audio_data
            
        except Exception as e:
            logger.error(f"pyttsx3 synthesis error: {e}")
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        return ""
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get all available voices as dictionary"""
        voices = self.voice_catalog.get_all_voices()
        return [
            {
                "voice_id": v.voice_id,
                "name": v.name,
                "provider": v.provider,
                "language": v.language,
                "accent": v.accent,
                "gender": v.gender,
                "quality_rating": v.quality_rating,
                "tags": v.tags,
                "description": v.description,
                "is_premium": v.is_premium
            }
            for v in voices
        ]
    
    def get_voice_details(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific voice"""
        voice = self.voice_catalog.get_voice_by_id(voice_id)
        if not voice:
            return None
        
        return {
            "voice_id": voice.voice_id,
            "name": voice.name,
            "provider": voice.provider,
            "language": voice.language,
            "accent": voice.accent,
            "gender": voice.gender,
            "quality_rating": voice.quality_rating,
            "sample_url": voice.sample_url,
            "tags": voice.tags,
            "description": voice.description,
            "is_premium": voice.is_premium,
            "is_default": voice.is_default
        }
    
    def get_voices_by_language(self, language: str) -> List[Dict[str, Any]]:
        """Get voices for a specific language"""
        voices = self.voice_catalog.get_voices_by_language(language)
        return [
            {
                "voice_id": v.voice_id,
                "name": v.name,
                "provider": v.provider,
                "language": v.language,
                "gender": v.gender,
                "quality_rating": v.quality_rating,
                "tags": v.tags
            }
            for v in voices
        ]
    
    def get_voices_by_provider(self, provider: str) -> List[Dict[str, Any]]:
        """Get voices for a specific provider"""
        voices = self.voice_catalog.get_voices_by_provider(provider)
        return [
            {
                "voice_id": v.voice_id,
                "name": v.name,
                "language": v.language,
                "accent": v.accent,
                "gender": v.gender,
                "quality_rating": v.quality_rating,
                "tags": v.tags
            }
            for v in voices
        ]
    
    def get_languages(self) -> List[Dict[str, str]]:
        """Get available languages"""
        return self.voice_catalog.get_languages()
    
    def get_providers(self) -> List[Dict[str, Any]]:
        """Get available providers"""
        return self.voice_catalog.get_providers()
    
    def get_recommended_voices(self, use_case: str) -> List[Dict[str, Any]]:
        """Get recommended voices for a use case"""
        voices = self.voice_catalog.get_recommended_voices(use_case)
        return [
            {
                "voice_id": v.voice_id,
                "name": v.name,
                "provider": v.provider,
                "language": v.language,
                "gender": v.gender,
                "quality_rating": v.quality_rating,
                "tags": v.tags,
                "description": v.description
            }
            for v in voices
        ]
    
    def set_voice_properties(self, rate: int = 175, volume: float = 1.0):
        """Set voice properties for pyttsx3 (legacy)"""
        if self.pyttsx3_engine:
            self.pyttsx3_engine.setProperty('rate', rate)
            self.pyttsx3_engine.setProperty('volume', volume)
    
    def set_default_voice(self, voice_id: str) -> bool:
        """Set the default voice"""
        voice = self.voice_catalog.get_voice_by_id(voice_id)
        if voice:
            # Update the voice's default status
            voice.is_default = True
            # Clear cache to reflect changes
            VoiceCatalog.clear_cache()
            return True
        return False
    
    def get_default_voice(self) -> Optional[Dict[str, Any]]:
        """Get the default voice"""
        voices = self.voice_catalog.get_all_voices()
        for voice in voices:
            if voice.is_default:
                return {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "provider": voice.provider
                }
        
        # Return a sensible default
        default = voices[0] if voices else None
        if default:
            return {
                "voice_id": default.voice_id,
                "name": default.name,
                "provider": default.provider
            }
        return None
    
    def set_voice_settings(self, speed: float = None, pitch: float = None):
        """Set custom voice settings"""
        if speed is not None:
            self.voice_settings.speed = max(0.5, min(2.0, speed))
        if pitch is not None:
            self.voice_settings.pitch = max(0.5, min(2.0, pitch))
    
    def get_voice_settings(self) -> Dict[str, float]:
        """Get current voice settings"""
        return self.voice_settings.to_dict()


# Initialize global TTS manager
tts_manager = TTSManager()
