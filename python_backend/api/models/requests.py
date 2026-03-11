"""
API Request Models
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ScheduleRequest(BaseModel):
    """Request to schedule a new meeting"""
    title: str = Field(..., description="Meeting title")
    attendee_ids: List[str] = Field(..., description="List of attendee user IDs")
    duration: int = Field(..., ge=15, le=480, description="Duration in minutes")
    priority: str = Field("medium", pattern="^(high|medium|low)$")
    meeting_type: str = Field(
        "team_sync",
        description="Type of meeting"
    )
    notes: Optional[str] = Field(None, description="Additional notes")
    preferred_time_range: Optional[dict] = Field(
        None,
        description="Preferred time range {start, end}"
    )


class UpdatePreferenceRequest(BaseModel):
    """Request to update a user preference"""
    active: Optional[bool] = Field(None, description="Enable/disable preference")
    value: Optional[str] = Field(None, description="Preference value")


class RescheduleRequest(BaseModel):
    """Request to reschedule an existing meeting"""
    meeting_id: str
    reason: Optional[str] = None
    preferred_time_range: Optional[dict] = None
