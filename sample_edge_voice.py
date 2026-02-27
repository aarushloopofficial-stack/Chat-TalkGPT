"""
Sample Audio Demonstration for Aakansha Voice using Edge TTS
This script demonstrates the free Edge TTS female voice integration.
No API key required - uses Microsoft Edge TTS (free).
"""
import os
import asyncio
import base64

# Try importing Edge TTS
try:
    import edge_tts
    print("[OK] Edge TTS is installed")
except ImportError:
    print("[ERROR] Edge TTS not installed. Run: pip install edge-tts")
    exit(1)

# Voice configuration for Aakansha (female - sweet, polite, confident)
VOICE_MAPPINGS = {
    "aakansha": {
        "en": "en-US-JennyNeural",    # English female - polite, professional
        "hi": "hi-IN-SwaraNeural",     # Hindi female
        "ne": "hi-IN-SwaraNeural",     # Nepali (fallback to Hindi)
    },
    "abinash": {
        "en": "en-US-GuyNeural",       # English male
        "hi": "hi-IN-MadhurNeural",    # Hindi male
        "ne": "ne-NP-SagarNeural",     # Nepali male
    }
}

SAMPLE_TEXTS = {
    "en": [
        "Hello! I am Aakansha, your personal voice assistant. I am here to help you with warmth and professionalism.",
        "How may I assist you today? I'm here to make your tasks easier and more enjoyable.",
        "Thank you for choosing me as your assistant. I promise to always be polite, sweet, and confident in helping you."
    ],
    "hi": [
        "Namaste! Main Aakansha hoon, aapka personal voice assistant. Main yahan aapki madad ke liye bawaafuqta hoon.",
        "Aaj main aapki kaise madad kar sakta hoon? Main yahan aapke kaamon ko asani se pura karne ke liye hoon.",
        "Mujhe apne assistant ke roop mein choose karne ke liye dhanyavad. Main hamesha madad karne mein polite aur confident rahoongi."
    ]
}

async def generate_sample_audio():
    """Generate sample audio files using Edge TTS"""
    
    print("\n" + "="*60)
    print("Aakansha Voice Sample Demonstration (Edge TTS)")
    print("Voice: Jenny (Microsoft Edge) - Sweet, Polite & Confident")
    print("="*60 + "\n")
    
    languages = {
        "en": "English",
        "hi": "Hindi"
    }
    
    # Generate audio for each language
    for lang_code, lang_name in languages.items():
        print(f"\n--- {lang_name} Samples ---")
        texts = SAMPLE_TEXTS.get(lang_code, [])
        
        for i, text in enumerate(texts, 1):
            print(f"Generating {lang_name} sample {i}...")
            print(f"Text: ( Nepali text - see actual file )")
            
            try:
                # Get voice for language
                voice_name = VOICE_MAPPINGS["aakansha"].get(lang_code, "en-US-JennyNeural")
                
                # Create communicate object
                communicate = edge_tts.Communicate(text, voice_name)
                
                # Save to file
                filename = f"sample_aakansha_{lang_code}_{i}.mp3"
                await communicate.save(filename)
                
                print(f"[OK] Saved to: {filename}")
                
            except Exception as e:
                print(f"[ERROR] Error generating audio: {e}")
    
    print("\n" + "="*60)
    print("Sample audio generation complete!")
    print("="*60)
    print("\nAudio files created:")
    print("  - sample_aakansha_en_1.mp3 (English)")
    print("  - sample_aakansha_en_2.mp3 (English)")
    print("  - sample_aakansha_en_3.mp3 (English)")
    print("  - sample_aakansha_hi_1.mp3 (Hindi)")
    print("  - sample_aakansha_hi_2.mp3 (Hindi)")
    print("  - sample_aakansha_hi_3.mp3 (Hindi)")
    print("\nVoice used: Jenny Neural (English) / Swara Neural (Hindi)")
    print("These are free Microsoft Edge TTS voices - no API key needed!")
    print("For Nepali, the system uses Hindi voice as fallback.")

if __name__ == "__main__":
    asyncio.run(generate_sample_audio())
