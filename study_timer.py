"""
Chat&Talk GPT - Study Timer (Pomodoro)
A Pomodoro technique timer for focused study sessions with breaks
"""
import json
import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import time
import threading

logger = logging.getLogger("StudyTimer")


class StudyTimer:
    """
    Pomodoro-style study timer with local JSON storage
    Features:
    - Study sessions (default 25 min), short breaks (5 min), long breaks (15 min)
    - Pause/resume/stop functionality
    - Session history tracking
    - Study statistics and streaks
    - Async-compatible methods
    """
    
    # Default durations in minutes
    DEFAULT_DURATIONS = {
        "study": 25,
        "short_break": 5,
        "long_break": 15
    }
    
    def __init__(self, storage_file: str = None):
        """Initialize study timer with storage file"""
        if storage_file is None:
            storage_file = "memory/study_sessions.json"
        
        self.storage_file = Path(storage_file)
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Timer state
        self._current_session = None
        self._start_time = None
        self._remaining_seconds = 0
        self._is_paused = False
        self._is_running = False
        self._timer_thread = None
        self._stop_event = threading.Event()
        
        # Load session history
        self._data = self._load_data()
        
        logger.info("StudyTimer initialized")
    
    def _load_data(self) -> Dict[str, Any]:
        """Load study sessions from JSON file"""
        try:
            if self.storage_file.exists():
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data.get('sessions', []))} past sessions")
                    return data
        except Exception as e:
            logger.warning(f"Could not load study data: {e}")
        
        return {
            "sessions": [],
            "stats": {
                "total_study_time_minutes": 0,
                "total_sessions_completed": 0,
                "current_streak": 0,
                "longest_streak": 0,
                "last_session_date": None
            }
        }
    
    def _save_data(self):
        """Save study sessions to JSON file"""
        try:
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            logger.info("Study data saved")
        except Exception as e:
            logger.error(f"Error saving study data: {e}")
    
    def _generate_id(self) -> str:
        """Generate unique session ID"""
        return str(uuid.uuid4())[:8]
    
    def _update_stats(self, session_type: str, duration_minutes: int):
        """Update study statistics after a session"""
        stats = self._data.get("stats", {})
        
        if session_type == "study":
            stats["total_study_time_minutes"] = stats.get("total_study_time_minutes", 0) + duration_minutes
            stats["total_sessions_completed"] = stats.get("total_sessions_completed", 0) + 1
            
            # Update streak
            today = datetime.now().date().isoformat()
            last_date = stats.get("last_session_date")
            
            if last_date:
                last_date_obj = datetime.fromisoformat(last_date).date()
                today_obj = datetime.now().date()
                days_diff = (today_obj - last_date_obj).days
                
                if days_diff == 1:
                    # Consecutive day
                    stats["current_streak"] = stats.get("current_streak", 0) + 1
                elif days_diff > 1:
                    # Streak broken
                    stats["current_streak"] = 1
                # Same day - don't change streak
            else:
                stats["current_streak"] = 1
            
            # Update longest streak
            current_streak = stats.get("current_streak", 0)
            longest_streak = stats.get("longest_streak", 0)
            if current_streak > longest_streak:
                stats["longest_streak"] = current_streak
            
            stats["last_session_date"] = today
        
        self._data["stats"] = stats
        self._save_data()
    
    def start_timer(self, duration_minutes: int = None, session_type: str = "study") -> Dict[str, Any]:
        """
        Start a study or break timer
        
        Args:
            duration_minutes: Custom duration (uses default if not provided)
            session_type: "study", "short_break", or "long_break"
        
        Returns:
            Dictionary with timer status
        """
        # Validate session type
        if session_type not in self.DEFAULT_DURATIONS:
            raise ValueError(f"Invalid session type. Must be one of: {list(self.DEFAULT_DURATIONS.keys())}")
        
        # Use default duration if not provided
        if duration_minutes is None:
            duration_minutes = self.DEFAULT_DURATIONS[session_type]
        
        # Stop any existing timer
        if self._is_running:
            self.stop_timer()
        
        # Create new session
        self._current_session = {
            "id": self._generate_id(),
            "type": session_type,
            "duration_minutes": duration_minutes,
            "started_at": datetime.now().isoformat(),
            "paused_at": None,
            "completed_at": None,
            "status": "running"
        }
        
        self._start_time = datetime.now()
        self._remaining_seconds = duration_minutes * 60
        self._is_paused = False
        self._is_running = True
        self._stop_event.clear()
        
        logger.info(f"Started {session_type} timer for {duration_minutes} minutes")
        
        return self.get_timer_status()
    
    def pause_timer(self) -> Dict[str, Any]:
        """
        Pause the current timer
        
        Returns:
            Dictionary with timer status
        """
        if not self._is_running:
            return {"error": "No timer is running"}
        
        if self._is_paused:
            return {"error": "Timer is already paused"}
        
        self._is_paused = True
        if self._current_session:
            self._current_session["status"] = "paused"
            self._current_session["paused_at"] = datetime.now().isoformat()
        
        logger.info("Timer paused")
        return self.get_timer_status()
    
    def resume_timer(self) -> Dict[str, Any]:
        """
        Resume a paused timer
        
        Returns:
            Dictionary with timer status
        """
        if not self._is_running:
            return {"error": "No timer is running"}
        
        if not self._is_paused:
            return {"error": "Timer is not paused"}
        
        self._is_paused = False
        if self._current_session:
            self._current_session["status"] = "running"
        
        logger.info("Timer resumed")
        return self.get_timer_status()
    
    def stop_timer(self) -> Dict[str, Any]:
        """
        Stop the current timer
        
        Returns:
            Dictionary with timer status
        """
        if not self._current_session:
            return {"error": "No timer is running"}
        
        # Calculate elapsed time
        elapsed_minutes = 0
        if self._start_time and not self._is_paused:
            elapsed_seconds = (datetime.now() - self._start_time).total_seconds()
            elapsed_minutes = int(elapsed_seconds / 60)
        
        # Update session record
        self._current_session["completed_at"] = datetime.now().isoformat()
        self._current_session["elapsed_minutes"] = elapsed_minutes
        self._current_session["status"] = "stopped"
        
        # Save to history
        self._data["sessions"].append(self._current_session)
        
        # Update stats if it was a study session
        if self._current_session["type"] == "study" and elapsed_minutes > 0:
            self._update_stats("study", elapsed_minutes)
        
        # Reset timer state
        self._current_session = None
        self._start_time = None
        self._remaining_seconds = 0
        self._is_paused = False
        self._is_running = False
        self._stop_event.set()
        
        logger.info("Timer stopped")
        
        return {
            "status": "stopped",
            "session_type": "study",
            "elapsed_minutes": elapsed_minutes
        }
    
    def get_timer_status(self) -> Dict[str, Any]:
        """
        Get current timer status
        
        Returns:
            Dictionary with current timer state
        """
        if not self._current_session:
            return {
                "is_running": False,
                "is_paused": False,
                "session": None
            }
        
        # Calculate remaining time
        remaining_seconds = self._remaining_seconds
        if self._is_running and not self._is_paused and self._start_time:
            elapsed = (datetime.now() - self._start_time).total_seconds()
            remaining_seconds = max(0, (self._current_session["duration_minutes"] * 60) - elapsed)
            
            # Auto-complete if time is up
            if remaining_seconds == 0:
                return self._complete_session()
        
        minutes = int(remaining_seconds // 60)
        seconds = int(remaining_seconds % 60)
        
        return {
            "is_running": self._is_running,
            "is_paused": self._is_paused,
            "session": {
                "id": self._current_session.get("id"),
                "type": self._current_session.get("type"),
                "duration_minutes": self._current_session.get("duration_minutes"),
                "remaining_minutes": minutes,
                "remaining_seconds": seconds,
                "remaining_formatted": f"{minutes:02d}:{seconds:02d}",
                "status": self._current_session.get("status"),
                "started_at": self._current_session.get("started_at")
            }
        }
    
    def _complete_session(self) -> Dict[str, Any]:
        """Complete the current session"""
        if not self._current_session:
            return {"error": "No session to complete"}
        
        session_type = self._current_session.get("type")
        duration = self._current_session.get("duration_minutes", 0)
        
        # Update session record
        self._current_session["completed_at"] = datetime.now().isoformat()
        self._current_session["status"] = "completed"
        
        # Save to history
        self._data["sessions"].append(self._current_session)
        
        # Update stats
        if session_type == "study":
            self._update_stats("study", duration)
        
        # Reset state
        self._current_session = None
        self._start_time = None
        self._remaining_seconds = 0
        self._is_paused = False
        self._is_running = False
        
        logger.info(f"Completed {session_type} session")
        
        return {
            "status": "completed",
            "session_type": session_type,
            "duration_minutes": duration,
            "message": f"{session_type.replace('_', ' ').title()} session completed!"
        }
    
    def get_session_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get past study sessions
        
        Args:
            limit: Maximum number of sessions to return
        
        Returns:
            List of past sessions
        """
        sessions = self._data.get("sessions", [])
        # Return most recent first
        return sorted(sessions, key=lambda x: x.get("started_at", ""), reverse=True)[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get study statistics
        
        Returns:
            Dictionary with study stats
        """
        stats = self._data.get("stats", {})
        
        # Calculate total study time in hours and minutes
        total_minutes = stats.get("total_study_time_minutes", 0)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        return {
            "total_study_time_minutes": total_minutes,
            "total_study_time_formatted": f"{hours}h {minutes}m",
            "total_sessions_completed": stats.get("total_sessions_completed", 0),
            "current_streak": stats.get("current_streak", 0),
            "longest_streak": stats.get("longest_streak", 0),
            "last_session_date": stats.get("last_session_date")
        }
    
    def reset_stats(self) -> Dict[str, Any]:
        """
        Reset all statistics and history
        
        Returns:
            Confirmation message
        """
        self._data = {
            "sessions": [],
            "stats": {
                "total_study_time_minutes": 0,
                "total_sessions_completed": 0,
                "current_streak": 0,
                "longest_streak": 0,
                "last_session_date": None
            }
        }
        self._save_data()
        logger.info("Study stats and history reset")
        return {"message": "All study statistics and history have been reset"}


# For testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    timer = StudyTimer()
    
    # Test starting a timer
    print("Starting 1-minute study timer for testing...")
    status = timer.start_timer(duration_minutes=1, session_type="study")
    print(f"Timer status: {status}")
    
    # Get stats
    print(f"\nStats: {timer.get_stats()}")
    
    # Get history
    print(f"\nHistory: {timer.get_session_history()}")
