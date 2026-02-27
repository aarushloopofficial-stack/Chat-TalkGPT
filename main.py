"""
Chat&Talk GPT - Main Backend Server
FastAPI server for JARVIS-like personal assistant

This module provides a comprehensive REST API for the Chat&Talk GPT personal assistant.
It includes endpoints for authentication, chat, voice processing, task management, 
weather reminders, activity tracking, and more.

## API Documentation
- Swagger UI: `/api/docs`
- ReDoc: `/api/redoc"
"""
import os
import re
import json
import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, Query, Body
from fastapi.openapi.utils import get_openapi
import aiofiles
from PyPDF2 import PdfReader
from io import BytesIO
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Chat&TalkGPT")

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse

# Import our modules
from database import init_database
from chat import ChatManager
from model import ModelManager
from tts import TTSManager
from stt import STTManager
from voice_commands import voice_processor
from user_profile import user_profile
from notifications import email_notifier
from activity_tracker import activity_tracker
from sheets_sync import sheets_sync, excel_exporter
from task_manager import task_manager
from security_system import security_system
from weather_reminder import aakansha_weather_reminder
from reminder_manager import reminder_manager, ReminderType, RecurrencePattern, Priority, SnoozeDuration
from reminder_routes import router as reminder_router
from voice_clone_routes import router as voice_clone_router
from auth_manager import auth_manager

# Import NEW modules (feature expansion)
try:
    from ocr_manager import ocr_manager
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    from email_client import email_client
    EMAIL_CLIENT_AVAILABLE = True
except ImportError:
    EMAIL_CLIENT_AVAILABLE = False

try:
    from sms_manager import sms_manager
    SMS_AVAILABLE = True
except ImportError:
    SMS_AVAILABLE = False

try:
    from voice_clone import voice_clone_manager
    VOICE_CLONE_AVAILABLE = True
except ImportError:
    VOICE_CLONE_AVAILABLE = False

try:
    from iot_manager import iot_manager
    IOT_AVAILABLE = True
except ImportError:
    IOT_AVAILABLE = False

try:
    from sentiment_analyzer import sentiment_analyzer
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False

try:
    from chat_exporter import chat_exporter
    CHAT_EXPORT_AVAILABLE = True
except ImportError:
    CHAT_EXPORT_AVAILABLE = False

try:
    from file_compressor import file_compressor
    FILE_COMPRESS_AVAILABLE = True
except ImportError:
    FILE_COMPRESS_AVAILABLE = False

try:
    from url_shortener import url_shortener
    URL_SHORTENER_AVAILABLE = True
except ImportError:
    URL_SHORTENER_AVAILABLE = False

try:
    from meeting_notes import meeting_notes_manager
    MEETING_NOTES_AVAILABLE = True
except ImportError:
    MEETING_NOTES_AVAILABLE = False

# Import Notes Manager
try:
    from notes_manager import NotesManager
    notes_manager = NotesManager()
    NOTES_AVAILABLE = True
except ImportError:
    NOTES_AVAILABLE = False
    notes_manager = None

# Import Alarm Manager
try:
    from alarm_manager import AlarmManager
    alarm_manager = AlarmManager()
    ALARMS_AVAILABLE = True
except ImportError:
    ALARMS_AVAILABLE = False
    alarm_manager = None

# Import Wake Word Detector
try:
    from wake_word import WakeWordDetector, wake_detector
    WAKE_WORD_AVAILABLE = True
except ImportError:
    WAKE_WORD_AVAILABLE = False
    wake_detector = None

# Import Calendar Manager
try:
    from calendar_manager import CalendarManager
    calendar_manager = CalendarManager()
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False
    calendar_manager = None

# Import Study Timer
try:
    from study_timer import StudyTimer
    study_timer = StudyTimer()
    STUDY_TIMER_AVAILABLE = True
except ImportError:
    STUDY_TIMER_AVAILABLE = False
    study_timer = None

# Import Flashcards
try:
    from flashcards import FlashcardManager
    flashcard_manager = FlashcardManager()
    FLASHCARDS_AVAILABLE = True
except ImportError:
    FLASHCARDS_AVAILABLE = False
    flashcard_manager = None

# Import News Subscription Manager
try:
    from news_subscription import NewsSubscriptionManager, news_subscription_manager
    NEWS_SUBSCRIPTION_AVAILABLE = True
except ImportError:
    NEWS_SUBSCRIPTION_AVAILABLE = False
    news_subscription_manager = None

# Import Notification Manager
try:
    from notification_manager import NotificationManager
    notification_manager = NotificationManager()
    NOTIFICATION_AVAILABLE = True
except ImportError:
    NOTIFICATION_AVAILABLE = False
    notification_manager = None

# ============================================
# Pydantic Models for Request/Response Schema
# ============================================

class RegisterRequest(BaseModel):
    """Request model for user registration"""
    username: str = Field(..., description="Unique username", min_length=3, max_length=50)
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password", min_length=6)

class LoginRequest(BaseModel):
    """Request model for user login"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")

class LogoutRequest(BaseModel):
    """Request model for logout"""
    token: str = Field(..., description="Authentication token")

class ChangePasswordRequest(BaseModel):
    """Request model for changing password"""
    token: str = Field(..., description="Authentication token")
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., description="New password", min_length=6)

class UpdateProfileRequest(BaseModel):
    """Request model for updating user profile"""
    token: str = Field(..., description="Authentication token")
    updates: Dict[str, Any] = Field(..., description="Fields to update")

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User message", min_length=1)
    language: str = Field("english", description="Message language (english, hindi, nepali)")
    deep_search: bool = Field(False, description="Enable deep search mode (Perplexity-like web research with verified sources)")
    verified_only: bool = Field(False, description="Only search verified/trusted sources (academic, government, official)")

class PromptEnhanceRequest(BaseModel):
    """Request model for prompt enhancement"""
    message: str = Field(..., description="Original prompt message")
    style: str = Field("professional", description="Enhancement style (professional, technical, creative, academic, casual, funny, serious)")
    model: str = Field("llama2", description="Ollama model to use")
    temperature: float = Field(0.7, description="Generation temperature (0.0-1.0)")

class TTSRequest(BaseModel):
    """Request model for text-to-speech"""
    text: str = Field(..., description="Text to convert to speech")
    voice: str = Field("abinash", description="Voice name or voice ID")
    language: str = Field("english", description="Language code (english, hindi, nepali)")
    speed: Optional[float] = Field(1.0, description="Speech speed (0.5-2.0)")
    pitch: Optional[float] = Field(1.0, description="Speech pitch (0.5-2.0)")

class VoiceSettingsRequest(BaseModel):
    """Request model for voice settings"""
    voice_id: str = Field(..., description="Voice ID to set as default")

class VoicePreferencesRequest(BaseModel):
    """Request model for voice preferences"""
    default_voice_id: Optional[str] = Field(None, description="Default voice ID")
    preferred_language: Optional[str] = Field(None, description="Preferred language")
    speed: Optional[float] = Field(1.0, description="Speech speed (0.5-2.0)")
    pitch: Optional[float] = Field(1.0, description="Speech pitch (0.5-2.0)")
    voice_profiles: Optional[Dict[str, str]] = Field(None, description="Voice profiles for different contexts")

class TTSConvertRequest(BaseModel):
    """Request model for TTS conversion with full options"""
    text: str = Field(..., description="Text to convert to speech")
    voice_id: str = Field("edge_en_us_guy", description="Voice ID")
    language: str = Field("en", description="Language code")
    speed: Optional[float] = Field(1.0, description="Speech speed (0.5-2.0)")
    pitch: Optional[float] = Field(1.0, description="Speech pitch (0.5-2.0)")

class STTRequest(BaseModel):
    """Request model for speech-to-text"""
    audio: str = Field(..., description="Base64 encoded audio data")

class ListenRequest(BaseModel):
    """Request model for voice command listening"""
    audio: str = Field(..., description="Base64 encoded audio data")
    mode: str = Field("once", description="Listening mode (once, continuous)")

class SetUserNameRequest(BaseModel):
    """Request model for setting user name"""
    name: str = Field(..., description="User's name", min_length=1)
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")

class QuickWeatherRequest(BaseModel):
    """Request model for quick weather"""
    location: str = Field("Kathmandu", description="Location for weather")

class SaveHistoryRequest(BaseModel):
    """Request model for saving history"""
    email: Optional[str] = Field(None, description="User email")

class WeatherReminderRequest(BaseModel):
    """Request model for weather reminders"""
    reminder_type: str = Field(..., description="Type of reminder (temperature, rain, storm, etc.)")
    condition: str = Field(..., description="Condition (above, below, equals)")
    message: str = Field(..., description="Reminder message")
    time: Optional[str] = Field(None, description="Time for reminder")
    location: Optional[str] = Field(None, description="Location")

class UpdateTaskRequest(BaseModel):
    """Request model for updating task"""
    email: str = Field(..., description="User email")
    activity: str = Field(..., description="Task activity")
    status: str = Field(..., description="New status (pending, in_progress, completed)")

# Initialize FastAPI app with OpenAPI metadata
app = FastAPI(
    title="Chat&Talk GPT API",
    description="""
