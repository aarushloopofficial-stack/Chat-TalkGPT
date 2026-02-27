"""
Chat&Talk GPT - Activity Tracking System
Tracks all user activities and interactions
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger("ActivityTracker")


class ActivityTracker:
    """Tracks and stores all user activities"""
    
    def __init__(self, activity_file: str = ".json"):
        self.activity_file = Path("memory/activity_log.json")
        self.activity_file.parent.mkdir(parents=True, exist_ok=True)
        self.activities = self._load_activities()
        
        logger.info(f"ActivityTracker initialized with {len(self.activities)} records")
    
    def _load_activities(self) -> List[Dict[str, Any]]:
        """Load activities from file"""
        try:
            if self.activity_file.exists():
                with open(self.activity_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data)} activity records")
                    return data
        except Exception as e:
            logger.warning(f"Could not load activities: {e}")
        return []
    
    def _save_activities(self):
        """Save activities to file"""
        try:
            with open(self.activity_file, "w", encoding="utf-8") as f:
                json.dump(self.activities, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving activities: {e}")
    
    def log_activity(self, activity_type: str, user_data: Dict[str, Any], 
                    details: Dict[str, Any] = None):
        """Log a new activity"""
        activity = {
            "id": len(self.activities) + 1,
            "timestamp": datetime.now().isoformat(),
            "type": activity_type,
            "user": {
                "name": user_data.get("name", "Unknown"),
                "email": user_data.get("email", ""),
                "session_id": user_data.get("session_id", "")
            },
            "details": details or {}
        }
        
        self.activities.append(activity)
        
        # Keep only last 10000 activities to prevent file from getting too big
        if len(self.activities) > 10000:
            self.activities = self.activities[-10000:]
        
        self._save_activities()
        
        logger.info(f"Activity logged: {activity_type} by {user_data.get('name', 'Unknown')}")
        
        return activity
    
    # Activity Types
    def log_user_login(self, user_data: Dict[str, Any]):
        """Log user login"""
        return self.log_activity("USER_LOGIN", user_data, {
            "login_method": "website",
            "ip_address": ""
        })
    
    def log_ai_message(self, user_data: Dict[str, Any], message: str, response: str):
        """Log AI chat interaction"""
        return self.log_activity("AI_CHAT", user_data, {
            "user_message": message,
            "ai_response": response,
            "message_length": len(message),
            "response_length": len(response)
        })
    
    def log_voice_command(self, user_data: Dict[str, Any], command: str, result: str):
        """Log voice command"""
        return self.log_activity("VOICE_COMMAND", user_data, {
            "command": command,
            "result": result
        })
    
    def log_voice_interaction(self, user_data: Dict[str, Any], transcript: str, 
                             response: str, is_command: bool):
        """Log voice interaction"""
        return self.log_activity("VOICE_INTERACTION", user_data, {
            "transcript": transcript,
            "response": response,
            "is_command": is_command
        })
    
    def log_app_opened(self, user_data: Dict[str, Any], app_name: str):
        """Log when user opens an app"""
        return self.log_activity("APP_OPENED", user_data, {
            "app_name": app_name
        })
    
    def log_settings_change(self, user_data: Dict[str, Any], setting: str, value: str):
        """Log settings change"""
        return self.log_activity("SETTINGS_CHANGE", user_data, {
            "setting": setting,
            "new_value": value
        })
    
    def log_error(self, user_data: Dict[str, Any], error_type: str, error_message: str):
        """Log error occurrence"""
        return self.log_activity("ERROR", user_data, {
            "error_type": error_type,
            "error_message": error_message
        })
    
    def log_voice_settings_change(self, user_data: Dict[str, Any], voice: str):
        """Log voice preference change"""
        return self.log_activity("VOICE_CHANGE", user_data, {
            "selected_voice": voice
        })
    
    def log_language_change(self, user_data: Dict[str, Any], language: str):
        """Log language preference change"""
        return self.log_activity("LANGUAGE_CHANGE", user_data, {
            "selected_language": language
        })
    
    def get_user_activities(self, user_email: str = None, limit: int = 100) -> List[Dict]:
        """Get activities, optionally filtered by user"""
        if user_email:
            filtered = [a for a in self.activities if a.get("user", {}).get("email") == user_email]
            return filtered[-limit:]
        return self.activities[-limit:]
    
    def get_activities_by_type(self, activity_type: str, limit: int = 100) -> List[Dict]:
        """Get activities by type"""
        filtered = [a for a in self.activities if a.get("type") == activity_type]
        return filtered[-limit:]
    
    def get_all_activities(self) -> List[Dict]:
        """Get all activities"""
        return self.activities
    
    def clear_user_activities(self, user_email: str = None):
        """Clear activities for a specific user or all if email is None"""
        if user_email:
            self.activities = [a for a in self.activities if a.get("user", {}).get("email") != user_email]
        else:
            self.activities = []
        
        self._save_activities()
        logger.info(f"Activities cleared{' for ' + user_email if user_email else ' for all users'}")
        return True
    
    def get_activity_summary(self) -> Dict[str, Any]:
        """Get summary of activities"""
        total = len(self.activities)
        
        # Count by type
        type_counts = {}
        for activity in self.activities:
            act_type = activity.get("type", "UNKNOWN")
            type_counts[act_type] = type_counts.get(act_type, 0) + 1
        
        # Count unique users
        unique_users = len(set(a.get("user", {}).get("email", "") for a in self.activities))
        
        # Get recent activities
        recent = self.activities[-10:] if self.activities else []
        
        return {
            "total_activities": total,
            "unique_users": unique_users,
            "activity_types": type_counts,
            "recent_activities": recent
        }
    
    def export_to_csv(self, filepath: str = "memory/activity_export.csv"):
        """Export activities to CSV"""
        import csv
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                if not self.activities:
                    return False
                
                # Get all possible fields
                fieldnames = ['id', 'timestamp', 'type', 'user_name', 'user_email', 
                             'details']
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for activity in self.activities:
                    row = {
                        'id': activity.get('id', ''),
                        'timestamp': activity.get('timestamp', ''),
                        'type': activity.get('type', ''),
                        'user_name': activity.get('user', {}).get('name', ''),
                        'user_email': activity.get('user', {}).get('email', ''),
                        'details': json.dumps(activity.get('details', {}))
                    }
                    writer.writerow(row)
            
            logger.info(f"Exported {len(self.activities)} activities to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False


# Initialize activity tracker
activity_tracker = ActivityTracker()
