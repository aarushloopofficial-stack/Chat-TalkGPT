"""
Chat&Talk GPT - Chat Manager
Handles message history, prompt formatting, and conversation context with SQLite storage
"""
import json
import logging
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from database import (
    init_database,
    add_chat_message as db_add_message,
    get_chat_history as db_get_history,
    clear_chat_history as db_clear_history
)

logger = logging.getLogger("ChatManager")

# Import webhook manager for triggering webhooks on chat events
try:
    from webhook_manager import trigger_webhook
except ImportError:
    trigger_webhook = None
    logger.warning("Webhook manager not available - chat webhooks disabled")

# Default system prompt for student-friendly AI
DEFAULT_SYSTEM_PROMPT = """You are Chat&Talk GPT, a friendly AI study buddy designed for students.

Your personality:
- Friendly, casual, and approachable
- Patient and encouraging
- Speak like a helpful friend, not too formal
- **IMPORTANT**: Provide very detailed, comprehensive, and helpful answers. 
- **BE TALKATIVE**: Don't just give one-sentence answers. Explain the "Why" and "How" behind every topic.
- Use multiple paragraphs, bullet points, and step-by-step breakdowns to make your response thorough.
- Keep responses clear and easy to understand
- Use simple language suitable for students
- Feel free to use emojis occasionally 😊
- Be enthusiastic about helping with learning!
- If a user asks a simple question, expand on it with interesting facts related to that topic.

You can help students with:
- Answering homework questions
- Explaining difficult concepts simply
- **Real-time Internet Research**: Summarizing the latest information from the web
- Summarizing topics and notes
- Quiz generation and testing (Suggest "Quiz Hub")
- Code snippets and programming (Suggest "Code Sandbox")
- Study tips and tricks

QUIZ GENERATION:
If the user asks for a quiz or test:
1. Suggest they use the "Quiz Hub" button in settings for an interactive experience.
2. Or generate 3 Multiple Choice Questions here.
3. Do NOT show answers.

CODE SANDBOX:
If the user wants to practice coding:
1. Suggest they open the "Code Sandbox" from settings to run JavaScript.

LANGUAGES:
- Support English, Hindi, and Nepali.

STUDENT INFO:
Respond naturally. Use the student's name if provided in the context below.
"""

from user_profile import user_profile


