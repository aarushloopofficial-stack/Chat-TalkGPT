"""
Chat&Talk GPT - SMS Manager
Send and receive SMS messages via Twilio and other providers
Supports bulk messaging and scheduled SMS
"""
import os
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import time

logger = logging.getLogger("SMSManager")

# Try to import Twilio
TWILIO_AVAILABLE = False
try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    TWILIO_AVAILABLE = True
    logger.info("Twilio is available")
except ImportError:
    logger.warning("Twilio not available - install twilio package")

# Try to import Vonage
VONAGE_AVAILABLE = False
try:
    import vonage
    VONAGE_AVAILABLE = True
    logger.info("Vonage (Nexmo) is available")
except ImportError:
    logger.warning("Vonage not available")


class SMSManager:
    """
    SMS Manager for sending and receiving SMS
    
    Features:
    - Multiple provider support (Twilio, Vonage)
    - Bulk messaging
    - Scheduled SMS
    - MMS support (media messages)
    - Message templates
    - Delivery status tracking
    """
    
    def __init__(self, provider: str = "twilio"):
        """
        Initialize SMS Manager
        
        Args:
            provider: SMS provider ('twilio', 'vonage')
        """
        self.provider = provider
        self.twilio_client = None
        self.vonage_client = None
        self.scheduled_messages = []
        
        logger.info(f"SMS Manager initialized for {provider}")
    
    def configure(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        application_id: Optional[str] = None
    ):
        """
        Configure SMS provider
        
        Args:
            account_sid: Twilio Account SID
            auth_token: Twilio Auth Token
            from_number: Your Twilio phone number
            api_key: Vonage API key
            api_secret: Vonage API secret
            application_id: Vonage Application ID
        """
        self.account_sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = auth_token or os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = from_number or os.getenv("TWILIO_PHONE_NUMBER")
        
        self.api_key = api_key or os.getenv("VONAGE_API_KEY")
        self.api_secret = api_secret or os.getenv("VONAGE_API_SECRET")
        self.vonage_application_id = application_id or os.getenv("VONAGE_APPLICATION_ID")
        
        # Initialize Twilio client if configured
        if TWILIO_AVAILABLE and self.account_sid and self.auth_token:
            try:
                self.twilio_client = Client(self.account_sid, self.auth_token)
                logger.info("Twilio client initialized")
            except Exception as e:
                logger.error(f"Twilio initialization error: {e}")
        
        # Initialize Vonage client if configured
        if VONAGE_AVAILABLE and self.api_key and self.api_secret:
            try:
                self.vonage_client = vonage.Client(
                    key=self.api_key,
                    secret=self.api_secret
                )
                logger.info("Vonage client initialized")
            except Exception as e:
                logger.error(f"Vonage initialization error: {e}")
    
    def send_sms(
        self,
        to_number: str,
        message: str,
        media_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an SMS message
        
        Args:
            to_number: Recipient phone number (E.164 format)
            message: Message text
            media_url: URL for MMS media (optional)
            
        Returns:
            Send status with message ID
        """
        try:
            # Validate phone number format
            if not to_number.startswith('+'):
                return {
                    "success": False,
                    "error": "Phone number must be in E.164 format (e.g., +1234567890)"
                }
            
            if self.provider == "twilio":
                return self._send_twilio_sms(to_number, message, media_url)
            elif self.provider == "vonage":
                return self._send_vonage_sms(to_number, message)
            else:
                return {
                    "success": False,
                    "error": f"Unknown provider: {self.provider}"
                }
                
        except Exception as e:
            logger.error(f"Send SMS error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _send_twilio_sms(
        self,
        to_number: str,
        message: str,
        media_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send SMS via Twilio"""
        if not self.twilio_client:
            if not self.account_sid or not self.auth_token:
                return {
                    "success": False,
                    "error": "Twilio not configured. Call configure() first."
                }
            self.twilio_client = Client(self.account_sid, self.auth_token)
        
        try:
            if media_url:
                # Send MMS
                msg = self.twilio_client.messages.create(
                    body=message,
                    from_=self.from_number,
                    to=to_number,
                    media_url=[media_url]
                )
            else:
                # Send SMS
                msg = self.twilio_client.messages.create(
                    body=message,
                    from_=self.from_number,
                    to=to_number
                )
            
            logger.info(f"SMS sent via Twilio: {msg.sid}")
            
            return {
                "success": True,
                "message_id": msg.sid,
                "status": msg.status,
                "to": to_number,
                "from": self.from_number
            }
            
        except TwilioRestException as e:
            logger.error(f"Twilio error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _send_vonage_sms(self, to_number: str, message: str) -> Dict[str, Any]:
        """Send SMS via Vonage"""
        if not self.vonage_client:
            if not self.api_key or not self.api_secret:
                return {
                    "success": False,
                    "error": "Vonage not configured. Call configure() first."
                }
            self.vonage_client = vonage.Client(
                key=self.api_key,
                secret=self.api_secret
            )
        
        try:
            response = self.vonage_client.sms.send_message({
                "from": self.from_number or "Chat&TalkGPT",
                "to": to_number.replace("+", ""),
                "text": message
            })
            
            messages = response.get("messages", [])
            if messages:
                result = messages[0]
                if result.get("status") == "0":
                    return {
                        "success": True,
                        "message_id": result.get("message-id"),
                        "to": to_number
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("error-text", "Unknown error")
                    }
            
            return {
                "success": False,
                "error": "No response from Vonage"
            }
            
        except Exception as e:
            logger.error(f"Vonage error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_bulk_sms(
        self,
        recipients: List[Dict[str, Any]],
        message: str,
        delay_seconds: int = 1
    ) -> Dict[str, Any]:
        """
        Send SMS to multiple recipients
        
        Args:
            recipients: List of recipient dicts with 'phone' and optional 'name'
            message: Message text
            delay_seconds: Delay between messages
            
        Returns:
            Bulk send status
        """
        results = {
            "success": True,
            "total": len(recipients),
            "sent": 0,
            "failed": 0,
            "details": []
        }
        
        for recipient in recipients:
            phone = recipient.get("phone")
            if not phone:
                results["failed"] += 1
                results["details"].append({
                    "phone": phone,
                    "success": False,
                    "error": "No phone number provided"
                })
                continue
            
            # Personalize message if name provided
            msg = message
            if "name" in recipient:
                msg = message.replace("{name}", recipient["name"])
            
            # Send SMS
            result = self.send_sms(phone, msg)
            
            if result.get("success"):
                results["sent"] += 1
            else:
                results["failed"] += 1
            
            results["details"].append({
                "phone": phone,
                "success": result.get("success", False),
                "message_id": result.get("message_id"),
                "error": result.get("error")
            })
            
            # Delay between messages
            if delay_seconds > 0:
                time.sleep(delay_seconds)
        
        results["success"] = results["failed"] == 0
        
        return results
    
    def schedule_sms(
        self,
        to_number: str,
        message: str,
        scheduled_time: datetime,
        media_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Schedule an SMS to be sent later
        
        Args:
            to_number: Recipient phone number
            message: Message text
            scheduled_time: When to send the message
            media_url: URL for MMS (optional)
            
        Returns:
            Schedule confirmation
        """
        try:
            # Validate scheduled time
            if scheduled_time <= datetime.now():
                return {
                    "success": False,
                    "error": "Scheduled time must be in the future"
                }
            
            # Store scheduled message
            schedule_id = f"sched_{int(time.time())}_{len(self.scheduled_messages)}"
            
            scheduled_msg = {
                "id": schedule_id,
                "to": to_number,
                "message": message,
                "scheduled_time": scheduled_time.isoformat(),
                "media_url": media_url,
                "status": "scheduled"
            }
            
            self.scheduled_messages.append(scheduled_msg)
            
            logger.info(f"SMS scheduled: {schedule_id}")
            
            return {
                "success": True,
                "schedule_id": schedule_id,
                "scheduled_time": scheduled_time.isoformat(),
                "message": "SMS scheduled successfully"
            }
            
        except Exception as e:
            logger.error(f"Schedule SMS error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def cancel_scheduled_sms(self, schedule_id: str) -> Dict[str, Any]:
        """Cancel a scheduled SMS"""
        try:
            for msg in self.scheduled_messages:
                if msg["id"] == schedule_id:
                    msg["status"] = "cancelled"
                    return {
                        "success": True,
                        "message": f"Scheduled SMS {schedule_id} cancelled"
                    }
            
            return {
                "success": False,
                "error": "Schedule not found"
            }
            
        except Exception as e:
            logger.error(f"Cancel scheduled SMS error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_scheduled_sms(self) -> List[Dict[str, Any]]:
        """Get all scheduled SMS messages"""
        return [msg for msg in self.scheduled_messages if msg["status"] == "scheduled"]
    
    def process_scheduled_sms(self):
        """Process and send scheduled SMS messages that are due"""
        now = datetime.now()
        
        for msg in self.scheduled_messages:
            if msg["status"] == "scheduled":
                scheduled_time = datetime.fromisoformat(msg["scheduled_time"])
                if scheduled_time <= now:
                    # Send the SMS
                    result = self.send_sms(msg["to"], msg["message"], msg.get("media_url"))
                    msg["status"] = "sent" if result.get("success") else "failed"
                    msg["result"] = result
    
    def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """
        Get the status of a sent message
        
        Args:
            message_id: Message ID from send response
            
        Returns:
            Message status information
        """
        try:
            if self.provider == "twilio" and self.twilio_client:
                msg = self.twilio_client.messages(message_id).fetch()
                
                return {
                    "success": True,
                    "message_id": msg.sid,
                    "status": msg.status,
                    "to": msg.to,
                    "from": msg.from_,
                    "date_sent": str(msg.date_sent) if msg.date_sent else None,
                    "error_code": msg.error_code,
                    "error_message": msg.error_message
                }
            else:
                return {
                    "success": False,
                    "error": "Status tracking only available for Twilio"
                }
                
        except Exception as e:
            logger.error(f"Get message status error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_template_sms(
        self,
        to_number: str,
        template_name: str,
        template_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send SMS using a template
        
        Args:
            to_number: Recipient phone number
            template_name: Name of template
            template_data: Data to fill in template
            
        Returns:
            Send status
        """
        templates = {
            "reminder": "Reminder: {title} at {time}. {description}",
            "verification": "Your verification code is: {code}. Valid for {minutes} minutes.",
            "alert": "Alert: {message}. Time: {time}",
            "welcome": "Welcome {name}! Thanks for joining Chat&Talk GPT.",
            "appointment": "Appointment reminder: {service} on {date} at {time}.",
            "otp": "Your OTP is {code}. Don't share it with anyone."
        }
        
        template = templates.get(template_name)
        if not template:
            return {
                "success": False,
                "error": f"Template '{template_name}' not found"
            }
        
        try:
            message = template.format(**template_data)
            return self.send_sms(to_number, message)
            
        except KeyError as e:
            return {
                "success": False,
                "error": f"Missing template data: {e}"
            }
    
    def send_otp(
        self,
        to_number: str,
        code_length: int = 6,
        validity_minutes: int = 5
    ) -> Dict[str, Any]:
        """
        Send a one-time password (OTP)
        
        Args:
            to_number: Recipient phone number
            code_length: Length of OTP code
            validity_minutes: How long the code is valid
            
        Returns:
            Send status with generated code
        """
        import random
        
        # Generate random code
        code = ''.join([str(random.randint(0, 9)) for _ in range(code_length)])
        
        # Store code with expiration
        self.otp_store = getattr(self, 'otp_store', {})
        self.otp_store[to_number] = {
            "code": code,
            "expires": datetime.now() + timedelta(minutes=validity_minutes)
        }
        
        # Send SMS
        return self.send_template_sms(
            to_number,
            "otp",
            {"code": code}
        )
    
    def verify_otp(self, to_number: str, code: str) -> Dict[str, Any]:
        """
        Verify an OTP code
        
        Args:
            to_number: Phone number
            code: OTP code to verify
            
        Returns:
            Verification result
        """
        if not hasattr(self, 'otp_store'):
            return {
                "success": False,
                "error": "No OTP found. Request OTP first."
            }
        
        otp_data = self.otp_store.get(to_number)
        if not otp_data:
            return {
                "success": False,
                "error": "No OTP found for this number"
            }
        
        # Check expiration
        if datetime.now() > otp_data["expires"]:
            del self.otp_store[to_number]
            return {
                "success": False,
                "error": "OTP has expired"
            }
        
        # Verify code
        if otp_data["code"] == code:
            del self.otp_store[to_number]
            return {
                "success": True,
                "message": "OTP verified successfully"
            }
        
        return {
            "success": False,
            "error": "Invalid OTP code"
        }


# Singleton instance
sms_manager = SMSManager()


# Standalone functions
def send_sms(*args, **kwargs) -> Dict[str, Any]:
    """Standalone function to send SMS"""
    return sms_manager.send_sms(*args, **kwargs)


def send_otp(*args, **kwargs) -> Dict[str, Any]:
    """Standalone function to send OTP"""
    return sms_manager.send_otp(*args, **kwargs)


def verify_otp(*args, **kwargs) -> Dict[str, Any]:
    """Standalone function to verify OTP"""
    return sms_manager.verify_otp(*args, **kwargs)
