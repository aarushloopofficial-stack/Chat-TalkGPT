"""
Chat&Talk GPT - Voice Clone Routes
FastAPI routes for voice cloning functionality
"""
import logging
import base64
from typing import Optional, List
from fastapi import APIRouter, Query, Path, Body, HTTPException
from pydantic import BaseModel, Field
import json

from voice_clone import (
    voice_clone_manager,
    AudioValidator
)

logger = logging.getLogger("VoiceCloneRoutes")

# Create router
router = APIRouter(prefix="/api/voice-clone", tags=["voice-cloning"])


# Request models
class CreateVoiceCloneRequest(BaseModel):
    """Request model for creating a voice clone"""
    name: str = Field(..., description="Name for the voice clone", min_length=1)
    language: str = Field(default="en", description="Language code (en, hi, ne, etc.)")
    description: str = Field(default="", description="Optional description")
    method: str = Field(default="auto", description="Cloning method: auto, elevenlabs, coqui")


class SynthesizeRequest(BaseModel):
    """Request model for synthesizing speech with a clone"""
    profile_id: str = Field(..., description="Voice clone profile ID")
    text: str = Field(..., description="Text to synthesize", min_length=1)
    speed: float = Field(default=1.0, description="Speech speed (0.5-2.0)")
    pitch: float = Field(default=1.0, description="Pitch adjustment (0.5-2.0)")
    output_format: str = Field(default="mp3", description="Output format: mp3, wav")


class ValidateSampleRequest(BaseModel):
    """Request model for validating an audio sample"""
    audio_data: str = Field(..., description="Base64-encoded audio data")
    filename: str = Field(default="audio.mp3", description="Original filename")


# Routes
@router.get("/capabilities")
async def get_capabilities():
    """
    Get available voice cloning capabilities and requirements
    """
    return voice_clone_manager.get_clone_capabilities()


@router.get("/clones")
async def get_voice_clones():
    """
    Get all voice clones
    """
    return {
        "success": True,
        "clones": voice_clone_manager.get_voice_clones()
    }


@router.get("/clones/{profile_id}")
async def get_voice_clone(profile_id: str = Path(..., description="Voice clone profile ID")):
    """
    Get a specific voice clone
    """
    clone = voice_clone_manager.get_voice_clone(profile_id)
    if not clone:
        raise HTTPException(status_code=404, detail="Voice clone not found")
    return {
        "success": True,
        "clone": clone
    }


