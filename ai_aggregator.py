"""
Chat&Talk GPT - AI Aggregator & Web Search
Provides Perplexity-like search with verified resources and multi-AI API integration
"""
import os
import json
import logging
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger("AIAggregator")

# Try importing required libraries
try:
    from googlesearch import search as gsearch
    GOOGLE_SEARCH_AVAILABLE = True
except ImportError:
    GOOGLE_SEARCH_AVAILABLE = False
    logger.warning("googlesearch-python not available")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests library not available")

try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False
    logger.warning("duckduckgo-search not available")

# AI Provider availability
OPENAI_AVAILABLE = False
ANTHROPIC_AVAILABLE = False
GOOGLE_AVAILABLE = False
COHERE_AVAILABLE = False
MISTRAL_AVAILABLE = False
PERPLEXITY_AVAILABLE = False

# Try importing AI providers
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    logger.warning("OpenAI not available")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    logger.warning("Anthropic not available")

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    logger.warning("Google Generative AI not available")

try:
    import cohere
    COHERE_AVAILABLE = True
except ImportError:
    logger.warning("Cohere not available")

try:
    from mistralai import Mistral
    MISTRAL_AVAILABLE = True
except ImportError:
    logger.warning("Mistral AI not available")

try:
    import requests
    PERPLEXITY_AVAILABLE = True
except ImportError:
    logger.warning("Perplexity AI not available (requests needed)")


class WebSearchEngine:
    """Enhanced web search with verified resources using Google"""
    
    def __init__(self):
        self.google_search = None
        if GOOGLE_SEARCH_AVAILABLE:
            try:
                self.google_search = gsearch
            except Exception as e:
                logger.error(f"Failed to initialize Google Search: {e}")
        
        # Verified domain sources for credibility
        self.verified_domains = [
            # Academic & Research
            "arxiv.org", "scholar.google.com", "pubmed.ncbi.nlm.nih.gov",
            "nature.com", "science.org", "ieee.org", "acm.org",
            # Official Documentation
            "docs.python.org", "developer.mozilla.org", "docs.microsoft.com",
            "cloud.google.com", "docs.aws.amazon.com", "developer.apple.com",
            # Trusted News & Media
            "reuters.com", "apnews.com", "bbc.com", "npr.org",
            "theguardian.com", "nytimes.com", "washingtonpost.com",
            # Government & Educational
            "gov", "edu", "who.int", "cdc.gov", "nih.gov",
            # Tech Giants
            "github.com", "stackoverflow.com", "medium.com",
            "wikipedia.org", "wikidata.org",
        ]
        
        # Domain categories for display
        self.domain_categories = {
            "arxiv.org": "📚 Academic Paper",
            "scholar.google.com": "📚 Google Scholar",
            "nature.com": "📰 Nature Journal",
            "science.org": "📰 Science Journal",
            "ieee.org": "📚 IEEE",
            "github.com": "💻 Source Code",
            "stackoverflow.com": "💻 Stack Overflow",
            "wikipedia.org": "📖 Encyclopedia",
            "reuters.com": "📰 Reuters News",
            "bbc.com": "📰 BBC News",
            "gov": "🏛️ Government",
            "edu": "🎓 Educational",
        }
    
    def _categorize_domain(self, url: str) -> str:
        """Categorize a domain for display"""
        url_lower = url.lower()
        for domain, category in self.domain_categories.items():
            if domain in url_lower:
                return category
        return "🌐 Website"
    
    def _is_verified(self, url: str) -> bool:
        """Check if URL is from a verified source"""
        url_lower = url.lower()
        return any(verified in url_lower for verified in self.verified_domains)
    
    async def search(
        self, 
        query: str, 
        num_results: int = 10,
        verified_only: bool = False
    ) -> Dict[str, Any]:
        """
        Search the web using Google and return results with verified sources
        
        Args:
            query: Search query
            num_results: Number of results to return
            verified_only: Only return results from verified sources
            
        Returns:
            Dictionary with search results and metadata
        """
        results = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "results": [],
            "verified_results": [],
            "total_results": 0,
            "verified_count": 0,
            "search_provider": "Google"
        }
        
        if not GOOGLE_SEARCH_AVAILABLE or not self.google_search:
            logger.warning("Google Search not available, trying fallback")
            return await self._fallback_search(query, num_results)
        
        try:
            # Perform search using Google
            search_results = list(self.google_search(query, num_results=num_results * 2))
            
            for url in search_results:
                try:
                    if not url:
                        continue
                    
                    is_verified = self._is_verified(url)
                    category = self._categorize_domain(url)
                    
                    # Get title from URL
                    title = url.split('/')[-1].replace('-', ' ').replace('_', ' ').title()
                    if len(title) > 50:
                        title = title[:50]
                    
                    result = {
                        "title": title or url,
                        "url": url,
                        "snippet": f"Source: {url}",
                        "verified": is_verified,
                        "category": category,
                        "date": ""
                    }
                    
                    results["results"].append(result)
                    
                    if is_verified:
                        results["verified_results"].append(result)
                        
                except Exception as e:
                    logger.error(f"Error processing search result: {e}")
                    continue
            
            results["total_results"] = len(results["results"])
            results["verified_count"] = len(results["verified_results"])
            
            # Filter if verified_only is requested
            if verified_only:
                results["results"] = results["verified_results"]
                
        except Exception as e:
            logger.error(f"Google search error: {e}")
            return await self._fallback_search(query, num_results)
        
        return results
    
    async def _fallback_search(self, query: str, num_results: int) -> Dict[str, Any]:
        """Fallback search using Wikipedia and other sources"""
        results = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "results": [],
            "verified_results": [],
            "total_results": 0,
            "verified_count": 0,
            "fallback": True
        }
        
        # Try Wikipedia
        try:
            import wikipediaapi
            wiki = wikipediaapi.Wikipedia(user_agent="ChatAndTalkGPT/1.0")
            wiki_page = wiki.page(query)
            
            if wiki_page.exists():
                result = {
                    "title": wiki_page.title,
                    "url": wiki_page.fullurl,
                    "snippet": wiki_page.summary[:500] if wiki_page.summary else "No summary available",
                    "verified": True,
                    "category": "📖 Wikipedia",
                    "date": ""
                }
                results["results"].append(result)
                results["verified_results"].append(result)
        except Exception as e:
            logger.error(f"Wikipedia fallback error: {e}")
        
        results["total_results"] = len(results["results"])
        results["verified_count"] = len(results["verified_results"])
        
        return results


