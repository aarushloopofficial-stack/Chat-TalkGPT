"""
Voice Sample Generation Script for Chat&Talk GPT
=================================================

This script generates audio files from the voice sample content
using the ElevenLabs API.

Usage:
    python generate_voice_samples.py

Requirements:
    - ELEVENLABS_API_KEY in .env file
    - ElevenLabs SDK installed: pip install elevenlabs
"""

import os
import asyncio
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import voice sample content
from voice_sample_content import VOICE_SAMPLES

# Check if ElevenLabs is available
try:
    from eleven import ElevenLabs
    print("✓ ElevenLabs SDK is installed")
except ImportError:
    print("✗ ElevenLabs SDK not installed. Run: pip install elevenlabs")
    exit(1)

# Check for API key
api_key = os.getenv("ELEVENLABS_API_KEY")
if not api_key or api_key == "your_elevenlabs_api_key_here":
    print("✗ ElevenLabs API key not configured in .env")
    print("  Please add: ELEVENLABS_API_KEY=your_api_key_here")
    exit(1)

print("✓ ElevenLabs API key found")

# Initialize client
client = ElevenLabs(api_key=api_key)

# Voice IDs
VOICE_IDS = {
    "aabinash": "pNInz6obpgDQGcFmaJgB",  # Adam - male voice (confident, professional)
    "aankansha": "21m00Tcm4TlvDq8ikWAM"  # Rachel - female voice (warm, professional)
}

# Model to use
VOICE_MODEL = "eleven_multilingual_v2"  # Supports multiple languages


async def generate_audio_file(text, voice_id, filename, model=VOICE_MODEL):
    """Generate audio for a single text and save to file"""
    try:
        print(f"  Generating: {filename}...")
        
        audio_generator = client.generate(
            text=text,
            voice_id=voice_id,
            model=model
        )
        
        # Convert generator to bytes
        audio_bytes = b"".join(audio_generator)
        
        # Save to file
        filepath = f"backend/voice_samples/{filename}"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, "wb") as f:
            f.write(audio_bytes)
        
        print(f"  ✓ Saved: {filepath}")
        return True
        
    except Exception as e:
        print(f"  ✗ Error generating {filename}: {e}")
        return False


async def generate_voice_samples():
    """Generate all voice samples"""
    
    print("\n" + "=" * 70)
    print("VOICE SAMPLE GENERATION")
    print("Using ElevenLabs API with multilingual v2 model")
    print("=" * 70 + "\n")
    
    total_generated = 0
    total_failed = 0
    
    # Generate samples for each assistant
    for assistant_name, languages in VOICE_SAMPLES.items():
        voice_id = VOICE_IDS.get(assistant_name)
        
        print(f"\n{'=' * 70}")
        print(f"Generating samples for: {assistant_name.upper()}")
        print(f"Voice ID: {voice_id}")
        print("=" * 70)
        
        for language, scenarios in languages.items():
            print(f"\n--- {language.upper()} ---")
            
            for scenario, items in scenarios.items():
                print(f"\n{scenario.capitalize()}:")
                
                for item in items:
                    filename = f"{item['id']}.mp3"
                    
                    success = await generate_audio_file(
                        text=item["text"],
                        voice_id=voice_id,
                        filename=filename,
                        model=VOICE_MODEL
                    )
                    
                    if success:
                        total_generated += 1
                    else:
                        total_failed += 1
    
    print("\n" + "=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)
    print(f"✓ Successfully generated: {total_generated}")
    print(f"✗ Failed: {total_failed}")
    print(f"\nAudio files saved in: backend/voice_samples/")
    print("\nNote: ElevenLabs free tier includes 10,000 characters/month")


async def generate_single_sample(assistant_name, language, scenario, index):
    """Generate a single sample for testing"""
    
    voice_id = VOICE_IDS.get(assistant_name.lower())
    if not voice_id:
        print(f"✗ Unknown assistant: {assistant_name}")
        return
    
    samples = VOICE_SAMPLES.get(assistant_name.lower(), {})
    lang_samples = samples.get(language.lower(), {})
    scenario_samples = lang_samples.get(scenario.lower(), [])
    
    if not scenario_samples:
        print(f"✗ No samples found for {assistant_name}/{language}/{scenario}")
        return
    
    if index >= len(scenario_samples):
        print(f"✗ Index {index} out of range. Max index: {len(scenario_samples) - 1}")
        return
    
    item = scenario_samples[index]
    
    print(f"\nGenerating single sample:")
    print(f"  Assistant: {assistant_name}")
    print(f"  Language: {language}")
    print(f"  Scenario: {scenario}")
    print(f"  Text: {item['text'][:50]}...")
    
    await generate_audio_file(
        text=item["text"],
        voice_id=voice_id,
        filename=f"test_{item['id']}.mp3",
        model=VOICE_MODEL
    )


def print_sample_list():
    """Print all available samples"""
    print("\n" + "=" * 70)
    print("AVAILABLE VOICE SAMPLES")
    print("=" * 70)
    
    for assistant_name, languages in VOICE_SAMPLES.items():
        print(f"\n{assistant_name.upper()}")
        
        for language, scenarios in languages.items():
            print(f"\n  {language.upper()}:")
            
            for scenario, items in scenarios.items():
                print(f"    {scenario.capitalize()}:")
                
                for i, item in enumerate(items):
                    print(f"      {i+1}. {item['text'][:60]}...")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--list":
            print_sample_list()
        elif sys.argv[1] == "--single" and len(sys.argv) >= 5:
            # python generate_voice_samples.py --single aabinash english greetings 1
            asyncio.run(generate_single_sample(
                sys.argv[2],  # assistant
                sys.argv[3],  # language
                sys.argv[4],  # scenario
                int(sys.argv[5]) - 1  # index (0-based)
            ))
        else:
            print("Usage:")
            print("  python generate_voice_samples.py           # Generate all samples")
            print("  python generate_voice_samples.py --list     # List all samples")
            print("  python generate_voice_samples.py --single <assistant> <language> <scenario> <index>")
    else:
        asyncio.run(generate_voice_samples())
