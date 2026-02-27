"""
Chat&Talk GPT - Meeting Notes Module
AI-powered meeting notes summarization and management
"""
import os
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger("MeetingNotes")


class MeetingNotesManager:
    """
    Meeting Notes Manager
    
    Features:
    - Create and manage meeting notes
    - AI-powered summarization
    - Action item extraction
    - Meeting transcription
    - Export to multiple formats
    """
    
    def __init__(self, storage_dir: str = "memory/meetings"):
        """Initialize Meeting Notes Manager"""
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.meetings = {}
        self._load_meetings()
        logger.info("Meeting Notes Manager initialized")
    
    def _load_meetings(self):
        """Load meetings from storage"""
        try:
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.json'):
                    with open(os.path.join(self.storage_dir, filename), 'r') as f:
                        meeting = json.load(f)
                        self.meetings[meeting.get('id')] = meeting
        except Exception as e:
            logger.warning(f"Could not load meetings: {e}")
    
    def create_meeting(
        self,
        title: str,
        date: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        agenda: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new meeting
        
        Args:
            title: Meeting title
            date: Meeting date (ISO format)
            attendees: List of attendees
            agenda: Meeting agenda items
            
        Returns:
            Meeting creation result
        """
        try:
            meeting_id = f"meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            meeting = {
                "id": meeting_id,
                "title": title,
                "date": date or datetime.now().isoformat(),
                "attendees": attendees or [],
                "agenda": agenda or [],
                "notes": "",
                "summary": "",
                "action_items": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            self.meetings[meeting_id] = meeting
            self._save_meeting(meeting)
            
            return {
                "success": True,
                "meeting": meeting,
                "message": f"Meeting '{title}' created"
            }
            
        except Exception as e:
            logger.error(f"Create meeting error: {e}")
            return {"success": False, "error": str(e)}
    
    def add_notes(self, meeting_id: str, notes: str) -> Dict[str, Any]:
        """Add notes to a meeting"""
        if meeting_id not in self.meetings:
            return {"success": False, "error": "Meeting not found"}
        
        self.meetings[meeting_id]["notes"] = notes
        self.meetings[meeting_id]["updated_at"] = datetime.now().isoformat()
        self._save_meeting(self.meetings[meeting_id])
        
        return {
            "success": True,
            "message": "Notes added"
        }
    
    def generate_summary(self, meeting_id: str) -> Dict[str, Any]:
        """Generate AI summary of meeting"""
        if meeting_id not in self.meetings:
            return {"success": False, "error": "Meeting not found"}
        
        meeting = self.meetings[meeting_id]
        notes = meeting.get("notes", "")
        
        if not notes:
            return {"success": False, "error": "No notes to summarize"}
        
        # Simple summarization
        lines = notes.split('\n')
        key_points = []
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 20:
                key_points.append(f"- {line[:100]}")
        
        summary = f"Meeting: {meeting['title']}\n"
        summary += f"Date: {meeting['date']}\n\n"
        summary += "Key Points:\n" + "\n".join(key_points[:5])
        
        meeting["summary"] = summary
        meeting["updated_at"] = datetime.now().isoformat()
        self._save_meeting(meeting)
        
        return {
            "success": True,
            "summary": summary
        }
    
    def extract_action_items(self, meeting_id: str) -> Dict[str, Any]:
        """Extract action items from meeting notes"""
        if meeting_id not in self.meetings:
            return {"success": False, "error": "Meeting not found"}
        
        meeting = self.meetings[meeting_id]
        notes = meeting.get("notes", "")
        
        # Simple action item detection
        action_keywords = ["todo", "action", "task", "will", "need to", "should", "must"]
        action_items = []
        
        lines = notes.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in action_keywords):
                action_items.append({
                    "item": line.strip(),
                    "status": "pending"
                })
        
        meeting["action_items"] = action_items
        meeting["updated_at"] = datetime.now().isoformat()
        self._save_meeting(meeting)
        
        return {
            "success": True,
            "action_items": action_items
        }
    
    def get_meeting(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        """Get meeting by ID"""
        return self.meetings.get(meeting_id)
    
    def list_meetings(self) -> List[Dict[str, Any]]:
        """List all meetings"""
        return list(self.meetings.values())
    
    def delete_meeting(self, meeting_id: str) -> Dict[str, Any]:
        """Delete a meeting"""
        if meeting_id not in self.meetings:
            return {"success": False, "error": "Meeting not found"}
        
        del self.meetings[meeting_id]
        
        filepath = os.path.join(self.storage_dir, f"{meeting_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return {
            "success": True,
            "message": "Meeting deleted"
        }
    
    def _save_meeting(self, meeting: Dict[str, Any]):
        """Save meeting to storage"""
        try:
            filepath = os.path.join(self.storage_dir, f"{meeting['id']}.json")
            with open(filepath, 'w') as f:
                json.dump(meeting, f, indent=2)
        except Exception as e:
            logger.error(f"Save meeting error: {e}")
    
    def export_meeting(self, meeting_id: str, format: str = "json") -> Dict[str, Any]:
        """Export meeting to format"""
        meeting = self.get_meeting(meeting_id)
        if not meeting:
            return {"success": False, "error": "Meeting not found"}
        
        if format == "json":
            return {"success": True, "data": json.dumps(meeting, indent=2)}
        elif format == "markdown":
            md = f"# {meeting['title']}\n\n"
            md += f"**Date:** {meeting['date']}\n\n"
            md += f"**Attendees:** {', '.join(meeting.get('attendees', []))}\n\n"
            md += "## Notes\n\n" + meeting.get('notes', 'No notes') + "\n\n"
            if meeting.get('summary'):
                md += "## Summary\n\n" + meeting['summary'] + "\n\n"
            if meeting.get('action_items'):
                md += "## Action Items\n\n"
                for item in meeting['action_items']:
                    md += f"- [ ] {item['item']}\n"
            return {"success": True, "data": md}
        
        return {"success": False, "error": "Unsupported format"}


# Singleton
meeting_notes_manager = MeetingNotesManager()


def create_meeting(*args, **kwargs) -> Dict[str, Any]:
    return meeting_notes_manager.create_meeting(*args, **kwargs)


def get_meetings() -> List[Dict[str, Any]]:
    return meeting_notes_manager.list_meetings()
