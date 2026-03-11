"""
Google Calendar Integration
OAuth flow and calendar sync
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleCalendarIntegration:
    """
    Google Calendar OAuth and API integration
    """
    
    SCOPES = [
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/google/callback")
    
    def get_authorization_url(self, user_id: str) -> str:
        """
        Generate OAuth authorization URL
        
        Returns URL to redirect user to for Google consent
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=user_id  # Pass user_id as state
        )
        
        return authorization_url
    
    async def handle_oauth_callback(
        self,
        code: str,
        state: str
    ) -> Dict[str, Any]:
        """
        Handle OAuth callback and exchange code for tokens
        
        Returns:
        {
            "user_id": "u1",
            "access_token": "...",
            "refresh_token": "...",
            "expires_at": datetime
        }
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        return {
            "user_id": state,  # state contains user_id
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "expires_at": credentials.expiry
        }
    
    def get_calendar_service(self, credentials_dict: Dict[str, Any]):
        """Build Google Calendar API service"""
        credentials = Credentials(
            token=credentials_dict["access_token"],
            refresh_token=credentials_dict.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        
        return build('calendar', 'v3', credentials=credentials)
    
    async def fetch_events(
        self,
        credentials_dict: Dict[str, Any],
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Fetch calendar events from Google Calendar
        
        Returns list of events in our format
        """
        try:
            service = self.get_calendar_service(credentials_dict)
            
            # Call Google Calendar API
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_date.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Convert to our format
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    "external_id": event['id'],
                    "title": event.get('summary', 'Untitled'),
                    "start_time": datetime.fromisoformat(start.replace('Z', '+00:00')),
                    "end_time": datetime.fromisoformat(end.replace('Z', '+00:00')),
                    "is_busy": event.get('transparency', 'opaque') == 'opaque',
                    "location": event.get('location'),
                    "attendees": [
                        a.get('email') for a in event.get('attendees', [])
                    ]
                })
            
            return formatted_events
            
        except HttpError as error:
            print(f"Google Calendar API error: {error}")
            return []
    
    async def create_event(
        self,
        credentials_dict: Dict[str, Any],
        event_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create event in Google Calendar
        
        Returns event ID if successful
        """
        try:
            service = self.get_calendar_service(credentials_dict)
            
            event = {
                'summary': event_data['title'],
                'start': {
                    'dateTime': event_data['start_time'].isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': event_data['end_time'].isoformat(),
                    'timeZone': 'UTC',
                },
                'attendees': [
                    {'email': email} for email in event_data.get('attendees', [])
                ],
            }
            
            if 'description' in event_data:
                event['description'] = event_data['description']
            
            if 'location' in event_data:
                event['location'] = event_data['location']
            
            created_event = service.events().insert(
                calendarId='primary',
                body=event,
                sendUpdates='all'  # Send email invites
            ).execute()
            
            return created_event['id']
            
        except HttpError as error:
            print(f"Google Calendar API error: {error}")
            return None
