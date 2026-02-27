"""
Chat&Talk GPT - Supabase Integration Module
Provides PostgreSQL/Supabase database connection and management
"""
import os
import logging
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger("SupabaseClient")

# Try importing Supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None
    logger.warning("Supabase Python client not installed. Install with: pip install supabase")


class SupabaseManager:
    """
    Supabase database manager for scalable user management
    Features:
    - User authentication and management
    - Real-time database sync
    - Row Level Security (RLS)
    - File storage for voice samples
    """
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL", "")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY", "")
        self.service_key = os.getenv("SUPABASE_SERVICE_KEY", "")
        self.client: Optional[Client] = None
        self.is_connected = False
        
        if SUPABASE_AVAILABLE and self.supabase_url and self.supabase_key:
            try:
                self.client = create_client(self.supabase_url, self.supabase_key)
                self.is_connected = True
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
        else:
            logger.warning("Supabase credentials not configured")
    
    def get_client(self) -> Optional[Client]:
        """Get Supabase client instance"""
        return self.client
    
    def is_configured(self) -> bool:
        """Check if Supabase is configured"""
        return self.is_connected and self.client is not None
    
    # ==================== USER MANAGEMENT ====================
    
    async def create_user(self, email: str, password: str, user_data: Dict = None) -> Dict:
        """Create a new user in Supabase Auth"""
        if not self.is_configured():
            return {"success": False, "error": "Supabase not configured"}
        
        try:
            # Create user in Supabase Auth
            response = self.client.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if response.user:
                # Add user profile to database
                user_metadata = user_data or {}
                profile_data = {
                    "id": response.user.id,
                    "email": email,
                    "username": user_metadata.get("username", email.split("@")[0]),
                    "name": user_metadata.get("name", ""),
                    "created_at": datetime.now().isoformat()
                }
                
                # Insert into profiles table
                self.client.table("profiles").insert(profile_data).execute()
                
                return {
                    "success": True,
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "session": response.session
                    }
                }
            
            return {"success": False, "error": "Failed to create user"}
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return {"success": False, "error": str(e)}
    
    async def authenticate_user(self, email: str, password: str) -> Dict:
        """Authenticate user and return session"""
        if not self.is_configured():
            return {"success": False, "error": "Supabase not configured"}
        
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                return {
                    "success": True,
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "session": response.session
                    }
                }
            
            return {"success": False, "error": "Authentication failed"}
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return {"success": False, "error": str(e)}
    
    async def sign_out(self, user_id: str) -> Dict:
        """Sign out user"""
        if not self.is_configured():
            return {"success": False, "error": "Supabase not configured"}
        
        try:
            self.client.auth.sign_out()
            return {"success": True, "message": "Signed out successfully"}
        except Exception as e:
            logger.error(f"Error signing out: {e}")
            return {"success": False, "error": str(e)}
    
    async def reset_password(self, email: str) -> Dict:
        """Send password reset email"""
        if not self.is_configured():
            return {"success": False, "error": "Supabase not configured"}
        
        try:
            response = self.client.auth.reset_password_email(email)
            return {"success": True, "message": "Password reset email sent"}
        except Exception as e:
            logger.error(f"Error resetting password: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== DATABASE OPERATIONS ====================
    
    async def insert(self, table: str, data: Dict) -> Dict:
        """Insert data into table"""
        if not self.is_configured():
            return {"success": False, "error": "Supabase not configured"}
        
        try:
            response = self.client.table(table).insert(data).execute()
            return {"success": True, "data": response.data}
        except Exception as e:
            logger.error(f"Error inserting into {table}: {e}")
            return {"success": False, "error": str(e)}
    
    async def select(self, table: str, filters: Dict = None, limit: int = 100) -> List[Dict]:
        """Select data from table"""
        if not self.is_configured():
            return []
        
        try:
            query = self.client.table(table).select("*")
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            response = query.limit(limit).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error selecting from {table}: {e}")
            return []
    
    async def update(self, table: str, filters: Dict, data: Dict) -> Dict:
        """Update data in table"""
        if not self.is_configured():
            return {"success": False, "error": "Supabase not configured"}
        
        try:
            query = self.client.table(table).update(data)
            
            for key, value in filters.items():
                query = query.eq(key, value)
            
            response = query.execute()
            return {"success": True, "data": response.data}
        except Exception as e:
            logger.error(f"Error updating {table}: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete(self, table: str, filters: Dict) -> Dict:
        """Delete data from table"""
        if not self.is_configured():
            return {"success": False, "error": "Supabase not configured"}
        
        try:
            query = self.client.table(table).delete()
            
            for key, value in filters.items():
                query = query.eq(key, value)
            
            response = query.execute()
            return {"success": True, "data": response.data}
        except Exception as e:
            logger.error(f"Error deleting from {table}: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== STORAGE ====================
    
    async def upload_file(self, bucket: str, file_path: str, file_data: bytes, content_type: str = "audio/mpeg") -> Dict:
        """Upload file to Supabase Storage"""
        if not self.is_configured():
            return {"success": False, "error": "Supabase not configured"}
        
        try:
            response = self.client.storage.from_(bucket).upload(
                file_path,
                file_data,
                {"content_type": content_type}
            )
            return {
                "success": True,
                "path": response.path,
                "url": self.client.storage.from_(bucket).get_public_url(file_path)
            }
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return {"success": False, "error": str(e)}
    
    async def download_file(self, bucket: str, file_path: str) -> Optional[bytes]:
        """Download file from Supabase Storage"""
        if not self.is_configured():
            return None
        
        try:
            response = self.client.storage.from_(bucket).download(file_path)
            return response
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return None
    
    async def delete_file(self, bucket: str, file_path: str) -> Dict:
        """Delete file from Supabase Storage"""
        if not self.is_configured():
            return {"success": False, "error": "Supabase not configured"}
        
        try:
            self.client.storage.from_(bucket).remove([file_path])
            return {"success": True, "message": "File deleted"}
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== REAL-TIME ====================
    
    def subscribe_to_table(self, table: str, callback, filters: Dict = None):
        """Subscribe to real-time updates on a table"""
        if not self.is_configured():
            return None
        
        try:
            channel = self.client.channel(f"public:{table}")
            
            if filters:
                for key, value in filters.items():
                    channel = channel.on(f"postgres_changes", {
                        "event": "*",
                        "schema": "public",
                        "table": table,
                        "filter": f"{key}=eq.{value}"
                    }, callback)
            else:
                channel = channel.on(f"postgres_changes", {
                    "event": "*",
                    "schema": "public",
                    "table": table
                }, callback)
            
            channel.subscribe()
            return channel
        except Exception as e:
            logger.error(f"Error subscribing to {table}: {e}")
            return None


# Global instance
supabase_manager = SupabaseManager()


def get_supabase_manager() -> SupabaseManager:
    """Get Supabase manager instance"""
    return supabase_manager


# ==================== SUPABASE SQL SETUP ====================
# Run these SQL commands in Supabase SQL Editor to set up tables

SUPABASE_SCHEMA = """
-- Users profile table (links to Supabase Auth)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    username TEXT,
    name TEXT,
    avatar_url TEXT,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Create policies for profiles
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

-- Chat history table
CREATE TABLE IF NOT EXISTS chat_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    language TEXT DEFAULT 'english',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own chat history" ON chat_history
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own chat history" ON chat_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Notes table
CREATE TABLE IF NOT EXISTS notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT,
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE notes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own notes" ON notes
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own notes" ON notes
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own notes" ON notes
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own notes" ON notes
    FOR DELETE USING (auth.uid() = user_id);

-- Flashcards table
CREATE TABLE IF NOT EXISTS flashcard_decks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT DEFAULT 'general',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_studied TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS flashcards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deck_id UUID REFERENCES flashcard_decks(id) ON DELETE CASCADE,
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    known BOOLEAN DEFAULT false,
    times_reviewed INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Reminders table
CREATE TABLE IF NOT EXISTS reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    reminder_time TIMESTAMP WITH TIME ZONE NOT NULL,
    recurrence TEXT,
    completed BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Study sessions table
CREATE TABLE IF NOT EXISTS study_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    subject TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    notes TEXT
);

-- Voice samples table
CREATE TABLE IF NOT EXISTS voice_samples (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    language TEXT NOT NULL,
    voice_id TEXT,
    file_path TEXT,
    file_url TEXT,
    duration_seconds INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- News subscriptions table
CREATE TABLE IF NOT EXISTS news_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    frequency TEXT DEFAULT 'daily',
    notification_time TEXT DEFAULT '08:00',
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, category)
);

-- User push tokens table
CREATE TABLE IF NOT EXISTS push_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    token TEXT NOT NULL,
    platform TEXT NOT NULL,
    device_name TEXT,
    last_used TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_created_at ON chat_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notes_user_id ON notes(user_id);
CREATE INDEX IF NOT EXISTS idx_reminders_user_id ON reminders(user_id);
CREATE INDEX IF NOT EXISTS idx_reminders_time ON reminders(reminder_time);
CREATE INDEX IF NOT EXISTS idx_study_sessions_user_id ON study_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_news_subscriptions_user_id ON news_subscriptions(user_id);
"""

print("Supabase Schema ready to be executed in Supabase SQL Editor")
