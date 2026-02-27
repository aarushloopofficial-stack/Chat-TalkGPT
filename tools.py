"""
Chat&Talk GPT - Tools Manager
Handles external data fetching (Wikipedia, Weather, Search, Image Generation, Translation)
"""
import requests
import logging
import json
import asyncio
from typing import Optional, Dict, Any, List
import urllib.parse
import random
import os

# Import code executor module
try:
    from backend.code_executor import code_executor
    CODE_EXECUTOR_AVAILABLE = True
except ImportError:
    # Try relative import if running from backend directory
    try:
        from code_executor import code_executor
        CODE_EXECUTOR_AVAILABLE = True
    except ImportError:
        CODE_EXECUTOR_AVAILABLE = False
        logger.warning("code_executor module not available")

logger = logging.getLogger("ToolsManager")

# Import translator module
try:
    from translator import translator_manager
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    logger.warning("translator module not available")

# Import calendar module
try:
    from backend.calendar_manager import calendar_manager
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False
    logger.warning("calendar_manager module not available")

# Import flashcards module
try:
    from backend.flashcards import flashcard_manager
    FLASHCARDS_AVAILABLE = True
except ImportError:
    FLASHCARDS_AVAILABLE = False
    logger.warning("flashcards module not available")

# Import calculator module
try:
    from backend.calculator import calculator_manager
    CALCULATOR_AVAILABLE = True
except ImportError:
    try:
        from calculator import calculator_manager
        CALCULATOR_AVAILABLE = True
    except ImportError:
        CALCULATOR_AVAILABLE = False
        logger.warning("calculator module not available")

# Import subject solver module
try:
    from backend.subject_solver import subject_solver
    SUBJECT_SOLVER_AVAILABLE = True
except ImportError:
    try:
        from subject_solver import subject_solver
        SUBJECT_SOLVER_AVAILABLE = True
    except ImportError:
        SUBJECT_SOLVER_AVAILABLE = False
        logger.warning("subject_solver module not available")

# Import dictionary module
try:
    from backend.dictionary_manager import dictionary_manager
    DICTIONARY_AVAILABLE = True
except ImportError:
    try:
        from dictionary_manager import dictionary_manager
        DICTIONARY_AVAILABLE = True
    except ImportError:
        DICTIONARY_AVAILABLE = False
        logger.warning("dictionary_manager module not available")

# Import currency converter module
try:
    from backend.currency_converter import currency_converter, get_currency_converter
    CURRENCY_CONVERTER_AVAILABLE = True
except ImportError:
    try:
        from currency_converter import currency_converter, get_currency_converter
        CURRENCY_CONVERTER_AVAILABLE = True
    except ImportError:
        CURRENCY_CONVERTER_AVAILABLE = False
        logger.warning("currency_converter module not available")

# Import news manager module
try:
    from backend.news_manager import news_manager
    NEWS_AVAILABLE = True
except ImportError:
    NEWS_AVAILABLE = False
    logger.warning("news_manager module not available")

# Import recipe manager module
try:
    from backend.recipe_manager import recipe_manager
    RECIPE_AVAILABLE = True
except ImportError:
    RECIPE_AVAILABLE = False
    logger.warning("recipe_manager module not available")

# Import YouTube manager module
try:
    from backend.youtube_manager import get_youtube_manager
    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False
    logger.warning("youtube_manager module not available")

# Import Notes manager module
try:
    from backend.notes_manager import notes_manager
    NOTES_AVAILABLE = True
except ImportError:
    try:
        from notes_manager import notes_manager
        NOTES_AVAILABLE = True
    except ImportError:
        NOTES_AVAILABLE = False
        logger.warning("notes_manager module not available")

# Import Alarm manager module
try:
    from backend.alarm_manager import alarm_manager
    ALARM_AVAILABLE = True
except ImportError:
    try:
        from alarm_manager import alarm_manager
        ALARM_AVAILABLE = True
    except ImportError:
        ALARM_AVAILABLE = False
        logger.warning("alarm_manager module not available")

# Import Study Timer module
try:
    from backend.study_timer import study_timer
    STUDY_TIMER_AVAILABLE = True
except ImportError:
    try:
        from study_timer import study_timer
        STUDY_TIMER_AVAILABLE = True
    except ImportError:
        STUDY_TIMER_AVAILABLE = False
        logger.warning("study_timer module not available")

# Import Trivia Quiz module
try:
    from backend.trivia_quiz import trivia_quiz
    TRIVIA_AVAILABLE = True
except ImportError:
    try:
        from trivia_quiz import trivia_quiz
        TRIVIA_AVAILABLE = True
    except ImportError:
        TRIVIA_AVAILABLE = False
        logger.warning("trivia_quiz module not available")

# Import Jokes manager module
try:
    from backend.jokes_manager import jokes_manager
    JOKES_AVAILABLE = True
except ImportError:
    try:
        from jokes_manager import jokes_manager
        JOKES_AVAILABLE = True
    except ImportError:
        JOKES_AVAILABLE = False
        logger.warning("jokes_manager module not available")

# Import Quotes manager module
try:
    from backend.quotes_manager import quotes_manager
    QUOTES_AVAILABLE = True
except ImportError:
    try:
        from quotes_manager import quotes_manager
        QUOTES_AVAILABLE = True
    except ImportError:
        QUOTES_AVAILABLE = False
        logger.warning("quotes_manager module not available")

try:
    from googlesearch import search as gsearch
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    logger.warning("googlesearch-python not available")

try:
    import wikipediaapi
    WIKI_AVAILABLE = True
except ImportError:
    WIKI_AVAILABLE = False
    logger.warning("wikipedia-api not available")

# Import AI Aggregator module
try:
    from backend.ai_aggregator import ai_aggregator, get_ai_search, search_web
    AI_AGGREGATOR_AVAILABLE = True
except ImportError:
    try:
        from ai_aggregator import ai_aggregator, get_ai_search, search_web
        AI_AGGREGATOR_AVAILABLE = True
    except ImportError:
        AI_AGGREGATOR_AVAILABLE = False
        logger.warning("ai_aggregator module not available")

