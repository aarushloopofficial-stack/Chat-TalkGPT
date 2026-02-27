"""
Chat&Talk GPT - Security & Moderation System
Detects adult/bad content, notifies admin, and logs to Google Sheets.
"""
import os
import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from typing import Dict, Any, Optional

logger = logging.getLogger("SecuritySystem")

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

# Configuration - Use environment variables in production
# Read from environment variables (matching .env file names)
SMTP_USER = os.getenv("SMTP_EMAIL", "")  # Fixed: was SMTP_USER, now SMTP_EMAIL
SMTP_PASS = os.getenv("SMTP_PASSWORD", "")  # Fixed: was SMTP_PASS, now SMTP_PASSWORD
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "aarushloop273@gmail.com")  # Now reads from env
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

class SecuritySystem:
    def __init__(self):
        self.bad_keywords = [
            "18+", "porn", "sexy", "naked", "xxx", "adult", "fuck", "bitch", "shit", 
            "dick", "pussy", "horny", "sex", "nonsense", "useless", "stupid ai", "galli",
            "idiot", "bastard", "asshole", "motherfucker", "erotica", "onlyfans", "slut", 
            "whore", "blowjob", "cum", "nude", "marry me", "be my girlfriend", "kiss me", 
            "hot stuff", "sexy voice", "darling", "honey", "randi", "saala", "harami",
            "kamina", "sala", "kutte", "hijra", "chutiya", "gaandu", "bakwas"

        ]
        self.hacking_patterns = [
            "<script", "javascript:", "union select", "drop table", "sleep(", 
            "waitfor delay", "exec(", "system(", "bin/sh", "/v1/api", "../"
        ]
        self.blocked_ips = set()
        self.request_logs = {} # ip -> [timestamps]
        self.violation_counts = {} # email -> count
        self.credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
        self.log_sheet_name = "Chat&Talk GPT Violations"
        self.enabled = False
        
        if GSPREAD_AVAILABLE and os.path.exists(self.credentials_file):
            try:
                self._init_sheets()
                self.enabled = True
            except Exception as e:
                logger.error(f"Security GSheets init failed: {e}")

    def is_ip_blocked(self, ip: str) -> bool:
        """Check if an IP is in the blacklist"""
        return ip in self.blocked_ips

    def check_hacking_attempt(self, message: str, ip: str, email: str) -> bool:
        """Scan for SQL injection or Script attacks"""
        msg_lower = message.lower()
        for pattern in self.hacking_patterns:
            if pattern in msg_lower:
                logger.warning(f"🔒 HACKING ATTEMPT DETECTED! IP: {ip}, Pattern: {pattern}")
                self.blocked_ips.add(ip)
                self._notify_admin(email, f"HACKER DETECTED! Pattern: {pattern}", 100, "CRITICAL: HACKING", "Hacker")
                return True
        return False

    def check_rate_limit(self, ip: str) -> bool:
        """Simple rate limiting: Max 30 requests per minute"""
        import time
        now = time.time()
        if ip not in self.request_logs:
            self.request_logs[ip] = []
        
        # Keep only last 60 seconds of logs
        self.request_logs[ip] = [t for t in self.request_logs[ip] if now - t < 60]
        
        if len(self.request_logs[ip]) > 30:
            logger.warning(f"⚠️ Rate limit exceeded for IP: {ip}")
            return False # Limit exceeded
            
        self.request_logs[ip].append(now)
        return True

    def check_content(self, message: str, email: str, user_name: str = "Unknown", ip: str = "0.0.0.0") -> Optional[Dict[str, Any]]:
        """Hyper Security: Checks hacking, rate limit, and bad content."""
        
        # 1. Check if user is already blocked
        if self.is_ip_blocked(ip):
            return {"action": "deny", "message": "⚠️ Access Denied: Your IP has been blacklisted for security violations."}

        # 2. Check for hacking patterns
        if self.check_hacking_attempt(message, ip, email):
            return {"action": "deny", "message": "🚨 Critical Security Alert: Your session has been terminated due to suspicious activity."}

        # 3. Request Rate Limiting
        if not self.check_rate_limit(ip):
            return {"action": "warn", "message": "Rate limit exceeded. Slow down!"}

        # 4. Standard Content Moderation
        message_lower = message.lower()
        is_bad = any(word in message_lower for word in self.bad_keywords)
        
        if is_bad:
            count = self.violation_counts.get(email, 0) + 1
            self.violation_counts[email] = count
            offense_type = "First Offense" if count == 1 else "BLOCK: Second Offense"
            
            # Log & Notify for EVERY violation (as requested)
            self._log_violation(email, message, count, offense_type, user_name)
            self._notify_admin(email, message, count, offense_type, user_name)
            
            if count >= 2:
                self.blocked_ips.add(ip)
                return {"action": "deny", "message": "🚨 Access Denied: You have been permanently blocked for repeated security violations."}
                
            if count == 1:
                return {
                    "action": "warn", 
                    "message": "Don't Say this type of words", 
                    "voice": "Sorry iam not talk about in this topics"
                }
        
        return None

    # (Keep internal methods like _init_sheets, _log_violation, _notify_admin the same but fix logs)
    def _init_sheets(self):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(self.credentials_file, scopes=scope)
        client = gspread.authorize(creds)
        try:
            self.spreadsheet = client.open(self.log_sheet_name)
        except:
            self.spreadsheet = client.create(self.log_sheet_name)
            
        try:
            self.worksheet = self.spreadsheet.sheet1
        except:
            self.worksheet = self.spreadsheet.add_worksheet("Violations", 1000, 5)
            
        if self.worksheet.row_count == 0 or not self.worksheet.cell(1, 1).value:
            self.worksheet.append_row(["Timestamp", "User Name", "User Email", "Message", "Violation Number", "Offense Type"])

    def _log_violation(self, email: str, message: str, count: int, offense_type: str, user_name: str = "Unknown"):
        if self.enabled:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                self.worksheet.append_row([now, user_name, email, message, count, offense_type])
            except Exception as e:
                logger.error(f"Failed to log violation: {e}")

    def _notify_admin(self, user_email: str, message: str, count: int, offense_type: str, user_name: str = "Unknown"):
        if not SMTP_USER or not SMTP_PASS:
            logger.warning("SMTP not configured, skipping notification")
            return

        if "CRITICAL" in offense_type:
            subject = f"� SECURITY BREACH ATTEMPT: {user_name}"
        elif count > 1:
            subject = f"🚨 REPEAT VIOLATION: {user_email}"
        else:
            subject = f"🚨 Security Alert: {user_email}"

        body = f"""HYPER SECURITY ALERT
Status: {offense_type}
User: {user_name} ({user_email})
Count: {count}
Payload: {message}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
SYSTEM ACTION: IP may be blacklisted.
"""
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = ADMIN_EMAIL
        
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
            logger.info(f"Notification sent to admin for security event")
        except Exception as e:
            logger.error(f"Failed to send security email: {e}")

security_system = SecuritySystem()
