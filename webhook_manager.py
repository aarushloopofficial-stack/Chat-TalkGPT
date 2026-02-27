"""
Chat&Talk GPT - Webhook Manager Module
Provides webhook management and delivery functionality for third-party integrations
"""
import asyncio
import hashlib
import hmac
import json
import logging
import secrets
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import aiohttp

from database import Database

logger = logging.getLogger("WebhookManager")

# Supported event types
SUPPORTED_EVENTS = [
    "alarm.triggered",
    "reminder.triggered",
    "calendar.event.starting",
    "chat.message.received",
    "weather.alert",
    "note.created",
    "note.updated",
    "flashcard.reviewed",
    "custom"
]

# Default configuration
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT = 30
DEFAULT_BACKOFF_BASE = 2  # Exponential backoff base

# Rate limiting
RATE_LIMIT_DICT: Dict[str, List[float]] = {}
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 10  # requests per window


class WebhookManager:
    """Manages webhooks and their delivery"""
    
    def __init__(self):
        self.db = Database()
        self._delivery_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
    
    # ==================== VALIDATION ====================
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate webhook URL (HTTP/HTTPS)"""
        try:
            result = urlparse(url)
            return all([result.scheme in ['http', 'https'], result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def generate_secret_key() -> str:
        """Generate a secure secret key for webhook signature"""
        return secrets.token_hex(32)
    
    @staticmethod
    def validate_events(events: List[str]) -> tuple[bool, List[str]]:
        """Validate event types"""
        valid_events = []
        invalid_events = []
        
        for event in events:
            if event in SUPPORTED_EVENTS:
                valid_events.append(event)
            else:
                invalid_events.append(event)
        
        return len(invalid_events) == 0, invalid_events
    
    # ==================== SIGNATURE ====================
    
    @staticmethod
    def generate_signature(payload: str, secret_key: str) -> str:
        """Generate HMAC-SHA256 signature for webhook payload"""
        if not secret_key:
            return ""
        return hmac.new(
            secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def verify_signature(payload: str, signature: str, secret_key: str) -> bool:
        """Verify webhook signature"""
        if not signature or not secret_key:
            return False
        expected = WebhookManager.generate_signature(payload, secret_key)
        return hmac.compare_digest(expected, signature)
    
    # ==================== CRUD OPERATIONS ====================
    
    async def create_webhook(
        self,
        user_id: int,
        name: str,
        url: str,
        events: List[str],
        enabled: bool = True,
        secret_key: str = None,
        retry_attempts: int = DEFAULT_RETRY_ATTEMPTS,
        timeout: int = DEFAULT_TIMEOUT
    ) -> Dict[str, Any]:
        """Create a new webhook"""
        # Validate URL
        if not self.validate_url(url):
            return {"success": False, "error": "Invalid URL format. Must be HTTP or HTTPS."}
        
        # Validate events
        valid, invalid = self.validate_events(events)
        if not valid:
            return {"success": False, "error": f"Invalid event types: {', '.join(invalid)}"}
        
        # Generate secret key if not provided
        if not secret_key:
            secret_key = self.generate_secret_key()
        
        conn = await self.db.connect()
        try:
            cursor = await conn.execute(
                """INSERT INTO webhooks 
                   (user_id, name, url, events, enabled, secret_key, retry_attempts, timeout)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, name, url, json.dumps(events), 1 if enabled else 0, 
                 secret_key, retry_attempts, timeout)
            )
            await conn.commit()
            webhook_id = cursor.lastrowid
            
            logger.info(f"Created webhook {webhook_id} for user {user_id}")
            
            return {
                "success": True,
                "webhook": await self.get_webhook(webhook_id, user_id)
            }
        except Exception as e:
            logger.error(f"Error creating webhook: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_webhook(self, webhook_id: int, user_id: int = 1) -> Optional[Dict[str, Any]]:
        """Get webhook by ID"""
        conn = await self.db.connect()
        cursor = await conn.execute(
            """SELECT id, user_id, name, url, events, enabled, secret_key, 
                      retry_attempts, timeout, created_at, last_triggered_at
               FROM webhooks WHERE id = ? AND user_id = ?""",
            (webhook_id, user_id)
        )
        row = await cursor.fetchone()
        
        if not row:
            return None
        
        return self._row_to_webhook(row)
    
    async def list_webhooks(self, user_id: int = 1, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """List all webhooks for a user"""
        conn = await self.db.connect()
        
        if enabled_only:
            cursor = await conn.execute(
                """SELECT id, user_id, name, url, events, enabled, secret_key,
                          retry_attempts, timeout, created_at, last_triggered_at
                   FROM webhooks WHERE user_id = ? AND enabled = 1""",
                (user_id,)
            )
        else:
            cursor = await conn.execute(
                """SELECT id, user_id, name, url, events, enabled, secret_key,
                          retry_attempts, timeout, created_at, last_triggered_at
                   FROM webhooks WHERE user_id = ?""",
                (user_id,)
            )
        
        rows = await cursor.fetchall()
        return [self._row_to_webhook(row) for row in rows]
    
    async def update_webhook(
        self,
        webhook_id: int,
        user_id: int,
        name: str = None,
        url: str = None,
        events: List[str] = None,
        enabled: bool = None,
        retry_attempts: int = None,
        timeout: int = None
    ) -> Dict[str, Any]:
        """Update a webhook"""
        webhook = await self.get_webhook(webhook_id, user_id)
        if not webhook:
            return {"success": False, "error": "Webhook not found"}
        
        # Validate URL if provided
        if url and not self.validate_url(url):
            return {"success": False, "error": "Invalid URL format"}
        
        # Validate events if provided
        if events:
            valid, invalid = self.validate_events(events)
            if not valid:
                return {"success": False, "error": f"Invalid event types: {', '.join(invalid)}"}
        
        # Build update query
        updates = []
        values = []
        
        if name is not None:
            updates.append("name = ?")
            values.append(name)
        if url is not None:
            updates.append("url = ?")
            values.append(url)
        if events is not None:
            updates.append("events = ?")
            values.append(json.dumps(events))
        if enabled is not None:
            updates.append("enabled = ?")
            values.append(1 if enabled else 0)
        if retry_attempts is not None:
            updates.append("retry_attempts = ?")
            values.append(retry_attempts)
        if timeout is not None:
            updates.append("timeout = ?")
            values.append(timeout)
        
        if not updates:
            return {"success": False, "error": "No fields to update"}
        
        values.extend([webhook_id, user_id])
        
        conn = await self.db.connect()
        try:
            await conn.execute(
                f"UPDATE webhooks SET {', '.join(updates)} WHERE id = ? AND user_id = ?",
                values
            )
            await conn.commit()
            
            logger.info(f"Updated webhook {webhook_id}")
            
            return {
                "success": True,
                "webhook": await self.get_webhook(webhook_id, user_id)
            }
        except Exception as e:
            logger.error(f"Error updating webhook: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_webhook(self, webhook_id: int, user_id: int = 1) -> Dict[str, Any]:
        """Delete a webhook"""
        conn = await self.db.connect()
        try:
            cursor = await conn.execute(
                "DELETE FROM webhooks WHERE id = ? AND user_id = ?",
                (webhook_id, user_id)
            )
            await conn.commit()
            
            if cursor.rowcount == 0:
                return {"success": False, "error": "Webhook not found"}
            
            logger.info(f"Deleted webhook {webhook_id}")
            return {"success": True, "message": "Webhook deleted successfully"}
        except Exception as e:
            logger.error(f"Error deleting webhook: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== DELIVERY ====================
    
    async def _check_rate_limit(self, url: str) -> bool:
        """Check if request is within rate limit"""
        now = time.time()
        
        if url not in RATE_LIMIT_DICT:
            RATE_LIMIT_DICT[url] = []
        
        # Remove old entries
        RATE_LIMIT_DICT[url] = [
            t for t in RATE_LIMIT_DICT[url]
            if now - t < RATE_LIMIT_WINDOW
        ]
        
        if len(RATE_LIMIT_DICT[url]) >= RATE_LIMIT_MAX:
            return False
        
        RATE_LIMIT_DICT[url].append(now)
        return True
    
    async def _deliver_webhook(
        self,
        webhook: Dict[str, Any],
        event_type: str,
        payload_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deliver webhook with retry logic and exponential backoff"""
        url = webhook['url']
        secret_key = webhook.get('secret_key', '')
        retry_attempts = webhook.get('retry_attempts', DEFAULT_RETRY_ATTEMPTS)
        timeout = webhook.get('timeout', DEFAULT_TIMEOUT)
        
        # Check rate limit
        if not await self._check_rate_limit(url):
            logger.warning(f"Rate limit exceeded for {url}")
            return {
                "success": False,
                "error": "Rate limit exceeded",
                "webhook_id": webhook['id']
            }
        
        # Build payload
        payload = self._build_payload(event_type, payload_data, webhook)
        payload_str = json.dumps(payload)
        
        # Generate signature
        signature = self.generate_signature(payload_str, secret_key)
        
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Event": event_type,
            "X-Webhook-Signature": signature,
            "X-Webhook-ID": str(webhook['id'])
        }
        
        # Retry with exponential backoff
        for attempt in range(retry_attempts):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        url,
                        data=payload_str,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=timeout)
                    ) as response:
                        if response.status < 400:
                            # Update last_triggered_at
                            await self._update_last_triggered(webhook['id'])
                            
                            logger.info(f"Webhook {webhook['id']} delivered successfully")
                            return {
                                "success": True,
                                "status_code": response.status,
                                "webhook_id": webhook['id']
                            }
                        else:
                            logger.warning(
                                f"Webhook {webhook['id']} returned {response.status}"
                            )
            except asyncio.TimeoutError:
                logger.warning(f"Webhook {webhook['id']} timeout on attempt {attempt + 1}")
            except Exception as e:
                logger.error(f"Webhook {webhook['id']} error: {e}")
            
            # Exponential backoff
            if attempt < retry_attempts - 1:
                backoff = DEFAULT_BACKOFF_BASE ** attempt
                await asyncio.sleep(backoff)
        
        return {
            "success": False,
            "error": "All retry attempts failed",
            "webhook_id": webhook['id']
        }
    
    async def _update_last_triggered(self, webhook_id: int):
        """Update last triggered timestamp"""
        conn = await self.db.connect()
        await conn.execute(
            "UPDATE webhooks SET last_triggered_at = CURRENT_TIMESTAMP WHERE id = ?",
            (webhook_id,)
        )
        await conn.commit()
    
    @staticmethod
    def _build_payload(
        event_type: str,
        data: Dict[str, Any],
        webhook: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build webhook payload with template"""
        return {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": event_type,
            "source": "chat_talk_gpt",
            "webhook_id": webhook.get('id'),
            "data": data
        }
    
    # ==================== TRIGGERING ====================
    
    async def trigger_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        user_id: int = 1
    ) -> List[Dict[str, Any]]:
        """Trigger webhooks for an event"""
        if event_type not in SUPPORTED_EVENTS:
            logger.warning(f"Unknown event type: {event_type}")
            return []
        
        # Get all enabled webhooks for this user that listen to this event
        webhooks = await self.list_webhooks(user_id, enabled_only=True)
        
        results = []
        for webhook in webhooks:
            events = webhook.get('events', [])
            if event_type in events or 'custom' in events:
                result = await self._deliver_webhook(webhook, event_type, data)
                results.append(result)
        
        return results
    
    async def test_webhook(self, webhook_id: int, user_id: int = 1) -> Dict[str, Any]:
        """Test webhook delivery"""
        webhook = await self.get_webhook(webhook_id, user_id)
        
        if not webhook:
            return {"success": False, "error": "Webhook not found"}
        
        # Create test payload
        test_data = {
            "test": True,
            "message": "This is a test webhook from Chat&Talk GPT",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        result = await self._deliver_webhook(webhook, "custom", test_data)
        
        return {
            "success": result["success"],
            "webhook_id": webhook_id,
            "message": "Test webhook delivered successfully" if result["success"] else "Test webhook delivery failed",
            "details": result
        }
    
    async def test_event(
        self,
        event_type: str,
        user_id: int = 1,
        test_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Test all webhooks for an event"""
        if event_type not in SUPPORTED_EVENTS:
            return {"success": False, "error": f"Invalid event type: {event_type}"}
        
        if not test_data:
            test_data = {
                "test": True,
                "message": f"This is a test for {event_type}",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        
        results = await self.trigger_event(event_type, test_data, user_id)
        
        successful = sum(1 for r in results if r.get("success"))
        failed = len(results) - successful
        
        return {
            "success": True,
            "event_type": event_type,
            "total_webhooks": len(results),
            "successful": successful,
            "failed": failed,
            "results": results
        }
    
    # ==================== UTILITIES ====================
    
    @staticmethod
    def _row_to_webhook(row) -> Dict[str, Any]:
        """Convert database row to webhook dict"""
        return {
            "id": row[0],
            "user_id": row[1],
            "name": row[2],
            "url": row[3],
            "events": json.loads(row[4]) if isinstance(row[4], str) else row[4],
            "enabled": bool(row[5]),
            "secret_key": row[6],
            "retry_attempts": row[7],
            "timeout": row[8],
            "created_at": row[9],
            "last_triggered_at": row[10] if len(row) > 10 else None
        }
    
    @staticmethod
    def get_supported_events() -> List[str]:
        """Get list of supported event types"""
        return SUPPORTED_EVENTS.copy()
    
    async def get_webhook_stats(self, webhook_id: int, user_id: int = 1) -> Dict[str, Any]:
        """Get webhook statistics"""
        webhook = await self.get_webhook(webhook_id, user_id)
        
        if not webhook:
            return {"success": False, "error": "Webhook not found"}
        
        return {
            "success": True,
            "webhook": webhook,
            "enabled": webhook['enabled'],
            "last_triggered": webhook.get('last_triggered_at'),
            "configured_events": webhook['events']
        }


# Singleton instance
webhook_manager = WebhookManager()


# ==================== STANDALONE FUNCTIONS ====================

async def create_webhook(
    user_id: int,
    name: str,
    url: str,
    events: List[str],
    enabled: bool = True,
    secret_key: str = None,
    retry_attempts: int = DEFAULT_RETRY_ATTEMPTS,
    timeout: int = DEFAULT_TIMEOUT
) -> Dict[str, Any]:
    """Create a new webhook (standalone function)"""
    return await webhook_manager.create_webhook(
        user_id, name, url, events, enabled, secret_key, retry_attempts, timeout
    )


async def get_webhook(webhook_id: int, user_id: int = 1) -> Optional[Dict[str, Any]]:
    """Get webhook by ID (standalone function)"""
    return await webhook_manager.get_webhook(webhook_id, user_id)


async def list_webhooks(user_id: int = 1, enabled_only: bool = False) -> List[Dict[str, Any]]:
    """List all webhooks for a user (standalone function)"""
    return await webhook_manager.list_webhooks(user_id, enabled_only)


async def update_webhook(
    webhook_id: int,
    user_id: int,
    name: str = None,
    url: str = None,
    events: List[str] = None,
    enabled: bool = None,
    retry_attempts: int = None,
    timeout: int = None
) -> Dict[str, Any]:
    """Update a webhook (standalone function)"""
    return await webhook_manager.update_webhook(
        webhook_id, user_id, name, url, events, enabled, retry_attempts, timeout
    )


async def delete_webhook(webhook_id: int, user_id: int = 1) -> Dict[str, Any]:
    """Delete a webhook (standalone function)"""
    return await webhook_manager.delete_webhook(webhook_id, user_id)


async def trigger_webhook(
    event_type: str,
    data: Dict[str, Any],
    user_id: int = 1
) -> List[Dict[str, Any]]:
    """Trigger webhooks for an event (standalone function)"""
    return await webhook_manager.trigger_event(event_type, data, user_id)


async def test_webhook(webhook_id: int, user_id: int = 1) -> Dict[str, Any]:
    """Test webhook delivery (standalone function)"""
    return await webhook_manager.test_webhook(webhook_id, user_id)


async def test_event_webhooks(
    event_type: str,
    user_id: int = 1,
    test_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Test all webhooks for an event (standalone function)"""
    return await webhook_manager.test_event(event_type, user_id, test_data)


def get_supported_events() -> List[str]:
    """Get supported event types (standalone function)"""
    return WebhookManager.get_supported_events()


def validate_webhook_url(url: str) -> bool:
    """Validate webhook URL (standalone function)"""
    return WebhookManager.validate_url(url)


def generate_webhook_secret() -> str:
    """Generate webhook secret key (standalone function)"""
    return WebhookManager.generate_secret_key()


def verify_webhook_signature(payload: str, signature: str, secret_key: str) -> bool:
    """Verify webhook signature (standalone function)"""
    return WebhookManager.verify_signature(payload, signature, secret_key)
