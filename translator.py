"""
Chat&Talk GPT - Translation Module
Provides free translation services using MyMemory API (primary) with LibreTranslate fallback
"""
import requests
import logging
import json
from typing import Dict, List, Optional

logger = logging.getLogger("TranslatorManager")

# Supported languages with language codes
SUPPORTED_LANGUAGES = [
    {"code": "en", "name": "English"},
    {"code": "hi", "name": "Hindi"},
    {"code": "ne", "name": "Nepali"},
    {"code": "es", "name": "Spanish"},
    {"code": "fr", "name": "French"},
    {"code": "de", "name": "German"},
    {"code": "zh", "name": "Chinese"},
    {"code": "ja", "name": "Japanese"},
    {"code": "ko", "name": "Korean"},
    {"code": "ar", "name": "Arabic"},
    {"code": "pt", "name": "Portuguese"},
    {"code": "ru", "name": "Russian"},
    {"code": "it", "name": "Italian"},
    {"code": "nl", "name": "Dutch"},
    {"code": "tr", "name": "Turkish"},
    {"code": "pl", "name": "Polish"},
    {"code": "vi", "name": "Vietnamese"},
    {"code": "th", "name": "Thai"},
    {"code": "id", "name": "Indonesian"},
    {"code": "uk", "name": "Ukrainian"},
    # Additional languages
    {"code": "ur", "name": "Urdu"},
    {"code": "bn", "name": "Bengali"},
    {"code": "ta", "name": "Tamil"},
    {"code": "te", "name": "Telugu"},
    {"code": "ml", "name": "Malayalam"},
    {"code": "pa", "name": "Punjabi"},
    {"code": "gu", "name": "Gujarati"},
    {"code": "mr", "name": "Marathi"},
    {"code": "sv", "name": "Swedish"},
    {"code": "da", "name": "Danish"},
    {"code": "no", "name": "Norwegian"},
    {"code": "fi", "name": "Finnish"},
    {"code": "el", "name": "Greek"},
    {"code": "he", "name": "Hebrew"},
    {"code": "cs", "name": "Czech"},
    {"code": "ro", "name": "Romanian"},
    {"code": "hu", "name": "Hungarian"},
    {"code": "ms", "name": "Malay"},
    {"code": "fa", "name": "Persian"},
]

# Language code mapping for MyMemory API
LANGUAGE_CODE_MAP = {
    "en": "en",
    "hi": "hi",
    "ne": "ne",
    "es": "es",
    "fr": "fr",
    "de": "de",
    "zh": "zh-CN",
    "ja": "ja",
    "ko": "ko",
    "ar": "ar",
    "pt": "pt",
    "ru": "ru",
    "it": "it",
    "nl": "nl",
    "tr": "tr",
    "pl": "pl",
    "vi": "vi",
    "th": "th",
    "id": "id",
    "uk": "uk",
}


