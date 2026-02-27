"""
Display Voice Samples for Aabinash (Male Assistant)
====================================================
Run this to see all male voice assistant samples
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from voice_sample_content import AABINASH_ENGLISH, AABINASH_NEPALI, AABINASH_HINDI

def display_samples():
    print("="*80)
    print("AABINASH (MALE) VOICE SAMPLES")
    print("Voice Character: Confident, Professional, Natural Human-like Tone")
    print("ElevenLabs Voice ID: pNInz6obpgDQGcFmaJgB (Adam)")
    print("="*80)
    
    # English Samples
    print("\n" + "="*80)
    print("ENGLISH SAMPLES (25 total)")
    print("="*80)
    
    for scenario, items in AABINASH_ENGLISH.items():
        print(f"\n--- {scenario.upper()} ---")
        for i, item in enumerate(items, 1):
            print(f"\n  {i}. [{item['id']}]")
            print(f"     Text: {item['text']}")
    
    # Nepali Samples - show phonetics only
    print("\n\n" + "="*80)
    print("NEPALI SAMPLES (25 total) - Phonetic Guide")
    print("="*80)
    
    for scenario, items in AABINASH_NEPALI.items():
        print(f"\n--- {scenario.upper()} ---")
        for i, item in enumerate(items, 1):
            print(f"\n  {i}. [{item['id']}]")
            print(f"     Phonetics: {item['phonetics']}")
    
    # Hindi Samples - show phonetics only
    print("\n\n" + "="*80)
    print("HINDI SAMPLES (25 total) - Phonetic Guide")
    print("="*80)
    
    for scenario, items in AABINASH_HINDI.items():
        print(f"\n--- {scenario.upper()} ---")
        for i, item in enumerate(items, 1):
            print(f"\n  {i}. [{item['id']}]")
            print(f"     Phonetics: {item['phonetics']}")
    
    print("\n" + "="*80)
    print("TOTAL: 75 voice samples for Aabinash (Male Assistant)")
    print("="*80)

if __name__ == "__main__":
    display_samples()
