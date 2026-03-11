"""
User Data Service
Provides privacy-preserving access to user data for personal agents
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from database.models import (
    User, Meeting, MeetingAttendee, UserPreferences,
    CalendarEvent, HistoricalMeeting, TimeSlot
)
from database.connection import get_db


class UserDataService:
    """
    Service for loading user data for personal agents
    
    PRIVACY: Each method only returns data for the specified user
    """
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db or next(get_db())
    
    def get_user_calendar(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get user's calendar events for date range
        
        PRIVACY: Only returns this user's events
        """
        events = self.db.query(CalendarEvent).filter(
            and_(
                CalendarEvent.user_id == user_id,
                CalendarEvent.start_time >= start_date,
                CalendarEvent.end_time <= end_date
            )
        ).all()
        
        return [
            {
                "id": event.id,
                "start_time": event.start_time,
                "end_time": event.end_time,
                "title": event.title,
                "is_busy": event.is_busy,
                "is_flexible": event.is_flexible,
                "priority": event.priority
            }
            for event in events
        ]
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's scheduling preferences
        
        PRIVACY: Only returns this user's preferences
        """
        prefs = self.db.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()
        
        if not prefs:
            return self._get_default_preferences()
        
        return {
            "work_hours_start": prefs.work_hours_start,
            "work_hours_end": prefs.work_hours_end,
            "timezone": prefs.timezone,
            "preferred_meeting_duration": prefs.preferred_meeting_duration,
            "buffer_time": prefs.buffer_time,
            "max_meetings_per_day": prefs.max_meetings_per_day,
            "preferred_days": prefs.preferred_days or [],
            "avoid_days": prefs.avoid_days or [],
            "lunch_break_start": prefs.lunch_break_start,
            "lunch_break_end": prefs.lunch_break_end,
            "focus_time_blocks": prefs.focus_time_blocks or []
        }
    
    def get_historical_meetings(
        self,
        user_id: str,
        lookback_days: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Get user's historical meeting data for ML training
        
        PRIVACY: Only returns meetings this user attended
        """
        cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)
        
        # Get historical meetings
        historical = self.db.query(HistoricalMeeting).filter(
            and_(
                HistoricalMeeting.user_id == user_id,
                HistoricalMeeting.meeting_date >= cutoff_date
            )
        ).all()
        
        return [
            {
                "meeting_id": h.id,
                "start_time": h.meeting_date,
                "duration": h.duration,
                "type": h.meeting_type,
                "priority": h.priority,
                "was_accepted": h.was_accepted,
                "was_rescheduled": h.was_rescheduled,
                "response_time": h.response_time_seconds,
                "original_start": h.original_start_time,
                "actual_start": h.actual_start_time
            }
            for h in historical
        ]
    
    def check_availability(
        self,
        user_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> bool:
        """
        Check if user is available during time window
        
        Returns True if available (no conflicts), False if busy
        """
        # Check calendar events
        conflicts = self.db.query(CalendarEvent).filter(
            and_(
                CalendarEvent.user_id == user_id,
                CalendarEvent.is_busy == True,
                or_(
                    # Event starts during window
                    and_(
                        CalendarEvent.start_time >= start_time,
                        CalendarEvent.start_time < end_time
                    ),
                    # Event ends during window
                    and_(
                        CalendarEvent.end_time > start_time,
                        CalendarEvent.end_time <= end_time
                    ),
                    # Event spans entire window
                    and_(
                        CalendarEvent.start_time <= start_time,
                        CalendarEvent.end_time >= end_time
                    )
                )
            )
        ).count()
        
        return conflicts == 0
    
    def get_flexible_events(
        self,
        user_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get events that could potentially be rescheduled
        
        Returns events marked as flexible or low priority
        """
        events = self.db.query(CalendarEvent).filter(
            and_(
                CalendarEvent.user_id == user_id,
                or_(
                    CalendarEvent.is_flexible == True,
                    CalendarEvent.priority == "low"
                ),
                CalendarEvent.start_time >= start_time,
                CalendarEvent.end_time <= end_time
            )
        ).all()
        
        return [
            {
                "id": event.id,
                "start_time": event.start_time,
                "end_time": event.end_time,
                "title": event.title,
                "priority": event.priority,
                "is_flexible": event.is_flexible
            }
            for event in events
        ]
    
    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get basic user information"""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return None
        
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "timezone": user.timezone
        }
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """Default preferences if none set"""
        return {
            "work_hours_start": "09:00",
            "work_hours_end": "17:00",
            "timezone": "UTC",
            "preferred_meeting_duration": 30,
            "buffer_time": 5,
            "max_meetings_per_day": 8,
            "preferred_days": [1, 2, 3, 4],  # Mon-Thu
            "avoid_days": [],
            "lunch_break_start": "12:00",
            "lunch_break_end": "13:00",
            "focus_time_blocks": []
        }
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()
