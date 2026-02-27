"""
Chat&Talk GPT - Web Search with Citations
Real-time web search with source attribution
"""
import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import re
from urllib.parse import quote_plus, urljoin
import requests

logger = logging.getLogger("WebSearchWithCitations")

# Try importing Google search
try:
    from googlesearch import search as google_search
    GOOGLE_SEARCH_AVAILABLE = True
except ImportError:
    GOOGLE_SEARCH_AVAILABLE = False
    logger.warning("googlesearch-python not available")

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class SearchResult:
    """Represents a search result with citation"""
    
    def __init__(self, title: str, url: str, snippet: str, source: str = ""):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.source = source or self._extract_domain(url)
        self.timestamp = datetime.now().isoformat()
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            return domain.replace("www.", "")
        except:
            return "unknown"
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
            "timestamp": self.timestamp
        }
    
    def to_citation(self, index: int) -> str:
        """Format as citation: [1] Source"""
        return f"[{index}] {self.source}"


class WebSearchWithCitations:
    """
    Enhanced web search with source citations
    Used for Perplexity-like AI answers
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        self.max_results = 10
        self.timeout = 30
    
    async def search(
        self,
        query: str,
        num_results: int = 10,
        include_domains: List[str] = None,
        exclude_domains: List[str] = None
    ) -> Dict[str, Any]:
        """
        Perform web search with citations
        
        Args:
            query: Search query
            num_results: Number of results to return
            include_domains: Only include these domains
            exclude_domains: Exclude these domains
            
        Returns:
            Dict with results and citations
        """
        logger.info(f"Searching web for: {query}")
        
        results = []
        
        # Try Google Search first
        if GOOGLE_SEARCH_AVAILABLE:
            try:
                results = await self._google_search(query, num_results)
            except Exception as e:
                logger.error(f"Google search failed: {e}")
        
        # Fallback to DuckDuckGo if no results
        if not results:
            try:
                results = await self._duckduckgo_search(query, num_results)
            except Exception as e:
                logger.error(f"DuckDuckGo search failed: {e}")
        
        # Filter results if needed
        if include_domains:
            results = [r for r in results if any(d in r.url for d in include_domains)]
        
        if exclude_domains:
            results = [r for r in results if not any(d in r.url for d in exclude_domains)]
        
        # Limit results
        results = results[:num_results]
        
        # Generate citations
        citations = [r.to_citation(i+1) for i, r in enumerate(results)]
        
        # Get full content for each result
        enriched_results = await self._enrich_results(results)
        
        return {
            "query": query,
            "results": enriched_results,
            "citations": citations,
            "total_results": len(enriched_results),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _google_search(self, query: str, num_results: int) -> List[SearchResult]:
        """Search using Google"""
        results = []
        
        loop = asyncio.get_event_loop()
        
        def search_google():
            return list(google_search(
                query,
                num_results=num_results,
                lang='en'
            ))
        
        try:
            search_results = await loop.run_in_executor(None, search_google)
            
            for item in search_results:
                if isinstance(item, dict):
                    results.append(SearchResult(
                        title=item.get("title", "No title"),
                        url=item.get("url", ""),
                        snippet=item.get("description", ""),
                        source=item.get("source", "")
                    ))
                elif isinstance(item, str):
                    # Google search returns URLs directly
                    results.append(SearchResult(
                        title=query,
                        url=item,
                        snippet="",
                        source=""
                    ))
                    
        except Exception as e:
            logger.error(f"Google search error: {e}")
        
        return results
    
    async def _duckduckgo_search(self, query: str, num_results: int) -> List[SearchResult]:
        """Search using DuckDuckGo"""
        results = []
        
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.session.get(url, timeout=self.timeout)
            )
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                for result in soup.select('.result'):
                    title_elem = result.select_one('.result__title')
                    url_elem = result.select_one('.result__url')
                    snippet_elem = result.select_one('.result__snippet')
                    
                    if title_elem and url_elem:
                        title = title_elem.get_text(strip=True)
                        url = url_elem.get('href', '')
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                        
                        results.append(SearchResult(
                            title=title,
                            url=url,
                            snippet=snippet
                        ))
                        
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
        
        return results
    
    async def _enrich_results(self, results: List[SearchResult]) -> List[Dict[str, Any]]:
        """Get more content from each result"""
        enriched = []
        
        for result in results:
            try:
                # Try to get page content
                content = await self._fetch_page_content(result.url)
                
                enriched.append({
                    "title": result.title,
                    "url": result.url,
                    "snippet": result.snippet or content[:200] + "..." if content else "",
                    "source": result.source,
                    "full_content": content[:2000] if content else "",  # Limit content
                    "timestamp": result.timestamp
                })
            except Exception as e:
                logger.debug(f"Could not fetch {result.url}: {e}")
                enriched.append(result.to_dict())
        
        return enriched
    
    async def _fetch_page_content(self, url: str) -> str:
        """Fetch content from a URL"""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.session.get(url, timeout=10)
            )
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text
                text = soup.get_text(separator=' ', strip=True)
                
                # Clean up whitespace
                text = re.sub(r'\s+', ' ', text)
                
                return text[:5000]  # Limit to 5000 chars
                
        except Exception as e:
            pass
        
        return ""
    
    async def generate_answer(
        self,
        query: str,
        ai_client = None,
        system_prompt: str = None
    ) -> Dict[str, Any]:
        """
        Generate AI answer with citations
        
        Args:
            query: User question
            ai_client: AI client for generating answer
            system_prompt: Custom system prompt
            
        Returns:
            Dict with answer, sources, and citations
        """
        # First search the web
        search_result = await self.search(query, num_results=8)
        
        if not search_result["results"]:
            return {
                "answer": "I couldn't find any relevant information. Please try a different query.",
                "sources": [],
                "citations": [],
                "query": query
            }
        
        # Build context from search results
        context = self._build_context(search_result["results"])
        
        # Default system prompt
        if not system_prompt:
            system_prompt = """You are a helpful AI assistant. Use the provided web search results to answer the user's question. 
            Always cite your sources using the citation numbers provided. 
            Format citations as [1], [2], etc.
            If the information is not in the search results, say so honestly."""
        
        # Generate answer using AI
        if ai_client:
            try:
                full_prompt = f"""Web Search Results:
{context}

