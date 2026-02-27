"""
Chat&Talk GPT - Email Client
Send and receive emails via IMAP/SMTP
Supports multiple email providers and attachments
"""
import os
import json
import logging
import base64
import email
from typing import Optional, Dict, Any, List
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import imaplib
import smtplib

logger = logging.getLogger("EmailClient")

# Try to import email libraries
try:
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    logger.warning("Email libraries not available")


class EmailClient:
    """
    Email Client for sending and receiving emails
    
    Features:
    - SMTP email sending
    - IMAP email receiving
    - Attachment support
    - Multiple provider support (Gmail, Outlook, Yahoo, etc.)
    - HTML email support
    - Email templates
    """
    
    # Email provider configurations
    PROVIDERS = {
        "gmail": {
            "smtp": "smtp.gmail.com",
            "smtp_port": 587,
            "imap": "imap.gmail.com",
            "imap_port": 993
        },
        "outlook": {
            "smtp": "smtp.office365.com",
            "smtp_port": 587,
            "imap": "outlook.office365.com",
            "imap_port": 993
        },
        "yahoo": {
            "smtp": "smtp.mail.yahoo.com",
            "smtp_port": 587,
            "imap": "imap.mail.yahoo.com",
            "imap_port": 993
        },
        "custom": {
            "smtp": None,
            "smtp_port": 587,
            "imap": None,
            "imap_port": 993
        }
    }
    
    def __init__(self, provider: str = "gmail"):
        """
        Initialize Email Client
        
        Args:
            provider: Email provider ('gmail', 'outlook', 'yahoo', 'custom')
        """
        self.provider = provider
        self.smtp_connection = None
        self.imap_connection = None
        self.config = self.PROVIDERS.get(provider, self.PROVIDERS["custom"])
        
        logger.info(f"Email Client initialized for {provider}")
    
    def configure(
        self,
        email_address: str,
        password: str,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        imap_server: Optional[str] = None,
        imap_port: Optional[int] = None
    ):
        """
        Configure email account
        
        Args:
            email_address: Your email address
            password: App password or account password
            smtp_server: Custom SMTP server (optional)
            smtp_port: Custom SMTP port (optional)
            imap_server: Custom IMAP server (optional)
            imap_port: Custom IMAP port (optional)
        """
        self.email_address = email_address
        self.password = password
        
        if smtp_server:
            self.config["smtp"] = smtp_server
        if smtp_port:
            self.config["smtp_port"] = smtp_port
        if imap_server:
            self.config["imap"] = imap_server
        if imap_port:
            self.config["imap_port"] = imap_port
    
    def connect_smtp(self) -> Dict[str, Any]:
        """
        Connect to SMTP server
        
        Returns:
            Connection status
        """
        try:
            if not hasattr(self, 'email_address'):
                return {
                    "success": False,
                    "error": "Email not configured. Call configure() first."
                }
            
            # Create SMTP connection
            self.smtp_connection = smtplib.SMTP(
                self.config["smtp"],
                self.config["smtp_port"]
            )
            
            # Start TLS
            self.smtp_connection.starttls()
            
            # Login
            self.smtp_connection.login(self.email_address, self.password)
            
            logger.info(f"SMTP connected to {self.config['smtp']}")
            
            return {
                "success": True,
                "message": "Connected to SMTP server"
            }
            
        except Exception as e:
            logger.error(f"SMTP connection error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def connect_imap(self) -> Dict[str, Any]:
        """
        Connect to IMAP server
        
        Returns:
            Connection status
        """
        try:
            if not hasattr(self, 'email_address'):
                return {
                    "success": False,
                    "error": "Email not configured. Call configure() first."
                }
            
            # Create IMAP connection
            self.imap_connection = imaplib.IMAP4_SSL(
                self.config["imap"],
                self.config["imap_port"]
            )
            
            # Login
            self.imap_connection.login(self.email_address, self.password)
            
            logger.info(f"IMAP connected to {self.config['imap']}")
            
            return {
                "success": True,
                "message": "Connected to IMAP server"
            }
            
        except Exception as e:
            logger.error(f"IMAP connection error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_email(
        self,
        to_address: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        is_html: bool = False
    ) -> Dict[str, Any]:
        """
        Send an email
        
        Args:
            to_address: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            html_body: Email body (HTML)
            cc: CC recipients
            bcc: BCC recipients
            attachments: List of attachments
            is_html: Whether body is HTML
            
        Returns:
            Send status
        """
        try:
            # Connect if not connected
            if not self.smtp_connection:
                result = self.connect_smtp()
                if not result.get("success"):
                    return result
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_address
            msg['To'] = to_address
            msg['Subject'] = subject
            msg['Date'] = email.utils.formatdate()
            
            if cc:
                msg['Cc'] = ", ".join(cc)
            if bcc:
                msg['Bcc'] = ", ".join(bcc)
            
            # Add plain text body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add HTML body if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            elif is_html:
                msg.attach(MIMEText(body, 'html'))
            
            # Add attachments
            if attachments:
                for att in attachments:
                    self._add_attachment(msg, att)
            
            # Send email
            recipients = [to_address]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            
            self.smtp_connection.sendmail(
                self.email_address,
                recipients,
                msg.as_string()
            )
            
            logger.info(f"Email sent to {to_address}")
            
            return {
                "success": True,
                "message": f"Email sent to {to_address}",
                "to": to_address,
                "subject": subject
            }
            
        except Exception as e:
            logger.error(f"Send email error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]):
        """Add attachment to email"""
        try:
            filename = attachment.get("filename", "attachment")
            content = attachment.get("content")  # Base64 encoded or raw bytes
            
            # Decode base64 if needed
            if isinstance(content, str):
                content = base64.b64decode(content)
            
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(content)
            encoders.encode_base64(part)
            
            # Add filename header
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            
            msg.attach(part)
            
        except Exception as e:
            logger.error(f"Add attachment error: {e}")
    
    def send_template_email(
        self,
        to_address: str,
        template_name: str,
        template_data: Dict[str, Any],
        subject: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send email using a template
        
        Args:
            to_address: Recipient email address
            template_name: Name of email template
            template_data: Data to fill in template
            subject: Email subject (optional, can be in template)
            
        Returns:
            Send status
        """
        # Load template
        templates = {
            "welcome": {
                "subject": "Welcome to Chat&Talk GPT!",
                "body": """Hello {name},

Welcome to Chat&Talk GPT! We're excited to have you on board.

Your account has been created successfully with email: {email}

Get started by exploring our features:
- Voice commands
- Smart reminders
- Task management
- And much more!

Best regards,
The Chat&Talk GPT Team
"""
            },
            "reminder": {
                "subject": "Reminder: {title}",
                "body": """Hello {name},

This is a reminder for:

{title}

Description: {description}

Time: {time}

Best regards,
Chat&Talk GPT
"""
            },
            "notification": {
                "subject": "Notification from Chat&Talk GPT",
                "body": """Hello {name},

You have a new notification:

{message}

Best regards,
Chat&Talk GPT
"""
            }
        }
        
        template = templates.get(template_name)
        if not template:
            return {
                "success": False,
                "error": f"Template '{template_name}' not found"
            }
        
        # Fill template
        try:
            body = template["body"].format(**template_data)
            email_subject = subject or template["subject"].format(**template_data)
            
            return self.send_email(
                to_address=to_address,
                subject=email_subject,
                body=body
            )
            
        except KeyError as e:
            return {
                "success": False,
                "error": f"Missing template data: {e}"
            }
    
    def fetch_emails(
        self,
        folder: str = "INBOX",
        limit: int = 10,
        search_criteria: Optional[str] = None,
        unread_only: bool = False
    ) -> Dict[str, Any]:
        """
        Fetch emails from inbox
        
        Args:
            folder: Email folder to fetch from
            limit: Maximum number of emails
            search_criteria: IMAP search criteria
            unread_only: Only fetch unread emails
            
        Returns:
            List of emails
        """
        try:
            # Connect if not connected
            if not self.imap_connection:
                result = self.connect_imap()
                if not result.get("success"):
                    return result
            
            # Select folder
            status, _ = self.imap_connection.select(folder)
            if status != 'OK':
                return {
                    "success": False,
                    "error": f"Could not select folder: {folder}"
                }
            
            # Build search criteria
            if search_criteria:
                criteria = search_criteria
            elif unread_only:
                criteria = "UNSEEN"
            else:
                criteria = "ALL"
            
            # Search emails
            status, email_ids = self.imap_connection.search(None, criteria)
            if status != 'OK':
                return {
                    "success": False,
                    "error": "Could not search emails"
                }
            
            email_ids = email_ids[0].split()
            email_ids = email_ids[-limit:]  # Get last 'limit' emails
            
            emails = []
            for email_id in email_ids:
                email_data = self._fetch_single_email(email_id)
                if email_data:
                    emails.append(email_data)
            
            return {
                "success": True,
                "count": len(emails),
                "emails": emails
            }
            
        except Exception as e:
            logger.error(f"Fetch emails error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _fetch_single_email(self, email_id: bytes) -> Optional[Dict[str, Any]]:
        """Fetch a single email by ID"""
        try:
            status, msg_data = self.imap_connection.fetch(email_id, '(RFC822)')
            if status != 'OK':
                return None
            
            msg = email.message_from_bytes(msg_data[0][1])
            
            # Parse email
            email_data = {
                "id": email_id.decode(),
                "from": msg.get("From"),
                "to": msg.get("To"),
                "subject": msg.get("Subject"),
                "date": msg.get("Date"),
                "body": "",
                "html_body": "",
                "attachments": []
            }
            
            # Parse message body
            if msg.is_multipart:
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        email_data["body"] = part.get_payload(decode=True).decode()
                    elif content_type == "text/html":
                        email_data["html_body"] = part.get_payload(decode=True).decode()
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    email_data["body"] = payload.decode()
            
            # Parse attachments
            for part in msg.walk():
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    if filename:
                        attachment_data = part.get_payload(decode=True)
                        email_data["attachments"].append({
                            "filename": filename,
                            "size": len(attachment_data) if attachment_data else 0
                        })
            
            return email_data
            
        except Exception as e:
            logger.error(f"Fetch single email error: {e}")
            return None
    
    def mark_as_read(self, email_id: str) -> Dict[str, Any]:
        """Mark email as read"""
        try:
            if not self.imap_connection:
                result = self.connect_imap()
                if not result.get("success"):
                    return result
            
            self.imap_connection.store(email_id, '+FLAGS', '\\Seen')
            
            return {
                "success": True,
                "message": "Email marked as read"
            }
            
        except Exception as e:
            logger.error(f"Mark as read error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_email(self, email_id: str) -> Dict[str, Any]:
        """Delete an email"""
        try:
            if not self.imap_connection:
                result = self.connect_imap()
                if not result.get("success"):
                    return result
            
            self.imap_connection.store(email_id, '+FLAGS', '\\Deleted')
            self.imap_connection.expunge()
            
            return {
                "success": True,
                "message": "Email deleted"
            }
            
        except Exception as e:
            logger.error(f"Delete email error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def disconnect(self):
        """Disconnect from email servers"""
        try:
            if self.smtp_connection:
                self.smtp_connection.quit()
                self.smtp_connection = None
            
            if self.imap_connection:
                self.imap_connection.close()
                self.imap_connection.logout()
                self.imap_connection = None
            
            logger.info("Email connections closed")
            
        except Exception as e:
            logger.error(f"Disconnect error: {e}")


# Singleton instance
email_client = EmailClient()


# Standalone functions
def send_email(*args, **kwargs) -> Dict[str, Any]:
    """Standalone function to send email"""
    return email_client.send_email(*args, **kwargs)


def fetch_emails(*args, **kwargs) -> Dict[str, Any]:
    """Standalone function to fetch emails"""
    return email_client.fetch_emails(*args, **kwargs)
