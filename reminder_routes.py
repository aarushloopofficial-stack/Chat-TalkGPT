"""
Chat&Talk GPT - Reminder Routes
FastAPI routes for the general reminder system
"""
import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Query, Path, Body
from pydantic import BaseModel, Field

from reminder_manager import (
    reminder_manager,
    ReminderType,
    Priority,
    SnoozeDuration
)

logger = logging.getLogger("ReminderRoutes")

# Create router
router = APIRouter(prefix="/api/reminders", tags=["reminders"])


# Request models
class CreateReminderRequest(BaseModel):
    """Request model for creating a reminder"""
    title: str = Field(..., description="Reminder title", min_length=1)
    message: str = Field(..., description="Reminder message")
    reminder_type: str = Field(default=ReminderType.TIME_BASED, description="Type of reminder")
    trigger_time: Optional[str] = Field(None, description="When to trigger (ISO format)")
    recurrence_pattern: Optional[str] = Field(None, description="Recurrence pattern")
    recurrence_days: Optional[List[str]] = Field(default=[], description="Days for recurrence")
    priority: str = Field(default=Priority.MEDIUM, description="Priority level")
    categories: Optional[List[str]] = Field(default=[], description="Categories/tags")
    linked_item_id: Optional[int] = Field(None, description="ID of linked item")
    linked_item_type: Optional[str] = Field(None, description="Type of linked item")
    trigger_conditions: Optional[Dict[str, Any]] = Field(default={}, description="Custom trigger conditions")
    enabled: bool = Field(default=True, description="Whether reminder is enabled")


class UpdateReminderRequest(BaseModel):
    """Request model for updating a reminder"""
    title: Optional[str] = None
    message: Optional[str] = None
    reminder_type: Optional[str] = None
    trigger_time: Optional[str] = None
    recurrence_pattern: Optional[str] = None
    recurrence_days: Optional[List[str]] = None
    priority: Optional[str] = None
    categories: Optional[List[str]] = None
    linked_item_id: Optional[int] = None
    linked_item_type: Optional[str] = None
    trigger_conditions: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None
    completed: Optional[bool] = None
    snoozed: Optional[bool] = None


class SnoozeReminderRequest(BaseModel):
    """Request model for snoozing a reminder"""
    duration: str = Field(default=SnoozeDuration.FIFTEEN_MIN, description="Snooze duration")
    custom_minutes: Optional[int] = Field(None, description="Custom snooze minutes")


class CreateFromTemplateRequest(BaseModel):
    """Request model for creating reminder from template"""
    template_id: str = Field(..., description="Template ID")
    trigger_time: str = Field(..., description="When to trigger")
    custom_message: Optional[str] = Field(None, description="Custom message override")


# Routes
@router.post("")
async def create_reminder(
    user_id: int = Query(default=1, description="User ID"),
    request: CreateReminderRequest = None
):
    """Create a new reminder"""
    try:
        reminder = await reminder_manager.create_reminder(
            user_id=user_id,
            title=request.title,
            message=request.message,
            reminder_type=request.reminder_type,
            trigger_time=request.trigger_time,
            recurrence_pattern=request.recurrence_pattern,
            recurrence_days=request.recurrence_days,
            priority=request.priority,
            categories=request.categories,
            linked_item_id=request.linked_item_id,
            linked_item_type=request.linked_item_type,
            trigger_conditions=request.trigger_conditions,
            enabled=request.enabled
        )
        return {"success": True, "reminder": reminder}
    except Exception as e:
        logger.error(f"Error creating reminder: {e}")
        return {"success": False, "message": str(e)}


@router.get("")
async def get_reminders(
    user_id: int = Query(default=1, description="User ID"),
    enabled_only: bool = Query(default=False, description="Get only enabled reminders"),
    upcoming: bool = Query(default=False, description="Get only upcoming reminders"),
    include_completed: bool = Query(default=True, description="Include completed reminders")
):
    """Get all reminders for a user"""
    try:
        reminders = await reminder_manager.get_reminders(
            user_id=user_id,
            enabled_only=enabled_only,
            upcoming=upcoming,
            include_completed=include_completed
        )
        return {"success": True, "reminders": reminders, "count": len(reminders)}
    except Exception as e:
        logger.error(f"Error getting reminders: {e}")
        return {"success": False, "message": str(e)}


@router.get("/{reminder_id}")
async def get_reminder(reminder_id: int):
    """Get a specific reminder by ID"""
    try:
        reminder = await reminder_manager.get_reminder_by_id(reminder_id)
        if reminder:
            return {"success": True, "reminder": reminder}
        return {"success": False, "message": "Reminder not found"}
    except Exception as e:
        logger.error(f"Error getting reminder: {e}")
        return {"success": False, "message": str(e)}