class ToolsManager:
    def __init__(self):
        self.user_agent = "ChatAndTalkGPT/1.0 (Educational Assistant)"
        self.wiki = None
        self.currency_converter = None
        self.youtube_manager = None
        self.trivia_quiz = None
        self.jokes_manager = None
        self.quotes_manager = None
        
        if WIKI_AVAILABLE:
            try:
                # Initialize Wikipedia with a clear user agent
                self.wiki = wikipediaapi.Wikipedia(user_agent=self.user_agent, language='en')
            except Exception as e:
                logger.error(f"Wiki init error: {e}")
        
        # Initialize currency converter
        if CURRENCY_CONVERTER_AVAILABLE:
            try:
                self.currency_converter = get_currency_converter()
            except Exception as e:
                logger.error(f"Currency converter init error: {e}")
        
        # Initialize YouTube manager
        if YOUTUBE_AVAILABLE:
            try:
                self.youtube_manager = get_youtube_manager()
            except Exception as e:
                logger.error(f"YouTube manager init error: {e}")
        
        # Initialize Trivia Quiz
        if TRIVIA_AVAILABLE:
            try:
                self.trivia_quiz = trivia_quiz
            except Exception as e:
                logger.error(f"Trivia quiz init error: {e}")
        
        # Initialize Jokes Manager
        if JOKES_AVAILABLE:
            try:
                self.jokes_manager = jokes_manager
            except Exception as e:
                logger.error(f"Jokes manager init error: {e}")
        
        # Initialize Quotes Manager
        if QUOTES_AVAILABLE:
            try:
                self.quotes_manager = quotes_manager
            except Exception as e:
                logger.error(f"Quotes manager init error: {e}")
        
        # Initialize AI Aggregator
        if AI_AGGREGATOR_AVAILABLE:
            try:
                self.ai_aggregator = ai_aggregator
            except Exception as e:
                logger.error(f"AI Aggregator init error: {e}")
        
        # Initialize Subject Solver
        if SUBJECT_SOLVER_AVAILABLE:
            try:
                self.subject_solver = subject_solver
            except Exception as e:
                logger.error(f"Subject solver init error: {e}")

    async def search_google(self, query: str) -> Dict[str, Any]:
        """Search Google for current information"""
        if not GOOGLE_AVAILABLE:
            return {"text": "Google search tool is currently unavailable.", "sources": []}
            
        try:
            results = []
            sources = []
            # googlesearch-python returns a generator of URLs
            # We can't get bodies easily without extra scraping, so we just get links
            # and perhaps use Wikipedia for the body
            count = 0
            for url in gsearch(query, num_results=5):
                sources.append(url)
                count += 1
                if count >= 3: break
            
            if sources:
                return {
                    "text": f"I found several resources on this topic from Google. Top links: {', '.join(sources[:2])}",
                    "sources": sources
                }
            return {"text": "I searched Google but didn't find specific answers.", "sources": []}
        except Exception as e:
            logger.error(f"Google search error: {e}")
            return {"text": "I had trouble connecting to Google.", "sources": []}

    async def search_wikipedia(self, query: str) -> Dict[str, Any]:
        """Search Wikipedia for detailed information"""
        if not self.wiki:
            return {"text": "Wikipedia is currently unavailable.", "sources": []}
            
        try:
            page = self.wiki.page(query)
            if page.exists():
                return {
                    "text": page.summary[:1000], # First 1000 chars
                    "sources": [page.fullurl]
                }
            return {"text": f"I couldn't find a Wikipedia page for '{query}'.", "sources": []}
        except Exception as e:
            logger.error(f"Wiki search error: {e}")
            return {"text": "I had trouble connecting to Wikipedia.", "sources": []}

    async def global_research(self, query: str) -> Dict[str, Any]:
        """Combined research from Wiki and Google"""
        wiki_res = await self.search_wikipedia(query)
        google_res = await self.search_google(query)
        
        combined_text = ""
        if wiki_res["sources"]:
            combined_text += f"WIKIPEDIA INFO:\n{wiki_res['text']}\n\n"
        if google_res["sources"]:
            combined_text += f"GOOGLE TOP LINKS:\n" + "\n".join(google_res["sources"])
            
        return {
            "text": combined_text or "No results found from Wiki or Google.",
            "sources": wiki_res["sources"] + google_res["sources"]
        }

    async def ai_search(self, query: str, verified_only: bool = False) -> Dict[str, Any]:
        """
        AI-powered web search with verified sources (Perplexity-like)
        Returns answer with sources from trusted domains
        """
        if not AI_AGGREGATOR_AVAILABLE:
            return {
                "text": "AI search is currently unavailable. Please try other search methods.",
                "sources": [],
                "verified_sources": []
            }
        
        try:
            result = await self.ai_aggregator.search_and_answer(
                query=query,
                use_web_search=True,
                provider="auto"
            )
            
            # Format the response for the chat
            answer = result.get("answer", "")
            verified_sources = result.get("verified_sources", [])
            
            # Format sources for display
            sources_text = ""
            if verified_sources:
                sources_text = "\n\n📚 **Verified Sources:**\n"
                for i, src in enumerate(verified_sources[:5], 1):
                    sources_text += f"{i}. [{src.get('title', 'Source')}]({src.get('url', '')})\n"
            
            return {
                "text": answer + sources_text,
                "sources": [s.get("url", "") for s in verified_sources],
                "verified_sources": verified_sources
            }
        except Exception as e:
            logger.error(f"AI search error: {e}")
            return {
                "text": f"I had trouble searching the web. Error: {str(e)}",
                "sources": [],
                "verified_sources": []
            }

    async def search_with_ai(self, query: str) -> Dict[str, Any]:
        """
        Search the web and get AI-generated answer
        Like Perplexity's conversational search
        """
        return await self.ai_search(query, verified_only=False)

    async def verified_search(self, query: str) -> Dict[str, Any]:
        """
        Search only verified/trusted sources
        Returns results from academic, government, and official sources
        """
        return await self.ai_search(query, verified_only=True)

    def get_available_ai_providers(self) -> List[str]:
        """Get list of available AI providers"""
        if not AI_AGGREGATOR_AVAILABLE:
            return []
        return self.ai_aggregator.get_available_providers()

    async def compare_ai_responses(self, query: str) -> Dict[str, Any]:
        """
        Compare responses from multiple AI providers
        Useful for research and verification
        """
        if not AI_AGGREGATOR_AVAILABLE:
            return {
                "text": "AI aggregator is unavailable.",
                "results": {}
            }
        
        return await self.ai_aggregator.compare_providers(query)

    async def fetch_wikipedia_summary(self, query: str) -> str:
        """Fetch a summary from Wikipedia"""
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
            response = requests.get(url, headers={"User-Agent": self.user_agent}, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get("extract", "I found the page but couldn't get a summary.")
            return "I couldn't find any Wikipedia information on that topic."
        except Exception as e:
            logger.error(f"Wikipedia fetch error: {e}")
            return "I had trouble connecting to Wikipedia."

    async def _geocode_location(self, location: str) -> Optional[Dict[str, Any]]:
        """Geocode a location using Nominatim (OpenStreetMap)."""
        nominatim_url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(location)}&format=json&limit=1"
        try:
            response = requests.get(nominatim_url, headers={"User-Agent": self.user_agent}, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data:
                return {
                    "lat": data[0]["lat"],
                    "lon": data[0]["lon"],
                    "display_name": data[0]["display_name"]
                }
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Nominatim geocoding error for '{location}': {e}")
            return None
        except json.JSONDecodeError:
            logger.error(f"Nominatim geocoding JSON decode error for '{location}'")
            return None

    async def get_weather(self, location: str) -> Dict[str, Any]:
        """
        Fetch weather information for a given location using wttr.in and Nominatim for geocoding.
        Returns a dictionary with 'text' and 'sources'.
        """
        weather_info = {"text": "I couldn't fetch weather information for that location.", "sources": []}
        
        try:
            # First, try to geocode the location
            geocoded_location = await self._geocode_location(location)
            
            if geocoded_location:
                # Use coordinates for wttr.in for more precise results
                query_param = f"{geocoded_location['lat']},{geocoded_location['lon']}"
                display_name = geocoded_location['display_name']
            else:
                # Fallback to original location string if geocoding fails
                query_param = urllib.parse.quote(location)
                display_name = location

            # Fetch weather from wttr.in in JSON format
            wttr_url = f"https://wttr.in/{query_param}?format=j1"
            response = requests.get(wttr_url, headers={"User-Agent": self.user_agent}, timeout=10)
            response.raise_for_status() # Raise an exception for HTTP errors
            
            weather_data = response.json()

            if weather_data and 'current_condition' in weather_data:
                current = weather_data['current_condition'][0]
                nearest_area = weather_data['nearest_area'][0] if 'nearest_area' in weather_data else {}
                
                city = nearest_area.get('areaName', [{}])[0].get('value', display_name)
                region = nearest_area.get('region', [{}])[0].get('value', '')
                country = nearest_area.get('country', [{}])[0].get('value', '')

                location_display = f"{city}"
                if region and region != city:
                    location_display += f", {region}"
                if country and country != region and country != city:
                    location_display += f", {country}"

                temp_c = current.get('temp_C')
                temp_f = current.get('temp_F')
                feels_like_c = current.get('FeelsLikeC')
                feels_like_f = current.get('FeelsLikeF')
                weather_desc = current.get('weatherDesc', [{}])[0].get('value', 'N/A')
                humidity = current.get('humidity')
                wind_speed_kmph = current.get('windspeedKmph')
                wind_dir = current.get('winddir16Point')
                pressure = current.get('pressure')

                text_output = (
                    f"Current weather in {location_display}:\n"
                    f"Condition: {weather_desc}\n"
                    f"Temperature: {temp_c}°C ({temp_f}°F)\n"
                    f"Feels like: {feels_like_c}°C ({feels_like_f}°F)\n"
                    f"Humidity: {humidity}%\n"
                    f"Wind: {wind_speed_kmph} km/h {wind_dir}\n"
                    f"Pressure: {pressure} hPa"
                )
                weather_info["text"] = text_output
                weather_info["sources"] = ["https://wttr.in/"]
            else:
                weather_info["text"] = f"I found no detailed weather data for {display_name}."

        except requests.exceptions.RequestException as e:
            logger.error(f"Weather fetch error for '{location}': {e}")
            weather_info["text"] = "I had trouble connecting to the weather service."
        except json.JSONDecodeError:
            logger.error(f"Weather JSON decode error for '{location}'")
            weather_info["text"] = "I received unreadable weather data."
        except Exception as e:
            logger.error(f"An unexpected error occurred during weather fetch for '{location}': {e}")
            weather_info["text"] = "An unexpected error occurred while fetching weather."

        return weather_info

    async def get_weather_full(self, location: str) -> Dict[str, Any]:
        """
        Get structured weather data with lat/lon for map display.
        Uses wttr.in (FREE) + Nominatim OpenStreetMap (FREE).
        """
        try:
            # Geocode first for precise coords
            geocoded = await self._geocode_location(location)
            
            if geocoded:
                query_param = f"{geocoded['lat']},{geocoded['lon']}"
                lat = float(geocoded['lat'])
                lon = float(geocoded['lon'])
            else:
                query_param = urllib.parse.quote(location)
                lat = 27.7172  # Default: Kathmandu
                lon = 85.3240

            wttr_url = f"https://wttr.in/{query_param}?format=j1"
            response = requests.get(wttr_url, headers={"User-Agent": self.user_agent}, timeout=10)
            
            if response.status_code != 200:
                return {"success": False, "error": f"Could not find weather for '{location}'"}

            data = response.json()
            current = data.get("current_condition", [{}])[0]
            nearest_area = data.get("nearest_area", [{}])[0] if data.get("nearest_area") else {}

            area_name = nearest_area.get("areaName", [{}])[0].get("value", location) if nearest_area.get("areaName") else location
            country = nearest_area.get("country", [{}])[0].get("value", "") if nearest_area.get("country") else ""
            region = nearest_area.get("region", [{}])[0].get("value", "") if nearest_area.get("region") else ""
            # Use nominatim lat/lon if available, else wttr.in's nearest_area
            if geocoded:
                lat_str = geocoded['lat']
                lon_str = geocoded['lon']
            else:
                lat_str = nearest_area.get("latitude", str(lat))
                lon_str = nearest_area.get("longitude", str(lon))
                lat = float(lat_str)
                lon = float(lon_str)

            desc_list = current.get("weatherDesc", [{}])
            desc = desc_list[0].get("value", "Unknown") if desc_list else "Unknown"

            return {
                "success": True,
                "location": {
                    "name": area_name,
                    "region": region,
                    "country": country,
                    "display": f"{area_name}, {country}" if country else area_name,
                    "lat": lat,
                    "lon": lon,
                },
                "current": {
                    "temp_c": current.get("temp_C", "N/A"),
                    "temp_f": current.get("temp_F", "N/A"),
                    "feels_like_c": current.get("FeelsLikeC", "N/A"),
                    "humidity": current.get("humidity", "N/A"),
                    "wind_kmph": current.get("windspeedKmph", "N/A"),
                    "wind_dir": current.get("winddir16Point", "N/A"),
                    "description": desc,
                    "uv_index": current.get("uvIndex", "N/A"),
                    "visibility": current.get("visibility", "N/A"),
                    "pressure": current.get("pressure", "N/A"),
                    "cloud_cover": current.get("cloudcover", "N/A"),
                    "precip_mm": current.get("precipMM", "0"),
                },
                "map_url": f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=10/{lat}/{lon}",
                "embed_map_url": (
                    f"https://www.openstreetmap.org/export/embed.html"
                    f"?bbox={lon-0.5},{lat-0.5},{lon+0.5},{lat+0.5}"
                    f"&layer=mapnik&marker={lat},{lon}"
                ),
            }

        except Exception as e:
            logger.error(f"get_weather_full error for '{location}': {e}")
            return {"success": False, "error": str(e)}

    async def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """
        Convert currency from one to another.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code (e.g., 'USD', 'EUR')
            to_currency: Target currency code (e.g., 'INR', 'NPR')
            
        Returns:
            Dictionary with conversion result
        """
        if not self.currency_converter:
            return {
                "success": False,
                "error": "Currency converter is not available"
            }
        
        try:
            result = self.currency_converter.convert(amount, from_currency, to_currency)
            return result
        except Exception as e:
            logger.error(f"Currency conversion error: {e}")
            return {
                "success": False,
                "error": f"Failed to convert currency: {str(e)}"
            }

    async def get_exchange_rates(self, base_currency: str = "USD") -> Dict[str, Any]:
        """
        Get all exchange rates for a base currency.
        
        Args:
            base_currency: Base currency code (default: 'USD')
            
        Returns:
            Dictionary with all exchange rates
        """
        if not self.currency_converter:
            return {
                "success": False,
                "error": "Currency converter is not available"
            }
        
        try:
            result = self.currency_converter.get_all_rates(base_currency)
            return result
        except Exception as e:
            logger.error(f"Get exchange rates error: {e}")
            return {
                "success": False,
                "error": f"Failed to get exchange rates: {str(e)}"
            }

    async def get_supported_currencies(self) -> Dict[str, Any]:
        """
        Get list of supported currencies.
        
        Returns:
            Dictionary of supported currency codes and names
        """
        if not self.currency_converter:
            return {
                "success": False,
                "error": "Currency converter is not available"
            }
        
        try:
            currencies = self.currency_converter.get_supported_currencies()
            return {
                "success": True,
                "currencies": currencies
            }
        except Exception as e:
            logger.error(f"Get supported currencies error: {e}")
            return {
                "success": False,
                "error": f"Failed to get supported currencies: {str(e)}"
            }

    async def generate_image(self, prompt: str) -> Dict[str, Any]:
        """Generate an image using Pollinations.ai"""
        try:
            # Clean and encode the prompt
            encoded_prompt = urllib.parse.quote(prompt.strip())
            seed = random.randint(1, 1000000)
            
            # Use configurations from .env
            model = os.getenv("IMAGE_GENERATION_MODEL", "flux")
            width = os.getenv("IMAGE_GENERATION_WIDTH", "1024")
            height = os.getenv("IMAGE_GENERATION_HEIGHT", "1024")
            
            # Pollinations.ai URL format
            image_url = f"https://pollinations.ai/p/{encoded_prompt}?width={width}&height={height}&seed={seed}&model={model}"
            
            return {
                "url": image_url,
                "text": f"I've generated an image for you: {prompt}",
                "prompt": prompt
            }
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            return {"text": "I had trouble generating that image.", "url": None}

    async def translate(
        self, text: str, source: str = "auto", target: str = "en"
    ) -> Dict[str, Any]:
        """
        Translate text from source language to target language.
        Uses free MyMemory API with LibreTranslate fallback.
        """
        if not TRANSLATOR_AVAILABLE:
            return {
                "success": False,
                "original_text": text,
                "translated_text": "",
                "source_lang": source,
                "target_lang": target,
                "detected_lang": "unknown",
                "error": "Translation service is not available.",
            }

        try:
            result = await translator_manager.translate(text, source, target)
            return result
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return {
                "success": False,
                "original_text": text,
                "translated_text": "",
                "source_lang": source,
                "target_lang": target,
                "detected_lang": "unknown",
                "error": f"Translation failed: {str(e)}",
            }

    async def get_supported_languages(self) -> List[Dict]:
        """Get list of supported languages for translation"""
        if not TRANSLATOR_AVAILABLE:
            return []
        return translator_manager.get_supported_languages()

    async def detect_language(self, text: str) -> str:
        """Detect the language of the input text"""
        if not TRANSLATOR_AVAILABLE:
            return "en"
        return translator_manager.detect_language(text)

    # ============== Calendar Methods ==============
    
    async def add_calendar_event(
        self, 
        title: str, 
        description: str = "", 
        date: str = None, 
        time: str = "00:00", 
        event_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Add a new event to the calendar.
        
        Args:
            title: Event title
            description: Event description (optional)
            date: Date in "YYYY-MM-DD" format (optional, defaults to today)
            time: Time in "HH:MM" or "HH:MM AM/PM" format (optional)
            event_type: Type of event (exam, assignment, reminder, general)
        
        Returns:
            Dictionary containing the created event or error message
        """
        if not CALENDAR_AVAILABLE:
            return {
                "success": False,
                "error": "Calendar service is not available."
            }
        
        try:
            # Default to today's date if not provided
            if not date:
                from datetime import datetime
                date = datetime.now().strftime("%Y-%m-%d")
            
            event = calendar_manager.add_event(
                title=title,
                description=description,
                date=date,
                time=time,
                event_type=event_type
            )
            
            return {
                "success": True,
                "message": f"Event '{title}' added for {date} at {time}",
                "event": event
            }
        except Exception as e:
            logger.error(f"Error adding calendar event: {e}")
            return {
                "success": False,
                "error": f"Failed to add event: {str(e)}"
            }
    
    async def get_calendar_events(
        self, 
        date: str = None, 
        upcoming: int = 7
    ) -> Dict[str, Any]:
        """
        Get calendar events for a specific date or upcoming days.
        
        Args:
            date: Specific date in "YYYY-MM-DD" format (optional)
            upcoming: Number of upcoming days to fetch if no date specified
        
        Returns:
            Dictionary containing list of events
        """
        if not CALENDAR_AVAILABLE:
            return {
                "success": False,
                "events": [],
                "error": "Calendar service is not available."
            }
        
        try:
            events = calendar_manager.get_events(date=date, upcoming=upcoming)
            
            return {
                "success": True,
                "events": events,
                "count": len(events)
            }
        except Exception as e:
            logger.error(f"Error getting calendar events: {e}")
            return {
                "success": False,
                "events": [],
                "error": f"Failed to get events: {str(e)}"
            }
    
    async def get_today_events(self) -> Dict[str, Any]:
        """
        Get today's calendar events.
        
        Returns:
            Dictionary containing list of today's events
        """
        if not CALENDAR_AVAILABLE:
            return {
                "success": False,
                "events": [],
                "error": "Calendar service is not available."
            }
        
        try:
            events = calendar_manager.get_today_events()
            
            return {
                "success": True,
                "events": events,
                "count": len(events),
                "date": events[0]["date"] if events else None
            }
        except Exception as e:
            logger.error(f"Error getting today's events: {e}")
            return {
                "success": False,
                "events": [],
                "error": f"Failed to get today's events: {str(e)}"
            }
    
    async def delete_calendar_event(self, event_id: int) -> Dict[str, Any]:
        """
        Delete a calendar event by ID.
        
        Args:
            event_id: ID of the event to delete
        
        Returns:
            Dictionary indicating success or failure
        """
        if not CALENDAR_AVAILABLE:
            return {
                "success": False,
                "error": "Calendar service is not available."
            }
        
        try:
            success = calendar_manager.delete_event(event_id)
            
            if success:
                return {
                    "success": True,
                    "message": f"Event {event_id} deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Event {event_id} not found"
                }
        except Exception as e:
            logger.error(f"Error deleting calendar event: {e}")
            return {
                "success": False,
                "error": f"Failed to delete event: {str(e)}"
            }
    
    async def set_event_reminder(
        self, 
        event_id: int, 
        minutes_before: int = 30
    ) -> Dict[str, Any]:
        """
        Set a reminder for an event.
        
        Args:
            event_id: ID of the event
            minutes_before: Minutes before event to trigger reminder
        
        Returns:
            Dictionary indicating success or failure
        """
        if not CALENDAR_AVAILABLE:
            return {
                "success": False,
                "error": "Calendar service is not available."
            }
        
        try:
            success = calendar_manager.set_reminder(event_id, minutes_before)
            
            if success:
                return {
                    "success": True,
                    "message": f"Reminder set for event {event_id}: {minutes_before} minutes before"
                }
            else:
                return {
                    "success": False,
                    "error": f"Event {event_id} not found"
                }
        except Exception as e:
            logger.error(f"Error setting reminder: {e}")
            return {
                "success": False,
                "error": f"Failed to set reminder: {str(e)}"
            }
    
    async def get_calendar_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the calendar.
        
        Returns:
            Dictionary containing calendar statistics
        """
        if not CALENDAR_AVAILABLE:
            return {
                "success": False,
                "error": "Calendar service is not available."
            }
        
        try:
            summary = calendar_manager.get_calendar_summary()
            
            return {
                "success": True,
                "summary": summary
            }
        except Exception as e:
            logger.error(f"Error getting calendar summary: {e}")
            return {
                "success": False,
                "error": f"Failed to get summary: {str(e)}"
            }

    # ============== Flashcard Methods ==============

    async def create_flashcard_deck(
        self, 
        name: str, 
        description: str = "", 
        category: str = "general"
    ) -> Dict[str, Any]:
        """
        Create a new flashcard deck.
        
        Args:
            name: Name of the deck
            description: Optional description
            category: Category (language, science, math, history, general)
        
        Returns:
            Dictionary containing the created deck
        """
        if not FLASHCARDS_AVAILABLE:
            return {
                "success": False,
                "error": "Flashcard service is not available."
            }
        
        try:
            result = flashcard_manager.create_deck(name, description, category)
            return result
        except Exception as e:
            logger.error(f"Error creating flashcard deck: {e}")
            return {
                "success": False,
                "error": f"Failed to create deck: {str(e)}"
            }

    async def add_flashcard(
        self, 
        deck_id: int, 
        front: str, 
        back: str
    ) -> Dict[str, Any]:
        """
        Add a flashcard to a deck.
        
        Args:
            deck_id: ID of the deck
            front: Front side (question/term)
            back: Back side (answer/definition)
        
        Returns:
            Dictionary containing the created card
        """
        if not FLASHCARDS_AVAILABLE:
            return {
                "success": False,
                "error": "Flashcard service is not available."
            }
        
        try:
            result = flashcard_manager.add_card(deck_id, front, back)
            return result
        except Exception as e:
            logger.error(f"Error adding flashcard: {e}")
            return {
                "success": False,
                "error": f"Failed to add card: {str(e)}"
            }

    async def get_flashcard_decks(self) -> Dict[str, Any]:
        """
        Get all flashcard decks.
        
        Returns:
            Dictionary containing list of decks
        """
        if not FLASHCARDS_AVAILABLE:
            return {
                "success": False,
                "error": "Flashcard service is not available.",
                "decks": []
            }
        
        try:
            result = flashcard_manager.get_all_decks()
            return result
        except Exception as e:
            logger.error(f"Error getting flashcard decks: {e}")
            return {
                "success": False,
                "error": f"Failed to get decks: {str(e)}",
                "decks": []
            }

    async def get_flashcard_deck(self, deck_id: int) -> Dict[str, Any]:
        """
        Get a specific flashcard deck with all cards.
        
        Args:
            deck_id: ID of the deck
        
        Returns:
            Dictionary containing deck details
        """
        if not FLASHCARDS_AVAILABLE:
            return {
                "success": False,
                "error": "Flashcard service is not available."
            }
        
        try:
            result = flashcard_manager.get_deck(deck_id)
            return result
        except Exception as e:
            logger.error(f"Error getting flashcard deck: {e}")
            return {
                "success": False,
                "error": f"Failed to get deck: {str(e)}"
            }

    async def study_flashcards(
        self, 
        deck_id: int, 
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get cards from a deck for studying.
        
        Args:
            deck_id: ID of the deck to study
            limit: Maximum number of cards to return
        
        Returns:
            Dictionary containing cards for studying
        """
        if not FLASHCARDS_AVAILABLE:
            return {
                "success": False,
                "error": "Flashcard service is not available."
            }
        
        try:
            result = flashcard_manager.study_deck(deck_id, limit)
            return result
        except Exception as e:
            logger.error(f"Error studying flashcards: {e}")
            return {
                "success": False,
                "error": f"Failed to study deck: {str(e)}"
            }

    async def mark_flashcard_known(
        self, 
        deck_id: int, 
        card_id: int
    ) -> Dict[str, Any]:
        """
        Mark a flashcard as known.
        
        Args:
            deck_id: ID of the deck
            card_id: ID of the card
        
        Returns:
            Dictionary indicating success or failure
        """
        if not FLASHCARDS_AVAILABLE:
            return {
                "success": False,
                "error": "Flashcard service is not available."
            }
        
        try:
            success = flashcard_manager.mark_known(deck_id, card_id)
            if success:
                return {
                    "success": True,
                    "message": "Card marked as known"
                }
            return {
                "success": False,
                "error": "Card not found"
            }
        except Exception as e:
            logger.error(f"Error marking flashcard known: {e}")
            return {
                "success": False,
                "error": f"Failed to mark card: {str(e)}"
            }

    async def delete_flashcard_deck(self, deck_id: int) -> Dict[str, Any]:
        """
        Delete a flashcard deck.
        
        Args:
            deck_id: ID of the deck to delete
        
        Returns:
            Dictionary indicating success or failure
        """
        if not FLASHCARDS_AVAILABLE:
            return {
                "success": False,
                "error": "Flashcard service is not available."
            }
        
        try:
            success = flashcard_manager.delete_deck(deck_id)
            if success:
                return {
                    "success": True,
                    "message": f"Deck {deck_id} deleted successfully"
                }
            return {
                "success": False,
                "error": f"Deck {deck_id} not found"
            }
        except Exception as e:
            logger.error(f"Error deleting flashcard deck: {e}")
            return {
                "success": False,
                "error": f"Failed to delete deck: {str(e)}"
            }

    async def search_flashcard_decks(self, query: str) -> Dict[str, Any]:
        """
        Search flashcard decks by name, description, or category.
        
        Args:
            query: Search query
        
        Returns:
            Dictionary containing search results
        """
        if not FLASHCARDS_AVAILABLE:
            return {
                "success": False,
                "error": "Flashcard service is not available.",
                "results": []
            }
        
        try:
            result = flashcard_manager.search_decks(query)
            return result
        except Exception as e:
            logger.error(f"Error searching flashcard decks: {e}")
            return {
                "success": False,
                "error": f"Failed to search: {str(e)}",
                "results": []
            }

    async def get_flashcard_stats(self, deck_id: int) -> Dict[str, Any]:
        """
        Get statistics for a flashcard deck.
        
        Args:
            deck_id: ID of the deck
        
        Returns:
            Dictionary containing deck statistics
        """
        if not FLASHCARDS_AVAILABLE:
            return {
                "success": False,
                "error": "Flashcard service is not available."
            }
        
        try:
            result = flashcard_manager.get_deck_stats(deck_id)
            return result
        except Exception as e:
            logger.error(f"Error getting flashcard stats: {e}")
            return {
                "success": False,
                "error": f"Failed to get stats: {str(e)}"
            }

    # ============== News Methods ==============

    async def get_latest_news(
        self, 
        category: str = None, 
        country: str = "us", 
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get the latest news headlines.
        
        Args:
            category: Category of news (technology, business, sports, etc.)
            country: Country code (us, in, np, uk, etc.)
            limit: Maximum number of results (max 250)
        
        Returns:
            Dictionary containing news articles in specified format
        """
        if not NEWS_AVAILABLE:
            return {
                "success": False,
                "total_results": 0,
                "articles": [],
                "error": "News service is not available."
            }
        
        try:
            result = news_manager.get_latest_news(category, country, limit)
            return result
        except Exception as e:
            logger.error(f"Error getting latest news: {e}")
            return {
                "success": False,
                "total_results": 0,
                "articles": [],
                "error": f"Failed to get news: {str(e)}"
            }

    async def search_news(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search news by keyword.
        
        Args:
            query: Search query string
            limit: Maximum number of results
        
        Returns:
            Dictionary containing news articles in specified format
        """
        if not NEWS_AVAILABLE:
            return {
                "success": False,
                "total_results": 0,
                "articles": [],
                "error": "News service is not available."
            }
        
        try:
            result = news_manager.search_news(query, limit)
            return result
        except Exception as e:
            logger.error(f"Error searching news: {e}")
            return {
                "success": False,
                "total_results": 0,
                "articles": [],
                "error": f"Failed to search news: {str(e)}"
            }

    async def get_news_by_source(self, source: str, limit: int = 10) -> Dict[str, Any]:
        """
        Get news from a specific source.
        
        Args:
            source: News source name (e.g., "BBC", "CNN", "Reuters")
            limit: Maximum number of results
        
        Returns:
            Dictionary containing news articles in specified format
        """
        if not NEWS_AVAILABLE:
            return {
                "success": False,
                "total_results": 0,
                "articles": [],
                "error": "News service is not available."
            }
        
        try:
            result = news_manager.get_news_by_source(source, limit)
            return result
        except Exception as e:
            logger.error(f"Error getting news by source: {e}")
            return {
                "success": False,
                "total_results": 0,
                "articles": [],
                "error": f"Failed to get news by source: {str(e)}"
            }

    async def get_trending_topics(self) -> Dict[str, Any]:
        """
        Get trending topics.
        
        Returns:
            Dictionary containing list of trending topics
        """
        if not NEWS_AVAILABLE:
            return {
                "success": False,
                "topics": [],
                "error": "News service is not available."
            }
        
        try:
            topics = news_manager.get_trending_topics()
            return {
                "success": True,
                "topics": topics
            }
        except Exception as e:
            logger.error(f"Error getting trending topics: {e}")
            return {
                "success": False,
                "topics": [],
                "error": f"Failed to get trending topics: {str(e)}"
            }

    async def execute_code(self, code: str, language: str, args: List[str] = None) -> Dict[str, Any]:
        """
        Execute code in the specified programming language using Piston API.
        
        Args:
            code: Source code to execute
            language: Programming language (python, javascript, java, c, cpp, go, rust, ruby, php, typescript, etc.)
            args: Optional command-line arguments
            
        Returns:
            Dictionary containing:
                - success: bool - Whether execution was successful
                - language: str - Language used
                - version: str - Language version
                - output: str - Standard output
                - stderr: str - Standard error
                - code: str - The executed code
                - error: str - Error message if any
        """
        if not CODE_EXECUTOR_AVAILABLE:
            return {
                "success": False,
                "language": language,
                "version": "",
                "output": "",
                "stderr": "",
                "code": code,
                "error": "Code executor is not available"
            }
        
        try:
            result = code_executor.execute(code, language, args)
            return result
        except Exception as e:
            logger.error(f"Error executing code: {e}")
            return {
                "success": False,
                "language": language,
                "version": "",
                "output": "",
                "stderr": "",
                "code": code,
                "error": f"Code execution failed: {str(e)}"
            }

    async def get_code_supported_languages(self) -> List[Dict[str, Any]]:
        """
        Get list of supported programming languages for code execution.
        
        Returns:
            List of dictionaries containing language name and version
        """
        if not CODE_EXECUTOR_AVAILABLE:
            return []
        
        try:
            return code_executor.get_supported_languages()
        except Exception as e:
            logger.error(f"Error getting supported languages: {e}")
            return []

    # ============== Calculator Methods ==============

    async def calculate(self, expression: str) -> Dict[str, Any]:
        """
        Evaluate a mathematical expression.
        
        Args:
            expression: Mathematical expression (e.g., "2 + 2", "sqrt(16)", "sin(pi/2)")
        
        Returns:
            Dictionary containing the result and expression info
        """
        if not CALCULATOR_AVAILABLE:
            return {
                "success": False,
                "expression": expression,
                "error": "Calculator service is not available.",
                "type": "error"
            }
        
        try:
            result = await calculator_manager.calculate(expression)
            return result
        except Exception as e:
            logger.error(f"Error calculating expression: {e}")
            return {
                "success": False,
                "expression": expression,
                "error": f"Calculation failed: {str(e)}",
                "type": "error"
            }

    async def solve_equation(self, equation: str) -> Dict[str, Any]:
        """
        Solve a simple equation (linear or quadratic).
        
        Args:
            equation: Equation to solve (e.g., "2x + 5 = 15", "x^2 - 5x + 6 = 0")
        
        Returns:
            Dictionary containing the solution(s)
        """
        if not CALCULATOR_AVAILABLE:
            return {
                "success": False,
                "equation": equation,
                "error": "Calculator service is not available.",
                "type": "error"
            }
        
        try:
            result = await calculator_manager.solve_equation(equation)
            return result
        except Exception as e:
            logger.error(f"Error solving equation: {e}")
            return {
                "success": False,
                "equation": equation,
                "error": f"Equation solving failed: {str(e)}",
                "type": "error"
            }

    async def calculate_tip(self, amount: float, percentage: float) -> Dict[str, Any]:
        """
        Calculate tip amount and total.
        
        Args:
            amount: Bill amount
            percentage: Tip percentage (e.g., 15 for 15%)
        
        Returns:
            Dictionary containing tip amount and total
        """
        if not CALCULATOR_AVAILABLE:
            return {
                "success": False,
                "error": "Calculator service is not available.",
                "type": "error"
            }
        
        try:
            result = await calculator_manager.calculate_tip(amount, percentage)
            return result
        except Exception as e:
            logger.error(f"Error calculating tip: {e}")
            return {
                "success": False,
                "error": f"Tip calculation failed: {str(e)}",
                "type": "error"
            }

    async def convert_units(self, value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
        """
        Convert between different units.
        
        Args:
            value: Numeric value to convert
            from_unit: Source unit (e.g., "km", "miles", "kg", "celsius")
            to_unit: Target unit (e.g., "miles", "km", "lbs", "fahrenheit")
        
        Returns:
            Dictionary containing converted value
        """
        if not CALCULATOR_AVAILABLE:
            return {
                "success": False,
                "error": "Calculator service is not available.",
                "type": "error"
            }
        
        try:
            result = await calculator_manager.convert_units(value, from_unit, to_unit)
            return result
        except Exception as e:
            logger.error(f"Error converting units: {e}")
            return {
                "success": False,
                "error": f"Unit conversion failed: {str(e)}",
                "type": "error"
            }

    async def calculate_percentage(self, value: float, percentage: float) -> Dict[str, Any]:
        """
        Calculate percentage of a value.
        
        Args:
            value: The base value
            percentage: The percentage to calculate (e.g., 20 for 20%)
        
        Returns:
            Dictionary containing the calculated percentage
        """
        if not CALCULATOR_AVAILABLE:
            return {
                "success": False,
                "error": "Calculator service is not available.",
                "type": "error"
            }
        
        try:
            result = await calculator_manager.calculate_percentage(value, percentage)
            return result
        except Exception as e:
            logger.error(f"Error calculating percentage: {e}")
            return {
                "success": False,
                "error": f"Percentage calculation failed: {str(e)}",
                "type": "error"
            }

    async def get_math_help(self, topic: str) -> Dict[str, Any]:
        """
        Get math formulas and help for a topic.
        
        Args:
            topic: Topic to get help on (e.g., "area", "trigonometry", "quadratic")
        
        Returns:
            Dictionary containing formulas and explanations
        """
        if not CALCULATOR_AVAILABLE:
            return {
                "success": False,
                "error": "Calculator service is not available.",
                "type": "error"
            }
        
        try:
            result = await calculator_manager.get_math_help(topic)
            return result
        except Exception as e:
            logger.error(f"Error getting math help: {e}")
            return {
                "success": False,
                "error": f"Math help failed: {str(e)}",
                "type": "error"
            }

    async def get_available_conversions(self) -> Dict[str, Any]:
        """
        Get list of available unit conversions.
        
        Returns:
            Dictionary containing available conversion categories
        """
        if not CALCULATOR_AVAILABLE:
            return {
                "success": False,
                "error": "Calculator service is not available.",
                "type": "error"
            }
        
        try:
            result = await calculator_manager.get_available_conversions()
            return result
        except Exception as e:
            logger.error(f"Error getting conversions: {e}")
            return {
                "success": False,
                "error": f"Failed to get conversions: {str(e)}",
                "type": "error"
            }

    # ============== Dictionary Methods ==============

    async def define_word(self, word: str) -> Dict[str, Any]:
        """
        Get the definition, pronunciation, part of speech, and examples for a word.
        
        Args:
            word: The word to look up
        
        Returns:
            Dictionary containing word definition information
        """
        if not DICTIONARY_AVAILABLE:
            return {
                "success": False,
                "word": word,
                "error": "Dictionary service is not available."
            }
        
        try:
            result = await dictionary_manager.define(word)
            return result
        except Exception as e:
            logger.error(f"Error defining word '{word}': {e}")
            return {
                "success": False,
                "word": word,
                "error": f"Definition lookup failed: {str(e)}"
            }

    async def get_synonyms(self, word: str) -> Dict[str, Any]:
        """
        Get synonyms for a word.
        
        Args:
            word: The word to find synonyms for
        
        Returns:
            Dictionary containing list of synonyms
        """
        if not DICTIONARY_AVAILABLE:
            return {
                "success": False,
                "word": word,
                "error": "Dictionary service is not available.",
                "synonyms": []
            }
        
        try:
            synonyms = await dictionary_manager.get_synonyms(word)
            return {
                "success": True,
                "word": word,
                "synonyms": synonyms
            }
        except Exception as e:
            logger.error(f"Error getting synonyms for '{word}': {e}")
            return {
                "success": False,
                "word": word,
                "error": f"Synonym lookup failed: {str(e)}",
                "synonyms": []
            }

    async def get_antonyms(self, word: str) -> Dict[str, Any]:
        """
        Get antonyms for a word.
        
        Args:
            word: The word to find antonyms for
        
        Returns:
            Dictionary containing list of antonyms
        """
        if not DICTIONARY_AVAILABLE:
            return {
                "success": False,
                "word": word,
                "error": "Dictionary service is not available.",
                "antonyms": []
            }
        
        try:
            antonyms = await dictionary_manager.get_antonyms(word)
            return {
                "success": True,
                "word": word,
                "antonyms": antonyms
            }
        except Exception as e:
            logger.error(f"Error getting antonyms for '{word}': {e}")
            return {
                "success": False,
                "word": word,
                "error": f"Antonym lookup failed: {str(e)}",
                "antonyms": []
            }

    async def get_word_info(self, word: str) -> Dict[str, Any]:
        """
        Get complete word information including definitions, synonyms, and antonyms.
        
        Args:
            word: The word to look up
        
        Returns:
            Dictionary containing complete word information
        """
        if not DICTIONARY_AVAILABLE:
            return {
                "success": False,
                "word": word,
                "error": "Dictionary service is not available."
            }
        
        try:
            result = await dictionary_manager.get_word_info(word)
            return result
        except Exception as e:
            logger.error(f"Error getting word info for '{word}': {e}")
            return {
                "success": False,
                "word": word,
                "error": f"Word lookup failed: {str(e)}"
            }

    async def search_words(self, prefix: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search for words starting with a given prefix.
        
        Args:
            prefix: The prefix to search for
            limit: Maximum number of results (default 10)
        
        Returns:
            Dictionary containing list of matching words
        """
        if not DICTIONARY_AVAILABLE:
            return {
                "success": False,
                "prefix": prefix,
                "error": "Dictionary service is not available.",
                "words": []
            }
        
        try:
            words = await dictionary_manager.search_words(prefix, limit)
            return {
                "success": True,
                "prefix": prefix,
                "words": words
            }
        except Exception as e:
            logger.error(f"Error searching words for prefix '{prefix}': {e}")
            return {
                "success": False,
                "prefix": prefix,
                "error": f"Word search failed: {str(e)}",
                "words": []
            }

    # ============== Recipe Methods ==============

    async def search_recipes(self, query: str) -> Dict[str, Any]:
        """
        Search for recipes by name or ingredient.
        
        Args:
            query: The dish name or ingredient to search for
        
        Returns:
            Dictionary containing search results with recipes
        """
        if not RECIPE_AVAILABLE:
            return {
                "success": False,
                "error": "Recipe service is not available.",
                "total_results": 0,
                "recipes": []
            }
        
        try:
            # First try searching by name
            result = await recipe_manager.search_by_name(query)
            
            # If no results, try searching by ingredient
            if not result.get("recipes") or len(result.get("recipes", [])) == 0:
                result = await recipe_manager.search_by_ingredient(query)
            
            return result
        except Exception as e:
            logger.error(f"Error searching recipes for '{query}': {e}")
            return {
                "success": False,
                "error": f"Recipe search failed: {str(e)}",
                "total_results": 0,
                "recipes": []
            }

    async def search_recipes_by_name(self, name: str) -> Dict[str, Any]:
        """
        Search for recipes by dish name.
        
        Args:
            name: The dish name to search for
        
        Returns:
            Dictionary containing matching recipes
        """
        if not RECIPE_AVAILABLE:
            return {
                "success": False,
                "error": "Recipe service is not available.",
                "total_results": 0,
                "recipes": []
            }
        
        try:
            result = await recipe_manager.search_by_name(name)
            return result
        except Exception as e:
            logger.error(f"Error searching recipes by name '{name}': {e}")
            return {
                "success": False,
                "error": f"Recipe search failed: {str(e)}",
                "total_results": 0,
                "recipes": []
            }

    async def search_recipes_by_ingredient(self, ingredient: str) -> Dict[str, Any]:
        """
        Find recipes by ingredient.
        
        Args:
            ingredient: The ingredient to search by
        
        Returns:
            Dictionary containing recipes with that ingredient
        """
        if not RECIPE_AVAILABLE:
            return {
                "success": False,
                "error": "Recipe service is not available.",
                "total_results": 0,
                "recipes": []
            }
        
        try:
            result = await recipe_manager.search_by_ingredient(ingredient)
            return result
        except Exception as e:
            logger.error(f"Error searching recipes by ingredient '{ingredient}': {e}")
            return {
                "success": False,
                "error": f"Recipe search failed: {str(e)}",
                "total_results": 0,
                "recipes": []
            }

    async def get_random_recipe(self) -> Dict[str, Any]:
        """
        Get a random recipe.
        
        Returns:
            Dictionary containing a random recipe
        """
        if not RECIPE_AVAILABLE:
            return {
                "success": False,
                "error": "Recipe service is not available.",
                "total_results": 0,
                "recipes": []
            }
        
        try:
            result = await recipe_manager.get_random_recipe()
            return result
        except Exception as e:
            logger.error(f"Error getting random recipe: {e}")
            return {
                "success": False,
                "error": f"Failed to get random recipe: {str(e)}",
                "total_results": 0,
                "recipes": []
            }

    async def get_recipe_details(self, recipe_id: str) -> Dict[str, Any]:
        """
        Get full recipe details by ID.
        
        Args:
            recipe_id: The recipe ID to lookup
        
        Returns:
            Dictionary containing full recipe details
        """
        if not RECIPE_AVAILABLE:
            return {
                "success": False,
                "error": "Recipe service is not available.",
                "total_results": 0,
                "recipes": []
            }
        
        try:
            result = await recipe_manager.get_recipe_details(recipe_id)
            return result
        except Exception as e:
            logger.error(f"Error getting recipe details for ID '{recipe_id}': {e}")
            return {
                "success": False,
                "error": f"Failed to get recipe details: {str(e)}",
                "total_results": 0,
                "recipes": []
            }

    async def get_recipe_categories(self) -> Dict[str, Any]:
        """
        Get all recipe categories.
        
        Returns:
            Dictionary containing all categories
        """
        if not RECIPE_AVAILABLE:
            return {
                "success": False,
                "error": "Recipe service is not available.",
                "total_results": 0,
                "categories": []
            }
        
        try:
            result = await recipe_manager.get_categories()
            return result
        except Exception as e:
            logger.error(f"Error getting recipe categories: {e}")
            return {
                "success": False,
                "error": f"Failed to get categories: {str(e)}",
                "total_results": 0,
                "categories": []
            }

    async def get_recipes_by_category(self, category: str) -> Dict[str, Any]:
        """
        Get recipes by category.
        
        Args:
            category: The category to filter by
        
        Returns:
            Dictionary containing recipes in that category
        """
        if not RECIPE_AVAILABLE:
            return {
                "success": False,
                "error": "Recipe service is not available.",
                "total_results": 0,
                "recipes": []
            }
        
        try:
            result = await recipe_manager.get_recipes_by_category(category)
            return result
        except Exception as e:
            logger.error(f"Error getting recipes for category '{category}': {e}")
            return {
                "success": False,
                "error": f"Failed to get recipes: {str(e)}",
                "total_results": 0,
                "recipes": []
            }

    # ============== YouTube Methods ==============

    async def search_youtube(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search for YouTube videos.
        
        Args:
            query: Search query
            limit: Maximum number of results (default 10)
        
        Returns:
            Dictionary containing search results
        """
        if not YOUTUBE_AVAILABLE or not self.youtube_manager:
            return {
                "success": False,
                "error": "YouTube service is not available.",
                "videos": []
            }
        
        try:
            videos = await self.youtube_manager.search_videos(query, limit)
            return {
                "success": True,
                "query": query,
                "videos": videos
            }
        except Exception as e:
            logger.error(f"Error searching YouTube: {e}")
            return {
                "success": False,
                "error": f"YouTube search failed: {str(e)}",
                "videos": []
            }

    async def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a YouTube video.
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            Dictionary containing video information
        """
        if not YOUTUBE_AVAILABLE or not self.youtube_manager:
            return {
                "success": False,
                "error": "YouTube service is not available."
            }
        
        try:
            video_info = await self.youtube_manager.get_video_info(video_id)
            if video_info:
                return {
                    "success": True,
                    "video": video_info
                }
            return {
                "success": False,
                "error": "Video not found"
            }
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return {
                "success": False,
                "error": f"Failed to get video info: {str(e)}"
            }

    async def get_trending_videos(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get trending YouTube videos.
        
        Args:
            limit: Maximum number of results (default 10)
        
        Returns:
            Dictionary containing trending videos
        """
        if not YOUTUBE_AVAILABLE or not self.youtube_manager:
            return {
                "success": False,
                "error": "YouTube service is not available.",
                "videos": []
            }
        
        try:
            videos = await self.youtube_manager.get_trending(limit)
            return {
                "success": True,
                "videos": videos
            }
        except Exception as e:
            logger.error(f"Error getting trending videos: {e}")
            return {
                "success": False,
                "error": f"Failed to get trending: {str(e)}",
                "videos": []
            }

    # ============== Notes Methods ==============

    async def create_note(self, title: str, content: str, tags: List[str] = None) -> Dict[str, Any]:
        """
        Create a new note.
        
        Args:
            title: Note title
            content: Note content
            tags: Optional list of tags
        
        Returns:
            Dictionary containing the created note
        """
        if not NOTES_AVAILABLE:
            return {
                "success": False,
                "error": "Notes service is not available."
            }
        
        try:
            result = notes_manager.create_note(title, content, tags)
            return result
        except Exception as e:
            logger.error(f"Error creating note: {e}")
            return {
                "success": False,
                "error": f"Failed to create note: {str(e)}"
            }

    async def get_notes(self, limit: int = None) -> Dict[str, Any]:
        """
        Get all notes.
        
        Args:
            limit: Optional limit on number of notes
        
        Returns:
            Dictionary containing notes
        """
        if not NOTES_AVAILABLE:
            return {
                "success": False,
                "error": "Notes service is not available.",
                "notes": []
            }
        
        try:
            notes = notes_manager.get_notes(limit)
            return {
                "success": True,
                "notes": notes,
                "count": len(notes)
            }
        except Exception as e:
            logger.error(f"Error getting notes: {e}")
            return {
                "success": False,
                "error": f"Failed to get notes: {str(e)}",
                "notes": []
            }

    async def get_note(self, note_id: str) -> Dict[str, Any]:
        """
        Get a specific note by ID.
        
        Args:
            note_id: Note ID
        
        Returns:
            Dictionary containing the note
        """
        if not NOTES_AVAILABLE:
            return {
                "success": False,
                "error": "Notes service is not available."
            }
        
        try:
            note = notes_manager.get_note(note_id)
            if note:
                return {
                    "success": True,
                    "note": note
                }
            return {
                "success": False,
                "error": "Note not found"
            }
        except Exception as e:
            logger.error(f"Error getting note: {e}")
            return {
                "success": False,
                "error": f"Failed to get note: {str(e)}"
            }

    async def update_note(self, note_id: str, title: str = None, content: str = None, 
                          tags: List[str] = None) -> Dict[str, Any]:
        """
        Update an existing note.
        
        Args:
            note_id: Note ID
            title: New title (optional)
            content: New content (optional)
            tags: New tags (optional)
        
        Returns:
            Dictionary containing the updated note
        """
        if not NOTES_AVAILABLE:
            return {
                "success": False,
                "error": "Notes service is not available."
            }
        
        try:
            note = notes_manager.update_note(note_id, title, content, tags)
            if note:
                return {
                    "success": True,
                    "note": note
                }
            return {
                "success": False,
                "error": "Note not found"
            }
        except Exception as e:
            logger.error(f"Error updating note: {e}")
            return {
                "success": False,
                "error": f"Failed to update note: {str(e)}"
            }

    async def delete_note(self, note_id: str) -> Dict[str, Any]:
        """
        Delete a note.
        
        Args:
            note_id: Note ID
        
        Returns:
            Dictionary indicating success or failure
        """
        if not NOTES_AVAILABLE:
            return {
                "success": False,
                "error": "Notes service is not available."
            }
        
        try:
            success = notes_manager.delete_note(note_id)
            return {
                "success": success,
                "message": "Note deleted" if success else "Note not found"
            }
        except Exception as e:
            logger.error(f"Error deleting note: {e}")
            return {
                "success": False,
                "error": f"Failed to delete note: {str(e)}"
            }

    async def search_notes(self, query: str) -> Dict[str, Any]:
        """
        Search notes by query.
        
        Args:
            query: Search query
        
        Returns:
            Dictionary containing matching notes
        """
        if not NOTES_AVAILABLE:
            return {
                "success": False,
                "error": "Notes service is not available.",
                "notes": []
            }
        
        try:
            notes = notes_manager.search_notes(query)
            return {
                "success": True,
                "notes": notes,
                "count": len(notes)
            }
        except Exception as e:
            logger.error(f"Error searching notes: {e}")
            return {
                "success": False,
                "error": f"Failed to search notes: {str(e)}",
                "notes": []
            }

    # ============== Alarm Methods ==============

    async def set_alarm(self, time: str, label: str = "", days: List[str] = None) -> Dict[str, Any]:
        """
        Set a new alarm.
        
        Args:
            time: Alarm time (e.g., "07:00", "7:00 AM")
            label: Optional label for the alarm
            days: Optional list of days (e.g., ["monday", "wednesday"])
        
        Returns:
            Dictionary containing the created alarm
        """
        if not ALARM_AVAILABLE:
            return {
                "success": False,
                "error": "Alarm service is not available."
            }
        
        try:
            result = alarm_manager.set_alarm(time, label, days)
            return result
        except Exception as e:
            logger.error(f"Error setting alarm: {e}")
            return {
                "success": False,
                "error": f"Failed to set alarm: {str(e)}"
            }

    async def get_alarms(self, enabled_only: bool = False) -> Dict[str, Any]:
        """
        Get all alarms.
        
        Args:
            enabled_only: If True, return only enabled alarms
        
        Returns:
            Dictionary containing alarms
        """
        if not ALARM_AVAILABLE:
            return {
                "success": False,
                "error": "Alarm service is not available.",
                "alarms": []
            }
        
        try:
            alarms = alarm_manager.get_alarms(enabled_only)
            return {
                "success": True,
                "alarms": alarms,
                "count": len(alarms)
            }
        except Exception as e:
            logger.error(f"Error getting alarms: {e}")
            return {
                "success": False,
                "error": f"Failed to get alarms: {str(e)}",
                "alarms": []
            }

    async def delete_alarm(self, alarm_id: str) -> Dict[str, Any]:
        """
        Delete an alarm.
        
        Args:
            alarm_id: Alarm ID
        
        Returns:
            Dictionary indicating success or failure
        """
        if not ALARM_AVAILABLE:
            return {
                "success": False,
                "error": "Alarm service is not available."
            }
        
        try:
            success = alarm_manager.delete_alarm(alarm_id)
            return {
                "success": success,
                "message": "Alarm deleted" if success else "Alarm not found"
            }
        except Exception as e:
            logger.error(f"Error deleting alarm: {e}")
            return {
                "success": False,
                "error": f"Failed to delete alarm: {str(e)}"
            }

    async def snooze_alarm(self, alarm_id: str, minutes: int = 10) -> Dict[str, Any]:
        """
        Snooze an alarm.
        
        Args:
            alarm_id: Alarm ID
            minutes: Minutes to snooze (default 10)
        
        Returns:
            Dictionary containing the snoozed alarm
        """
        if not ALARM_AVAILABLE:
            return {
                "success": False,
                "error": "Alarm service is not available."
            }
        
        try:
            result = alarm_manager.snooze_alarm(alarm_id, minutes)
            return result
        except Exception as e:
            logger.error(f"Error snoozing alarm: {e}")
            return {
                "success": False,
                "error": f"Failed to snooze alarm: {str(e)}"
            }

    # ============== Study Timer Methods ==============

    async def start_study_timer(self, duration_minutes: int = None, session_type: str = "study") -> Dict[str, Any]:
        """
        Start a study timer (Pomodoro).
        
        Args:
            duration_minutes: Duration in minutes (default 25 for study)
            session_type: Type of session ("study", "short_break", "long_break")
        
        Returns:
            Dictionary containing timer status
        """
        if not STUDY_TIMER_AVAILABLE:
            return {
                "success": False,
                "error": "Study timer is not available."
            }
        
        try:
            result = study_timer.start_timer(duration_minutes, session_type)
            return result
        except Exception as e:
            logger.error(f"Error starting study timer: {e}")
            return {
                "success": False,
                "error": f"Failed to start timer: {str(e)}"
            }

    async def get_timer_status(self) -> Dict[str, Any]:
        """
        Get current study timer status.
        
        Returns:
            Dictionary containing timer status
        """
        if not STUDY_TIMER_AVAILABLE:
            return {
                "success": False,
                "error": "Study timer is not available."
            }
        
        try:
            result = study_timer.get_timer_status()
            return result
        except Exception as e:
            logger.error(f"Error getting timer status: {e}")
            return {
                "success": False,
                "error": f"Failed to get status: {str(e)}"
            }

    async def pause_timer(self) -> Dict[str, Any]:
        """
        Pause the current study timer.
        
        Returns:
            Dictionary containing timer status
        """
        if not STUDY_TIMER_AVAILABLE:
            return {
                "success": False,
                "error": "Study timer is not available."
            }
        
        try:
            result = study_timer.pause_timer()
            return result
        except Exception as e:
            logger.error(f"Error pausing timer: {e}")
            return {
                "success": False,
                "error": f"Failed to pause timer: {str(e)}"
            }

    async def stop_timer(self) -> Dict[str, Any]:
        """
        Stop the current study timer.
        
        Returns:
            Dictionary containing timer status
        """
        if not STUDY_TIMER_AVAILABLE:
            return {
                "success": False,
                "error": "Study timer is not available."
            }
        
        try:
            result = study_timer.stop_timer()
            return result
        except Exception as e:
            logger.error(f"Error stopping timer: {e}")
            return {
                "success": False,
                "error": f"Failed to stop timer: {str(e)}"
            }

    async def get_study_stats(self) -> Dict[str, Any]:
        """
        Get study statistics.
        
        Returns:
            Dictionary containing study statistics
        """
        if not STUDY_TIMER_AVAILABLE:
            return {
                "success": False,
                "error": "Study timer is not available."
            }
        
        try:
            result = study_timer.get_stats()
            return {
                "success": True,
                "stats": result
            }
        except Exception as e:
            logger.error(f"Error getting study stats: {e}")
            return {
                "success": False,
                "error": f"Failed to get stats: {str(e)}"
            }

    # ============== Trivia Methods ==============

    async def get_trivia_questions(self, amount: int = 10, category: int = None, 
                                    difficulty: str = None) -> Dict[str, Any]:
        """
        Get trivia questions.
        
        Args:
            amount: Number of questions (default 10)
            category: Category ID (optional)
            difficulty: Difficulty level ("easy", "medium", "hard")
        
        Returns:
            Dictionary containing trivia questions
        """
        if not TRIVIA_AVAILABLE or not self.trivia_quiz:
            return {
                "success": False,
                "error": "Trivia service is not available.",
                "questions": []
            }
        
        try:
            result = self.trivia_quiz.get_questions(amount, category, difficulty)
            return result
        except Exception as e:
            logger.error(f"Error getting trivia questions: {e}")
            return {
                "success": False,
                "error": f"Failed to get questions: {str(e)}",
                "questions": []
            }

    async def get_trivia_categories(self) -> Dict[str, Any]:
        """
        Get available trivia categories.
        
        Returns:
            Dictionary containing categories
        """
        if not TRIVIA_AVAILABLE or not self.trivia_quiz:
            return {
                "success": False,
                "error": "Trivia service is not available.",
                "categories": []
            }
        
        try:
            categories = self.trivia_quiz.get_categories()
            return {
                "success": True,
                "categories": categories
            }
        except Exception as e:
            logger.error(f"Error getting trivia categories: {e}")
            return {
                "success": False,
                "error": f"Failed to get categories: {str(e)}",
                "categories": []
            }

    async def check_trivia_answer(self, question_id: str, user_answer: str) -> Dict[str, Any]:
        """
        Check an answer to a trivia question.
        
        Args:
            question_id: Question ID
            user_answer: User's answer
        
        Returns:
            Dictionary containing result
        """
        if not TRIVIA_AVAILABLE or not self.trivia_quiz:
            return {
                "success": False,
                "error": "Trivia service is not available."
            }
        
        try:
            result = self.trivia_quiz.check_answer(question_id, user_answer)
            return result
        except Exception as e:
            logger.error(f"Error checking trivia answer: {e}")
            return {
                "success": False,
                "error": f"Failed to check answer: {str(e)}"
            }

    # ============== Jokes Methods ==============

    async def get_random_joke(self) -> Dict[str, Any]:
        """
        Get a random joke.
        
        Returns:
            Dictionary containing a random joke
        """
        if not JOKES_AVAILABLE or not self.jokes_manager:
            return {
                "success": False,
                "error": "Jokes service is not available."
            }
        
        try:
            joke = self.jokes_manager.get_random_joke()
            return {
                "success": True,
                "joke": joke
            }
        except Exception as e:
            logger.error(f"Error getting random joke: {e}")
            return {
                "success": False,
                "error": f"Failed to get joke: {str(e)}"
            }

    async def get_jokes(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get multiple jokes.
        
        Args:
            limit: Number of jokes (default 10)
        
        Returns:
            Dictionary containing jokes
        """
        if not JOKES_AVAILABLE or not self.jokes_manager:
            return {
                "success": False,
                "error": "Jokes service is not available.",
                "jokes": []
            }
        
        try:
            result = self.jokes_manager.get_jokes(limit)
            return result
        except Exception as e:
            logger.error(f"Error getting jokes: {e}")
            return {
                "success": False,
                "error": f"Failed to get jokes: {str(e)}",
                "jokes": []
            }

    # ============== Quotes Methods ==============

    async def get_random_quote(self) -> Dict[str, Any]:
        """
        Get a random inspirational quote.
        
        Returns:
            Dictionary containing a random quote
        """
        if not QUOTES_AVAILABLE or not self.quotes_manager:
            return {
                "success": False,
                "error": "Quotes service is not available."
            }
        
        try:
            quote = self.quotes_manager.get_random_quote()
            return {
                "success": True,
                "quote": quote
            }
        except Exception as e:
            logger.error(f"Error getting random quote: {e}")
            return {
                "success": False,
                "error": f"Failed to get quote: {str(e)}"
            }

    async def get_today_quote(self) -> Dict[str, Any]:
        """
        Get today's inspirational quote.
        
        Returns:
            Dictionary containing today's quote
        """
        if not QUOTES_AVAILABLE or not self.quotes_manager:
            return {
                "success": False,
                "error": "Quotes service is not available."
            }
        
        try:
            quote = self.quotes_manager.get_today_quote()
            return {
                "success": True,
                "quote": quote
            }
        except Exception as e:
            logger.error(f"Error getting today's quote: {e}")
            return {
                "success": False,
                "error": f"Failed to get quote: {str(e)}"
            }

    async def solve_subject_question(self, question: str) -> Dict[str, Any]:
        """
        Solve questions from various subjects with detailed solutions
        Supported subjects: Mathematics, Physics, Chemistry, Biology, Social Science, Economics, Health, Computer Science
        
        Returns comprehensive solution with:
        - Step-by-step solution
        - Explanation of the concept
        - Method used
        - Why it works
        - How it's possible
        - Reasons behind
        - Verified resources
        """
        if not SUBJECT_SOLVER_AVAILABLE:
            return {
                "success": False,
                "error": "Subject solver module not available"
            }
        
        try:
            # Use the subject solver to get the solution
            result = self.subject_solver.solve_question(question)
            
            # Format the response nicely
            formatted_response = self.subject_solver.format_response(result)
            
            return {
                "success": True,
                "question": question,
                "solution": result,
                "formatted_response": formatted_response,
                "detected_subject": result.get("detected_subject", "unknown"),
                "confidence": result.get("confidence", 0),
                "resources": result.get("resources", [])
            }
        except Exception as e:
            logger.error(f"Error solving subject question: {e}")
            return {
                "success": False,
                "error": f"Failed to solve question: {str(e)}"
            }


tools_manager = ToolsManager()
