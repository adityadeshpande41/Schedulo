"""
API Response Models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime


class AttendeeResponse(BaseModel):
    """Attendee information"""
    id: str
    name: str
    email: str
    role: str
    availability: str
    response_status: str


class ConflictResponse(BaseModel):
    """Conflict information"""
    type: str  # "soft" or "hard"
    description: str
    attendee_id: Optional[str] = None
    resolution: Optional[str] = None


class TimeSlotResponse(BaseModel):
    """Recommended time slot"""
    id: str
    start_time: datetime
    end_time: datetime
    score: float
    confidence: float
    rank: int
    reasoning: str
    conflicts: List[ConflictResponse]
    attendee_availability: List[dict]
    requires_approval: bool
    recommended: bool


class ScheduleResponse(BaseModel):
    """Response from schedule request"""
    request_id: str
    status: str
    recommended_slots: List[TimeSlotResponse]
    approval_needed: bool
    confidence: float
    message: str


class MeetingResponse(BaseModel):
    """Meeting information"""
    id: str
    title: str
    type: str
    start_time: datetime
    end_time: datetime
    duration: int
    attendees: List[AttendeeResponse]
    status: str
    priority: str
    location: Optional[str] = None
    description: Optional[str] = None


class AgentInsightResponse(BaseModel):
    """Agent insight"""
    agent: str
    insight: str


class DecisionExplanationResponse(BaseModel):
    """AI decision explanation"""
    meeting_id: str
    request_summary: str
    recommended_slot: TimeSlotResponse
    alternative_slots: List[TimeSlotResponse]
    tradeoffs: List[str]
    overall_confidence: float
    approval_needed: bool
    approval_reason: Optional[str] = None
    agent_insights: List[AgentInsightResponse]


class AgentActivityResponse(BaseModel):
    """Agent activity status"""
    id: str
    agent_type: str
    status: str
    message: str
    timestamp: datetime
    progress: Optional[int] = None


class AgentInfoResponse(BaseModel):
    """Agent information"""
    type: str
    name: str
    description: str
    capabilities: List[str]
    icon: str
    color: str


class UserPreferenceResponse(BaseModel):
    """User preference"""
    id: str
    user_id: str
    category: str
    label: str
    description: str
    value: str
    icon: str
    active: bool
