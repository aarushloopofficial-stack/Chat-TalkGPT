"""
Generate Male Voice (Aabinash) Audio Samples using Edge TTS
===========================================================
This script generates audio files using Microsoft Edge's free TTS service.
No API key required!
"""

import asyncio
import os
import edge_tts
from voice_sample_content import AABINASH_ENGLISH, AABINASH_NEPALI, AABINASH_HINDI

# Voice mappings for Edge TTS
VOICE_MAP = {
    "english": "en-US-GuyNeural",      # Male voice - confident
    "nepali": "ne-NP-SagarNeural",    # Nepali male
    "hindi": "hi-IN-MadhurNeural"     # Hindi male
}

OUTPUT_DIR = "backend/voice_samples"
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def generate_audio(text, voice, filename):
    """Generate audio using Edge TTS"""
    try:
        print(f"  Generating: {filename}...")
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(f"{OUTPUT_DIR}/{filename}")
        print(f"  [OK] Saved: {OUTPUT_DIR}/{filename}")
        return True
    except Exception as e:
        print(f"  [X] Error: {e}")
        return False

async def generate_all_samples():
    """Generate all Aabinash voice samples"""
    
    print("\n" + "="*70)
    print("GENERATING MALE VOICE (AABINASH) AUDIO SAMPLES")
    print("Using Edge TTS (Free - No API Key Required)")
    print("="*70 + "\n")
    
    total = 0
    
    # English samples
    print("--- ENGLISH ---")
    for scenario, items in AABINASH_ENGLISH.items():
        for item in items:
            filename = f"aabinash_en_{item['id']}.mp3"
            await generate_audio(item["text"], VOICE_MAP["english"], filename)
            total += 1
    
    # Nepali samples  
    print("\n--- NEPALI ---")
    for scenario, items in AABINASH_NEPALI.items():
        for item in items:
            filename = f"aabinash_ne_{item['id']}.mp3"
            await generate_audio(item["text"], VOICE_MAP["nepali"], filename)
            total += 1
    
    # Hindi samples
    print("\n--- HINDI ---")
    for scenario, items in AABINASH_HINDI.items():
        for item in items:
            filename = f"aabinash_hi_{item['id']}.mp3"
            await generate_audio(item["text"], VOICE_MAP["hindi"], filename)
            total += 1
    
    print("\n" + "="*70)
    print(f"COMPLETE! Generated {total} audio files")
    print(f"Files saved in: {OUTPUT_DIR}/")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(generate_all_samples())