class TranslatorManager:
    """Manager for translation services using free APIs"""

    def __init__(self):
        self.user_agent = "ChatAndTalkGPT/1.0 (Translation Service)"
        self.mymemory_url = "https://api.mymemory.translated.net/get"
        # LibreTranslate endpoints (public instances)
        self.libretranslate_endpoints = [
            "https://libretranslate.com/translate",
            "https://translate.terraprint.co/translate",
            "https://translate.argosopentech.com/translate",
        ]
        logger.info("TranslatorManager initialized")

    def get_supported_languages(self) -> List[Dict]:
        """Return list of supported languages"""
        return SUPPORTED_LANGUAGES

    def detect_language(self, text: str) -> str:
        """
        Detect the language of the input text using simple heuristics.
        For production, could use a dedicated detection API.
        """
        if not text or not text.strip():
            return "en"

        # Simple heuristic-based detection
        text = text.strip()

        # Common Hindi characters (Devanagari script)
        hindi_chars = set("\u0900-\u097F")
        # Common Nepali characters (Devanagari script)
        nepali_chars = set("\u0900-\u097F")
        # Common Chinese characters
        chinese_chars = set("\u4e00-\u9fff")
        # Common Japanese characters (Hiragana + Katakana + Kanji)
        japanese_chars = set("\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FBF")
        # Common Korean characters (Hangul)
        korean_chars = set("\uAC00-\uD7AF\u1100-\u11FF")
        # Common Arabic characters
        arabic_chars = set("\u0600-\u06FF")
        # Common Cyrillic (Russian, Ukrainian)
        cyrillic_chars = set("\u0400-\u04FF")
        # Common Thai characters
        thai_chars = set("\u0E00-\u0E7F")

        text_set = set(text)

        if text_set & hindi_chars or text_set & nepali_chars:
            # Check for Nepali-specific characters
            nepali_specific = set("\u093E-\u0942\u0966-\u096F")  # Vedic accents, Nepali digits
            if text_set & nepali_specific or " nepali" in text.lower() or " नेपाली" in text:
                return "ne"
            return "hi"

        if text_set & chinese_chars:
            return "zh"

        if text_set & japanese_chars:
            return "ja"

        if text_set & korean_chars:
            return "ko"

        if text_set & arabic_chars:
            return "ar"

        if text_set & thai_chars:
            return "th"

        if text_set & cyrillic_chars:
            # Distinguish between Russian and Ukrainian
            ukrainian_specific = set("\u0490\u0491\u0404")  # Ukrainian-specific letters
            if text_set & ukrainian_specific:
                return "uk"
            return "ru"

        # Default to English for Latin script
        return "en"

    async def translate(
        self, text: str, source: str = "auto", target: str = "en"
    ) -> Dict:
        """
        Translate text from source language to target language.
        
        Args:
            text: The text to translate
            source: Source language code (or 'auto' for auto-detection)
            target: Target language code
            
        Returns:
            Dict with translation results
        """
        if not text or not text.strip():
            return {
                "success": False,
                "original_text": text,
                "translated_text": "",
                "source_lang": source,
                "target_lang": target,
                "detected_lang": "en",
                "error": "Empty text provided",
            }

        original_text = text.strip()

        # Handle auto-detection
        detected_lang = source
        if source == "auto" or source == "":
            detected_lang = self.detect_language(original_text)
            source = detected_lang

        # Normalize language codes
        source_code = LANGUAGE_CODE_MAP.get(source, source)
        target_code = LANGUAGE_CODE_MAP.get(target, target)

        # Validate target language
        if target not in [lang["code"] for lang in SUPPORTED_LANGUAGES]:
            return {
                "success": False,
                "original_text": original_text,
                "translated_text": "",
                "source_lang": source,
                "target_lang": target,
                "detected_lang": detected_lang,
                "error": f"Unsupported target language: {target}",
            }

        # Try MyMemory API first (free, no key required)
        try:
            result = await self._translate_mymemory(
                original_text, source_code, target_code
            )
            if result:
                result["detected_lang"] = detected_lang
                return result
        except Exception as e:
            logger.warning(f"MyMemory translation failed: {e}")

        # Fallback to LibreTranslate
        try:
            result = await self._translate_libretranslate(
                original_text, source_code, target_code
            )
            if result:
                result["detected_lang"] = detected_lang
                return result
        except Exception as e:
            logger.warning(f"LibreTranslate translation failed: {e}")

        # If all APIs fail
        return {
            "success": False,
            "original_text": original_text,
            "translated_text": "",
            "source_lang": source,
            "target_lang": target,
            "detected_lang": detected_lang,
            "error": "Translation service temporarily unavailable. Please try again later.",
        }

    async def _translate_mymemory(
        self, text: str, source: str, target: str
    ) -> Optional[Dict]:
        """
        Translate using MyMemory API (free, no key required)
        API: https://api.mymemory.translated.net/get?q=text&langpair=en|hi
        """
        try:
            # MyMemory format: source|target
            lang_pair = f"{source}|{target}"
            params = {
                "q": text,
                "langpair": lang_pair,
            }

            headers = {
                "User-Agent": self.user_agent,
            }

            response = requests.get(
                self.mymemory_url, params=params, headers=headers, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                response_data = data.get("responseData", {})

                if response_data.get("translatedText"):
                    return {
                        "success": True,
                        "original_text": text,
                        "translated_text": response_data["translatedText"],
                        "source_lang": source,
                        "target_lang": target,
                        "detected_lang": source,
                    }

            logger.warning(f"MyMemory API returned status: {response.status_code}")
            return None

        except requests.exceptions.Timeout:
            logger.error("MyMemory API timeout")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"MyMemory API request error: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"MyMemory API JSON decode error: {e}")
            return None

    async def _translate_libretranslate(
        self, text: str, source: str, target: str
    ) -> Optional[Dict]:
        """
        Translate using LibreTranslate public instances (free, no key required)
        Tries multiple public endpoints for reliability
        """
        # Normalize source for LibreTranslate (use 'auto' for detection)
        lib_source = source if source != "zh-CN" else "zh"
        lib_source = "auto" if source == "zh-CN" or source == "zh" else lib_source

        # Map back target codes
        lib_target = target
        if target == "zh-CN":
            lib_target = "zh"

        payload = {
            "q": text,
            "source": lib_source,
            "target": lib_target,
            "format": "text",
        }

        headers = {
            "User-Agent": self.user_agent,
            "Content-Type": "application/json",
        }

        # Try each LibreTranslate endpoint
        for endpoint in self.libretranslate_endpoints:
            try:
                response = requests.post(
                    endpoint, json=payload, headers=headers, timeout=15
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("translatedText"):
                        return {
                            "success": True,
                            "original_text": text,
                            "translated_text": data["translatedText"],
                            "source_lang": source,
                            "target_lang": target,
                            "detected_lang": data.get("detectedLanguage", source),
                        }

                logger.warning(
                    f"LibreTranslate endpoint {endpoint} returned: {response.status_code}"
                )

            except requests.exceptions.Timeout:
                logger.warning(f"LibreTranslate endpoint {endpoint} timeout")
                continue
            except requests.exceptions.RequestException as e:
                logger.warning(f"LibreTranslate endpoint {endpoint} error: {e}")
                continue
            except json.JSONDecodeError as e:
                logger.warning(f"LibreTranslate endpoint {endpoint} JSON error: {e}")
                continue

        return None

    async def translate_batch(
        self, texts: List[str], source: str = "auto", target: str = "en"
    ) -> Dict:
        """
        Translate multiple texts at once.
        
        Args:
            texts: List of texts to translate
            source: Source language code (or 'auto' for auto-detection)
            target: Target language code
            
        Returns:
            Dict with batch translation results
        """
        if not texts or len(texts) == 0:
            return {
                "success": False,
                "results": [],
                "error": "No texts provided",
            }
        
        results = []
        for text in texts:
            result = await self.translate(text, source, target)
            results.append(result)
        
        return {
            "success": True,
            "results": results,
            "count": len(results),
        }

    def get_pronunciation_guide(self, text: str, language: str) -> Dict:
        """
        Generate a simple pronunciation guide for the given text.
        Uses basic phonetic approximations.
        
        Args:
            text: The text to generate pronunciation for
            language: Language code
            
        Returns:
            Dict with pronunciation guides
        """
        if not text or not text.strip():
            return {
                "success": False,
                "original": text,
                "pronunciations": [],
                "error": "Empty text provided",
            }
        
        original = text.strip()
        words = original.split()
        pronunciations = []
        
        # Simple phonetic approximations for common languages
        phonetic_map = self._get_phonetic_map(language)
        
        for word in words:
            # Try to find phonetic equivalent
            lower_word = word.lower()
            phonetic = phonetic_map.get(lower_word, f"[{word}]")
            pronunciations.append({
                "word": word,
                "phonetic": phonetic,
            })
        
        return {
            "success": True,
            "original": original,
            "language": language,
            "pronunciations": pronunciations,
            "reading": " ".join([p["phonetic"] for p in pronunciations]),
        }

    def _get_phonetic_map(self, language: str) -> Dict[str, str]:
        """Get phonetic mapping for a language"""
        # Common phonetic mappings for different languages
        phonetic_maps = {
            "hi": {  # Hindi
                "namaste": "nuh-muh-STAY",
                "dhanyavad": "dhun-yuh-VAHD",
                "shukriya": "shuhk-REE-yuh",
                "haan": "HAHN",
                "nahin": "nuh-HEEN",
                "kya": "KYAH",
                "hai": "HEH",
            },
            "ne": {  # Nepali
                "namaste": "nuh-muh-STAY",
                "dhanyabad": "dhun-yuh-BAHD",
                "sanchai": "SAHN-chay",
                "hajur": "huh-JOOR",
            },
            "ja": {  # Japanese
                "konnichiwa": "kohn-nee-chee-WAH",
                "arigatou": "ah-ree-GAH-toh",
                "sayonara": "sah-yoh-NAH-rah",
                "hai": "HEH",
                "iie": "EE-eh",
            },
            "zh": {  # Chinese
                "nihao": "nee-HOW",
                "xiexie": "shyeh-shyeh",
                "zaijian": "zai-JYEN",
            },
            "ko": {  # Korean
                "annyeonghaseyo": "ah-NYUNG-ha-seh-YOH",
                "gamsahamnida": "kahm-sah-hahm-nee-dah",
                "annyeonghi gaseyo": "ah-NYUNG-hee gah-SEH-yoh",
            },
            "es": {  # Spanish
                "hola": "OH-lah",
                "gracias": "GRAH-syahs",
                "adios": "ah-DYOHS",
                "por favor": "por fah-VOR",
            },
            "fr": {  # French
                "bonjour": "bohn-ZHOOR",
                "merci": "mehr-SEE",
                "au revoir": "oh ruh-VWAHR",
            },
            "de": {  # German
                "guten tag": "GOO-ten tahk",
                "danke": "DAHN-kuh",
                "auf wiedersehen": "owf VEE-der-zay-en",
            },
        }
        return phonetic_maps.get(language, {})

    async def translate_to_all(
        self, text: str, source: str = "auto"
    ) -> Dict:
        """
        Translate text to all supported languages.
        
        Args:
            text: The text to translate
            source: Source language code (or 'auto' for auto-detection)
            
        Returns:
            Dict with translations to all languages
        """
        if not text or not text.strip():
            return {
                "success": False,
                "original": text,
                "translations": [],
                "error": "Empty text provided",
            }
        
        original = text.strip()
        
        # Detect source language if auto
        if source == "auto" or source == "":
            source = self.detect_language(original)
        
        # Get all target languages (exclude source)
        targets = [lang["code"] for lang in SUPPORTED_LANGUAGES if lang["code"] != source]
        
        translations = []
        for target in targets:
            result = await self.translate(original, source, target)
            if result.get("success"):
                translations.append({
                    "language": target,
                    "language_name": next((lang["name"] for lang in SUPPORTED_LANGUAGES if lang["code"] == target), target),
                    "translation": result.get("translated_text"),
                })
        
        return {
            "success": True,
            "original": original,
            "source_lang": source,
            "source_lang_name": next((lang["name"] for lang in SUPPORTED_LANGUAGES if lang["code"] == source), source),
            "translations": translations,
            "count": len(translations),
        }


# Singleton instance
translator_manager = TranslatorManager()