## Overview
Chat&Talk GPT is a JARVIS-like personal assistant API that provides:
- **Authentication**: User registration, login, logout, profile management
- **Chat**: AI-powered conversational responses with security filtering
- **Voice**: Text-to-Speech (TTS) and Speech-to-Text (STT) capabilities
- **Tasks**: Task management with Google Sheets sync
- **Weather**: Weather forecasts and smart reminders
- **Reminders**: General reminder system with multiple types and recurrence
- **Activities**: Activity tracking and analytics

## Authentication
Most endpoints require authentication via token. Include the token in the request body or headers.

## Rate Limits
- Standard: 100 requests per minute
- TTS/STT: 20 requests per minute
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Include reminder routes
app.include_router(reminder_router)

# Include voice clone routes
app.include_router(voice_clone_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        await init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

# Static files will be mounted at the end to avoid route conflicts

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
chat_manager = ChatManager()
model_manager = ModelManager()
tts_manager = TTSManager()
stt_manager = STTManager()

logger.info("Chat&Talk GPT server starting...")



@app.get("/", tags=["Health"], summary="Health Check", description="""
## Health Check Endpoint

Returns the health status of the API.

### Response
Returns basic information about the assistant including name, version, and enabled features.

**Example Response:**
```json
{
  "name": "Chat&Talk GPT",
  "version": "1.0.0",
  "status": "healthy"
}
```
""")
async def health_check():
    """Health check endpoint"""
    return {
        "name": "Chat&Talk GPT",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/api/config", tags=["Configuration"], summary="Get Assistant Configuration", description="""
## Get Assistant Configuration

Returns the assistant configuration including available features and settings.

### Authentication
Not required for this endpoint.

### Response
Returns configuration object with feature flags and assistant metadata.

**Example Response:**
```json
{
  "name": "Chat&Talk GPT",
  "version": "1.0.0",
  "features": {
    "chat": true,
    "voice": true,
    "tasks": true,
    "activities": true,
    "sheets": true,
    "weather_reminder": true
  }
}
```
""")
async def get_config():
    """Get assistant configuration"""
    return {
        "name": "Chat&Talk GPT",
        "version": "1.0.0",
        "features": {
            "chat": True,
            "voice": True,
            "tasks": True,
            "activities": True,
            "sheets": sheets_sync.enabled,
            "weather_reminder": True,
            # NEW FEATURES
            "ocr": OCR_AVAILABLE,
            "email": EMAIL_CLIENT_AVAILABLE,
            "sms": SMS_AVAILABLE,
            "voice_clone": VOICE_CLONE_AVAILABLE,
            "iot_control": IOT_AVAILABLE,
            "sentiment_analysis": SENTIMENT_AVAILABLE,
            "chat_export": CHAT_EXPORT_AVAILABLE,
            "file_compression": FILE_COMPRESS_AVAILABLE,
            "url_shortener": URL_SHORTENER_AVAILABLE,
            "meeting_notes": MEETING_NOTES_AVAILABLE
        }
    }

# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.post("/api/auth/register", tags=["Authentication"], summary="Register New User", description="""
## Register a New User

Create a new user account with username, email, and password.

### Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | string | Yes | Unique username (3-50 characters) |
| email | string | Yes | Valid email address |
| password | string | Yes | Password (minimum 6 characters) |

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - User registered |
| 400 | Error - Invalid input or user exists |

**Example Success Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "user_id": "123"
}
```

**Example Error Response:**
```json
{
  "success": false,
  "error": "Username or email already exists"
}
```
""")
async def register(data: RegisterRequest):
    """Register a new user account"""
    try:
        username = data.username.strip()
        email = data.email.strip()
        password = data.password
        
        if not username or not email or not password:
            return {"success": False, "error": "Username, email, and password are required"}
        
        result = auth_manager.register(username, email, password)
        return result
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return {"success": False, "error": str(e)}


@app.post("/api/auth/login", tags=["Authentication"], summary="User Login", description="""
## User Login

Authenticate a user and create a session token.

### Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | string | Yes | Username or email |
| password | string | Yes | User password |

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - Returns auth token |
| 401 | Error - Invalid credentials |

**Example Success Response:**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "user_id": "123",
    "username": "john",
    "email": "john@example.com"
  }
}
```

**Example Error Response:**
```json
{
  "success": false,
  "error": "Invalid username or password"
}
```
""")
async def login(data: LoginRequest):
    """Login and create session"""
    try:
        username = data.username.strip()
        password = data.password
        
        if not username or not password:
            return {"success": False, "error": "Username and password are required"}
        
        result = auth_manager.login(username, password)
        return result
    except Exception as e:
        logger.error(f"Login error: {e}")
        return {"success": False, "error": str(e)}


@app.post("/api/auth/logout", tags=["Authentication"], summary="User Logout", description="""
## User Logout

Invalidate the current session token.

### Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| token | string | Yes | Authentication token to invalidate |

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - Token invalidated |
| 400 | Error - Invalid token |

**Example Response:**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```
""")
async def logout(data: LogoutRequest):
    """Logout and invalidate session"""
    try:
        token = data.token
        result = auth_manager.logout(token)
        return result
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return {"success": False, "error": str(e)}


@app.get("/api/auth/me", tags=["Authentication"], summary="Get Current User", description="""
## Get Current User

Retrieve the current user's information using their authentication token.

### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| token | string | Yes | Authentication token |

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - Returns user data |
| 401 | Error - Invalid or expired token |

**Example Success Response:**
```json
{
  "success": true,
  "user": {
    "user_id": "123",
    "username": "john",
    "email": "john@example.com",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```
""")
async def get_current_user(token: str = Query(..., description="Authentication token")):
    """Get current user info from token"""
    try:
        user = auth_manager.verify_token(token)
        if not user:
            return {"success": False, "error": "Invalid or expired token"}
        
        return {"success": True, "user": user.to_dict()}
    except Exception as e:
        logger.error(f"Get user error: {e}")
        return {"success": False, "error": str(e)}


@app.post("/api/auth/change-password", tags=["Authentication"], summary="Change Password", description="""
## Change User Password

Update the user's password by providing the old and new password.

### Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| token | string | Yes | Authentication token |
| old_password | string | Yes | Current password |
| new_password | string | Yes | New password (minimum 6 characters) |

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - Password changed |
| 400 | Error - Invalid old password |

**Example Success Response:**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```
""")
async def change_password(data: ChangePasswordRequest):
    """Change user password"""
    try:
        token = data.token
        old_password = data.old_password
        new_password = data.new_password
        
        user = auth_manager.verify_token(token)
        if not user:
            return {"success": False, "error": "Invalid session"}
        
        result = auth_manager.change_password(user.user_id, old_password, new_password)
        return result
    except Exception as e:
        logger.error(f"Change password error: {e}")
        return {"success": False, "error": str(e)}


@app.post("/api/auth/update-profile", tags=["Authentication"], summary="Update User Profile", description="""
## Update User Profile

Update user profile information.

### Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| token | string | Yes | Authentication token |
| updates | object | Yes | Dictionary of fields to update |

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - Profile updated |
| 400 | Error - Invalid session |

**Example Request:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "updates": {
    "name": "John Doe",
    "language": "en"
  }
}
```
""")
async def update_profile(data: UpdateProfileRequest):
    """Update user profile"""
    try:
        token = data.token
        updates = data.updates
        
        user = auth_manager.verify_token(token)
        if not user:
            return {"success": False, "error": "Invalid session"}
        
        result = auth_manager.update_user(user.user_id, updates)
        return result
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        return {"success": False, "error": str(e)}


# ============================================
# FILE & UPLOAD ENDPOINTS
# ============================================

@app.post("/api/upload", tags=["Files"], summary="Upload File", description="""
## Upload File

Upload and analyze documents (PDF, TXT, MD, PY, JS). The file content is extracted 
and analyzed by the AI model to provide a summary.

### Request
- **Content-Type**: multipart/form-data
- **Body**: File upload

### Supported File Types
- PDF documents (.pdf)
- Text files (.txt)
- Markdown files (.md)
- Python files (.py)
- JavaScript files (.js)

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - Returns analysis |
| 400 | Error - Unsupported file type |

**Example Success Response:**
```json
{
  "success": true,
  "filename": "document.pdf",
  "summary": "This document discusses...",
  "text_sample": "First 500 characters of extracted text..."
}
```

**Example Error Response:**
```json
{
  "success": false,
  "message": "Unsupported file type: .exe"
}
```
""")
async def upload_file(file: UploadFile = File(..., description="File to upload (PDF, TXT, MD, PY, JS)")):
    """Handle document/image upload and basic analysis"""
    try:
        content = await file.read()
        filename = file.filename
        text = ""
        
        # Basic PDF parsing
        if filename.endswith(".pdf"):
            pdf = PdfReader(BytesIO(content))
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        # Basic text parsing
        elif filename.endswith((".txt", ".md", ".py", ".js")):
            text = content.decode("utf-8")
        else:
            return {"success": False, "message": f"Unsupported file type: {filename}"}

        # Analyze with AI
        analysis_prompt = f"Analyze the following content from '{filename}' and give a quick summary for a student:\n\n{text[:2000]}"
        response = await model_manager.get_response(analysis_prompt)
        
        return {
            "success": True, 
            "filename": filename,
            "summary": response,
            "text_sample": text[:500]
        }
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return {"success": False, "message": str(e)}

from fastapi import FastAPI, UploadFile, File, Form, Request

@app.post("/api/chat", tags=["Chat"], summary="Send Chat Message", description="""
## Send Chat Message

Send a message to the AI assistant and receive a response. Includes content security filtering.

### Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message | string | Yes | The message to send to the AI |
| language | string | No | Message language (english, hindi, nepali). Default: "english" |

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - Returns AI response |
| 400 | Error - Invalid message |

**Example Request:**
```json
{
  "message": "What is Python?",
  "language": "english"
}
```

**Example Success Response:**
```json
{
  "response": "Python is a high-level programming language...",
  "speak": "Python is a high-level programming language...",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Example Blocked Response:**
```json
{
  "response": "Security violation detected.",
  "blocked": true
}
```

### Security
This endpoint includes content filtering and IP-based security checks. 
Inappropriate content will be blocked with a warning or denial.
""")
async def chat(data: ChatRequest, request: Request):
    """Handle chat messages with Hyper Security"""
    try:
        message = data.message
        language = data.language
        deep_search = data.deep_search
        verified_only = data.verified_only
        user_email = user_profile.profile.get("email", "default")
        user_name = user_profile.profile.get("name", "Unknown")
        client_ip = request.client.host
        
        if not message:
            return {"response": "Please enter a message."}
        
        # Content & IP Security Check
        security_result = security_system.check_content(message, user_email, user_name, client_ip)
        if security_result:
            action = security_result.get("action")
            response_text = security_result.get("message", "Security violation detected.")
            voice_text = security_result.get("voice")
            
            # If it's a permanent block or access denial
            if action == "deny":
                return {"response": response_text, "blocked": True}
            
            # If it's a warning (First Offense)
            return {
                "response": response_text, 
                "speak": voice_text, 
                "violation": True
            }
        
        # ============================================
        # DEEP SEARCH MODE - Perplexity-like research
        # ============================================
        if deep_search:
            try:
                from tools import tools_manager as _tools_mgr
                
                # Show user that search is in progress
                logger.info(f"Deep search triggered for: {message}")
                
                # Perform AI-powered web search with verified sources
                if verified_only:
                    search_result = await _tools_mgr.verified_search(message)
                else:
                    search_result = await _tools_mgr.ai_search(message)
                
                response = search_result.get("text", "I couldn't find relevant information. Please try a different query.")
                verified_sources = search_result.get("verified_sources", [])
                
                # Format sources for display
                sources_info = ""
                if verified_sources:
                    sources_info = "\n\n📚 **Sources:**\n"
                    for i, src in enumerate(verified_sources[:5], 1):
                        title = src.get('title', 'Source')
                        url = src.get('url', '')
                        sources_info += f"{i}. [{title}]({url})\n"
                
                # Combine response with sources
                full_response = response + sources_info
                
                # Determine what to speak (strip markdown for TTS)
                speak_text = full_response.replace("**", "").replace("#", "").replace("*", "")
                speak_text = re.sub(r'\[.*?\]\(.*?\)', '', speak_text)
                
                # Save to history
                chat_manager.load_history(user_email)
                chat_manager.add_message("user", f"[Deep Search] {message}")
                chat_manager.add_message("assistant", full_response)
                chat_manager.save_history()
                
                # Log activity
                activity_tracker.log_chat_interaction(user_email, f"[Deep Search] {message[:50]}")
                
                return {
                    "response": full_response,
                    "speak": speak_text,
                    "deep_search": True,
                    "verified_sources": verified_sources,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Deep search error: {e}")
                return {
                    "response": f"Deep search encountered an error: {str(e)}. Please try again or use regular chat mode.",
                    "deep_search": True,
                    "error": True,
                    "timestamp": datetime.now().isoformat()
                }
        
        # Load user history
        chat_manager.load_history(user_email)
        history = chat_manager.get_history()
        
        # Get AI response
        response = await model_manager.get_response(message, language, history)
        
        # Determine what to speak (strip markdown for TTS)
        speak_text = response
        if "### 🎨 Image Generated!" in response:
            speak_text = f"I have generated the image for you! {message.split('generate')[-1].strip() if 'generate' in message.lower() else ''}"
        elif "![" in response and "](http" in response:
            # Basic markdown image stripping for speech
            speak_text = re.sub(r'!\[.*?\]\(.*?\)', 'the image', response)
            speak_text = speak_text.replace("#", "").replace("*", "")
        
        # --- AUTOMATIC SAVING & SYNCING ---
        # 1. Save to local history
        chat_manager.add_message("user", message)
        chat_manager.add_message("assistant", response)
        chat_manager.save_history()
        
        # 2. Log interaction activity
        activity_tracker.log_chat_interaction(user_email, message[:50])
        
        # 3. Automatic Google Sheets Sync (Async)
        if sheets_sync.enabled:
            activities = activity_tracker.get_user_activities(user_email)
            if activities:
                asyncio.create_task(sheets_sync.sync_batch([activities[-1]]))
        
        # Return response
        return {
            "response": response, 
            "speak": speak_text,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return {"response": f"An error occurred: {str(e)}"}

@app.post("/api/prompt-enhance", tags=["AI"], summary="Enhance Prompt", description="""
## Enhance Prompt

Enhance user prompts using Ollama (local AI). This endpoint transforms basic prompts
into more sophisticated, context-rich prompts optimized for different use cases.

### Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message | string | Yes | Original prompt to enhance |
| style | string | No | Enhancement style (default: professional). Options: professional, technical, creative, academic, casual, funny, serious |
| model | string | No | Ollama model to use (default: llama2) |
| temperature | float | No | Generation temperature 0.0-1.0 (default: 0.7) |

### Enhancement Styles
| Style | Description |
|-------|-------------|
| professional | Fortune 500 quality prompts with executive framing |
| technical | Technical prompts with specs and architecture |
| creative | Innovative prompts with design thinking |
| academic | Scholarly prompts with research methodology |
| casual | Easy-to-understand conversational prompts |
| funny | Hilarious, witty, entertaining prompts |
| serious | Direct, focused, no-nonsense prompts |

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - Returns enhanced prompt |
| 400 | Error - Missing message or Ollama not running |

**Example Request:**
```json
{
  "message": "Write about AI",
  "style": "creative",
  "model": "llama2",
  "temperature": 0.7
}
```

**Example Success Response:**
```json
{
  "success": true,
  "enhanced_prompt": "You are a creative innovation expert...",
  "style": "creative",
  "model": "llama2"
}
```

**Example Error Response:**
```json
{
  "success": false,
  "enhanced_prompt": "Ollama not running. Start Ollama first."
}
```

### Note
Requires Ollama to be running locally on port 11434.
""")
async def prompt_enhance(data: PromptEnhanceRequest):
    """Enhance prompts using Ollama (local AI)"""
    try:
        message = data.message
        style = data.style
        model = data.model
        temperature = data.temperature
        
        if not message:
            return {"success": False, "enhanced_prompt": "Please provide a message to enhance."}
        
        # Different prompts based on style selection (now with funny & serious!)
        style_prompts = {
            "professional": f"""You are an elite AI Prompt Engineer. Transform this into a Fortune 500 quality prompt:\n\nOriginal: {message}\n\nEnhance with executive framing, strategic objectives, KPI metrics, and professional terminology.""",
            "technical": f"""You are a senior technical architect. Transform this into a precise technical prompt:\n\nOriginal: {message}\n\nAdd technical specs, architecture considerations, code standards, and optimization goals.""",
            "creative": f"""You are a creative innovation expert. Transform this into an innovative prompt:\n\nOriginal: {message}\n\nAdd design thinking, creative frameworks, and out-of-the-box approaches.""",
            "academic": f"""You are an academic scholar. Transform this into a scholarly research prompt:\n\nOriginal: {message}\n\nAdd research methodology, evidence-based reasoning, and academic rigor.""",
            "casual": f"""You are a friendly expert. Transform this into an easy-to-understand prompt:\n\nOriginal: {message}\n\nAdd conversational tone, relatable analogies, and simple explanations.""",
            "funny": f"""You are a hilarious AI comedy writer. Transform this into a hilarious, witty, and entertaining prompt:\n\nOriginal: {message}\n\nAdd humor, witty remarks, funny analogies, playful language, and comedic timing. Make it entertaining!""",
            "serious": f"""You are a no-nonsense expert. Transform this into a direct, serious, and focused prompt:\n\nOriginal: {message}\n\nRemove all fluff. Get straight to the point. Focus on facts, evidence, and actionable outcomes. No jokes, no filler."""
        }
        
        enhancement_prompt = style_prompts.get(style, style_prompts["professional"])
        
        try:
            import httpx
            ollama_url = "http://localhost:11434/api/generate"
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(ollama_url, json={"model": model, "prompt": enhancement_prompt, "stream": False, "options": {"temperature": temperature, "top_p": 0.9}})
                if response.status_code == 200:
                    result = response.json()
                    enhanced = result.get("response", "").strip()
                    return {"success": True, "enhanced_prompt": enhanced, "style": style, "model": model}
                else:
                    return {"success": False, "enhanced_prompt": "Ollama error: " + str(response.status_code)}
        except Exception as e:
            logger.error(f"Ollama connection error: {e}")
            return {"success": False, "enhanced_prompt": "Ollama not running. Start Ollama first."}
        
        # Memory Extraction (Simple keyword based for now)
        # In a real app, you'd use the LLM to extract facts
        message_lower = message.lower()
        if "i like" in message_lower or "my interest" in message_lower:
            interest = message.split("like")[-1].strip(" .!") if "like" in message_lower else message.split("interest")[-1].strip(" .!")
            user_profile.profile["academic_interests"].append(interest)
            user_profile._save_profile()
        
        if "difficult" in message_lower or "hard for me" in message_lower:
            subject = message.split("difficult")[-1].strip(" .!") if "difficult" in message_lower else message.split("hard for me")[-1].strip(" .!")
            user_profile.profile["weak_subjects"].append(subject)
            user_profile._save_profile()

        # Save to chat history
        chat_manager.add_message("user", message)
        chat_manager.add_message("assistant", response)
        chat_manager.save_history()
        
        # Log activity
        activity_tracker.log_chat_interaction(
            user_profile.profile.get("email", "unknown"),
            message[:50]
        )
        
        return {
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return {"response": f"I encountered an error: {str(e)}"}

@app.post("/api/tts", tags=["Voice"], summary="Text to Speech", description="""
## Text to Speech (TTS)

Convert text to speech using various TTS engines (Edge TTS, GTTS, pyttsx3).

### Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| text | string | Yes | Text to convert to speech |
| voice | string | No | Voice name (default: abinash) |
| language | string | No | Language code (default: english) |

### Available Voices
- **English**: abinash, aakansha
- **Hindi**: abinash_hi, aakansha_hi
- **Nepali**: abinash_ne

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - Returns audio data |
| 400 | Error - No text provided |
| 500 | Error - TTS synthesis failed |

**Example Request:**
```json
{
  "text": "Hello, how are you?",
  "voice": "abinash",
  "language": "english"
}
```

**Example Success Response:**
```json
{
  "audio": "data:audio/mp3;base64,//uQxAAAAANI..."
}
```

**Example Error Response:**
```json
{
  "error": "TTS failed"
}
```
""")
async def text_to_speech(data: TTSRequest):
    """Convert text to speech"""
    try:
        text = data.text
        voice = data.voice
        language = data.language
        speed = data.speed
        pitch = data.pitch
        
        if not text:
            return {"error": "No text provided"}
        
        audio_base64 = await tts_manager.synthesize(text, voice, language, speed, pitch)
        
        if audio_base64:
            return {"audio": audio_base64}
        else:
            return {"error": "TTS failed"}
            
    except Exception as e:
        logger.error(f"TTS error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# VOICE CATALOG API ENDPOINTS
# ============================================

@app.get("/api/tts/voices", tags=["Voice"], summary="Get All Available Voices", description="""
## Get All Available Voices

Returns a list of all available TTS voices across all providers.

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - Returns list of voices |

**Example Success Response:**
```json
{
  "voices": [
    {
      "voice_id": "edge_en_us_guy",
      "name": "Guy",
      "provider": "edge",
      "language": "en",
      "accent": "US",
      "gender": "male",
      "quality_rating": 5,
      "tags": ["natural", "professional", "confident"],
      "description": "Confident and professional American male voice",
      "is_premium": false
    }
  ]
}
```
""")
async def get_all_voices():
    """Get all available voices"""
    try:
        voices = tts_manager.get_available_voices()
        return {"voices": voices, "count": len(voices)}
    except Exception as e:
        logger.error(f"Error getting voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tts/voices/{voice_id}", tags=["Voice"], summary="Get Voice Details", description="""
## Get Voice Details

Returns detailed information about a specific voice.

### Parameters
| Field | Type | Description |
|-------|------|-------------|
| voice_id | string | The voice ID |

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - Returns voice details |
| 404 | Voice not found |
""")
async def get_voice_details(voice_id: str):
    """Get details for a specific voice"""
    try:
        voice = tts_manager.get_voice_details(voice_id)
        if voice:
            return voice
        else:
            raise HTTPException(status_code=404, detail="Voice not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting voice details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tts/voices/providers", tags=["Voice"], summary="Get Voices by Provider", description="""
## Get Voices by Provider

Returns a list of available TTS providers and their voices.

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - Returns providers and their voices |

**Example Success Response:**
```json
{
  "providers": [
    {
      "name": "edge",
      "display_name": "Microsoft Edge TTS",
      "description": "High-quality neural voices, free",
      "quality": "High"
    }
  ]
}
```
""")
async def get_voices_by_provider(provider: str = None):
    """Get voices by provider or all providers"""
    try:
        if provider:
            voices = tts_manager.get_voices_by_provider(provider)
            return {"provider": provider, "voices": voices, "count": len(voices)}
        else:
            providers = tts_manager.get_providers()
            return {"providers": providers}
    except Exception as e:
        logger.error(f"Error getting providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tts/voices/languages", tags=["Voice"], summary="Get Available Languages", description="""
## Get Available Languages

Returns a list of available languages for TTS.

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - Returns list of languages |
""")
async def get_available_languages():
    """Get available languages"""
    try:
        languages = tts_manager.get_languages()
        return {"languages": languages, "count": len(languages)}
    except Exception as e:
        logger.error(f"Error getting languages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tts/voices/default", tags=["Voice"], summary="Set Default Voice", description="""
## Set Default Voice

Sets the default voice for TTS.

### Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| voice_id | string | Yes | Voice ID to set as default |

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - Voice set as default |
| 400 | Invalid voice ID |
""")
async def set_default_voice(data: VoiceSettingsRequest):
    """Set the default voice"""
    try:
        success = tts_manager.set_default_voice(data.voice_id)
        if success:
            # Also save to user profile
            user_profile.profile["preferred_voice"] = data.voice_id
            user_profile._save_profile()
            return {"success": True, "message": f"Voice {data.voice_id} set as default"}
        else:
            raise HTTPException(status_code=400, detail="Invalid voice ID")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting default voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tts/voices/default", tags=["Voice"], summary="Get Default Voice", description="""
## Get Default Voice

Returns the current default voice.

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - Returns default voice |
""")
async def get_default_voice():
    """Get the default voice"""
    try:
        voice = tts_manager.get_default_voice()
        if voice:
            return voice
        else:
            return {"voice_id": "edge_en_us_guy", "name": "Guy", "provider": "edge"}
    except Exception as e:
        logger.error(f"Error getting default voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tts/convert", tags=["Voice"], summary="Convert Text to Speech (Extended)", description="""
## Convert Text to Speech (Extended)

Extended TTS endpoint with full voice customization options.

### Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| text | string | Yes | Text to convert to speech |
| voice_id | string | No | Voice ID (default: edge_en_us_guy) |
| language | string | No | Language code (default: en) |
| speed | float | No | Speech speed 0.5-2.0 (default: 1.0) |
| pitch | float | No | Speech pitch 0.5-2.0 (default: 1.0) |

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - Returns audio data |
| 400 | Error - Invalid parameters |
| 500 | Error - TTS synthesis failed |
""")
async def convert_text_to_speech(data: TTSConvertRequest):
    """Convert text to speech with extended options"""
    try:
        text = data.text
        voice_id = data.voice_id
        language = data.language
        speed = data.speed or 1.0
        pitch = data.pitch or 1.0
        
        if not text:
            raise HTTPException(status_code=400, detail="No text provided")
        
        audio_base64 = await tts_manager.synthesize(text, voice_id, language, speed, pitch)
        
        if audio_base64:
            return {
                "audio": audio_base64,
                "voice_id": voice_id,
                "language": language,
                "speed": speed,
                "pitch": pitch
            }
        else:
            raise HTTPException(status_code=500, detail="TTS synthesis failed")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS convert error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tts/voices/recommended", tags=["Voice"], summary="Get Recommended Voices", description="""
## Get Recommended Voices

Returns recommended voices for specific use cases.

### Query Parameters
| Field | Type | Description |
|-------|------|-------------|
| use_case | string | Use case (casual, professional, news, storytelling, learning, presentation) |

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - Returns recommended voices |
""")
async def get_recommended_voices(use_case: str = "professional"):
    """Get recommended voices for a use case"""
    try:
        voices = tts_manager.get_recommended_voices(use_case)
        return {
            "use_case": use_case,
            "voices": voices,
            "count": len(voices)
        }
    except Exception as e:
        logger.error(f"Error getting recommended voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tts/settings", tags=["Voice"], summary="Get Voice Settings", description="""
## Get Voice Settings

Returns current voice settings (speed, pitch).

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - Returns current settings |
""")
async def get_voice_settings():
    """Get current voice settings"""
    try:
        settings = tts_manager.get_voice_settings()
        return settings
    except Exception as e:
        logger.error(f"Error getting voice settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tts/settings", tags=["Voice"], summary="Update Voice Settings", description="""
## Update Voice Settings

Updates voice settings (speed, pitch).

### Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| speed | float | No | Speech speed 0.5-2.0 |
| pitch | float | No | Speech pitch 0.5-2.0 |

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - Settings updated |
""")
async def update_voice_settings(speed: float = 1.0, pitch: float = 1.0):
    """Update voice settings"""
    try:
        tts_manager.set_voice_settings(speed, pitch)
        # Save to user profile
        user_profile.profile["voice_speed"] = speed
        user_profile.profile["voice_pitch"] = pitch
        user_profile._save_profile()
        return {"success": True, "settings": tts_manager.get_voice_settings()}
    except Exception as e:
        logger.error(f"Error updating voice settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tts/voices/language/{language}", tags=["Voice"], summary="Get Voices by Language", description="""
## Get Voices by Language

Returns voices available for a specific language.

### Parameters
| Field | Type | Description |
|-------|------|-------------|
| language | string | Language code (en, hi, ne) |

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - Returns voices for language |
""")
async def get_voices_by_language(language: str):
    """Get voices for a specific language"""
    try:
        voices = tts_manager.get_voices_by_language(language)
        return {
            "language": language,
            "voices": voices,
            "count": len(voices)
        }
    except Exception as e:
        logger.error(f"Error getting voices by language: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stt", tags=["Voice"], summary="Speech to Text", description="""
## Speech to Text (STT)

Convert speech audio to text using speech recognition.

### Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| audio | string | Yes | Base64 encoded audio data |

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - Returns transcribed text |
| 500 | Error - STT processing failed |

**Example Request:**
```json
{
  "audio": "data:audio/wav;base64,UklGRi..."
}
```

**Example Success Response:**
```json
{
  "text": "Hello, this is a test message"
}
```

**Example Error Response:**
```json
{
  "detail": "STT processing failed"
}
```
""")
async def speech_to_text(data: STTRequest):
    """Convert speech to text"""
    try:
        audio_data = data.audio
        
        logger.info("STT request received")
        
        text = await stt_manager.recognize(audio_data)
        
        logger.info(f"STT result: {text[:50]}...")
        
        return {"text": text}
    except Exception as e:
        logger.error(f"STT error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stt/status", tags=["Voice"], summary="Get STT Status", description="""
## Get STT Status

Get the current status and capabilities of the Speech-to-Text service.

### Response
Returns information about available STT engines and their status.

**Example Response:**
```json
{
  "whisper_available": true,
  "speech_recognition_available": true,
  "microphone_tested": true,
  "message": "Backend STT available. For best results, use browser's Web Speech API."
}
```
""")
async def stt_status():
    """Get STT capabilities and status"""
    return {
        "whisper_available": stt_manager.use_whisper,
        "speech_recognition_available": stt_manager.use_speech_recognition,
        "microphone_tested": stt_manager.test_microphone() if stt_manager.recognizer else False,
        "message": "Backend STT available. For best results, use browser's Web Speech API."
    }

@app.post("/api/listen", tags=["Voice"], summary="Voice Command Listener", description="""
## Voice Command Listener

Listen for voice commands (Alexa-style) with security checking. Transcribes audio and 
either processes it as a command or gets an AI response.

### Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| audio | string | Yes | Base64 encoded audio data |
| mode | string | No | Listening mode (once, continuous). Default: once |

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - Returns command result or AI response |
| 500 | Error - Processing failed |

**Example Command Response:**
```json
{
  "status": "command_executed",
  "text": "set alarm for 7am",
  "result": {
    "message": "Alarm set for 7:00 AM"
  }
}
```

**Example AI Response:**
```json
{
  "status": "ai_response",
  "text": "what is the weather",
  "response": "The weather is sunny...",
  "speak": "The weather is sunny..."
}
```

**Example No Speech Response:**
```json
{
  "status": "no_speech",
  "text": "",
  "response": "I didn't catch that. Could you please repeat?"
}
```

**Example Security Block Response:**
```json
{
  "status": "security_block",
  "text": "inappropriate content",
  "response": "Security violation detected.",
  "blocked": true
}
```
""")
async def listen(data: ListenRequest, request: Request):
    """Listen for voice command (Alexa-style) with Security Check"""
    try:
        audio_data = data.audio
        mode = data.mode
        user_email = user_profile.profile.get("email", "default")
        user_name = user_profile.profile.get("name", "Unknown")
        client_ip = request.client.host
        
        # First, transcribe the audio
        text = await stt_manager.recognize(audio_data)
        
        if not text or len(text.strip()) < 2:
            return {
                "status": "no_speech",
                "text": "",
                "response": "I didn't catch that. Could you please repeat?"
            }
        
        # Hyper Security Check for spoken words
        security_result = security_system.check_content(text, user_email, user_name, client_ip)
        if security_result:
            return {
                "status": "security_block",
                "text": text,
                "response": security_result.get("message"),
                "speak": security_result.get("voice"),
                "blocked": security_result.get("action") == "deny"
            }
            
        # Process as voice command
        result = voice_processor.process_command(text)
        
        if result:
            return {
                "status": "command_executed",
                "text": text,
                "result": result
            }
        else:
            # Not a command, get AI response
            response = await model_manager.get_response(text, "english")
            return {
                "status": "ai_response",
                "text": text,
                "response": response,
                "speak": None 
            }
            
    except Exception as e:
        logger.error(f"Listen error: {e}", exc_info=True)
        return {
            "status": "error",
            "text": "",
            "response": "Sorry, I had trouble processing that."
        }

@app.get("/api/voice-history", tags=["Voice"], summary="Get Voice History", description="""
## Get Voice History

Retrieve the history of voice commands executed.

### Response
Returns list of previously executed voice commands.

**Example Response:**
```json
{
  "history": [
    {
      "command": "set alarm for 7am",
      "result": "Alarm set for 7:00 AM",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ]
}
```
""")
async def get_voice_history():
    """Get voice command history"""
    return {"history": voice_processor.get_history()}

@app.get("/api/user", tags=["User"], summary="Get Current User", description="""
## Get Current User

Get information about the current logged-in user.

### Response
Returns user profile information including name and email.

**Example Response:**
```json
{
  "has_name": true,
  "name": "John Doe",
  "email": "john@example.com"
}
```
""")
async def get_user():
    """Get current user info"""
    has_name = bool(user_profile.profile.get("name"))
    return {
        "has_name": has_name,
        "name": user_profile.profile.get("name", ""),
        "email": user_profile.profile.get("email", "")
    }


@app.get("/api/user/theme", tags=["User"], summary="Get User Theme", description="""
## Get User Theme

Get the user's theme preference.

### Response
Returns the user's current theme preference (light, dark, or system).

**Example Response:**
```json
{
  "theme": "dark"
}
```
""")
async def get_user_theme():
    """Get user's theme preference"""
    return {
        "theme": user_profile.get_theme()
    }


class ThemeRequest(BaseModel):
    """Request model for updating theme"""
    theme: str = Field(..., description="Theme preference: light, dark, or system")


@app.post("/api/user/theme", tags=["User"], summary="Set User Theme", description="""
## Set User Theme

Set the user's theme preference.

### Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| theme | string | Yes | Theme preference: light, dark, or system |

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - Theme set |
| 400 | Error - Invalid theme value |

**Example Request:**
```json
{
  "theme": "light"
}
```

**Example Success Response:**
```json
{
  "success": true,
  "theme": "light"
}
```
""")
async def set_user_theme(data: ThemeRequest):
    """Set user's theme preference"""
    if data.theme not in ["light", "dark", "system"]:
        raise HTTPException(status_code=400, detail="Invalid theme value. Must be: light, dark, or system")
    
    user_profile.set_theme(data.theme)
    return {
        "success": True,
        "theme": data.theme
    }

@app.post("/api/user/name", tags=["User"], summary="Set User Name", description="""
## Set User Name

Set the user's name for personalization. Requires email and password for authentication.

### Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | User's display name |
| email | string | Yes | User email address |
| password | string | Yes | User password |

### Response
| Status | Description |
|--------|-------------|
| 200 | Success - Name set |
| 400 | Error - Missing required fields |

**Example Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "secret123"
}
```

**Example Success Response:**
```json
{
  "success": true,
  "message": "Great! I'll call you John Doe from now on! 😊",
  "name": "John Doe"
}
```
""")
async def set_user_name(data: SetUserNameRequest):
    """Set user's name for personalization - EMAIL AND PASSWORD ARE REQUIRED"""
    name = data.name.strip()
    email = data.email.strip()
    password = data.password.strip()
    
    if not name or not email or not password:
        return {
            "success": False,
            "message": "Name, Email, and Password are all required."
        }
    
    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

@app.get("/api/tasks/status")
async def get_tasks_status():
    """Get task management status"""
    return {
        "enabled": task_manager.enabled,
        "message": "Task management is enabled" if task_manager.enabled else "Google Sheets credentials not configured"
    }

@app.get("/api/tasks")
async def get_user_tasks(email: str = None):
    """Get tasks for a user"""
    if not task_manager.enabled:
        return {"success": False, "message": "Task management not configured", "tasks": []}
    
    try:
        user_email = email or user_profile.profile.get("email")
        if not user_email:
            return {"success": False, "message": "No email provided", "tasks": []}
        
        tasks = task_manager.get_user_tasks(user_email)
        return {
            "success": True,
            "tasks": tasks
        }
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        return {"success": False, "message": str(e), "tasks": []}

@app.get("/api/tasks/all")
async def get_all_tasks():
    """Get all tasks (admin)"""
    if not task_manager.enabled:
        return {"success": False, "message": "Task management not configured", "tasks": []}
    
    try:
        tasks = task_manager.get_all_tasks()
        return {
            "success": True,
            "tasks": tasks
        }
    except Exception as e:
        logger.error(f"Error getting all tasks: {e}")
        return {"success": False, "message": str(e), "tasks": []}

@app.post("/api/tasks/update")
async def update_task(data: Dict[str, Any]):
    """Update a task status"""
    if not task_manager.enabled:
        return {"success": False, "message": "Task management not configured"}
    
    try:
        email = data.get("email", "")
        activity = data.get("activity", "")
        status = data.get("status", "")
        
        if not email or not activity or not status:
            return {"success": False, "message": "Missing required fields"}
        
        success = task_manager.update_task_status(email, activity, status)
        
        if success:
            # Sync to sheets
            if sheets_sync.enabled:
                await sheets_sync.sync_tasks()
            
            return {"success": True, "message": f"Task updated to {status}"}
        else:
            return {"success": False, "message": "Failed to update task"}
            
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        return {"success": False, "message": str(e)}

@app.post("/api/tasks/sync")
async def sync_tasks():
    """Sync tasks from Google Sheets"""
    if not task_manager.enabled:
        return {"success": False, "message": "Task management not configured"}
    
    try:
        await task_manager.sync_from_sheets()
        return {"success": True, "message": "Tasks synced from Google Sheets"}
    except Exception as e:
        logger.error(f"Error syncing tasks: {e}")
        return {"success": False, "message": str(e)}

@app.get("/api/tasks/notifications")
async def get_task_notifications(email: str = None):
    """Get task notifications for user"""
    if not task_manager.enabled:
        return {"success": False, "notifications": []}
    
    try:
        user_email = email or user_profile.profile.get("email")
        if not user_email:
            return {"success": False, "notifications": []}
        
        notifications = task_manager.get_pending_notifications(user_email)
        return {
            "success": True,
            "notifications": notifications
        }
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        return {"success": False, "notifications": []}

# ============ Weather Reminder API Endpoints for Aakansha ============

@app.get("/api/weather/aakansha/current")
async def get_aakansha_weather(location: str = None):
    """Get current weather for Aakansha"""
    try:
        result = await aakansha_weather_reminder.get_current_weather(location)
        if result.get("success"):
            advice = aakansha_weather_reminder.get_weather_advice(result["weather"])
            result["advice"] = advice
        return result
    except Exception as e:
        logger.error(f"Error getting weather: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/weather/aakansha/reminders")
async def get_aakansha_weather_reminders():
    """Get all weather reminders for Aakansha"""
    try:
        reminders = aakansha_weather_reminder.get_reminders()
        return {
            "success": True,
            "reminders": reminders,
            "count": len(reminders)
        }
    except Exception as e:
        logger.error(f"Error getting reminders: {e}")
        return {"success": False, "reminders": [], "error": str(e)}

@app.post("/api/weather/aakansha/reminders")
async def add_aakansha_weather_reminder(
    reminder_type: str = Form(...),
    condition: str = Form(...),
    message: str = Form(...),
    time: str = Form(None),
    location: str = Form(None)
):
    """Add a weather reminder for Aakansha"""
    try:
        result = aakansha_weather_reminder.add_reminder(
            reminder_type=reminder_type,
            condition=condition,
            message=message,
            time=time,
            location=location
        )
        return result
    except Exception as e:
        logger.error(f"Error adding reminder: {e}")
        return {"success": False, "message": str(e)}

@app.delete("/api/weather/aakansha/reminders/{reminder_id}")
async def delete_aakansha_weather_reminder(reminder_id: int):
    """Delete a weather reminder for Aakansha"""
    try:
        result = aakansha_weather_reminder.remove_reminder(reminder_id)
        return result
    except Exception as e:
        logger.error(f"Error deleting reminder: {e}")
        return {"success": False, "message": str(e)}

@app.post("/api/weather/aakansha/reminders/setup")
async def setup_default_weather_reminders():
    """Setup default weather reminders for Aakansha"""
    try:
        result = aakansha_weather_reminder.setup_default_reminders()
        return result
    except Exception as e:
        logger.error(f"Error setting up reminders: {e}")
        return {"success": False, "message": str(e)}

# ============ Global Weather API (any location worldwide, FREE) ============

@app.get("/api/weather/location")
async def get_weather_for_location(location: str = "Kathmandu"):
    """
    Get full weather data (with map coords) for any city/country on Earth.
    Uses wttr.in (free) + OpenStreetMap Nominatim (free) for geocoding.
    Default: Kathmandu, Nepal
    """
    try:
        from tools import tools_manager as _tools_mgr
        result = await _tools_mgr.get_weather_full(location)
        if result.get("success"):
            weather = result.get("current", {})
            temp = weather.get("temp_c", "20")
            desc = weather.get("description", "").lower()
            advice = []
            try:
                t = int(temp)
                if t >= 35:
                    advice.append("\U0001f321\ufe0f Very hot! Stay hydrated and avoid direct sunlight.")
                elif t >= 28:
                    advice.append("\u2600\ufe0f Warm weather. Don't forget sunscreen!")
                elif t >= 18:
                    advice.append("\U0001f60a Pleasant weather today!")
                elif t >= 10:
                    advice.append("\U0001f9e5 A bit cool. Bring a jacket!")
                else:
                    advice.append("\U0001f976 Cold! Bundle up and stay warm!")
            except Exception:
                pass
            if "rain" in desc or "drizzle" in desc:
                advice.append("\U0001f327\ufe0f Don't forget your umbrella!")
            elif "thunder" in desc or "storm" in desc:
                advice.append("\u26c8\ufe0f Storm warning! Stay indoors.")
            elif "snow" in desc:
                advice.append("\u2744\ufe0f Snow expected! Drive carefully.")
            elif "fog" in desc or "mist" in desc:
                advice.append("\U0001f32b\ufe0f Foggy. Drive carefully!")
            result["advice"] = " ".join(advice)
        return result
    except Exception as e:
        logger.error(f"Error fetching weather for '{location}': {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/weather/quick")
async def get_quick_weather(data: Dict[str, Any]):
    """
    Quick weather text for chat/voice.
    Body: { "location": "Paris" }
    """
    try:
        from tools import tools_manager as _tools_mgr
        location = data.get("location", "Kathmandu")
        result = await _tools_mgr.get_weather(location)
        weather_text = result.get("text", "Could not fetch weather.")
        return {"success": True, "text": weather_text, "location": location}
    except Exception as e:
        logger.error(f"Quick weather error: {e}")
        return {"success": False, "text": str(e)}

@app.post("/api/history/save")
async def save_history_explicit(data: Dict[str, Any]):
    """Manually save and sync history + send email report"""
    try:
        email = data.get("email") or user_profile.profile.get("email")
        if not email:
            return {"success": False, "message": "Email is required to save history"}
        
        # 1. Sync all activities to Google Sheets
        if sheets_sync.enabled:
            activities = activity_tracker.get_user_activities(email)
            if activities:
                asyncio.create_task(sheets_sync.sync_batch(activities))
        
        # 2. Get full chat history
        chat_manager.load_history(email)
        history = chat_manager.get_history()
        
        # 3. Format history for email
        history_text = "\n".join([f"{m['role'].upper()} at {m.get('timestamp', 'N/A')}:\n{m['content']}\n" for m in history])
        
        # 4. Send email report
        user_name = user_profile.profile.get("name", "Student")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        subject = f"📑 Chat History Report - {user_name} ({timestamp})"
        body = f"Here is the detailed chat and activity history for {user_name} ({email}).\n\n{history_text}\n\nGenerated by Chat&Talk GPT Assistant."
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="background: #6c5ce7; padding: 20px; color: white; border-radius: 10px;">
                <h2>📑 Chat & Activity History Report</h2>
                <p>User: {user_name} ({email})</p>
                <p>Date: {timestamp}</p>
            </div>
            <div style="margin-top: 20px; background: #f9f9f9; padding: 15px; border-radius: 8px;">
                <pre style="white-space: pre-wrap;">{history_text}</pre>
            </div>
        </body>
        </html>
        """
        
        asyncio.create_task(email_notifier.send_email(subject, body, html))
        
        return {"success": True, "message": "History saved to Google Sheets and sent to your email!"}
        
    except Exception as e:
        logger.error(f"Error saving history: {e}")
        return {"success": False, "message": str(e)}

@app.delete("/api/history/clear")
async def clear_history_endpoint(email: str = None):
    """Clear chat and activity history for a specific user"""
    try:
        user_email = email or user_profile.profile.get("email")
        if not user_email:
            return {"success": False, "message": "Email required to clear history"}
        
        # Clear chat messages
        chat_manager.load_history(user_email)
        chat_manager.clear_history()
        
        # Clear activity logs
        activity_tracker.clear_user_activities(user_email)
        
        return {"success": True, "message": "All history has been cleared locally."}
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        return {"success": False, "message": str(e)}

@app.get("/api/weather/aakansha/check")
async def check_weather_and_reminders(location: str = None):
    """Check weather and trigger any matching reminders for Aakansha"""
    try:
        # First get current weather
        weather_result = await aakansha_weather_reminder.get_current_weather(location)
        
        if not weather_result.get("success"):
            return weather_result
        
        # Check for triggered reminders
        triggered = await aakansha_weather_reminder.check_and_trigger_reminders()
        
        # Get advice
        advice = aakansha_weather_reminder.get_weather_advice(weather_result["weather"])
        
        return {
            "success": True,
            "weather": weather_result["weather"],
            "advice": advice,
            "triggered_reminders": triggered,
            "triggered_count": len(triggered)
        }
    except Exception as e:
        logger.error(f"Error checking weather: {e}")
        return {"success": False, "error": str(e)}

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Chat&Talk GPT server started!")
    
    # Setup default weather reminders for Aakansha
    try:
        aakansha_weather_reminder.setup_default_reminders()
        logger.info("Aakansha weather reminders initialized!")
    except Exception as e:
        logger.warning(f"Could not setup weather reminders: {e}")
    
    # Test TTS
    try:
        voices = tts_manager.get_available_voices()
        logger.info(f"TTS voices available: {len(voices)}")
    except Exception as e:
        logger.warning(f"Could not get TTS voices: {e}")

# Mount frontend directory at the root
try:
    base_dir = Path(__file__).parent.parent
    frontend_dir = base_dir / "frontend"
    if frontend_dir.exists():
        app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
        logger.info(f"Frontend mounted from {frontend_dir}")
except Exception as e:
    logger.warning(f"Could not mount frontend: {e}")

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
