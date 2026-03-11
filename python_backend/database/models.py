"""
SQLAlchemy Database Models
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey, Enum
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()


class MeetingStatus(str, enum.Enum):
    """Meeting status enum"""
    CONFIRMED = "confirmed"
    PENDING = "pending"
    RESCHEDULED = "rescheduled"
    CANCELLED = "cancelled"


class MeetingPriority(str, enum.Enum):
    """Meeting priority enum"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MeetingType(str, enum.Enum):
    """Meeting type enum"""
    TEAM_SYNC = "team_sync"
    ONE_ON_ONE = "one_on_one"
    CLIENT_CALL = "client_call"
    STANDUP = "standup"
    WORKSHOP = "workshop"
    INTERVIEW = "interview"


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    avatar = Column(String(500), nullable=True)
    role = Column(String(100), nullable=True)
    timezone = Column(String(50), default="UTC")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan")
    meetings = relationship("MeetingAttendee", back_populates="user")


class Meeting(Base):
    """Meeting model"""
    __tablename__ = "meetings"

    id = Column(String(50), primary_key=True)
    title = Column(String(255), nullable=False)
    type = Column(Enum(MeetingType), nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=False)  # in minutes
    status = Column(Enum(MeetingStatus), default=MeetingStatus.PENDING, index=True)
    priority = Column(Enum(MeetingPriority), default=MeetingPriority.MEDIUM)
    location = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    created_by = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    attendees = relationship("MeetingAttendee", back_populates="meeting", cascade="all, delete-orphan")
    decision = relationship("MeetingDecision", back_populates="meeting", uselist=False, cascade="all, delete-orphan")


class MeetingAttendee(Base):
    """Meeting attendee association"""
    __tablename__ = "meeting_attendees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_id = Column(String(50), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    availability = Column(String(20), default="unknown")  # available, soft_conflict, hard_conflict, unknown
    response_status = Column(String(20), default="pending")  # accepted, declined, tentative, pending
    created_at = Column(DateTime, default=func.now())

    # Relationships
    meeting = relationship("Meeting", back_populates="attendees")
    user = relationship("User", back_populates="meetings")


class TimeSlot(Base):
    """Recommended time slot"""
    __tablename__ = "time_slots"

    id = Column(String(50), primary_key=True)
    meeting_id = Column(String(50), nullable=True)  # Optional: link to meeting if confirmed
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    rank = Column(Integer, nullable=False)
    reasoning = Column(Text, nullable=True)
    conflicts = Column(JSON, default=list)  # List of conflict objects
    attendee_availability = Column(JSON, default=list)  # List of availability objects
    requires_approval = Column(Boolean, default=False)
    recommended = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())


class MeetingDecision(Base):
    """AI decision explanation for a meeting"""
    __tablename__ = "meeting_decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_id = Column(String(50), ForeignKey("meetings.id", ondelete="CASCADE"), unique=True, nullable=False)
    request_summary = Column(Text, nullable=True)
    recommended_slot_id = Column(String(50), nullable=True)
    alternative_slots = Column(JSON, default=list)  # List of slot IDs
    tradeoffs = Column(JSON, default=list)  # List of tradeoff strings
    overall_confidence = Column(Float, nullable=False)
    approval_needed = Column(Boolean, default=False)
    approval_reason = Column(Text, nullable=True)
    agent_insights = Column(JSON, default=list)  # List of insight objects
    created_at = Column(DateTime, default=func.now())

    # Relationships
    meeting = relationship("Meeting", back_populates="decision")


class UserPreference(Base):
    """User scheduling preference"""
    __tablename__ = "user_preferences"

    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(50), nullable=False)  # time, behavior, priority, escalation
    label = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    value = Column(String(255), nullable=False)
    icon = Column(String(50), nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="preferences")


class AgentActivity(Base):
    """Agent activity log"""
    __tablename__ = "agent_activities"

    id = Column(String(50), primary_key=True)
    agent_type = Column(String(50), nullable=False, index=True)  # calendar, behavior, coordination, orchestrator
    status = Column(String(50), nullable=False)  # idle, scanning, analyzing, negotiating, ranking, complete, waiting, error
    message = Column(Text, nullable=True)
    details = Column(Text, nullable=True)
    progress = Column(Integer, nullable=True)  # 0-100
    timestamp = Column(DateTime, default=func.now(), index=True)


class ScheduleRequest(Base):
    """Schedule request history"""
    __tablename__ = "schedule_requests"

    id = Column(String(50), primary_key=True)
    title = Column(String(255), nullable=False)
    attendee_ids = Column(JSON, nullable=False)  # List of user IDs
    duration = Column(Integer, nullable=False)
    priority = Column(Enum(MeetingPriority), default=MeetingPriority.MEDIUM)
    meeting_type = Column(Enum(MeetingType), nullable=False)
    notes = Column(Text, nullable=True)
    preferred_time_range = Column(JSON, nullable=True)  # {start, end}
    status = Column(String(50), default="processing")  # processing, completed, failed
    result_meeting_id = Column(String(50), nullable=True)  # Link to created meeting
    created_at = Column(DateTime, default=func.now(), index=True)
    completed_at = Column(DateTime, nullable=True)


class CalendarEvent(Base):
    """External calendar events (cached)"""
    __tablename__ = "calendar_events"

    id = Column(String(100), primary_key=True)
    user_id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    external_id = Column(String(255), nullable=False)  # ID from external calendar
    calendar_provider = Column(String(50), nullable=False)  # google, outlook, etc.
    title = Column(String(255), nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    is_all_day = Column(Boolean, default=False)
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(Text, nullable=True)
    location = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    attendees = Column(JSON, default=list)
    synced_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())


class HistoricalMeeting(Base):
    """Historical meeting data for behavior analysis"""
    __tablename__ = "historical_meetings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    meeting_type = Column(String(50), nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0-6
    hour_of_day = Column(Integer, nullable=False)  # 0-23
    was_accepted = Column(Boolean, default=True)
    was_rescheduled = Column(Boolean, default=False)
    was_cancelled = Column(Boolean, default=False)
    attendee_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())


class CalendarIntegration(Base):
    """Calendar integration OAuth tokens"""
    __tablename__ = "calendar_integrations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    provider = Column(String(50), nullable=False)  # google, outlook
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    scope = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    last_synced_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
