"""
Calendar Service
Integrates with Google Calendar and Outlook for calendar sync
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import msal


class CalendarService:
    """
    Syncs meetings with external calendar providers
    Supports Google Calendar and Microsoft Outlook
    """
    
    def __init__(self):
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.microsoft_client_id = os.getenv("MICROSOFT_CLIENT_ID")
        self.microsoft_client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")
    
    async def sync_to_google_calendar(
        self,
        user_credentials: Dict[str, Any],
        meeting: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create meeting in user's Google Calendar
        
        Args:
            user_credentials: User's OAuth credentials
            meeting: Meeting details
            
        Returns:
            Google Calendar event ID or None
        """
        try:
            creds = Credentials(
                token=user_credentials['access_token'],
                refresh_token=user_credentials.get('refresh_token'),
                token_uri='https://oauth2.googleapis.com/token',
                client_id=self.google_client_id,
                client_secret=self.google_client_secret
            )
            
            service = build('calendar', 'v3', credentials=creds)
            
            event = {
                'summary': meeting['title'],
                'description': meeting.get('description', ''),
                'start': {
                    'dateTime': meeting['start_time'].isoformat(),
                    'timeZone': meeting.get('timezone', 'UTC'),
                },
                'end': {
                    'dateTime': meeting['end_time'].isoformat(),
                    'timeZone': meeting.get('timezone', 'UTC'),
                },
                'attendees': [
                    {'email': attendee['email']}
                    for attendee in meeting.get('attendees', [])
                ],
            }
            
            if meeting.get('location'):
                event['location'] = meeting['location']
            
            result = service.events().insert(
                calendarId='primary',
                body=event,
                sendUpdates='all'
            ).execute()
            
            return result.get('id')
            
        except Exception as e:
            print(f"❌ Error syncing to Google Calendar: {e}")
            return None
    
    async def sync_to_outlook_calendar(
        self,
        user_credentials: Dict[str, Any],
        meeting: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create meeting in user's Outlook Calendar
        
        Args:
            user_credentials: User's OAuth credentials
            meeting: Meeting details
            
        Returns:
            Outlook event ID or None
        """
        try:
            # Use Microsoft Graph API
            import requests
            
            headers = {
                'Authorization': f"Bearer {user_credentials['access_token']}",
                'Content-Type': 'application/json'
            }
            
            event = {
                'subject': meeting['title'],
                'body': {
                    'contentType': 'HTML',
                    'content': meeting.get('description', '')
                },
                'start': {
                    'dateTime': meeting['start_time'].isoformat(),
                    'timeZone': meeting.get('timezone', 'UTC')
                },
                'end': {
                    'dateTime': meeting['end_time'].isoformat(),
                    'timeZone': meeting.get('timezone', 'UTC')
                },
                'attendees': [
                    {
                        'emailAddress': {'address': attendee['email']},
                        'type': 'required'
                    }
                    for attendee in meeting.get('attendees', [])
                ]
            }
            
            if meeting.get('location'):
                event['location'] = {'displayName': meeting['location']}
            
            response = requests.post(
                'https://graph.microsoft.com/v1.0/me/events',
                headers=headers,
                json=event
            )
            
            if response.status_code == 201:
                return response.json().get('id')
            
            return None
            
        except Exception as e:
            print(f"❌ Error syncing to Outlook: {e}")
            return None
    
    async def get_google_calendar_events(
        self,
        user_credentials: Dict[str, Any],
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Fetch events from user's Google Calendar
        
        Args:
            user_credentials: User's OAuth credentials
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            List of calendar events
        """
        try:
            creds = Credentials(
                token=user_credentials['access_token'],
                refresh_token=user_credentials.get('refresh_token'),
                token_uri='https://oauth2.googleapis.com/token',
                client_id=self.google_client_id,
                client_secret=self.google_client_secret
            )
            
            service = build('calendar', 'v3', credentials=creds)
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_date.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            return [
                {
                    'id': event['id'],
                    'title': event.get('summary', 'No title'),
                    'start_time': event['start'].get('dateTime', event['start'].get('date')),
                    'end_time': event['end'].get('dateTime', event['end'].get('date')),
                    'is_busy': event.get('transparency', 'opaque') == 'opaque'
                }
                for event in events
            ]
            
        except Exception as e:
            print(f"❌ Error fetching Google Calendar events: {e}")
            return []
    
    async def get_outlook_calendar_events(
        self,
        user_credentials: Dict[str, Any],
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Fetch events from user's Outlook Calendar
        
        Args:
            user_credentials: User's OAuth credentials
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            List of calendar events
        """
        try:
            import requests
            
            headers = {
                'Authorization': f"Bearer {user_credentials['access_token']}",
            }
            
            params = {
                'startDateTime': start_date.isoformat(),
                'endDateTime': end_date.isoformat(),
                '$select': 'subject,start,end,showAs'
            }
            
            response = requests.get(
                'https://graph.microsoft.com/v1.0/me/calendarview',
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                events = response.json().get('value', [])
                
                return [
                    {
                        'id': event['id'],
                        'title': event.get('subject', 'No title'),
                        'start_time': event['start']['dateTime'],
                        'end_time': event['end']['dateTime'],
                        'is_busy': event.get('showAs', 'busy') != 'free'
                    }
                    for event in events
                ]
            
            return []
            
        except Exception as e:
            print(f"❌ Error fetching Outlook events: {e}")
            return []
