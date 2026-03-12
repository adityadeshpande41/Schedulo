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

# Store flow instances temporarily (in production, use Redis or database)
_flow_storage = {}


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
        
        # Load credentials from JSON file
        self.credentials_file = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "google_credentials.json"
        )
    
    def get_authorization_url(self, user_id: str) -> str:
        """
        Generate OAuth authorization URL
        
        Returns URL to redirect user to for Google consent
        """
        flow = Flow.from_client_secrets_file(
            self.credentials_file,
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=user_id,  # Pass user_id as state
            prompt='consent'  # Force consent screen to get refresh token
        )
        
        # Store flow for later use in callback
        _flow_storage[user_id] = flow
        
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
        user_id = state
        
        # Retrieve the stored flow
        flow = _flow_storage.get(user_id)
        if not flow:
            # Fallback: create new flow (won't work with PKCE but try anyway)
            flow = Flow.from_client_secrets_file(
                self.credentials_file,
                scopes=self.SCOPES,
                redirect_uri=self.redirect_uri
            )
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Clean up stored flow
        if user_id in _flow_storage:
            del _flow_storage[user_id]
        
        return {
            "user_id": user_id,
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
