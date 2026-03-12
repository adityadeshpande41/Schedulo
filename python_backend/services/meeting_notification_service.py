"""
Meeting Notification Service
Handles sending notifications when meetings are created, updated, or cancelled
Integrates email service and calendar service
"""

from typing import Dict, Any, List
from datetime import datetime
from .email_service import EmailService
from .calendar_service import CalendarService


class MeetingNotificationService:
    """
    Orchestrates notifications for meeting lifecycle events
    """
    
    def __init__(self):
        self.email_service = EmailService()
        self.calendar_service = CalendarService()
    
    async def notify_meeting_created(
        self,
        meeting: Dict[str, Any],
        organizer: Dict[str, Any],
        attendees: List[Dict[str, Any]],
        external_fallback_users: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send notifications when meeting is created
        
        Args:
            meeting: Meeting details
            organizer: Organizer info
            attendees: List of attendees
            external_fallback_users: Users who need email fallback
            
        Returns:
            Status of notifications sent
        """
        results = {
            "emails_sent": [],
            "calendar_synced": [],
            "fallback_emails": [],
            "errors": []
        }
        
        # Categorize attendees
        internal_attendees = []
        external_with_schedulo = []
        external_without_schedulo = external_fallback_users or []
        
        for attendee in attendees:
            if attendee.get("is_external"):
                # Check if they need fallback
                needs_fallback = any(
                    fb["email"] == attendee["email"] 
                    for fb in external_without_schedulo
                )
                if needs_fallback:
                    continue  # Handle separately
                else:
                    external_with_schedulo.append(attendee)
            else:
                internal_attendees.append(attendee)
        
        # Send to internal + external with Schedulo
        for attendee in internal_attendees + external_with_schedulo:
            try:
                # Send email invitation
                success = await self.email_service.send_meeting_invitation(
                    to_email=attendee["email"],
                    meeting=meeting,
                    organizer=organizer
                )
                
                if success:
                    results["emails_sent"].append(attendee["email"])
                
                # Sync to calendar if they have it connected
                if attendee.get("calendar_credentials"):
                    calendar_id = await self.calendar_service.sync_to_google_calendar(
                        user_credentials=attendee["calendar_credentials"],
                        meeting=meeting
                    )
                    if calendar_id:
                        results["calendar_synced"].append(attendee["email"])
                
            except Exception as e:
                results["errors"].append({
                    "email": attendee["email"],
                    "error": str(e)
                })
        
        # Send fallback emails to external users without Schedulo
        for fallback_user in external_without_schedulo:
            try:
                success = await self.email_service.send_external_invitation(
                    to_email=fallback_user["email"],
                    meeting=meeting,
                    organizer=organizer,
                    schedulo_url=None  # They don't have Schedulo
                )
                
                if success:
                    results["fallback_emails"].append({
                        "email": fallback_user["email"],
                        "reason": fallback_user.get("reason", "External system unavailable"),
                        "method": "email_with_ics"
                    })
                
            except Exception as e:
                results["errors"].append({
                    "email": fallback_user["email"],
                    "error": str(e)
                })
        
        return results
    
    async def notify_meeting_updated(
        self,
        meeting: Dict[str, Any],
        change_type: str,
        organizer: Dict[str, Any],
        attendees: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Send notifications when meeting is updated
        
        Args:
            meeting: Updated meeting details
            change_type: Type of change (time_changed, cancelled, etc.)
            organizer: Organizer info
            attendees: List of attendees
            
        Returns:
            Status of notifications sent
        """
        results = {
            "emails_sent": [],
            "errors": []
        }
        
        for attendee in attendees:
            try:
                success = await self.email_service.send_meeting_update(
                    to_email=attendee["email"],
                    meeting=meeting,
                    change_type=change_type,
                    organizer=organizer
                )
                
                if success:
                    results["emails_sent"].append(attendee["email"])
                
            except Exception as e:
                results["errors"].append({
                    "email": attendee["email"],
                    "error": str(e)
                })
        
        return results
    
    async def send_meeting_reminders(
        self,
        meeting: Dict[str, Any],
        attendees: List[Dict[str, Any]],
        minutes_before: int = 15
    ) -> Dict[str, Any]:
        """
        Send meeting reminders
        
        Args:
            meeting: Meeting details
            attendees: List of attendees
            minutes_before: How many minutes before meeting
            
        Returns:
            Status of reminders sent
        """
        results = {
            "reminders_sent": [],
            "errors": []
        }
        
        for attendee in attendees:
            try:
                success = await self.email_service.send_meeting_reminder(
                    to_email=attendee["email"],
                    meeting=meeting,
                    minutes_before=minutes_before
                )
                
                if success:
                    results["reminders_sent"].append(attendee["email"])
                
            except Exception as e:
                results["errors"].append({
                    "email": attendee["email"],
                    "error": str(e)
                })
        
        return results