class AIAggregator:
    """
    AI Aggregator - Like Perplexity, aggregates multiple AI providers
    Supports: OpenAI, Anthropic, Google, Cohere, Mistral, Groq
    """
    
    def __init__(self):
        # Initialize API keys from environment
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.cohere_api_key = os.getenv("COHERE_API_KEY", "")
        self.mistral_api_key = os.getenv("MISTRAL_API_KEY", "")
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY", "")
        
        # Initialize clients
        self.openai_client = None
        self.anthropic_client = None
        self.google_model = None
        self.cohere_client = None
        self.mistral_client = None
        
        # Initialize web search
        self.search_engine = WebSearchEngine()
        
        # Track available providers
        self.providers = []
        
        self._initialize_providers()
        
        logger.info(f"AIAggregator initialized with providers: {self.providers}")
    
    def _initialize_providers(self):
        """Initialize available AI providers"""
        
        # Groq (already available in main app)
        if os.getenv("GROQ_API_KEY"):
            self.providers.append("groq")
            logger.info("Groq provider available")
        
        # OpenAI
        if OPENAI_AVAILABLE and self.openai_api_key and self.openai_api_key != "your_openai_key_here":
            try:
                openai.api_key = self.openai_api_key
                self.providers.append("openai")
                logger.info("OpenAI provider available")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
        
        # Anthropic
        if ANTHROPIC_AVAILABLE and self.anthropic_api_key and self.anthropic_api_key != "your_anthropic_key_here":
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
                self.providers.append("anthropic")
                logger.info("Anthropic provider available")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic: {e}")
        
        # Google
        if GOOGLE_AVAILABLE and self.google_api_key and self.google_api_key != "your_google_key_here":
            try:
                genai.configure(api_key=self.google_api_key)
                self.providers.append("google")
                logger.info("Google provider available")
            except Exception as e:
                logger.error(f"Failed to initialize Google: {e}")
        
        # Cohere
        if COHERE_AVAILABLE and self.cohere_api_key and self.cohere_api_key != "your_cohere_key_here":
            try:
                self.cohere_client = cohere.Client(self.cohere_api_key)
                self.providers.append("cohere")
                logger.info("Cohere provider available")
            except Exception as e:
                logger.error(f"Failed to initialize Cohere: {e}")
        
        # Mistral
        if MISTRAL_AVAILABLE and self.mistral_api_key and self.mistral_api_key != "your_mistral_key_here":
            try:
                self.mistral_client = Mistral(api_key=self.mistral_api_key)
                self.providers.append("mistral")
                logger.info("Mistral provider available")
            except Exception as e:
                logger.error(f"Failed to initialize Mistral: {e}")
        
        # Perplexity (Cheapest option)
        if PERPLEXITY_AVAILABLE and self.perplexity_api_key and self.perplexity_api_key != "your_perplexity_key_here":
            try:
                self.providers.append("perplexity")
                logger.info("Perplexity provider available")
            except Exception as e:
                logger.error(f"Failed to initialize Perplexity: {e}")
    
    async def search_and_answer(
        self,
        query: str,
        use_web_search: bool = True,
        provider: str = "auto"
    ) -> Dict[str, Any]:
        """
        Search the web and get AI-generated answer with sources
        
        Like Perplexity's conversational search
        """
        response = {
            "query": query,
            "answer": "",
            "sources": [],
            "verified_sources": [],
            "providers_used": [],
            "web_search_results": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Step 1: Web search
        if use_web_search:
            search_results = await self.search_engine.search(query, num_results=10)
            response["web_search_results"] = search_results.get("results", [])
            response["verified_sources"] = search_results.get("verified_results", [])
            
            # Format sources for display
            for src in search_results.get("verified_results", [])[:5]:
                response["sources"].append({
                    "title": src.get("title", ""),
                    "url": src.get("url", ""),
                    "category": src.get("category", "")
                })
        
        # Step 2: Generate answer using available AI
        if provider == "auto":
            # Use first available provider
            provider = self.providers[0] if self.providers else "groq"
        
        try:
            answer = await self._generate_answer(query, provider, response["web_search_results"])
            response["answer"] = answer
            response["providers_used"] = [provider]
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            response["answer"] = f"I found information but couldn't generate a complete answer. Error: {str(e)}"
        
        return response
    
    async def _generate_answer(
        self, 
        query: str, 
        provider: str,
        search_results: List[Dict]
    ) -> str:
        """Generate answer using specified provider with search context"""
        
        # Build context from search results
        context = ""
        if search_results:
            context = "\n\nRelevant information from web search:\n"
            for i, result in enumerate(search_results[:5], 1):
                context += f"{i}. {result.get('title', 'No title')}\n"
                context += f"   {result.get('snippet', 'No description')}\n\n"
        
        prompt = f"""You are a helpful AI assistant. Answer the user's question based on the provided context and your knowledge.

Question: {query}

{context}

Provide a clear, accurate, and well-structured answer. If the context doesn't contain enough information, use your own knowledge but mention that.
"""
        
        # Route to appropriate provider
        if provider == "groq":
            return await self._get_groq_response(prompt)
        elif provider == "openai":
            return await self._get_openai_response(prompt)
        elif provider == "anthropic":
            return await self._get_anthropic_response(prompt)
        elif provider == "google":
            return await self._get_google_response(prompt)
        elif provider == "cohere":
            return await self._get_cohere_response(prompt)
        elif provider == "mistral":
            return await self._get_mistral_response(prompt)
        elif provider == "perplexity":
            return await self._get_perplexity_response(prompt)
        else:
            return "No AI provider available. Please configure an API key."
    
    async def _get_groq_response(self, prompt: str) -> str:
        """Get response from Groq (free)"""
        try:
            from groq import Groq
            client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
            
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq error: {e}")
            raise
    
    async def _get_openai_response(self, prompt: str) -> str:
        """Get response from OpenAI"""
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            raise
    
    async def _get_anthropic_response(self, prompt: str) -> str:
        """Get response from Anthropic Claude"""
        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Anthropic error: {e}")
            raise
    
    async def _get_google_response(self, prompt: str) -> str:
        """Get response from Google Gemini"""
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Google error: {e}")
            raise
    
    async def _get_cohere_response(self, prompt: str) -> str:
        """Get response from Cohere"""
        try:
            response = self.cohere_client.generate(
                model="command-r-plus",
                prompt=prompt,
                max_tokens=1024
            )
            return response.generations[0].text
        except Exception as e:
            logger.error(f"Cohere error: {e}")
            raise
    
    async def _get_mistral_response(self, prompt: str) -> str:
        """Get response from Mistral AI"""
        try:
            chat_response = self.mistral_client.chat.complete(
                model="mistral-small-latest",
                messages=[{"role": "user", "content": prompt}]
            )
            return chat_response.choices[0].message.content
        except Exception as e:
            logger.error(f"Mistral error: {e}")
            raise
    
    async def _get_perplexity_response(self, prompt: str) -> str:
        """Get response from Perplexity AI (one of the cheapest options)"""
        try:
            import requests
            
            url = "https://api.perplexity.ai/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Perplexity error: {e}")
            raise
    
    def get_available_providers(self) -> List[str]:
        """Return list of available AI providers"""
        return self.providers.copy()
    
    async def compare_providers(
        self,
        query: str,
        providers: List[str] = None
    ) -> Dict[str, Any]:
        """
        Compare responses from multiple AI providers
        Useful for research and verification
        """
        if providers is None:
            providers = self.providers[:3]  # Limit to 3 for performance
        
        results = {}
        
        for provider in providers:
            try:
                answer = await self._generate_answer(query, provider, [])
                results[provider] = {
                    "answer": answer,
                    "success": True
                }
            except Exception as e:
                results[provider] = {
                    "answer": f"Error: {str(e)}",
                    "success": False
                }
        
        return {
            "query": query,
            "providers_compared": providers,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }


# Global instance
ai_aggregator = AIAggregator()


# Convenience function for tools
async def get_ai_search(query: str, verified_only: bool = False) -> Dict[str, Any]:
    """
    Search the web with AI-powered answer generation
    Returns answer with verified sources like Perplexity
    """
    return await ai_aggregator.search_and_answer(
        query=query,
        use_web_search=True,
        provider="auto"
    )


async def search_web(query: str, num_results: int = 10) -> Dict[str, Any]:
    """Simple web search with verified sources"""
    return await ai_aggregator.search_engine.search(query, num_results)


async def get_multiple_ai_responses(query: str) -> Dict[str, Any]:
    """Get responses from multiple AI providers for comparison"""
    return await ai_aggregator.compare_providers(query)
