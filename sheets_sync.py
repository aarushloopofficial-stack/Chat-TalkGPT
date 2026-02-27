"""
Chat&Talk GPT - Google Sheets / Excel Sync
Automatically syncs activity data to Google Sheets
"""
import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger("SheetsSync")

# Try importing Google libraries
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False
    logger.warning("gspread not available - Google Sheets sync disabled")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class SheetsSync:
    """Syncs data to Google Sheets"""
    
    def __init__(self):
        self.enabled = False
        self.credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
        self.spreadsheet_name = os.getenv("SPREADSHEET_NAME", "Chat&Talk GPT Activity Log")
        self.worksheet = None
        self.client = None
        
        if GSPREAD_AVAILABLE and os.path.exists(self.credentials_file):
            try:
                self._initialize_google_sheets()
            except Exception as e:
                logger.error(f"Failed to initialize Google Sheets: {e}")
        else:
            logger.warning("Google Sheets sync disabled - credentials not found")
    
    def _initialize_google_sheets(self):
        """Initialize Google Sheets connection"""
        try:
            # Define scope
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Load credentials
            creds = Credentials.from_service_account_file(
                self.credentials_file, 
                scopes=scope
            )
            
            # Create client
            self.client = gspread.authorize(creds)
            
            # Try to open or create spreadsheet
            try:
                self.spreadsheet = self.client.open(self.spreadsheet_name)
                logger.info(f"Opened spreadsheet: {self.spreadsheet_name}")
            except:
                # Create new spreadsheet
                self.spreadsheet = self.client.create(self.spreadsheet_name)
                logger.info(f"Created spreadsheet: {self.spreadsheet_name}")
            
            # Get or create worksheet
            try:
                self.worksheet = self.spreadsheet.sheet1
            except:
                self.worksheet = self.spreadsheet.add_worksheet("Activity Log", 1000, 10)
            
            # Add headers if empty
            if self.worksheet.row_count == 0:
                headers = ["ID", "Timestamp", "Activity Type", "User Name", "User Email", 
                          "Details", "Message", "Response"]
                self.worksheet.append_row(headers)
            
            self.enabled = True
            logger.info("Google Sheets sync enabled!")
            
        except Exception as e:
            logger.error(f"Error initializing Google Sheets: {e}")
            self.enabled = False
    
    async def sync_activity(self, activity: Dict[str, Any]) -> bool:
        """Sync a single activity to Google Sheets"""
        if not self.enabled:
            return False
        
        try:
            row = [
                activity.get("id", ""),
                activity.get("timestamp", ""),
                activity.get("type", ""),
                activity.get("user", {}).get("name", ""),
                activity.get("user", {}).get("email", ""),
                json.dumps(activity.get("details", {})),
                activity.get("details", {}).get("user_message", ""),
                activity.get("details", {}).get("ai_response", "")
            ]
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: self.worksheet.append_row(row))
            
            logger.debug(f"Synced activity {activity.get('id')} to Google Sheets")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing to Google Sheets: {e}")
            return False
    
    async def sync_batch(self, activities: List[Dict[str, Any]]) -> bool:
        """Sync multiple activities at once"""
        if not self.enabled or not activities:
            return False
        
        try:
            rows = []
            for activity in activities:
                row = [
                    activity.get("id", ""),
                    activity.get("timestamp", ""),
                    activity.get("type", ""),
                    activity.get("user", {}).get("name", ""),
                    activity.get("user", {}).get("email", ""),
                    json.dumps(activity.get("details", {})),
                    activity.get("details", {}).get("user_message", ""),
                    activity.get("details", {}).get("ai_response", "")
                ]
                rows.append(row)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, 
                lambda: self.worksheet.append_rows(rows)
            )
            
            logger.info(f"Synced {len(rows)} activities to Google Sheets")
            return True
            
        except Exception as e:
            logger.error(f"Error batch syncing: {e}")
            return False
    
    def get_spreadsheet_url(self) -> str:
        """Get the spreadsheet URL"""
        if self.enabled and hasattr(self, 'spreadsheet'):
            return self.spreadsheet.url
        return ""


class ExcelExporter:
    """Exports data to Excel format"""
    
    def __init__(self):
        self.enabled = PANDAS_AVAILABLE
        logger.info(f"Excel export: {'enabled' if self.enabled else 'disabled'}")
    
    def export_to_excel(self, activities: List[Dict[str, Any]], 
                       filepath: str = "memory/activity_export.xlsx") -> bool:
        """Export activities to Excel file"""
        if not self.enabled:
            logger.warning("Pandas not available for Excel export")
            return False
        
        try:
            # Convert to DataFrame
            data = []
            for activity in activities:
                data.append({
                    "ID": activity.get("id", ""),
                    "Timestamp": activity.get("timestamp", ""),
                    "Activity Type": activity.get("type", ""),
                    "User Name": activity.get("user", {}).get("name", ""),
                    "User Email": activity.get("user", {}).get("email", ""),
                    "Details": json.dumps(activity.get("details", {})),
                    "Message": activity.get("details", {}).get("user_message", ""),
                    "Response": activity.get("details", {}).get("ai_response", ""),
                    "Command": activity.get("details", {}).get("command", ""),
                    "App Opened": activity.get("details", {}).get("app_name", "")
                })
            
            df = pd.DataFrame(data)
            
            # Save to Excel
            df.to_excel(filepath, index=False, engine='openpyxl')
            
            logger.info(f"Exported {len(activities)} activities to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            return False
    
    def export_daily_report(self, activities: List[Dict[str, Any]], 
                           date: str = None) -> bool:
        """Export daily activity report"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        filepath = f"memory/activity_report_{date}.xlsx"
        return self.export_to_excel(activities, filepath)


# Initialize sync modules
sheets_sync = SheetsSync()
excel_exporter = ExcelExporter()
