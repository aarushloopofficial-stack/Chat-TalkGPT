"""
Chat&Talk GPT - User Authentication Manager
Handles user registration, login, logout, and session management
"""
import os
import json
import logging
import hashlib
import secrets
import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger("AuthManager")

# Try importing JWT
try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    logger.warning("PyJWT not available - using simple token auth")

try:
    from passlib.hash import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    # Fallback to SHA256
    logger.warning("passlib not available - using SHA256 hashing")


class User:
    """User data model"""
    
    def __init__(self, user_id: str, username: str, email: str, password_hash: str, created_at: str):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at
        self.last_login = None
        self.is_active = True
        self.preferences = {
            "language": "english",
            "voice": "female",
            "theme": "dark"
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "is_active": self.is_active,
            "preferences": self.preferences
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'User':
        user = User(
            user_id=data.get("user_id", ""),
            username=data.get("username", ""),
            email=data.get("email", ""),
            password_hash=data.get("password_hash", ""),
            created_at=data.get("created_at", "")
        )
        user.last_login = data.get("last_login")
        user.is_active = data.get("is_active", True)
        user.preferences = data.get("preferences", user.preferences)
        return user


class AuthManager:
    """
    Manages user authentication with secure password hashing
    and JWT-based session management
    """
    
    def __init__(self):
        self.users_file = Path("memory/users.json")
        self.sessions_file = Path("memory/sessions.json")
        self.secret_key = os.getenv("JWT_SECRET", secrets.token_hex(32))
        self.token_expiry_hours = 24
        
        # Initialize storage files
        self._ensure_storage()
        
        # Load existing users and sessions
        self.users = self._load_users()
        self.sessions = self._load_sessions()
        
        logger.info(f"AuthManager initialized with {len(self.users)} users")
    
    def _ensure_storage(self):
        """Create storage files if they don't exist"""
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        self.sessions_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.users_file.exists():
            self._save_users({})
        
        if not self.sessions_file.exists():
            self._save_sessions({})
    
    def _load_users(self) -> Dict[str, User]:
        """Load users from storage"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {uid: User.from_dict(udata) for uid, udata in data.items()}
        except Exception as e:
            logger.error(f"Error loading users: {e}")
            return {}
    
    def _save_users(self, users: Dict[str, Dict]):
        """Save users to storage"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving users: {e}")
    
    def _load_sessions(self) -> Dict[str, Dict]:
        """Load sessions from storage"""
        try:
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading sessions: {e}")
            return {}
    
    def _save_sessions(self, sessions: Dict[str, Dict]):
        """Save sessions to storage"""
        try:
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(sessions, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving sessions: {e}")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt or SHA256 fallback"""
        if BCRYPT_AVAILABLE:
            return bcrypt.hash(password)
        else:
            # Simple SHA256 fallback (not as secure)
            return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        if BCRYPT_AVAILABLE:
            try:
                return bcrypt.verify(password, password_hash)
            except Exception:
                return False
        else:
            return hashlib.sha256(password.encode()).hexdigest() == password_hash
    
    def _generate_user_id(self) -> str:
        """Generate unique user ID"""
        return f"user_{secrets.token_hex(8)}"
    
    def _generate_session_token(self) -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(32)
    
    def register(
        self, 
        username: str, 
        email: str, 
        password: str,
        preferences: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Register a new user
        
        Args:
            username: Unique username
            email: User's email
            password: User's password
            preferences: Optional user preferences
            
        Returns:
            Dict with success status and user data or error message
        """
        # Validate input
        if not username or len(username) < 3:
            return {"success": False, "error": "Username must be at least 3 characters"}
        
        if not email or '@' not in email:
            return {"success": False, "error": "Valid email is required"}
        
        if not password or len(password) < 6:
            return {"success": False, "error": "Password must be at least 6 characters"}
        
        # Check if username or email already exists
        for user in self.users.values():
            if user.username.lower() == username.lower():
                return {"success": False, "error": "Username already taken"}
            if user.email.lower() == email.lower():
                return {"success": False, "error": "Email already registered"}
        
        # Create new user
        user_id = self._generate_user_id()
        password_hash = self._hash_password(password)
        created_at = datetime.datetime.now().isoformat()
        
        user = User(user_id, username, email, password_hash, created_at)
        if preferences:
            user.preferences.update(preferences)
        
        # Save user
        self.users[user_id] = user
        self._save_users({uid: u.to_dict() for uid, u in self.users.items()})
        
        logger.info(f"New user registered: {username} ({user_id})")
        
        # Return user without password
        return {
            "success": True,
            "user": user.to_dict(),
            "message": "Registration successful!"
        }
    
    def login(
        self, 
        username: str, 
        password: str
    ) -> Dict[str, Any]:
        """
        Authenticate user and create session
        
        Args:
            username: Username or email
            password: User's password
            
        Returns:
            Dict with success status, token, and user data or error
        """
        # Find user by username or email
        user = None
        for u in self.users.values():
            if u.username.lower() == username.lower() or u.email.lower() == username.lower():
                user = u
                break
        
        if not user:
            return {"success": False, "error": "Invalid username or password"}
        
        if not user.is_active:
            return {"success": False, "error": "Account is deactivated"}
        
        # Verify password
        if not self._verify_password(password, user.password_hash):
            logger.warning(f"Failed login attempt for {username}")
            return {"success": False, "error": "Invalid username or password"}
        
        # Generate session token
        token = self._generate_session_token()
        expires_at = (datetime.datetime.now() + datetime.timedelta(hours=self.token_expiry_hours)).isoformat()
        
        # Create session
        session = {
            "user_id": user.user_id,
            "token": token,
            "created_at": datetime.datetime.now().isoformat(),
            "expires_at": expires_at,
            "ip_address": None
        }
        
        # Save session
        self.sessions[token] = session
        self._save_sessions(self.sessions)
        
        # Update last login
        user.last_login = datetime.datetime.now().isoformat()
        self._save_users({uid: u.to_dict() for uid, u in self.users.items()})
        
        logger.info(f"User logged in: {user.username}")
        
        return {
            "success": True,
            "token": token,
            "user": user.to_dict(),
            "expires_at": expires_at,
            "message": f"Welcome back, {user.username}!"
        }
    
    def logout(self, token: str) -> Dict[str, Any]:
        """
        Logout user by invalidating session
        
        Args:
            token: Session token to invalidate
            
        Returns:
            Dict with success status
        """
        if token in self.sessions:
            del self.sessions[token]
            self._save_sessions(self.sessions)
            logger.info("User logged out")
            return {"success": True, "message": "Logged out successfully"}
        
        return {"success": False, "error": "Invalid session"}
    
    def verify_token(self, token: str) -> Optional[User]:
        """
        Verify session token and return user if valid
        
        Args:
            token: Session token to verify
            
        Returns:
            User object if valid, None otherwise
        """
        if not token or token not in self.sessions:
            return None
        
        session = self.sessions[token]
        
        # Check expiry
        try:
            expires_at = datetime.datetime.fromisoformat(session["expires_at"])
            if expires_at < datetime.datetime.now():
                # Token expired, remove it
                del self.sessions[token]
                self._save_sessions(self.sessions)
                return None
        except Exception:
            return None
        
        # Get user
        user_id = session.get("user_id")
        return self.users.get(user_id)
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def update_user(
        self, 
        user_id: str, 
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update user information
        
        Args:
            user_id: User's ID
            updates: Dict of fields to update
            
        Returns:
            Dict with success status and updated user
        """
        user = self.users.get(user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Update allowed fields
        if "email" in updates:
            user.email = updates["email"]
        if "preferences" in updates:
            user.preferences.update(updates["preferences"])
        
        # Save
        self._save_users({uid: u.to_dict() for uid, u in self.users.items()})
        
        return {
            "success": True,
            "user": user.to_dict()
        }
    
    def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> Dict[str, Any]:
        """
        Change user's password
        
        Args:
            user_id: User's ID
            old_password: Current password
            new_password: New password
            
        Returns:
            Dict with success status
        """
        user = self.users.get(user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Verify old password
        if not self._verify_password(old_password, user.password_hash):
            return {"success": False, "error": "Current password is incorrect"}
        
        # Validate new password
        if len(new_password) < 6:
            return {"success": False, "error": "New password must be at least 6 characters"}
        
        # Update password
        user.password_hash = self._hash_password(new_password)
        self._save_users({uid: u.to_dict() for uid, u in self.users.items()})
        
        logger.info(f"Password changed for user {user_id}")
        
        return {"success": True, "message": "Password changed successfully"}
    
    def delete_user(self, user_id: str, password: str) -> Dict[str, Any]:
        """
        Delete user account
        
        Args:
            user_id: User's ID
            password: Confirmation password
            
        Returns:
            Dict with success status
        """
        user = self.users.get(user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Verify password
        if not self._verify_password(password, user.password_hash):
            return {"success": False, "error": "Incorrect password"}
        
        # Remove user
        del self.users[user_id]
        self._save_users({uid: u.to_dict() for uid, u in self.users.items()})
        
        # Remove all sessions for this user
        tokens_to_remove = [
            token for token, session in self.sessions.items() 
            if session.get("user_id") == user_id
        ]
        for token in tokens_to_remove:
            del self.sessions[token]
        self._save_sessions(self.sessions)
        
        logger.info(f"User deleted: {user_id}")
        
        return {"success": True, "message": "Account deleted successfully"}
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get list of all users (admin function)"""
        return [u.to_dict() for u in self.users.values()]


# Global instance
auth_manager = AuthManager()


# Convenience functions
async def register_user(username: str, email: str, password: str) -> Dict[str, Any]:
    return auth_manager.register(username, email, password)


async def login_user(username: str, password: str) -> Dict[str, Any]:
    return auth_manager.login(username, password)


async def logout_user(token: str) -> Dict[str, Any]:
    return auth_manager.logout(token)


async def verify_session(token: str) -> Optional[User]:
    return auth_manager.verify_token(token)
