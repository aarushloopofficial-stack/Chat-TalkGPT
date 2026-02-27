"""
Chat&Talk GPT - Voice Cloning Module
Create custom voice clones from audio samples
Supports TTS voice synthesis with custom voices

Voice Cloning Features:
- ElevenLabs API integration (premium, high quality)
- Coqui TTS open-source voice cloning
- Audio sample processing and validation
- Voice profile management
"""
import os
import json
import logging
import base64
import io
import hashlib
import uuid
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

logger = logging.getLogger("VoiceClone")

# Try to import required libraries
COQUI_AVAILABLE = False
PYTTSX3_AVAILABLE = False
ELEVENLABS_AVAILABLE = False
OPENVOICE_AVAILABLE = False

try:
    from TTS.api import TTS
    COQUI_AVAILABLE = True
    logger.info("Coqui TTS is available")
except ImportError:
    logger.warning("Coqui TTS not available")

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
    logger.info("pyttsx3 is available")
except ImportError:
    logger.warning("pyttsx3 not available")

try:
    from eleven import ElevenLabs
    ELEVENLABS_AVAILABLE = True
    logger.info("ElevenLabs is available")
except ImportError:
    logger.warning("ElevenLabs not available")

try:
    # OpenVoice is Microsoft's voice cloning technology
    import torch
    OPENVOICE_AVAILABLE = True
    logger.info("OpenVoice dependencies available")
except ImportError:
    logger.warning("OpenVoice not available")


# Audio processing constants
MIN_SAMPLE_DURATION = 1  # seconds
MAX_SAMPLE_DURATION = 300  # seconds (5 minutes)
MIN_SAMPLES_REQUIRED = 1  # Minimum audio samples needed for cloning
RECOMMENDED_SAMPLES = 3  # Recommended number of samples
SUPPORTED_AUDIO_FORMATS = ['mp3', 'wav', 'ogg', 'm4a', 'flac']


class AudioValidator:
    """Validates audio samples for voice cloning"""
    
    @staticmethod
    def validate_audio_data(audio_data: bytes, filename: str = "audio") -> Dict[str, Any]:
        """
        Validate audio data for voice cloning
        
        Args:
            audio_data: Raw audio bytes
            filename: Original filename for format detection
            
        Returns:
            Validation result with details
        """
        result = {
            "valid": False,
            "format": None,
            "size": len(audio_data),
            "duration_estimate": None,
            "issues": []
        }
        
        # Check minimum size
        if len(audio_data) < 1024:  # 1KB minimum
            result["issues"].append("Audio file too small (minimum 1KB)")
            return result
        
        # Check maximum size (50MB limit)
        if len(audio_data) > 50 * 1024 * 1024:
            result["issues"].append("Audio file too large (maximum 50MB)")
            return result
        
        # Detect format from filename or magic bytes
        format_result = AudioValidator._detect_format(audio_data, filename)
        result["format"] = format_result["format"]
        
        if not format_result["valid"]:
            result["issues"].append(format_result["issue"])
            return result
        
        # Estimate duration based on size (rough estimate)
        # Assuming ~128kbps average for MP3
        if result["format"] == "mp3":
            result["duration_estimate"] = len(audio_data) / (128 * 1024 / 8)
        elif result["format"] == "wav":
            # WAV is typically 16-bit 44.1kHz stereo = ~176KB/sec
            result["duration_estimate"] = len(audio_data) / 176400
        else:
            # Rough estimate for other formats
            result["duration_estimate"] = len(audio_data) / 16000
        
        # Check duration constraints
        if result["duration_estimate"] < MIN_SAMPLE_DURATION:
            result["issues"].append(f"Audio too short (minimum {MIN_SAMPLE_DURATION} seconds)")
        elif result["duration_estimate"] > MAX_SAMPLE_DURATION:
            result["issues"].append(f"Audio too long (maximum {MAX_SAMPLE_DURATION} seconds)")
        
        # Mark as valid if no critical issues
        if not result["issues"] or all(
            "too short" not in issue and "too long" not in issue 
            for issue in result["issues"]
        ):
            result["valid"] = True
        
        return result
    
    @staticmethod
    def _detect_format(audio_data: bytes, filename: str) -> Dict[str, Any]:
        """Detect audio format from magic bytes and filename"""
        # Check magic bytes
        if audio_data[:3] == b'ID3':
            return {"valid": True, "format": "mp3"}
        if audio_data[:2] == b'\xff\xfb':
            return {"valid": True, "format": "mp3"}
        if audio_data[:4] == b'RIFF' and audio_data[8:12] == b'WAVE':
            return {"valid": True, "format": "wav"}
        if audio_data[:4] == b'OggS':
            return {"valid": True, "format": "ogg"}
        if audio_data[:4] == b'fLaC':
            return {"valid": True, "format": "flac"}
        if audio_data[:4] == b'ftyp':
            return {"valid": True, "format": "m4a"}
        
        # Try filename extension
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        if ext in SUPPORTED_AUDIO_FORMATS:
            return {"valid": True, "format": ext}
        
        return {"valid": False, "format": None, "issue": "Unknown audio format"}
    
    @staticmethod
    def calculate_audio_hash(audio_data: bytes) -> str:
        """Calculate hash of audio data for deduplication"""
        return hashlib.sha256(audio_data).hexdigest()[:16]