User Question: {query}

Instructions: {system_prompt}

Answer:"""
                
                answer = await ai_client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
                    ],
                    max_tokens=2000,
                    temperature=0.7
                )
                
                ai_answer = answer.choices[0].message.content
            except Exception as e:
                logger.error(f"AI answer generation failed: {e}")
                ai_answer = self._generate_summary(query, search_result["results"])
        else:
            # Fallback to summary
            ai_answer = self._generate_summary(query, search_result["results"])
        
        return {
            "answer": ai_answer,
            "sources": search_result["results"],
            "citations": search_result["citations"],
            "query": query,
            "timestamp": datetime.now().isoformat()
        }
    
    def _build_context(self, results: List[Dict[str, Any]]) -> str:
        """Build context string from search results"""
        context_parts = []
        
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"[{i}] {result.get('title', 'No title')}\n"
                f"Source: {result.get('source', result.get('url', ''))}\n"
                f"Content: {result.get('snippet', result.get('full_content', ''))[:500]}\n"
            )
        
        return "\n\n".join(context_parts)
    
    def _generate_summary(self, query: str, results: List[Dict[str, Any]]) -> str:
        """Generate a simple summary when AI is not available"""
        if not results:
            return "No information found."
        
        summary = f"Based on my search for '{query}', here are the key findings:\n\n"
        
        for i, result in enumerate(results[:3], 1):
            title = result.get("title", "No title")
            snippet = result.get("snippet", "No description")
            source = result.get("source", "")
            
            summary += f"{i}. **{title}** [{source}]\n"
            summary += f"   {snippet[:200]}...\n\n"
        
        summary += "\n*For more details, please refer to the sources above.*"
        
        return summary


# Singleton instance
_web_search: Optional[WebSearchWithCitations] = None


def get_web_search() -> WebSearchWithCitations:
    """Get or create web search singleton"""
    global _web_search
    if _web_search is None:
        _web_search = WebSearchWithCitations()
    return _web_search


async def search_with_citations(
    query: str,
    num_results: int = 10
) -> Dict[str, Any]:
    """
    Convenience function for web search with citations
    """
    search = get_web_search()
    return await search.search(query, num_results)


async def generate_answer_with_sources(
    query: str,
    ai_client = None
) -> Dict[str, Any]:
    """
    Generate AI answer with web sources
    """
    search = get_web_search()
    return await search.generate_answer(query, ai_client)
