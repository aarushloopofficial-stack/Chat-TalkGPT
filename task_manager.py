"""
Chat&Talk GPT - Task/Assignment Management System
Uses Google Sheets as database for user assignments
"""
import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger("TaskManager")

try:
    import gspread
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False


class TaskManager:
    """
    Manages user tasks/assignments with Google Sheets as backend
    Supports:
    - Read user profiles from Sheets
    - Assign tasks to users
    - Track task status
    - Bidirectional sync
    """
    
    # Column indices in Google Sheets
    COLUMNS = {
        "row_id": 0,
        "user_name": 1,
        "email": 2,
        "activity": 3,
        "status": 4,
        "due_date": 5,
        "notes": 6,
        "created_at": 7,
        "updated_at": 8
    }
    
    # Status options
    STATUS_PENDING = "Pending"
    STATUS_IN_PROGRESS = "In Progress"
    STATUS_COMPLETED = "Completed"
    
    def __init__(self):
        self.enabled = False
        self.credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
        self.tasks_sheet_name = os.getenv("TASKS_SPREADSHEET_NAME", "Chat&Talk GPT Tasks")
        self.spreadsheet = None
        self.worksheet = None
        self.last_sync = None
        self.sync_status = "Not synced"
        
        # Local cache of tasks
        self.tasks_cache = []
        self.users_cache = {}
        
        if GSPREAD_AVAILABLE and os.path.exists(self.credentials_file):
            try:
                self._initialize()
            except Exception as e:
                logger.error(f"Failed to initialize TaskManager: {e}")
        else:
            logger.warning("TaskManager disabled - credentials not found")
    
    def _initialize(self):
        """Initialize Google Sheets connection"""
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_file(
            self.credentials_file,
            scopes=scope
        )
        
        client = gspread.authorize(creds)
        
        # Try to open or create spreadsheet
        try:
            self.spreadsheet = client.open(self.tasks_sheet_name)
            logger.info(f"Opened spreadsheet: {self.tasks_sheet_name}")
        except:
            # Create new spreadsheet
            self.spreadsheet = client.create(self.tasks_sheet_name)
            logger.info(f"Created spreadsheet: {self.tasks_sheet_name}")
        
        # Get or create worksheet
        try:
            self.worksheet = self.spreadsheet.sheet1
        except:
            self.worksheet = self.spreadsheet.add_worksheet("Tasks", 1000, 10)
        
        # Add headers if empty
        if self.worksheet.row_count == 0:
            headers = [
                "Row ID", "User Name", "Email ID", "Activity/Task Description",
                "Activity Status", "Due Date", "Notes", "Created At", "Updated At"
            ]
            self.worksheet.append_row(headers)
            logger.info("Added headers to tasks sheet")
        
        self.enabled = True
        logger.info("TaskManager initialized successfully!")
    
    async def sync_tasks(self) -> Dict[str, Any]:
        """Sync tasks from Google Sheets"""
        if not self.enabled:
            return {"success": False, "message": "TaskManager not enabled"}
        
        try:
            # Fetch all records
            records = self.worksheet.get_all_records()
            
            # Update cache
            self.tasks_cache = []
            self.users_cache = {}
            
            for idx, record in enumerate(records):
                if not record.get("Email ID"):
                    continue
                
                task = {
                    "id": record.get("Row ID", idx + 1),
                    "user_name": record.get("User Name", ""),
                    "email": record.get("Email ID", ""),
                    "activity": record.get("Activity/Task Description", ""),
                    "status": record.get("Activity Status", self.STATUS_PENDING),
                    "due_date": record.get("Due Date", ""),
                    "notes": record.get("Notes", ""),
                    "created_at": record.get("Created At", ""),
                    "updated_at": record.get("Updated At", "")
                }
                
                self.tasks_cache.append(task)
                
                # Build users cache
                email = task["email"]
                if email not in self.users_cache:
                    self.users_cache[email] = {
                        "name": task["user_name"],
                        "email": email,
                        "tasks": []
                    }
                self.users_cache[email]["tasks"].append(task)
            
            self.last_sync = datetime.now()
            self.sync_status = f"Synced at {self.last_sync.strftime('%H:%M:%S')}"
            
            logger.info(f"Synced {len(self.tasks_cache)} tasks from Google Sheets")
            
            return {
                "success": True,
                "message": f"Synced {len(self.tasks_cache)} tasks",
                "task_count": len(self.tasks_cache),
                "sync_time": self.last_sync.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error syncing tasks: {e}")
            self.sync_status = f"Sync failed: {str(e)}"
            return {"success": False, "message": str(e)}
    
    def get_user_tasks(self, email: str) -> List[Dict]:
        """Get tasks for a specific user (role-based access)"""
        if email in self.users_cache:
            return self.users_cache[email]["tasks"]
        return []
    
    def get_all_tasks(self) -> List[Dict]:
        """Get all tasks (admin view)"""
        return self.tasks_cache
    
    async def update_task_status(self, email: str, activity: str, new_status: str) -> Dict[str, Any]:
        """Update task status (bidirectional sync)"""
        if not self.enabled:
            return {"success": False, "message": "TaskManager not enabled"}
        
        try:
            # Find the task row
            records = self.worksheet.get_all_records()
            
            for idx, record in enumerate(records):
                if (record.get("Email ID", "").lower() == email.lower() and 
                    record.get("Activity/Task Description", "") == activity):
                    
                    # Update in Google Sheets
                    row_num = idx + 2  # +2 because of header and 0-index
                    self.worksheet.update_cell(row_num, 5, new_status)  # Status column
                    self.worksheet.update_cell(row_num, 9, datetime.now().isoformat())  # Updated_at
                    
                    # Update local cache
                    if idx < len(self.tasks_cache):
                        self.tasks_cache[idx]["status"] = new_status
                        self.tasks_cache[idx]["updated_at"] = datetime.now().isoformat()
                    
                    logger.info(f"Updated task status: {activity} -> {new_status}")
                    
                    return {
                        "success": True,
                        "message": f"Task status updated to {new_status}"
                    }
            
            return {"success": False, "message": "Task not found"}
            
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            return {"success": False, "message": str(e)}
    
    async def add_task(self, user_name: str, email: str, activity: str, 
                      due_date: str = "", notes: str = "") -> Dict[str, Any]:
        """Add a new task (admin function)"""
        if not self.enabled:
            return {"success": False, "message": "TaskManager not enabled"}
        
        try:
            now = datetime.now().isoformat()
            row_id = len(self.tasks_cache) + 1
            
            row = [
                row_id, user_name, email, activity,
                self.STATUS_PENDING, due_date, notes,
                now, now
            ]
            
            self.worksheet.append_row(row)
            
            # Update cache
            task = {
                "id": row_id,
                "user_name": user_name,
                "email": email,
                "activity": activity,
                "status": self.STATUS_PENDING,
                "due_date": due_date,
                "notes": notes,
                "created_at": now,
                "updated_at": now
            }
            self.tasks_cache.append(task)
            
            if email not in self.users_cache:
                self.users_cache[email] = {"name": user_name, "email": email, "tasks": []}
            self.users_cache[email]["tasks"].append(task)
            
            logger.info(f"Added task for {email}: {activity}")
            
            return {
                "success": True,
                "message": "Task added successfully",
                "task_id": row_id
            }
            
        except Exception as e:
            logger.error(f"Error adding task: {e}")
            return {"success": False, "message": str(e)}
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status"""
        return {
            "enabled": self.enabled,
            "status": self.sync_status,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "total_tasks": len(self.tasks_cache),
            "total_users": len(self.users_cache)
        }
    
    def get_pending_notifications(self, email: str) -> List[Dict]:
        """Get new tasks assigned to user that haven't been seen"""
        user_tasks = self.get_user_tasks(email)
        pending = []
        
        for task in user_tasks:
            # Consider tasks as "new" if they're pending or in progress
            if task["status"] in [self.STATUS_PENDING, self.STATUS_IN_PROGRESS]:
                pending.append(task)
        
        return pending
    
    def validate_spreadsheet(self) -> Dict[str, Any]:
        """Validate spreadsheet structure"""
        if not self.enabled:
            return {"valid": False, "message": "Not connected"}
        
        try:
            headers = self.worksheet.row_values(1)
            required = ["Email ID", "Activity/Task Description", "Activity Status"]
            
            missing = [h for h in required if h not in headers]
            
            if missing:
                return {
                    "valid": False,
                    "message": f"Missing columns: {', '.join(missing)}"
                }
            
            return {
                "valid": True,
                "message": "Spreadsheet structure is valid"
            }
            
        except Exception as e:
            return {"valid": False, "message": str(e)}


# Initialize task manager
task_manager = TaskManager()
