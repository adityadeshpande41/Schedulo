"""
Email Service
Handles all email notifications for meeting invitations, updates, and reminders
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import resend
from icalendar import Calendar, Event
import base64


class EmailService:
    """
    Sends emails for meeting invitations, updates, and notifications
    Uses Resend for delivery
    """
    
    def __init__(self):
        self.api_key = os.getenv("RESEND_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL", "onboarding@resend.dev")
        if self.api_key:
            resend.api_key = self.api_key
    
    async def send_meeting_invitation(
        self,
        to_email: str,
        meeting: Dict[str, Any],
        organizer: Dict[str, Any]
    ) -> bool:
        """
        Send meeting invitation with calendar attachment
        
        Args:
            to_email: Recipient email
            meeting: Meeting details (title, start_time, end_time, etc.)
            organizer: Organizer details (name, email)
            
        Returns:
            True if sent successfully
        """
        if not self.api_key:
            print(f"⚠️  Email not configured. Would send invitation to {to_email}")
            return False
        
        try:
            # Generate calendar invite
            ics_content = self._generate_ics(meeting, organizer, to_email)
            
            # Create email
            subject = f"Meeting Invitation: {meeting['title']}"
            html_content = self._render_invitation_template(meeting, organizer)
            
            # Send with Resend
            params = {
                "from": self.from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
                "attachments": [{
                    "filename": "meeting.ics",
                    "content": base64.b64encode(ics_content.encode()).decode()
                }]
            }
            
            response = resend.Emails.send(params)
            return response.get("id") is not None
            
        except Exception as e:
            print(f"❌ Error sending invitation: {e}")
            return False
    
    async def send_meeting_update(
        self,
        to_email: str,
        meeting: Dict[str, Any],
        change_type: str,
        organizer: Dict[str, Any]
    ) -> bool:
        """
        Send meeting update notification
        
        Args:
            to_email: Recipient email
            meeting: Updated meeting details
            change_type: "time_changed", "cancelled", "attendee_added"
            organizer: Organizer details
            
        Returns:
            True if sent successfully
        """
        if not self.api_key:
            print(f"⚠️  Email not configured. Would send update to {to_email}")
            return False
        
        try:
            subject_map = {
                "time_changed": f"Time Changed: {meeting['title']}",
                "cancelled": f"Cancelled: {meeting['title']}",
                "attendee_added": f"Updated: {meeting['title']}"
            }
            
            subject = subject_map.get(change_type, f"Update: {meeting['title']}")
            html_content = self._render_update_template(meeting, change_type, organizer)
            
            params = {
                "from": self.from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_content
            }
            
            # Attach updated .ics if time changed
            if change_type == "time_changed":
                ics_content = self._generate_ics(meeting, organizer, to_email)
                params["attachments"] = [{
                    "filename": "meeting.ics",
                    "content": base64.b64encode(ics_content.encode()).decode()
                }]
            
            response = resend.Emails.send(params)
            return response.get("id") is not None
            
        except Exception as e:
            print(f"❌ Error sending update: {e}")
            return False
    
    async def send_meeting_reminder(
        self,
        to_email: str,
        meeting: Dict[str, Any],
        minutes_before: int = 15
    ) -> bool:
        """
        Send meeting reminder
        
        Args:
            to_email: Recipient email
            meeting: Meeting details
            minutes_before: How many minutes before meeting
            
        Returns:
            True if sent successfully
        """
        if not self.api_key:
            return False
        
        try:
            subject = f"Reminder: {meeting['title']} in {minutes_before} minutes"
            html_content = self._render_reminder_template(meeting, minutes_before)
            
            params = {
                "from": self.from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_content
            }
            
            response = resend.Emails.send(params)
            return response.get("id") is not None
            
        except Exception as e:
            print(f"❌ Error sending reminder: {e}")
            return False
    
    async def send_external_invitation(
        self,
        to_email: str,
        meeting: Dict[str, Any],
        organizer: Dict[str, Any],
        schedulo_url: Optional[str] = None
    ) -> bool:
        """
        Send invitation to external user (different company)
        Includes link to their Schedulo instance or calendar invite
        
        Args:
            to_email: External user email
            meeting: Meeting details
            organizer: Organizer details
            schedulo_url: External Schedulo instance URL
            
        Returns:
            True if sent successfully
        """
        if not self.api_key:
            print(f"⚠️  Email not configured. Would send external invitation to {to_email}")
            return False
        
        try:
            subject = f"Meeting Invitation from {organizer['name']}: {meeting['title']}"
            html_content = self._render_external_invitation_template(
                meeting, organizer, schedulo_url
            )
            
            # Always attach .ics for external users
            ics_content = self._generate_ics(meeting, organizer, to_email)
            
            params = {
                "from": self.from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
                "attachments": [{
                    "filename": "meeting.ics",
                    "content": base64.b64encode(ics_content.encode()).decode()
                }]
            }
            
            response = resend.Emails.send(params)
            return response.get("id") is not None
            
        except Exception as e:
            print(f"❌ Error sending external invitation: {e}")
            return False
    
    def _generate_ics(
        self,
        meeting: Dict[str, Any],
        organizer: Dict[str, Any],
        attendee_email: str
    ) -> str:
        """Generate iCalendar (.ics) file content"""
        cal = Calendar()
        cal.add('prodid', '-//Schedulo//Meeting Scheduler//EN')
        cal.add('version', '2.0')
        cal.add('method', 'REQUEST')
        
        event = Event()
        event.add('summary', meeting['title'])
        event.add('dtstart', meeting['start_time'])
        event.add('dtend', meeting['end_time'])
        event.add('dtstamp', datetime.utcnow())
        event.add('uid', f"{meeting['id']}@schedulo.app")
        
        # Organizer
        event.add('organizer', f"mailto:{organizer['email']}")
        
        # Attendees
        event.add('attendee', f"mailto:{attendee_email}")
        for attendee in meeting.get('attendees', []):
            if attendee['email'] != attendee_email:
                event.add('attendee', f"mailto:{attendee['email']}")
        
        # Optional fields
        if meeting.get('location'):
            event.add('location', meeting['location'])
        if meeting.get('description'):
            event.add('description', meeting['description'])
        
        # Status
        event.add('status', 'CONFIRMED')
        
        cal.add_component(event)
        return cal.to_ical().decode('utf-8')
    
    def _render_invitation_template(
        self,
        meeting: Dict[str, Any],
        organizer: Dict[str, Any]
    ) -> str:
        """Render HTML email template for invitation"""
        start_time = meeting['start_time'].strftime('%A, %B %d, %Y at %I:%M %p')
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .meeting-details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #667eea; 
                          color: white; text-decoration: none; border-radius: 6px; margin: 10px 5px; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📅 Meeting Invitation</h1>
                </div>
                <div class="content">
                    <p>Hi there,</p>
                    <p><strong>{organizer['name']}</strong> has invited you to a meeting:</p>
                    
                    <div class="meeting-details">
                        <h2>{meeting['title']}</h2>
                        <p><strong>📅 When:</strong> {start_time}</p>
                        <p><strong>⏱️ Duration:</strong> {meeting.get('duration', 30)} minutes</p>
                        {f"<p><strong>📍 Location:</strong> {meeting['location']}</p>" if meeting.get('location') else ""}
                        {f"<p><strong>📝 Notes:</strong> {meeting['description']}</p>" if meeting.get('description') else ""}
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="#" class="button">Accept</a>
                        <a href="#" class="button" style="background: #e74c3c;">Decline</a>
                    </div>
                    
                    <p style="margin-top: 20px; font-size: 14px; color: #666;">
                        A calendar invite (.ics file) is attached to this email. 
                        You can add it directly to your calendar.
                    </p>
                </div>
                <div class="footer">
                    <p>Powered by Schedulo - AI Meeting Scheduler</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _render_update_template(
        self,
        meeting: Dict[str, Any],
        change_type: str,
        organizer: Dict[str, Any]
    ) -> str:
        """Render HTML email template for updates"""
        messages = {
            "time_changed": "The meeting time has been changed.",
            "cancelled": "This meeting has been cancelled.",
            "attendee_added": "New attendees have been added to this meeting."
        }
        
        return f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2>Meeting Update</h2>
                <p>{messages.get(change_type, 'The meeting has been updated.')}</p>
                <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>{meeting['title']}</h3>
                    <p><strong>Organizer:</strong> {organizer['name']}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _render_reminder_template(
        self,
        meeting: Dict[str, Any],
        minutes_before: int
    ) -> str:
        """Render HTML email template for reminders"""
        return f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2>⏰ Meeting Reminder</h2>
                <p>Your meeting starts in {minutes_before} minutes!</p>
                <div style="background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>{meeting['title']}</h3>
                    <p><strong>Time:</strong> {meeting['start_time'].strftime('%I:%M %p')}</p>
                    {f"<p><strong>Location:</strong> {meeting['location']}</p>" if meeting.get('location') else ""}
                </div>
            </div>
        </body>
        </html>
        """
    
    async def send_scheduling_link_email(
        self,
        to_email: str,
        organizer: Dict[str, Any],
        scheduling_link: str,
        meeting_title: str
    ) -> bool:
        """
        Send email with scheduling link (Calendly-style)
        External user clicks link to pick a time
        """
        if not self.api_key:
            print(f"⚠️  Email not configured. Would send scheduling link to {to_email}")
            return False
        
        try:
            subject = f"{organizer['name']} wants to meet with you"
            html_content = self._render_scheduling_link_template(
                organizer, scheduling_link, meeting_title
            )
            
            params = {
                "from": self.from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_content
            }
            
            response = resend.Emails.send(params)
            return response.get("id") is not None
            
        except Exception as e:
            print(f"❌ Error sending scheduling link: {e}")
            return False
    
    def _render_scheduling_link_template(
        self,
        organizer: Dict[str, Any],
        scheduling_link: str,
        meeting_title: str
    ) -> str:
        """Render HTML email template for scheduling link"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 40px 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 40px 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; padding: 16px 40px; background: #667eea; 
                          color: white; text-decoration: none; border-radius: 6px; font-size: 16px;
                          font-weight: bold; margin: 20px 0; }}
                .button:hover {{ background: #5568d3; }}
                .info-box {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0;
                            border-left: 4px solid #667eea; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📅 Meeting Request</h1>
                </div>
                <div class="content">
                    <p style="font-size: 18px;">Hi there,</p>
                    <p style="font-size: 16px;">
                        <strong>{organizer['name']}</strong> from <strong>{organizer.get('company', 'their organization')}</strong> 
                        would like to schedule a meeting with you.
                    </p>
                    
                    <div class="info-box">
                        <h3 style="margin-top: 0;">{meeting_title}</h3>
                        <p style="margin-bottom: 0; color: #666;">
                            Click the button below to view available times and pick one that works for you.
                        </p>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="{scheduling_link}" class="button">Pick a Time</a>
                    </div>
                    
                    <p style="margin-top: 30px; font-size: 14px; color: #666; text-align: center;">
                        This link will show you {organizer['name']}'s available times.<br>
                        Simply click a time slot to confirm the meeting.
                    </p>
                </div>
                <div style="text-align: center; margin-top: 30px; color: #666; font-size: 12px;">
                    <p>Powered by Schedulo - AI Meeting Scheduler</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _render_external_invitation_template(
        self,
        meeting: Dict[str, Any],
        organizer: Dict[str, Any],
        schedulo_url: Optional[str]
    ) -> str:
        """Render HTML email template for external invitations"""
        start_time = meeting['start_time'].strftime('%A, %B %d, %Y at %I:%M %p')
        
        schedulo_section = ""
        if schedulo_url:
            schedulo_section = f"""
            <p style="text-align: center; margin: 20px 0;">
                <a href="{schedulo_url}" class="button">View in Your Schedulo</a>
            </p>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .meeting-details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #667eea; 
                          color: white; text-decoration: none; border-radius: 6px; }}
                .external-badge {{ background: #3498db; color: white; padding: 4px 12px; 
                                  border-radius: 12px; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌐 External Meeting Invitation</h1>
                    <span class="external-badge">Cross-Company Meeting</span>
                </div>
                <div class="content">
                    <p>Hi there,</p>
                    <p><strong>{organizer['name']}</strong> from <strong>{organizer.get('company', 'another organization')}</strong> 
                       has invited you to a meeting:</p>
                    
                    <div class="meeting-details">
                        <h2>{meeting['title']}</h2>
                        <p><strong>📅 When:</strong> {start_time}</p>
                        <p><strong>⏱️ Duration:</strong> {meeting.get('duration', 30)} minutes</p>
                        {f"<p><strong>📝 Notes:</strong> {meeting['description']}</p>" if meeting.get('description') else ""}
                    </div>
                    
                    {schedulo_section}
                    
                    <p style="margin-top: 20px; font-size: 14px; color: #666;">
                        A calendar invite (.ics file) is attached. You can add it to your calendar 
                        or respond through your Schedulo instance if available.
                    </p>
                </div>
                <div style="text-align: center; margin-top: 30px; color: #666; font-size: 12px;">
                    <p>Powered by Schedulo - AI Meeting Scheduler</p>
                </div>
            </div>
        </body>
        </html>
        """
