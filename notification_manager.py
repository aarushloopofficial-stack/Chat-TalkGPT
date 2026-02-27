"""
Chat&Talk GPT - Advanced Notification Manager
Comprehensive notification system supporting Email, SMS, WhatsApp, and Push notifications
"""
import os
import logging
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger("NotificationManager")

# Try importing optional dependencies
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Data storage
DATA_DIR = Path("backend/memory")
NOTIFICATIONS_FILE = DATA_DIR / "notifications.json"


class NotificationType(Enum):
    """Types of notifications"""
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    PUSH = "push"
    REMINDER = "reminder"


class Priority(Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationManager:
    """Comprehensive notification system"""

    def __init__(self):
        self.smtp_email = os.getenv("SMTP_EMAIL", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        
        # Twilio SMS configuration
        self.twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.twilio_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.twilio_phone = os.getenv("TWILIO_PHONE_NUMBER", "")
        
        # WhatsApp configuration (Twilio WhatsApp)
        self.whatsapp_enabled = bool(self.twilio_sid and self.twilio_token)
        
        # Push notification configuration
        self.push_deprecated_key = os.getenv("FIREBASE_DEPRECATED_KEY", "")
        self.push_enabled = bool(self.push_deprecated_key)
        
        # Email enabled
        self.email_enabled = bool(self.smtp_email and self.smtp_password)
        
        # Load notification history
        self.notifications = self._load_notifications()
        
        logger.info(f"Notification Manager initialized - Email: {self.email_enabled}, WhatsApp: {self.whatsapp_enabled}, Push: {self.push_enabled}")

    def _load_notifications(self) -> Dict:
        """Load notification history"""
        try:
            if NOTIFICATIONS_FILE.exists():
                with open(NOTIFICATIONS_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading notifications: {e}")
        return {"history": [], "scheduled": [], "preferences": {}}

    def _save_notifications(self):
        """Save notification history"""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(NOTIFICATIONS_FILE, 'w') as f:
                json.dump(self.notifications, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving notifications: {e}")

    def _add_to_history(self, notification_type: str, recipient: str, subject: str, status: str):
        """Add notification to history"""
        entry = {
            "id": len(self.notifications.get("history", [])) + 1,
            "type": notification_type,
            "recipient": recipient,
            "subject": subject,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        if "history" not in self.notifications:
            self.notifications["history"] = []
        self.notifications["history"].append(entry)
        
        # Keep only last 100 notifications
        if len(self.notifications["history"]) > 100:
            self.notifications["history"] = self.notifications["history"][-100:]
        
        self._save_notifications()

    # ========== EMAIL NOTIFICATIONS ==========
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: str = None,
        priority: str = "normal"
    ) -> Dict:
        """Send email notification"""
        if not self.email_enabled:
            logger.warning("Email notifications disabled")
            return {"success": False, "error": "Email not configured"}

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_email
            msg['To'] = to_email
            msg['X-Priority'] = '1' if priority == "urgent" else '3'
            
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            if html:
                html_part = MIMEText(html, 'html')
                msg.attach(html_part)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._send_smtp(msg)
            )
            
            self._add_to_history("email", to_email, subject, "sent")
            logger.info(f"Email sent to {to_email}: {subject}")
            return {"success": True, "message": "Email sent successfully"}
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            self._add_to_history("email", to_email, subject, f"failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def _send_smtp(self, msg):
        """Send via SMTP"""
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_email, self.smtp_password)
            server.send_message(msg)

    # ========== SMS NOTIFICATIONS ==========
    async def send_sms(self, to_phone: str, message: str) -> Dict:
        """Send SMS notification using Twilio"""
        if not self.twilio_sid or not self.twilio_token:
            logger.warning("SMS not configured")
            return {"success": False, "error": "SMS not configured"}

        if not REQUESTS_AVAILABLE:
            return {"success": False, "error": "requests library not available"}

        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_sid}/Messages.json"
            
            data = {
                "To": to_phone,
                "From": self.twilio_phone,
                "Body": message[:1600]  # SMS limit
            }
            
            auth = (self.twilio_sid, self.twilio_token)
            
            response = requests.post(url, data=data, auth=auth, timeout=30)
            
            if response.status_code in [200, 201]:
                self._add_to_history("sms", to_phone, message[:50], "sent")
                return {"success": True, "message": "SMS sent successfully"}
            else:
                error = response.json()
                logger.error(f"SMS error: {error}")
                return {"success": False, "error": error.get("message", "SMS failed")}
                
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return {"success": False, "error": str(e)}

    # ========== WHATSAPP NOTIFICATIONS ==========
    async def send_whatsapp(self, to_phone: str, message: str) -> Dict:
        """Send WhatsApp message using Twilio"""
        if not self.whatsapp_enabled:
            logger.warning("WhatsApp not configured")
            return {"success": False, "error": "WhatsApp not configured"}

        if not REQUESTS_AVAILABLE:
            return {"success": False, "error": "requests library not available"}

        try:
            # Format phone for WhatsApp (add whatsapp: prefix)
            to_whatsapp = f"whatsapp:{to_phone}"
            from_whatsapp = f"whatsapp:{self.twilio_phone}"
            
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_sid}/Messages.json"
            
            data = {
                "To": to_whatsapp,
                "From": from_whatsapp,
                "Body": message[:1600]
            }
            
            auth = (self.twilio_sid, self.twilio_token)
            
            response = requests.post(url, data=data, auth=auth, timeout=30)
            
            if response.status_code in [200, 201]:
                self._add_to_history("whatsapp", to_phone, message[:50], "sent")
                return {"success": True, "message": "WhatsApp sent successfully"}
            else:
                error = response.json()
                return {"success": False, "error": error.get("message", "WhatsApp failed")}
                
        except Exception as e:
            logger.error(f"Failed to send WhatsApp: {e}")
            return {"success": False, "error": str(e)}

    # ========== PUSH NOTIFICATIONS ==========
    async def send_push(self, token: str, title: str, body: str, data: Dict = None) -> Dict:
        """Send push notification (Firebase Cloud Messaging)"""
        if not self.push_enabled:
            logger.warning("Push notifications not configured")
            return {"success": False, "error": "Push not configured"}

        if not REQUESTS_AVAILABLE:
            return {"success": False, "error": "requests library not available"}

        try:
            # Legacy FCM API (deprecated but still works)
            fcm_url = "https://fcm.googleapis.com/fcm/send"
            
            payload = {
                "to": token,
                "notification": {
                    "title": title,
                    "body": body
                },
                "data": data or {}
            }
            
            headers = {
                "Authorization": f"key={self.push_deprecated_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(fcm_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success", 0) > 0:
                    self._add_to_history("push", token, title, "sent")
                    return {"success": True, "message": "Push sent successfully"}
                else:
                    return {"success": False, "error": "Push failed"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Failed to send push: {e}")
            return {"success": False, "error": str(e)}

    # ========== MULTI-CHANNEL NOTIFICATION ==========
    async def send_notification(
        self,
        channels: List[str],
        recipient: str,
        subject: str,
        message: str,
        html: str = None,
        phone: str = None,
        push_token: str = None
    ) -> Dict:
        """Send notification to multiple channels"""
        results = {}
        
        for channel in channels:
            channel = channel.lower()
            
            if channel == "email":
                result = await self.send_email(recipient, subject, message, html)
                results["email"] = result
                
            elif channel == "sms" and phone:
                result = await self.send_sms(phone, message)
                results["sms"] = result
                
            elif channel == "whatsapp" and phone:
                result = await self.send_whatsapp(phone, message)
                results["whatsapp"] = result
                
            elif channel == "push" and push_token:
                result = await self.send_push(push_token, subject, message)
                results["push"] = result
        
        # Check if at least one succeeded
        success = any(r.get("success", False) for r in results.values())
        
        return {
            "success": success,
            "channels": results
        }

    # ========== TEMPLATE NOTIFICATIONS ==========
    async def notify_reminder(
        self,
        notification_type: str,
        recipient: str,
        reminder_data: Dict,
        phone: str = None
    ) -> Dict:
        """Send reminder notification with templates"""
        templates = {
            "health": {
                "email_subject": "🏃 Health Reminder - Chat&Talk GPT",
                "sms_template": "🏃 Reminder: {message}. Stay healthy with Chat&Talk GPT!",
            },
            "alarm": {
                "email_subject": "⏰ Alarm Reminder - Chat&Talk GPT",
                "sms_template": "⏰ Reminder: {message}. Your AI assistant",
            },
            "task": {
                "email_subject": "✅ Task Reminder - Chat&Talk GPT",
                "sms_template": "✅ Task: {message}. Don't forget!",
            },
            "meeting": {
                "email_subject": "📅 Meeting Reminder - Chat&Talk GPT",
                "sms_template": "📅 Meeting: {message}. Starting soon!",
            },
            "weather": {
                "email_subject": "🌤️ Weather Alert - Chat&Talk GPT",
                "sms_template": "🌤️ Weather: {message}. Stay prepared!",
            },
            "custom": {
                "email_subject": "🔔 Notification - Chat&Talk GPT",
                "sms_template": "🔔 {message}",
            }
        }
        
        template = templates.get(notification_type, templates["custom"])
        message = reminder_data.get("message", "You have a reminder!")
        
        results = {}
        
        # Send email
        if self.email_enabled and recipient:
            subject = template["email_subject"]
            body = f"""
{ message }

---
This is an automated reminder from Chat&Talk GPT Personal Assistant
            """
            html_body = f"""
<html>
<body style="font-family: Arial, padding: 20px;">
    <h2 style="color: #6c5ce7;">🔔 Reminder</h2>
    <p style="font-size: 16px;">{message}</p>
    <hr>
    <p style="color: #666; font-size: 12px;">
        Sent from Chat&Talk GPT Personal Assistant
    </p>
</body>
</html>
            """
            results["email"] = await self.send_email(recipient, subject, body, html_body)
        
        # Send SMS
        if phone:
            sms_message = template["sms_template"].format(message=message)
            results["sms"] = await self.send_sms(phone, sms_message)
        
        success = any(r.get("success", False) for r in results.values())
        return {"success": success, "results": results}

    # ========== NOTIFICATION HISTORY ==========
    def get_history(self, limit: int = 20) -> List[Dict]:
        """Get notification history"""
        history = self.notifications.get("history", [])
        return history[-limit:]

    def get_stats(self) -> Dict:
        """Get notification statistics"""
        history = self.notifications.get("history", [])
        
        stats = {
            "total": len(history),
            "by_type": {},
            "by_status": {},
            "recent": history[-5:] if history else []
        }
        
        for entry in history:
            notif_type = entry.get("type", "unknown")
            status = entry.get("status", "unknown")
            
            stats["by_type"][notif_type] = stats["by_type"].get(notif_type, 0) + 1
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        
        return stats

    # ========== USER PREFERENCES ==========
    def set_preferences(self, user_id: str, preferences: Dict) -> Dict:
        """Set user notification preferences"""
        if "preferences" not in self.notifications:
            self.notifications["preferences"] = {}
        
        self.notifications["preferences"][user_id] = preferences
        self._save_notifications()
        
        return preferences

    def get_preferences(self, user_id: str) -> Dict:
        """Get user notification preferences"""
        defaults = {
            "email_enabled": True,
            "sms_enabled": False,
            "whatsapp_enabled": False,
            "push_enabled": False,
            "reminder_enabled": True
        }
        
        user_prefs = self.notifications.get("preferences", {}).get(user_id, {})
        return {**defaults, **user_prefs}


# Singleton instance
notification_manager = NotificationManager()
