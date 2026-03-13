"""
Meeting Service
Business logic for meeting operations
"""

from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from api.models.responses import (
    MeetingResponse,
    AttendeeResponse,
    DecisionExplanationResponse,
    TimeSlotResponse,
    AgentInsightResponse
)


class MeetingService:
    """Service for handling meeting operations"""
    
    async def get_upcoming_meetings(
        self,
        user_id: str,
        days: int
    ) -> List[MeetingResponse]:
        """Get upcoming meetings for a user - includes both Schedulo meetings and calendar events"""
        from database.connection import get_db
        from database.models import Meeting, MeetingAttendee, User, CalendarEvent
        from sqlalchemy import and_, or_
        
        # Query real meetings from database
        db = next(get_db())
        try:
            end_date = datetime.utcnow() + timedelta(days=days)
            
            # Get Schedulo meetings
            meetings = db.query(Meeting).join(
                MeetingAttendee, Meeting.id == MeetingAttendee.meeting_id
            ).filter(
                and_(
                    MeetingAttendee.user_id == user_id,
                    Meeting.start_time >= datetime.utcnow(),
                    Meeting.start_time <= end_date
                )
            ).order_by(Meeting.start_time).all()
            
            result = []
            
            # Add Schedulo meetings
            for meeting in meetings:
                # Get all attendees
                attendees = []
                for ma in meeting.attendees:
                    user = db.query(User).filter(User.id == ma.user_id).first()
                    if user:
                        attendees.append(AttendeeResponse(
                            id=user.id,
                            name=user.name,
                            email=user.email,
                            role=user.role or "Member",
                            availability="available",
                            response_status=ma.response_status or "pending"
                        ))
                
                result.append(MeetingResponse(
                    id=meeting.id,
                    title=meeting.title,
                    type=meeting.type.value if hasattr(meeting.type, 'value') else meeting.type,
                    start_time=meeting.start_time,
                    end_time=meeting.end_time,
                    duration=meeting.duration,
                    attendees=attendees,
                    status=meeting.status.value if hasattr(meeting.status, 'value') else meeting.status,
                    priority=meeting.priority.value if hasattr(meeting.priority, 'value') else meeting.priority,
                    location=meeting.location,
                    description=meeting.description
                ))
            
            # Get calendar events (from Google Calendar)
            calendar_events = db.query(CalendarEvent).filter(
                and_(
                    CalendarEvent.user_id == user_id,
                    CalendarEvent.start_time >= datetime.utcnow(),
                    CalendarEvent.start_time <= end_date
                )
            ).order_by(CalendarEvent.start_time).all()
            
            # Add calendar events as meetings (deduplicate with Schedulo meetings)
            for event in calendar_events:
                # Check if this calendar event overlaps with any Schedulo meeting
                is_duplicate = False
                for existing in result:
                    # Consider it a duplicate if times match exactly or overlap significantly
                    if (existing.start_time == event.start_time and 
                        existing.end_time == event.end_time):
                        is_duplicate = True
                        break
                    # Also check for title similarity (same meeting synced to calendar)
                    if (existing.title.lower() == event.title.lower() and
                        abs((existing.start_time - event.start_time).total_seconds()) < 300):  # Within 5 minutes
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    duration = int((event.end_time - event.start_time).total_seconds() / 60)
                    
                    result.append(MeetingResponse(
                        id=f"cal_{event.id}",
                        title=event.title,
                        type="external",  # Mark as external calendar event
                        start_time=event.start_time,
                        end_time=event.end_time,
                        duration=duration,
                        attendees=[AttendeeResponse(
                            id=user_id,
                            name="You",
                            email="",
                            role="Organizer",
                            availability="busy",
                            response_status="accepted"
                        )],
                        status="confirmed",
                        priority="medium",
                        location=event.location,
                        description=event.description
                    ))
            
            # Sort all by start time
            result.sort(key=lambda x: x.start_time)
            
            return result
        finally:
            db.close()
    
    async def get_meeting_by_id(
        self,
        meeting_id: str
    ) -> Optional[MeetingResponse]:
        """Get meeting by ID"""
        
        # TODO: Query database
        meetings = self._get_mock_meetings()
        return meetings[0] if meetings else None
    
    async def get_decision_explanation(
        self,
        meeting_id: str
    ) -> Optional[DecisionExplanationResponse]:
        """Get AI decision explanation for a meeting"""
        
        # TODO: Query database for stored decision
        return self._get_mock_decision()
    
    async def update_meeting_status(
        self,
        meeting_id: str,
        status: str
    ) -> bool:
        """Update meeting status"""
        
        # TODO: Update database
        return True
    
    async def cancel_meeting(
        self,
        meeting_id: str
    ) -> bool:
        """Cancel a meeting"""
        
        # TODO: Update database and send notifications
        return True
    
    def _get_mock_meetings(self) -> List[MeetingResponse]:
        """Mock meeting data"""
        base_time = datetime.utcnow() + timedelta(days=1)
        
        return [
            MeetingResponse(
                id="m1",
                title="Sprint Planning",
                type="team_sync",
                start_time=base_time.replace(hour=10, minute=0),
                end_time=base_time.replace(hour=11, minute=0),
                duration=60,
                attendees=[
                    AttendeeResponse(
                        id="u1",
                        name="Alex Rivera",
                        email="alex@schedulo.ai",
                        role="Product Manager",
                        availability="available",
                        response_status="accepted"
                    )
                ],
                status="confirmed",
                priority="high",
                location="Virtual — Zoom"
            )
        ]
    
    def _get_mock_decision(self) -> DecisionExplanationResponse:
        """Mock decision explanation"""
        base_time = datetime.utcnow() + timedelta(days=1)
        
        slot = TimeSlotResponse(
            id="s1",
            start_time=base_time.replace(hour=10, minute=0),
            end_time=base_time.replace(hour=11, minute=0),
            score=97,
            confidence=95,
            rank=1,
            reasoning="All attendees free. Optimal time based on preferences.",
            conflicts=[],
            attendee_availability=[],
            requires_approval=False,
            recommended=True
        )
        
        return DecisionExplanationResponse(
            meeting_id="m1",
            request_summary="Schedule a team sync meeting",
            recommended_slot=slot,
            alternative_slots=[],
            tradeoffs=[],
            overall_confidence=92,
            approval_needed=False,
            agent_insights=[
                AgentInsightResponse(
                    agent="calendar",
                    insight="Found 12 open windows"
                )
            ]
        )