@router.post("/clones")
async def create_voice_clone(
    name: str = Query(..., description="Name for the voice clone"),
    language: str = Query(default="en", description="Language code"),
    description: str = Query(default="", description="Optional description"),
    method: str = Query(default="auto", description="Cloning method"),
    samples_json: str = Query(..., description="JSON array of base64-encoded audio samples")
):
    """
    Create a new voice clone from audio samples
    """
    try:
        # Parse samples from JSON
        samples_data = json.loads(samples_json)
        
        if not samples_data or not isinstance(samples_data, list):
            raise HTTPException(status_code=400, detail="Invalid samples format")
        
        # Decode base64 audio samples
        audio_samples = []
        for sample_b64 in samples_data:
            try:
                audio_bytes = base64.b64decode(sample_b64)
                audio_samples.append(audio_bytes)
            except Exception as e:
                logger.warning(f"Failed to decode sample: {e}")
                continue
        
        if not audio_samples:
            raise HTTPException(status_code=400, detail="No valid audio samples provided")
        
        result = voice_clone_manager.create_voice_clone(
            name=name,
            audio_samples=audio_samples,
            language=language,
            description=description,
            method=method
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to create voice clone"))
        
        return result
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for samples")
    except Exception as e:
        logger.error(f"Create voice clone error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/synthesize")
async def synthesize_with_clone(request: SynthesizeRequest):
    """
    Synthesize speech using a voice clone
    """
    result = voice_clone_manager.synthesize_with_clone(
        profile_id=request.profile_id,
        text=request.text,
        speed=request.speed,
        pitch=request.pitch,
        output_format=request.output_format
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Synthesis failed"))
    
    return result


@router.post("/validate-sample")
async def validate_sample(request: ValidateSampleRequest):
    """
    Validate an audio sample before uploading
    """
    try:
        audio_bytes = base64.b64decode(request.audio_data)
        validation = AudioValidator.validate_audio_data(audio_bytes, request.filename)
        
        return {
            "success": True,
            "validation": validation
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "validation": {
                "valid": False,
                "issues": ["Failed to decode audio data"]
            }
        }


@router.delete("/clones/{profile_id}")
async def delete_voice_clone(profile_id: str = Path(..., description="Voice clone profile ID")):
    """
    Delete a voice clone
    """
    result = voice_clone_manager.delete_voice_clone(profile_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Failed to delete voice clone"))
    
    return result


@router.put("/clones/{profile_id}")
async def update_voice_clone(
    profile_id: str = Path(..., description="Voice clone profile ID"),
    name: Optional[str] = Query(None, description="New name"),
    description: Optional[str] = Query(None, description="New description"),
    language: Optional[str] = Query(None, description="New language code")
):
    """
    Update voice clone metadata
    """
    result = voice_clone_manager.update_voice_clone(
        profile_id=profile_id,
        name=name,
        description=description,
        language=language
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Failed to update voice clone"))
    
    return result


@router.get("/clones/{profile_id}/parameters")
async def get_voice_parameters(profile_id: str = Path(..., description="Voice clone profile ID")):
    """
    Get voice parameters for a clone
    """
    result = voice_clone_manager.get_voice_parameters(profile_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Failed to get voice parameters"))
    
    return result


@router.post("/clones/{profile_id}/parameters")
async def set_voice_parameters(
    profile_id: str = Path(..., description="Voice clone profile ID"),
    speed: Optional[float] = Query(None, ge=0.5, le=2.0, description="Speech speed (0.5-2.0)"),
    pitch: Optional[float] = Query(None, ge=0.5, le=2.0, description="Voice pitch (0.5-2.0)"),
    volume: Optional[float] = Query(None, ge=0.0, le=1.0, description="Volume (0.0-1.0)"),
    style: Optional[str] = Query(None, description="Voice style")
):
    """
    Set custom voice parameters for a clone
    """
    result = voice_clone_manager.set_voice_parameters(
        profile_id=profile_id,
        speed=speed,
        pitch=pitch,
        volume=volume,
        style=style
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Failed to set voice parameters"))
    
    return result


@router.post("/clones/{profile_id}/preview")
async def preview_voice(
    profile_id: str = Path(..., description="Voice clone profile ID"),
    text: Optional[str] = Query(None, description="Custom text to speak"),
    sample_type: Optional[str] = Query("greeting", description="Sample type: greeting, announcement, question, farewell")
):
    """
    Generate preview audio for a voice clone
    """
    sample_texts = {
        "greeting": "Hello! I'm your personalized voice assistant.",
        "announcement": "This is a sample announcement using my cloned voice.",
        "question": "How can I help you today?",
        "farewell": "Thank you for using my services. Goodbye!"
    }
    
    preview_text = text if text else sample_texts.get(sample_type, sample_texts["greeting"])
    
    result = voice_clone_manager.preview_voice(
        profile_id=profile_id,
        text=preview_text
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to generate preview"))
    
    return result


@router.post("/clones/{profile_id}/samples")
async def add_samples(
    profile_id: str = Path(..., description="Voice clone profile ID"),
    samples_json: str = Query(..., description="JSON array of base64-encoded audio samples")
):
    """
    Add more audio samples to an existing voice clone
    """
    try:
        samples_data = json.loads(samples_json)
        
        if not samples_data or not isinstance(samples_data, list):
            raise HTTPException(status_code=400, detail="Invalid samples format")
        
        audio_samples = []
        for sample_b64 in samples_data:
            try:
                audio_bytes = base64.b64decode(sample_b64)
                audio_samples.append(audio_bytes)
            except Exception:
                continue
        
        if not audio_samples:
            raise HTTPException(status_code=400, detail="No valid audio samples provided")
        
        result = voice_clone_manager.add_samples(profile_id, audio_samples)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to add samples"))
        
        return result
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for samples")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clones/{profile_id}/duplicate")
async def duplicate_clone(
    profile_id: str = Path(..., description="Source voice clone profile ID"),
    new_name: str = Query(..., description="Name for the new clone")
):
    """
    Duplicate an existing voice clone
    """
    result = voice_clone_manager.duplicate_clone(profile_id, new_name)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to duplicate clone"))
    
    return result


# Export router
__all__ = ["router"]