class VoiceCloneManager:
    """
    Voice Cloning Manager for creating custom voices
    
    Features:
    - Create voice profile from audio samples
    - Multiple voice cloning methods (ElevenLabs, Coqui, OpenVoice)
    - Multiple voice profiles per user
    - Voice synthesis with cloned voices
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize Voice Clone Manager
        
        Args:
            storage_path: Path to store voice profiles and samples
        """
        # Set up storage directory
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path(__file__).parent / "memory" / "voice_clones"
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing profiles
        self.profiles_file = self.storage_path / "profiles.json"
        self.voice_profiles = self._load_profiles()
        
        # Initialize TTS models
        self.coqui_tts = None
        self.elevenlabs_client = None
        
        # Initialize Coqui TTS if available
        if COQUI_AVAILABLE:
            try:
                self.coqui_tts = TTS(model_path="tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
                logger.info("Coqui TTS model loaded for voice cloning")
            except Exception as e:
                logger.warning(f"Failed to load Coqui model: {e}")
        
        # Initialize ElevenLabs if available
        if ELEVENLABS_AVAILABLE:
            try:
                api_key = os.getenv("ELEVENLABS_API_KEY")
                if api_key and api_key != "your_elevenlabs_api_key_here":
                    self.elevenlabs_client = ElevenLabs(api_key=api_key)
                    logger.info("ElevenLabs client initialized")
                else:
                    logger.warning("ElevenLabs API key not configured")
            except Exception as e:
                logger.warning(f"Failed to initialize ElevenLabs: {e}")
        
        logger.info("Voice Clone Manager initialized")
    
    def _load_profiles(self) -> Dict[str, Any]:
        """Load voice profiles from storage"""
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load profiles: {e}")
        return {}
    
    def _save_profiles(self):
        """Save voice profiles to storage"""
        try:
            with open(self.profiles_file, 'w') as f:
                json.dump(self.voice_profiles, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save profiles: {e}")
    
    def create_voice_clone(
        self,
        name: str,
        audio_samples: List[bytes],
        language: str = "en",
        description: str = "",
        method: str = "auto"
    ) -> Dict[str, Any]:
        """
        Create a voice clone from audio samples
        
        Args:
            name: Name for the voice clone
            audio_samples: List of audio file bytes
            language: Language code (en, hi, ne, etc.)
            description: Optional description
            method: Cloning method ('elevenlabs', 'coqui', 'openvoice', 'auto')
            
        Returns:
            Clone creation status with profile details
        """
        try:
            # Validate audio samples
            if not audio_samples:
                return {
                    "success": False,
                    "error": "No audio samples provided"
                }
            
            if len(audio_samples) < MIN_SAMPLES_REQUIRED:
                return {
                    "success": False,
                    "error": f"Minimum {MIN_SAMPLES_REQUIRED} audio sample(s) required"
                }
            
            # Validate each sample
            valid_samples = []
            sample_hashes = set()
            
            for i, sample in enumerate(audio_samples):
                validation = AudioValidator.validate_audio_data(sample, f"sample_{i}.mp3")
                
                if not validation["valid"]:
                    logger.warning(f"Sample {i} validation failed: {validation['issues']}")
                    # Still include if it's just duration issues
                    if validation["duration_estimate"]:
                        valid_samples.append({
                            "data": sample,
                            "hash": AudioValidator.calculate_audio_hash(sample),
                            "duration": validation["duration_estimate"]
                        })
                    continue
                
                # Check for duplicates
                sample_hash = AudioValidator.calculate_audio_hash(sample)
                if sample_hash in sample_hashes:
                    logger.warning(f"Duplicate sample detected, skipping")
                    continue
                
                sample_hashes.add(sample_hash)
                valid_samples.append({
                    "data": sample,
                    "hash": sample_hash,
                    "duration": validation["duration_estimate"]
                })
            
            if not valid_samples:
                return {
                    "success": False,
                    "error": "No valid audio samples found"
                }
            
            # Determine best cloning method
            clone_method = self._select_clone_method(method)
            
            # Create profile ID
            profile_id = f"clone_{uuid.uuid4().hex[:12]}"
            
            # Create profile directory
            profile_dir = self.storage_path / profile_id
            profile_dir.mkdir(parents=True, exist_ok=True)
            
            # Save audio samples
            sample_files = []
            for i, sample in enumerate(valid_samples):
                sample_path = profile_dir / f"sample_{i}.mp3"
                with open(sample_path, 'wb') as f:
                    f.write(sample["data"])
                sample_files.append(str(sample_path))
            
            # Create voice profile
            profile = {
                "id": profile_id,
                "name": name,
                "description": description,
                "language": language,
                "method": clone_method,
                "samples_count": len(valid_samples),
                "total_duration": sum(s["duration"] for s in valid_samples),
                "created_at": datetime.now().isoformat(),
                "status": "ready",
                "elevenlabs_voice_id": None,
                "sample_files": sample_files,
                "usage_count": 0
            }
            
            # If using ElevenLabs, create voice there
            if clone_method == "elevenlabs" and self.elevenlabs_client:
                eleven_result = self._create_elevenlabs_voice(
                    profile_id, 
                    valid_samples,
                    name
                )
                if eleven_result.get("success"):
                    profile["elevenlabs_voice_id"] = eleven_result.get("voice_id")
                    profile["status"] = "ready"
                else:
                    profile["status"] = "error"
                    profile["error"] = eleven_result.get("error", "ElevenLabs creation failed")
            
            # Save profile
            self.voice_profiles[profile_id] = profile
            self._save_profiles()
            
            logger.info(f"Voice clone created: {profile_id} using {clone_method}")
            
            return {
                "success": True,
                "profile_id": profile_id,
                "name": name,
                "method": clone_method,
                "samples_count": len(valid_samples),
                "message": f"Voice clone '{name}' created successfully"
            }
            
        except Exception as e:
            logger.error(f"Create voice clone error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _select_clone_method(self, preferred: str) -> str:
        """Select the best available cloning method"""
        methods = {
            "elevenlabs": ELEVENLABS_AVAILABLE and self.elevenlabs_client,
            "coqui": COQUI_AVAILABLE and self.coqui_tts,
            "openvoice": OPENVOICE_AVAILABLE
        }
        
        if preferred != "auto" and methods.get(preferred):
            return preferred
        
        # Auto-select: prioritize by quality
        if methods.get("elevenlabs"):
            return "elevenlabs"
        elif methods.get("coqui"):
            return "coqui"
        elif methods.get("openvoice"):
            return "openvoice"
        
        return "standard"  # Fallback to standard TTS
    
    def _create_elevenlabs_voice(
        self, 
        profile_id: str, 
        samples: List[Dict[str, Any]], 
        name: str
    ) -> Dict[str, Any]:
        """Create a voice in ElevenLabs from samples"""
        try:
            # Save samples to temporary files
            temp_dir = tempfile.mkdtemp()
            sample_paths = []
            
            for i, sample in enumerate(samples):
                path = os.path.join(temp_dir, f"sample_{i}.mp3")
                with open(path, 'wb') as f:
                    f.write(sample["data"])
                sample_paths.append(path)
            
            # Create voice
            response = self.elevenlabs_client.voice.create(
                name=name,
                files=sample_paths,
                description=f"Voice clone for {name}"
            )
            
            # Cleanup
            shutil.rmtree(temp_dir)
            
            return {
                "success": True,
                "voice_id": response.voice_id
            }
            
        except Exception as e:
            logger.error(f"ElevenLabs voice creation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def synthesize_with_clone(
        self,
        profile_id: str,
        text: str,
        speed: float = 1.0,
        pitch: float = 1.0,
        output_format: str = "mp3"
    ) -> Dict[str, Any]:
        """
        Synthesize speech using a voice clone
        
        Args:
            profile_id: Voice clone profile ID
            text: Text to synthesize
            speed: Speech speed (0.5-2.0)
            pitch: Pitch adjustment (0.5-2.0)
            output_format: Output format (mp3, wav)
            
        Returns:
            Synthesized audio data
        """
        try:
            # Get profile
            profile = self.voice_profiles.get(profile_id)
            if not profile:
                return {
                    "success": False,
                    "error": "Voice clone not found"
                }
            
            if profile.get("status") != "ready":
                return {
                    "success": False,
                    "error": f"Voice clone not ready: {profile.get('status')}"
                }
            
            # Update usage count
            profile["usage_count"] = profile.get("usage_count", 0) + 1
            self._save_profiles()
            
            method = profile.get("method", "coqui")
            
            # Synthesize based on method
            if method == "elevenlabs" and profile.get("elevenlabs_voice_id"):
                return self._synthesize_elevenlabs(
                    profile["elevenlabs_voice_id"],
                    text,
                    speed,
                    output_format
                )
            elif method == "coqui":
                return self._synthesize_coqui_clone(
                    profile_id,
                    text,
                    profile.get("language", "en"),
                    speed,
                    pitch,
                    output_format
                )
            else:
                # Fallback to standard TTS
                return self._synthesize_standard(text, speed, pitch)
                
        except Exception as e:
            logger.error(f"Synthesize with clone error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _synthesize_elevenlabs(
        self,
        voice_id: str,
        text: str,
        speed: float,
        output_format: str
    ) -> Dict[str, Any]:
        """Synthesize using ElevenLabs cloned voice"""
        try:
            # Convert speed from 0.5-2.0 to ElevenLabs API format
            # API uses "stability" and "similarity" instead
            
            audio_generator = self.elevenlabs_client.generate(
                text=text,
                voice_id=voice_id,
                model="eleven_multilingual_v2"
            )
            
            audio_bytes = b"".join(audio_generator)
            audio_base64 = base64.b64encode(audio_bytes).decode()
            
            return {
                "success": True,
                "audio": audio_base64,
                "format": output_format,
                "engine": "elevenlabs"
            }
            
        except Exception as e:
            logger.error(f"ElevenLabs synthesis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _synthesize_coqui_clone(
        self,
        profile_id: str,
        text: str,
        language: str,
        speed: float,
        pitch: float,
        output_format: str
    ) -> Dict[str, Any]:
        """Synthesize using Coqui TTS with voice reference"""
        try:
            if not self.coqui_tts:
                return {
                    "success": False,
                    "error": "Coqui TTS not available"
                }
            
            profile = self.voice_profiles.get(profile_id)
            if not profile or not profile.get("sample_files"):
                return {
                    "success": False,
                    "error": "No voice samples found"
                }
            
            # Use the first sample as reference
            reference_audio = profile["sample_files"][0]
            
            # Create output buffer
            output = io.BytesIO()
            
            # Generate speech with voice cloning
            # Note: XTTS v2 supports reference audio
            self.coqui_tts.tts_to_file(
                text=text,
                file_path=output,
                language=language.split('-')[0] if '-' in language else language,
                reference_file=reference_audio,
                speed=speed
            )
            
            audio_data = output.getvalue()
            audio_base64 = base64.b64encode(audio_data).decode()
            
            return {
                "success": True,
                "audio": audio_base64,
                "format": output_format,
                "engine": "coqui"
            }
            
        except Exception as e:
            logger.error(f"Coqui synthesis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _synthesize_standard(
        self,
        text: str,
        speed: float,
        pitch: float
    ) -> Dict[str, Any]:
        """Fallback to standard TTS synthesis"""
        try:
            if PYTTSX3_AVAILABLE:
                engine = pyttsx3.init()
                engine.setProperty('rate', int(200 * speed))
                engine.setProperty('pitch', pitch)
                
                output = io.BytesIO()
                # pyttsx3 doesn't support direct buffer, use temp file
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                    temp_path = f.name
                
                engine.save_to_file(text, temp_path)
                engine.runAndWait()
                
                with open(temp_path, 'rb') as f:
                    audio_data = f.read()
                os.remove(temp_path)
                
                audio_base64 = base64.b64encode(audio_data).decode()
                
                return {
                    "success": True,
                    "audio": audio_base64,
                    "format": "mp3",
                    "engine": "pyttsx3"
                }
            else:
                return {
                    "success": False,
                    "error": "No TTS engine available"
                }
                
        except Exception as e:
            logger.error(f"Standard synthesis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_voice_clones(self) -> List[Dict[str, Any]]:
        """Get all voice clones"""
        clones = []
        for profile_id, profile in self.voice_profiles.items():
            clones.append({
                "id": profile_id,
                "name": profile.get("name"),
                "description": profile.get("description"),
                "language": profile.get("language"),
                "method": profile.get("method"),
                "samples_count": profile.get("samples_count"),
                "status": profile.get("status"),
                "created_at": profile.get("created_at"),
                "usage_count": profile.get("usage_count", 0)
            })
        return clones
    
    def get_voice_clone(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific voice clone"""
        profile = self.voice_profiles.get(profile_id)
        if profile:
            return {
                "id": profile_id,
                "name": profile.get("name"),
                "description": profile.get("description"),
                "language": profile.get("language"),
                "method": profile.get("method"),
                "samples_count": profile.get("samples_count"),
                "total_duration": profile.get("total_duration"),
                "status": profile.get("status"),
                "created_at": profile.get("created_at"),
                "usage_count": profile.get("usage_count", 0)
            }
        return None
    
    def delete_voice_clone(self, profile_id: str) -> Dict[str, Any]:
        """Delete a voice clone"""
        try:
            if profile_id not in self.voice_profiles:
                return {
                    "success": False,
                    "error": "Voice clone not found"
                }
            
            profile = self.voice_profiles[profile_id]
            
            # Delete ElevenLabs voice if exists
            if profile.get("elevenlabs_voice_id") and self.elevenlabs_client:
                try:
                    self.elevenlabs_client.voice.delete(profile["elevenlabs_voice_id"])
                except Exception as e:
                    logger.warning(f"Failed to delete ElevenLabs voice: {e}")
            
            # Delete profile directory
            profile_dir = self.storage_path / profile_id
            if profile_dir.exists():
                shutil.rmtree(profile_dir)
            
            # Remove from storage
            del self.voice_profiles[profile_id]
            self._save_profiles()
            
            return {
                "success": True,
                "message": f"Voice clone deleted"
            }
            
        except Exception as e:
            logger.error(f"Delete voice clone error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_voice_clone(
        self,
        profile_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update voice clone metadata
        
        Args:
            profile_id: Voice clone profile ID
            name: New name
            description: New description
            language: New language code
            
        Returns:
            Update status
        """
        try:
            if profile_id not in self.voice_profiles:
                return {
                    "success": False,
                    "error": "Voice clone not found"
                }
            
            profile = self.voice_profiles[profile_id]
            
            if name is not None:
                profile["name"] = name
            if description is not None:
                profile["description"] = description
            if language is not None:
                profile["language"] = language
            
            profile["updated_at"] = datetime.now().isoformat()
            
            self._save_profiles()
            
            return {
                "success": True,
                "message": "Voice clone updated",
                "profile": {
                    "id": profile_id,
                    "name": profile.get("name"),
                    "description": profile.get("description"),
                    "language": profile.get("language")
                }
            }
            
        except Exception as e:
            logger.error(f"Update voice clone error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def set_voice_parameters(
        self,
        profile_id: str,
        speed: Optional[float] = None,
        pitch: Optional[float] = None,
        volume: Optional[float] = None,
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Set custom voice parameters for a profile
        
        Args:
            profile_id: Voice clone profile ID
            speed: Speech rate (0.5-2.0, default 1.0)
            pitch: Voice pitch (0.5-2.0, default 1.0)
            volume: Volume level (0.0-1.0, default 1.0)
            style: Voice style (default, cheerful, sad, angry, etc.)
            
        Returns:
            Parameters update status
        """
        try:
            if profile_id not in self.voice_profiles:
                return {
                    "success": False,
                    "error": "Voice clone not found"
                }
            
            profile = self.voice_profiles[profile_id]
            
            # Initialize parameters if not exists
            if "parameters" not in profile:
                profile["parameters"] = {
                    "speed": 1.0,
                    "pitch": 1.0,
                    "volume": 1.0,
                    "style": "default"
                }
            
            params = profile["parameters"]
            
            if speed is not None:
                params["speed"] = max(0.5, min(2.0, speed))
            if pitch is not None:
                params["pitch"] = max(0.5, min(2.0, pitch))
            if volume is not None:
                params["volume"] = max(0.0, min(1.0, volume))
            if style is not None:
                params["style"] = style
            
            self._save_profiles()
            
            return {
                "success": True,
                "message": "Voice parameters updated",
                "parameters": params
            }
            
        except Exception as e:
            logger.error(f"Set voice parameters error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_voice_parameters(self, profile_id: str) -> Dict[str, Any]:
        """
        Get voice parameters for a profile
        
        Args:
            profile_id: Voice clone profile ID
            
        Returns:
            Voice parameters
        """
        try:
            if profile_id not in self.voice_profiles:
                return {
                    "success": False,
                    "error": "Voice clone not found"
                }
            
            profile = self.voice_profiles[profile_id]
            params = profile.get("parameters", {
                "speed": 1.0,
                "pitch": 1.0,
                "volume": 1.0,
                "style": "default"
            })
            
            return {
                "success": True,
                "profile_id": profile_id,
                "parameters": params
            }
            
        except Exception as e:
            logger.error(f"Get voice parameters error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def preview_voice(
        self,
        profile_id: str,
        text: Optional[str] = None,
        sample_texts: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate preview audio for a voice clone
        
        Args:
            profile_id: Voice clone profile ID
            text: Custom text to speak
            sample_texts: Dictionary of sample texts by category
            
        Returns:
            Preview audio data
        """
        try:
            if profile_id not in self.voice_profiles:
                return {
                    "success": False,
                    "error": "Voice clone not found"
                }
            
            profile = self.voice_profiles[profile_id]
            
            # Default sample texts
            if sample_texts is None:
                sample_texts = {
                    "greeting": "Hello! I'm your personalized voice assistant.",
                    "announcement": "This is a sample announcement using my cloned voice.",
                    "question": "How can I help you today?",
                    "farewell": "Thank you for using my services. Goodbye!"
                }
            
            # Use custom text or first sample
            preview_text = text or sample_texts.get("greeting", "Hello!")
            
            # Get voice parameters
            params = profile.get("parameters", {})
            
            # Synthesize preview
            result = self.synthesize_with_clone(
                profile_id=profile_id,
                text=preview_text,
                speed=params.get("speed", 1.0),
                pitch=params.get("pitch", 1.0)
            )
            
            if result.get("success"):
                result["preview_text"] = preview_text
                result["sample_texts"] = sample_texts
            
            return result
            
        except Exception as e:
            logger.error(f"Preview voice error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def add_samples(
        self,
        profile_id: str,
        audio_samples: List[bytes]
    ) -> Dict[str, Any]:
        """
        Add more audio samples to an existing voice clone
        
        Args:
            profile_id: Voice clone profile ID
            audio_samples: List of new audio samples
            
        Returns:
            Add samples status
        """
        try:
            if profile_id not in self.voice_profiles:
                return {
                    "success": False,
                    "error": "Voice clone not found"
                }
            
            profile = self.voice_profiles[profile_id]
            
            # Validate new samples
            valid_samples = []
            for i, sample in enumerate(audio_samples):
                validation = AudioValidator.validate_audio_data(sample, f"additional_sample_{i}.mp3")
                if validation.get("valid"):
                    valid_samples.append({
                        "data": sample,
                        "hash": AudioValidator.calculate_audio_hash(sample),
                        "duration": validation.get("duration_estimate", 0)
                    })
            
            if not valid_samples:
                return {
                    "success": False,
                    "error": "No valid audio samples provided"
                }
            
            # Get existing samples directory
            profile_dir = self.storage_path / profile_id
            
            # Find existing sample count
            existing_count = len(profile.get("sample_files", []))
            
            # Save new samples
            sample_files = list(profile.get("sample_files", []))
            for i, sample in enumerate(valid_samples):
                sample_path = profile_dir / f"sample_{existing_count + i}.mp3"
                with open(sample_path, 'wb') as f:
                    f.write(sample["data"])
                sample_files.append(str(sample_path))
            
            # Update profile
            profile["sample_files"] = sample_files
            profile["samples_count"] = len(sample_files)
            profile["total_duration"] = profile.get("total_duration", 0) + sum(
                s["duration"] for s in valid_samples
            )
            profile["updated_at"] = datetime.now().isoformat()
            
            self._save_profiles()
            
            return {
                "success": True,
                "message": f"Added {len(valid_samples)} new samples",
                "total_samples": len(sample_files)
            }
            
        except Exception as e:
            logger.error(f"Add samples error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def duplicate_clone(
        self,
        profile_id: str,
        new_name: str
    ) -> Dict[str, Any]:
        """
        Duplicate an existing voice clone with a new name
        
        Args:
            profile_id: Source voice clone profile ID
            new_name: Name for the new clone
            
        Returns:
            Duplication status with new profile
        """
        try:
            if profile_id not in self.voice_profiles:
                return {
                    "success": False,
                    "error": "Voice clone not found"
                }
            
            source = self.voice_profiles[profile_id]
            
            # Create new profile ID
            new_profile_id = f"clone_{uuid.uuid4().hex[:12]}"
            
            # Copy samples
            source_dir = self.storage_path / profile_id
            new_dir = self.storage_path / new_profile_id
            new_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy sample files
            new_sample_files = []
            for i, sample_file in enumerate(source.get("sample_files", [])):
                if os.path.exists(sample_file):
                    new_sample_path = new_dir / f"sample_{i}.mp3"
                    shutil.copy2(sample_file, new_sample_path)
                    new_sample_files.append(str(new_sample_path))
            
            # Create new profile
            new_profile = {
                "id": new_profile_id,
                "name": new_name,
                "description": f"Clone of {source.get('name')}",
                "language": source.get("language"),
                "method": source.get("method"),
                "samples_count": len(new_sample_files),
                "total_duration": source.get("total_duration"),
                "created_at": datetime.now().isoformat(),
                "status": source.get("status"),
                "elevenlabs_voice_id": None,  # Don't copy ElevenLabs voice ID
                "sample_files": new_sample_files,
                "usage_count": 0,
                "parameters": source.get("parameters", {}).copy(),
                "parent_clone": profile_id
            }
            
            # Save new profile
            self.voice_profiles[new_profile_id] = new_profile
            self._save_profiles()
            
            return {
                "success": True,
                "message": f"Voice clone duplicated as '{new_name}'",
                "profile_id": new_profile_id,
                "name": new_name
            }
            
        except Exception as e:
            logger.error(f"Duplicate clone error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_clone_capabilities(self) -> Dict[str, Any]:
        """Get available voice cloning capabilities"""
        return {
            "elevenlabs": {
                "available": ELEVENLABS_AVAILABLE and self.elevenlabs_client is not None,
                "quality": "high",
                "description": "Premium voice cloning with ElevenLabs API"
            },
            "coqui": {
                "available": COQUI_AVAILABLE and self.coqui_tts is not None,
                "quality": "medium",
                "description": "Open-source voice cloning with Coqui TTS"
            },
            "openvoice": {
                "available": OPENVOICE_AVAILABLE,
                "quality": "medium",
                "description": "Microsoft's OpenVoice technology"
            },
            "standard": {
                "available": PYTTSX3_AVAILABLE,
                "quality": "low",
                "description": "Standard TTS without voice cloning"
            },
            "requirements": {
                "min_samples": MIN_SAMPLES_REQUIRED,
                "recommended_samples": RECOMMENDED_SAMPLES,
                "min_duration": MIN_SAMPLE_DURATION,
                "max_duration": MAX_SAMPLE_DURATION,
                "supported_formats": SUPPORTED_AUDIO_FORMATS
            }
        }


# Singleton instance
voice_clone_manager = VoiceCloneManager()


# Standalone functions
def create_voice_clone(*args, **kwargs) -> Dict[str, Any]:
    """Standalone function to create voice clone"""
    return voice_clone_manager.create_voice_clone(*args, **kwargs)


def synthesize_with_clone(*args, **kwargs) -> Dict[str, Any]:
    """Standalone function to synthesize with cloned voice"""
    return voice_clone_manager.synthesize_with_clone(*args, **kwargs)


def get_voice_clones() -> List[Dict[str, Any]]:
    """Standalone function to get all voice clones"""
    return voice_clone_manager.get_voice_clones()


def get_voice_clone(profile_id: str) -> Optional[Dict[str, Any]]:
    """Standalone function to get a specific voice clone"""
    return voice_clone_manager.get_voice_clone(profile_id)


def delete_voice_clone(profile_id: str) -> Dict[str, Any]:
    """Standalone function to delete a voice clone"""
    return voice_clone_manager.delete_voice_clone(profile_id)


def get_clone_capabilities() -> Dict[str, Any]:
    """Standalone function to get cloning capabilities"""
    return voice_clone_manager.get_clone_capabilities()