class ChatManager:
    """Manages chat history and prompt formatting with SQLite storage"""
    
    _db_initialized = False
    
    def __init__(self, history_dir: str = "memory/chats", max_history: int = 50):
        self.history_dir = Path(history_dir)
        self.max_history = max_history
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.current_user = "default"
        self.conversation: List[Dict[str, str]] = []
        self.system_prompt = DEFAULT_SYSTEM_PROMPT
        self._ensure_db_initialized()
        
        logger.info(f"ChatManager initialized. History directory: {self.history_dir}")
    
    def _ensure_db_initialized(self):
        """Ensure database is initialized"""
        if not ChatManager._db_initialized:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if not loop.is_running():
                    loop.run_until_complete(init_database())
            except:
                pass
            ChatManager._db_initialized = True
    
    def load_history(self, email: str = "default"):
        """Load chat history for a specific user"""
        import asyncio
        
        self.current_user = email.replace("@", "_at_").replace(".", "_")
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(db_get_history(1, self.max_history), loop)
                messages = future.result(timeout=10)
            else:
                messages = loop.run_until_complete(db_get_history(1, self.max_history))
            
            # Convert database format to conversation format
            self.conversation = []
            for msg in reversed(messages):
                self.conversation.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                    "timestamp": msg.get("timestamp", "")
                })
            
            logger.info(f"Loaded {len(self.conversation)} messages for {email}")
        except Exception as e:
            logger.warning(f"Could not load history from database: {e}")
            # Fallback to file-based
            self._load_history_file(email)
    
    def _load_history_file(self, email: str):
        """Fallback: load history from file"""
        history_file = self.history_dir / f"{self.current_user}.json"
        
        try:
            if history_file.exists():
                with open(history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.conversation = data.get("messages", [])
                    logger.info(f"Loaded {len(self.conversation)} messages from file for {email}")
            else:
                self.conversation = []
                logger.info(f"No history found for {email}, starting fresh")
        except Exception as e:
            logger.warning(f"Could not load history for {email}: {e}")
            self.conversation = []
    
    def save_history(self):
        """Save chat history to database"""
        import asyncio
        
        # Also save to file as backup
        self._save_history_file()
        
        # Save last few messages to database
        try:
            loop = asyncio.get_event_loop()
            for msg in self.conversation[-10:]:  # Save last 10 messages
                if loop.is_running():
                    asyncio.run_coroutine_threadsafe(
                        db_add_message(1, msg.get("role", "user"), msg.get("content", "")),
                        loop
                    )
                else:
                    loop.run_until_complete(
                        db_add_message(1, msg.get("role", "user"), msg.get("content", ""))
                    )
        except Exception as e:
            logger.warning(f"Could not save to database: {e}")
    
    def _save_history_file(self):
        """Fallback: save history to file"""
        if not self.current_user:
            return
        
        history_file = self.history_dir / f"{self.current_user}.json"
        try:
            data = {
                "messages": self.conversation,
                "last_updated": datetime.now().isoformat()
            }
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving history for {self.current_user}: {e}")
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.conversation.append(message)
        
        # Trim history if too long
        if len(self.conversation) > self.max_history:
            self.conversation = [self.conversation[0]] + self.conversation[-self.max_history+1:]
        
        # Save after each message
        self.save_history()
        
        # Trigger webhook for user messages
        if role == "user":
            self._trigger_message_webhook(content)
        
        logger.debug(f"Added {role} message: {content[:50]}...")
    
    def _trigger_message_webhook(self, content: str, user_id: int = 1):
        """Trigger webhook when a chat message is received"""
        if not trigger_webhook:
            return
        
        webhook_data = {
            "message": content,
            "received_at": datetime.now().isoformat(),
            "user_id": user_id
        }
        
        try:
            # Try to run async trigger in a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(trigger_webhook("chat.message.received", webhook_data, user_id))
            finally:
                loop.close()
            logger.debug(f"Chat message webhook triggered")
        except Exception as e:
            logger.error(f"Error triggering chat webhook: {e}")
    
    def get_history(self, last_n: Optional[int] = None) -> List[Dict[str, str]]:
        """Get conversation history"""
        if last_n:
            return self.conversation[-last_n:]
        return self.conversation
    
    def clear_history(self):
        """Clear all conversation history"""
        import asyncio
        
        self.conversation = []
        
        # Clear from database
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.run_coroutine_threadsafe(db_clear_history(1), loop)
            else:
                loop.run_until_complete(db_clear_history(1))
        except Exception as e:
            logger.warning(f"Could not clear database history: {e}")
        
        # Clear file backup
        self._save_history_file()
        logger.info("Chat history cleared")
    
    def format_prompt(self, user_message: str, language: str = "english") -> List[Dict[str, str]]:
        """Format the prompt for the LLM with system prompt and history"""
        # Get user context
        user_name = user_profile.get_name()
        memories = user_profile.get_memories_summary()
        
        # Build messages array
        sys_prompt = self.system_prompt
        if user_name:
            sys_prompt += f"\n\nStudent Name: {user_name}"
        if memories:
            sys_prompt += f"\n{memories}"
            
        messages = [{"role": "system", "content": sys_prompt}]
        
        # Add language instruction
        lang_instruction = f"\n\nRespond in {language} language. "
        
        if language == "nepali":
            lang_instruction += "Use easy to understand नेपाली."
        elif language == "hindi":
            lang_instruction += "Use easy to understand हिंदी."
        
        # Modify system prompt with language
        messages[0]["content"] += lang_instruction
        
        # Add recent conversation history (last 10 messages)
        recent_history = self.conversation[-10:] if len(self.conversation) > 10 else self.conversation
        messages.extend(recent_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        logger.debug(f"Formatted prompt with {len(messages)} messages")
        
        return messages
    
    def set_personality(self, personality: str):
        """Update the system prompt with custom personality"""
        self.system_prompt = f"""{DEFAULT_SYSTEM_PROMPT}

Additional personality traits: {personality}"""
        logger.info(f"Personality updated: {personality}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get chat statistics"""
        return {
            "total_messages": len(self.conversation),
            "history_file": str(self.history_dir),
            "max_history": self.max_history
        }