@router.put("/{reminder_id}")
async def update_reminder(reminder_id: int, request: UpdateReminderRequest = None):
    """Update a reminder"""
    try:
        update_data = request.dict(exclude_unset=True) if request else {}
        reminder = await reminder_manager.update_reminder(reminder_id, **update_data)
        if reminder:
            return {"success": True, "reminder": reminder}
        return {"success": False, "message": "Reminder not found"}
    except Exception as e:
        logger.error(f"Error updating reminder: {e}")
        return {"success": False, "message": str(e)}


@router.delete("/{reminder_id}")
async def delete_reminder(reminder_id: int):
    """Delete a reminder"""
    try:
        result = await reminder_manager.delete_reminder(reminder_id)
        if result:
            return {"success": True, "message": "Reminder deleted"}
        return {"success": False, "message": "Reminder not found"}
    except Exception as e:
        logger.error(f"Error deleting reminder: {e}")
        return {"success": False, "message": str(e)}


@router.post("/{reminder_id}/snooze")
async def snooze_reminder(reminder_id: int, request: SnoozeReminderRequest = None):
    """Snooze a reminder"""
    try:
        duration = request.duration if request else SnoozeDuration.FIFTEEN_MIN
        custom_minutes = request.custom_minutes if request else None
        reminder = await reminder_manager.snooze_reminder(reminder_id, duration, custom_minutes)
        if reminder:
            return {"success": True, "reminder": reminder}
        return {"success": False, "message": "Reminder not found"}
    except Exception as e:
        logger.error(f"Error snoozing reminder: {e}")
        return {"success": False, "message": str(e)}


@router.post("/{reminder_id}/complete")
async def complete_reminder(reminder_id: int):
    """Mark a reminder as completed"""
    try:
        reminder = await reminder_manager.complete_reminder(reminder_id)
        if reminder:
            return {"success": True, "reminder": reminder}
        return {"success": False, "message": "Reminder not found"}
    except Exception as e:
        logger.error(f"Error completing reminder: {e}")
        return {"success": False, "message": str(e)}


@router.post("/{reminder_id}/trigger")
async def trigger_reminder(reminder_id: int):
    """Manually trigger a reminder"""
    try:
        reminder = await reminder_manager.trigger_reminder(reminder_id)
        if reminder:
            return {"success": True, "reminder": reminder}
        return {"success": False, "message": "Reminder not found"}
    except Exception as e:
        logger.error(f"Error triggering reminder: {e}")
        return {"success": False, "message": str(e)}


@router.get("/due")
async def get_due_reminders(user_id: int = Query(default=1, description="User ID")):
    """Get all due reminders"""
    try:
        reminders = await reminder_manager.get_due_reminders(user_id)
        return {"success": True, "reminders": reminders, "count": len(reminders)}
    except Exception as e:
        logger.error(f"Error getting due reminders: {e}")
        return {"success": False, "message": str(e)}


@router.get("/templates")
async def get_reminder_templates():
    """Get available reminder templates"""
    try:
        templates = await reminder_manager.get_templates()
        return {"success": True, "templates": templates}
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        return {"success": False, "message": str(e)}


@router.post("/from-template")
async def create_reminder_from_template(
    user_id: int = Query(default=1, description="User ID"),
    request: CreateFromTemplateRequest = None
):
    """Create a reminder from a template"""
    try:
        reminder = await reminder_manager.create_from_template(
            user_id=user_id,
            template_id=request.template_id,
            trigger_time=request.trigger_time,
            custom_message=request.custom_message
        )
        if reminder:
            return {"success": True, "reminder": reminder}
        return {"success": False, "message": "Template not found"}
    except Exception as e:
        logger.error(f"Error creating from template: {e}")
        return {"success": False, "message": str(e)}


@router.get("/category/{category}")
async def get_reminders_by_category(
    user_id: int = Query(default=1, description="User ID"),
    category: str = Path(..., description="Category name")
):
    """Get reminders by category"""
    try:
        reminders = await reminder_manager.get_reminders_by_category(user_id, category)
        return {"success": True, "reminders": reminders, "count": len(reminders)}
    except Exception as e:
        logger.error(f"Error getting reminders by category: {e}")
        return {"success": False, "message": str(e)}


@router.get("/priority/{priority}")
async def get_reminders_by_priority(
    user_id: int = Query(default=1, description="User ID"),
    priority: str = Path(..., description="Priority level")
):
    """Get reminders by priority"""
    try:
        reminders = await reminder_manager.get_reminders_by_priority(user_id, priority)
        return {"success": True, "reminders": reminders, "count": len(reminders)}
    except Exception as e:
        logger.error(f"Error getting reminders by priority: {e}")
        return {"success": False, "message": str(e)}


@router.post("/check-due")
async def check_and_trigger_due_reminders(user_id: int = Query(default=1, description="User ID")):
    """Check and trigger all due reminders"""
    try:
        triggered = await reminder_manager.check_and_trigger_due_reminders(user_id)
        return {"success": True, "triggered": triggered, "count": len(triggered)}
    except Exception as e:
        logger.error(f"Error checking due reminders: {e}")
        return {"success": False, "message": str(e)}
