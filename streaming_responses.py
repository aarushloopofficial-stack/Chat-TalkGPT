"""
Chat&Talk GPT - Streaming Responses
Real-time token streaming for faster UX
"""
import os
import asyncio
import logging
from typing import AsyncGenerator, Dict, Any, Optional, Callable
from datetime import datetime
import json
import re

logger = logging.getLogger("StreamingResponses")


class StreamChunk:
    """Represents a chunk of streaming response"""
    
    def __init__(
        self,
        content: str,
        chunk_type: str = "content",  # content, citation, tool, done, error
        meta: Dict[str, Any] = None
    ):
        self.content = content
        self.chunk_type = chunk_type
        self.meta = meta or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "type": self.chunk_type,
            "meta": self.meta,
            "timestamp": self.timestamp
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class StreamingResponseManager:
    """
    Manages streaming responses for real-time AI interaction
    Similar to ChatGPT streaming
    """
    
    def __init__(self):
        self.active_streams: Dict[str, asyncio.Task] = {}
    
    async def stream_ai_response(
        self,
        prompt: str,
        model: str = "llama-3.1-70b-versatile",
        provider: str = "groq",
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        callback: Callable[[StreamChunk], None] = None
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Stream AI response token by token
        
        Args:
            prompt: User message
            model: AI model to use
            provider: AI provider (groq, openai, etc.)
            system_prompt: System instruction
            temperature: Creativity level
            max_tokens: Maximum response length
            callback: Optional callback for each chunk
            
        Yields:
            StreamChunk objects
        """
        try:
            # Import AI aggregator
            from ai_aggregator import get_ai_aggregator
            
            aggregator = get_ai_aggregator()
            
            # Build messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Get streaming response
            if provider == "groq":
                # Groq streaming
                client = aggregator.get_groq_client()
                if not client:
                    yield StreamChunk(
                        content="Error: Groq API not configured",
                        chunk_type="error"
                    )
                    return
                
                stream = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True
                )
                
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        stream_chunk = StreamChunk(
                            content=content,
                            chunk_type="content"
                        )
                        
                        if callback:
                            callback(stream_chunk)
                        
                        yield stream_chunk
                        
            elif provider == "openai":
                # OpenAI streaming
                client = aggregator.get_openai_client()
                if not client:
                    yield StreamChunk(
                        content="Error: OpenAI API not configured",
                        chunk_type="error"
                    )
                    return
                
                stream = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True
                )
                
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        stream_chunk = StreamChunk(
                            content=content,
                            chunk_type="content"
                        )
                        
                        if callback:
                            callback(stream_chunk)
                        
                        yield stream_chunk
            
            else:
                # Non-streaming fallback
                result = await aggregator.generate_response(
                    prompt=prompt,
                    provider=provider,
                    model=model,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Yield in chunks
                words = result.split()
                for i in range(0, len(words), 3):
                    chunk_text = " ".join(words[i:i+3])
                    yield StreamChunk(
                        content=chunk_text + " ",
                        chunk_type="content"
                    )
                    await asyncio.sleep(0.01)  # Small delay
            
            # Signal completion
            yield StreamChunk(
                content="",
                chunk_type="done",
                meta={"model": model, "provider": provider}
            )
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield StreamChunk(
                content=f"Error: {str(e)}",
                chunk_type="error"
            )
    
    async def stream_chat_with_context(
        self,
        message: str,
        history: list = None,
        use_web_search: bool = False,
        web_search_manager = None,
        callback: Callable[[StreamChunk], None] = None
    ) -> AsyncGenerator[StreamChunk, None]:
        """Stream chat response with optional web search
        
        Args:
            message: User message
            history: Chat history
            use_web_search: Whether to use web search
            web_search_manager: Web search instance
            callback: Optional callback
        """
        # First, check if web search is needed
        needs_search = use_web_search or self._should_use_web_search(message)
        
        if needs_search and web_search_manager:
            # Yield thinking indicator
            yield StreamChunk(
                content="🔍",
                chunk_type="tool",
                meta={"action": "searching"}
            )
            
            # Search the web
            search_results = await web_search_manager.search(message, num_results=5)
            
            # Yield search results
            yield StreamChunk(
                content=json.dumps(search_results["results"]),
                chunk_type="citation",
                meta={"citations": search_results["citations"]}
            )
        
        # Build context from history
        context = self._build_context_from_history(history) if history else ""
        
        # System prompt
        system_prompt = f"""You are a helpful AI assistant (like ChatGPT or Perplexity).
You provide accurate, well-researched answers with citations when needed.
Current knowledge cutoff: 2024-06

{context}

Instructions:
- Be concise but thorough
- Cite sources when providing factual information
- Use bullet points for multiple items
- Format code blocks properly"""
        
        # Stream the response
        async for chunk in self.stream_ai_response(
            prompt=message,
            system_prompt=system_prompt,
            callback=callback
        ):
            yield chunk
    
    def _should_use_web_search(self, query: str) -> bool:
        """Determine if query needs web search"""
        query_lower = query.lower()
        
        # Keywords that indicate need for current information
        current_keywords = [
            "latest", "recent", "today", "now", "current",
            "weather", "stock", "price", "news",
            "who is", "what is happening", "current price"
        ]
        
        return any(kw in query_lower for kw in current_keywords)
    
    def _build_context_from_history(self, history: list) -> str:
        """Build context string from chat history"""
        if not history:
            return ""
        
        context_parts = []
        for msg in history[-10:]:  # Last 10 messages
            role = msg.get("role", "user")
            content = msg.get("content", "")
            context_parts.append(f"{role.upper()}: {content[:200]}")
        
        return "Recent conversation:\n" + "\n".join(context_parts)
    
    async def stream_code_execution(
        self,
        code: str,
        language: str = "python",
        code_interpreter = None,
        callback: Callable[[StreamChunk], None] = None
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Stream code execution results
        
        Args:
            code: Code to execute
            language: Programming language
            code_interpreter: Code execution instance
            callback: Optional callback
        """
        yield StreamChunk(
            content="🔄",
            chunk_type="tool",
            meta={"action": "executing", "language": language}
        )
        
        try:
            if code_interpreter:
                result = await code_interpreter.execute(code, language)
            else:
                # Use built-in executor
                from code_executor import code_executor
                result = await code_executor.execute_code(code, language)
            
            if result.get("success"):
                output = result.get("output", "")
                yield StreamChunk(
                    content=output,
                    chunk_type="content",
                    meta={"action": "completed"}
                )
            else:
                error = result.get("error", "Unknown error")
                yield StreamChunk(
                    content=f"Error: {error}",
                    chunk_type="error"
                )
                
        except Exception as e:
            yield StreamChunk(
                content=f"Execution error: {str(e)}",
                chunk_type="error"
            )
        
        yield StreamChunk(
            content="",
            chunk_type="done"
        )


# FastAPI streaming response helper
async def sse_response(stream: AsyncGenerator[StreamChunk, None]):
    """
    Create a Server-Sent Events (SSE) response for streaming
    
    Usage:
        @app.get("/stream")
        async def stream_endpoint():
            manager = StreamingResponseManager()
            stream = manager.stream_ai_response("Hello")
            return await sse_response(stream)
    """
    import aiohttp
    
    async def event_generator():
        async for chunk in stream:
            yield f"data: {chunk.to_json()}\n\n"
    
    return aiohttp.web.Response(
        body=event_generator(),
        content_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# Singleton instance
_streaming_manager: Optional[StreamingResponseManager] = None


def get_streaming_manager() -> StreamingResponseManager:
    """Get or create streaming manager singleton"""
    global _streaming_manager
    if _streaming_manager is None:
        _streaming_manager = StreamingResponseManager()
    return _streaming_manager


async def stream_chat(
    message: str,
    history: list = None,
    **kwargs
) -> AsyncGenerator[StreamChunk, None]:
    """
    Convenience function for streaming chat
    """
    manager = get_streaming_manager()
    async for chunk in manager.stream_chat_with_context(
        message=message,
        history=history,
        **kwargs
    ):
        yield chunk
