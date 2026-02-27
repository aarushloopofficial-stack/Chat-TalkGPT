"""
Sample Audio Demonstration for Aakansha Voice (ElevenLabs)
This script demonstrates the ElevenLabs female voice integration.
Run this script after configuring your ElevenLabs API key in .env
"""
import os
import asyncio
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

# Voice ID for Rachel (sweet, calm, confident female voice)
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

# Sample text to speak
SAMPLE_TEXTS = [
    "Hello! I am Aakansha, your personal voice assistant. I am here to help you with warmth and professionalism.",
    "How may I assist you today? I'm here to make your tasks easier and more enjoyable.",
    "Thank you for choosing me as your assistant. I promise to always be polite, sweet, and confident in helping you."
]

async def generate_sample_audio():
    """Generate sample audio files using ElevenLabs"""
    
    print("\n" + "="*60)
    print("Aakansha Voice Sample Demonstration")
    print("Voice: Rachel (ElevenLabs) - Sweet, Polite & Confident")
    print("="*60 + "\n")
    
    # Generate audio for each sample text
    for i, text in enumerate(SAMPLE_TEXTS, 1):
        print(f"Generating sample {i}...")
        print(f"Text: {text[:50]}...")
        
        try:
            # Generate audio
            audio_generator = client.generate(
                text=text,
                voice_id=VOICE_ID,
                model="eleven_monolingual_v1"
            )
            
            # Convert generator to bytes
            audio_bytes = b"".join(audio_generator)
            
            # Save to file
            filename = f"sample_aakansha_{i}.mp3"
            with open(filename, "wb") as f:
                f.write(audio_bytes)
            
            print(f"✓ Saved to: {filename}")
            
            # Also save base64 version
            b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
            b64_filename = f"sample_aakansha_{i}.b64"
            with open(b64_filename, "w") as f:
                f.write(b64_audio)
            print(f"✓ Base64 saved to: {b64_filename}")
            
        except Exception as e:
            print(f"✗ Error generating audio: {e}")
    
    print("\n" + "="*60)
    print("Sample audio generation complete!")
    print("="*60)
    print("\nTo test the voice in the app:")
    print("1. Make sure ELEVENLABS_API_KEY is set in .env")
    print("2. Run the main application: python backend/main.py")
    print("3. Select 'Aakansha' as the voice in the UI")
    print("\nNote: ElevenLabs free tier includes 10,000 characters/month")

if __name__ == "__main__":
    asyncio.run(generate_sample_audio())
