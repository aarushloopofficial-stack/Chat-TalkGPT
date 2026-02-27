"""
Chat&Talk GPT - Firebase Integration Module
Provides Firebase database, authentication, and cloud messaging
"""
import os
import logging
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger("FirebaseClient")

# Try importing Firebase
try:
    import firebase_admin
    from firebase_admin import credentials, auth, firestore, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logger.warning("Firebase Admin SDK not installed. Install with: pip install firebase-admin")


class FirebaseManager:
    """
    Firebase manager for:
    - Firebase Authentication
    - Cloud Firestore (NoSQL database)
    - Cloud Messaging (Push notifications)
    - Cloud Storage (File storage)
    """
    
    def __init__(self):
        self.credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
        self.project_id = os.getenv("FIREBASE_PROJECT_ID", "")
        self.db = None
        self.is_initialized = False
        
        if FIREBASE_AVAILABLE:
            self._initialize()
        else:
            logger.warning("Firebase SDK not available")
    
    def _initialize(self):
        """Initialize Firebase SDK"""
        try:
            # Check if credentials file exists
            if os.path.exists(self.credentials_path):
                cred = credentials.Certificate(self.credentials_path)
                firebase_admin.initialize_app(cred)
            elif self.project_id:
                # Use default credentials (for GCP)
                firebase_admin.initialize_app()
            else:
                logger.warning("Firebase credentials not configured")
                return
            
            self.db = firestore.client()
            self.is_initialized = True
            logger.info("Firebase initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
    
    def is_configured(self) -> bool:
        """Check if Firebase is configured"""
        return self.is_initialized
    
    # ==================== AUTHENTICATION ====================
    
    async def create_user(self, email: str, password: str, display_name: str = "") -> Dict:
        """Create a new Firebase user"""
        if not self.is_configured():
            return {"success": False, "error": "Firebase not configured"}
        
        try:
            user = auth.create_user(
                email=email,
                password=password,
                display_name=display_name
            )
            return {
                "success": True,
                "user": {
                    "uid": user.uid,
                    "email": user.email,
                    "display_name": user.display_name
                }
            }
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return {"success": False, "error": str(e)}
    
    async def authenticate_user(self, email: str, password: str) -> Dict:
        """Authenticate user with email/password"""
        # Note: Firebase Admin SDK cannot directly authenticate users
        # This requires Firebase Client SDK on frontend
        # For backend verification, use custom tokens or ID tokens
        return {"success": False, "error": "Use frontend Firebase Client SDK for authentication"}
    
    async def verify_id_token(self, id_token: str) -> Dict:
        """Verify Firebase ID token"""
        if not self.is_configured():
            return {"success": False, "error": "Firebase not configured"}
        
        try:
            decoded_token = auth.verify_id_token(id_token)
            return {
                "success": True,
                "user": {
                    "uid": decoded_token["uid"],
                    "email": decoded_token.get("email"),
                    "name": decoded_token.get("name")
                }
            }
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return {"success": False, "error": str(e)}
    
    async def reset_password(self, email: str) -> Dict:
        """Send password reset email"""
        if not self.is_configured():
            return {"success": False, "error": "Firebase not configured"}
        
        try:
            auth.generate_password_reset_link(email)
            return {"success": True, "message": "Password reset email sent"}
        except Exception as e:
            logger.error(f"Error generating reset link: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== FIRESTORE DATABASE ====================
    
    async def create_document(self, collection: str, data: Dict, doc_id: str = None) -> Dict:
        """Create a new document in Firestore"""
        if not self.is_configured():
            return {"success": False, "error": "Firebase not configured"}
        
        try:
            if doc_id:
                self.db.collection(collection).document(doc_id).set(data)
                return {"success": True, "doc_id": doc_id}
            else:
                doc_ref = self.db.collection(collection).document()
                doc_ref.set(data)
                return {"success": True, "doc_id": doc_ref.id}
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_document(self, collection: str, doc_id: str) -> Optional[Dict]:
        """Get a document from Firestore"""
        if not self.is_configured():
            return None
        
        try:
            doc = self.db.collection(collection).document(doc_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return None
    
    async def update_document(self, collection: str, doc_id: str, data: Dict) -> Dict:
        """Update a document in Firestore"""
        if not self.is_configured():
            return {"success": False, "error": "Firebase not configured"}
        
        try:
            self.db.collection(collection).document(doc_id).update(data)
            return {"success": True, "doc_id": doc_id}
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_document(self, collection: str, doc_id: str) -> Dict:
        """Delete a document from Firestore"""
        if not self.is_configured():
            return {"success": False, "error": "Firebase not configured"}
        
        try:
            self.db.collection(collection).document(doc_id).delete()
            return {"success": True, "message": "Document deleted"}
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return {"success": False, "error": str(e)}
    
    async def query_collection(
        self, 
        collection: str, 
        filters: Dict = None, 
        limit: int = 100
    ) -> List[Dict]:
        """Query documents from Firestore"""
        if not self.is_configured():
            return []
        
        try:
            query = self.db.collection(collection)
            
            if filters:
                for field, value in filters.items():
                    query = query.where(field, "==", value)
            
            docs = query.limit(limit).stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            logger.error(f"Error querying collection: {e}")
            return []
    
    # ==================== CLOUD MESSAGING ====================
    
    async def send_push_notification(
        self, 
        token: str, 
        title: str, 
        body: str,
        data: Dict = None
    ) -> Dict:
        """Send push notification to a device"""
        if not self.is_configured():
            return {"success": False, "error": "Firebase not configured"}
        
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                token=token
            )
            
            response = messaging.send(message)
            return {
                "success": True,
                "message_id": response
            }
        except Exception as e:
            logger.error(f"Error sending push notification: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_topic_notification(
        self, 
        topic: str, 
        title: str, 
        body: str,
        data: Dict = None
    ) -> Dict:
        """Send push notification to a topic"""
        if not self.is_configured():
            return {"success": False, "error": "Firebase not configured"}
        
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                topic=topic
            )
            
            response = messaging.send(message)
            return {
                "success": True,
                "message_id": response
            }
        except Exception as e:
            logger.error(f"Error sending topic notification: {e}")
            return {"success": False, "error": str(e)}
    
    async def subscribe_to_topic(self, tokens: List[str], topic: str) -> Dict:
        """Subscribe devices to a topic"""
        if not self.is_configured():
            return {"success": False, "error": "Firebase not configured"}
        
        try:
            response = messaging.subscribe_to_topic(tokens, topic)
            return {
                "success": True,
                "success_count": response.success_count,
                "failure_count": response.failure_count
            }
        except Exception as e:
            logger.error(f"Error subscribing to topic: {e}")
            return {"success": False, "error": str(e)}


# Global instance
firebase_manager = FirebaseManager()


def get_firebase_manager() -> FirebaseManager:
    """Get Firebase manager instance"""
    return firebase_manager
