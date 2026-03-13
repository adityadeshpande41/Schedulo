"""
Personal Agent
Privacy-preserving agent that runs locally for each user
Analyzes calendar and preferences to generate availability signals
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass

from .base_agent import BaseAgent, AgentStatus, AgentResult
from .ml_behavior_model import BehaviorLearningModel


@dataclass
class AvailabilitySignal:
    """
    Privacy-preserving availability signal
    Only shares constrained availability, not raw calendar data
    """
    time_window: Dict[str, datetime]  # start_time, end_time
    availability_score: float  # 0.0 (unavailable) to 1.0 (highly available)
    confidence: float  # How confident the agent is in this score
    reasoning: str  # Why this score was given
    conflicts: List[Dict[str, Any]]  # Soft/hard conflicts


class PersonalAgent(BaseAgent):
    """
    Personal scheduling agent that runs for each user
    Analyzes calendar, preferences, and behavior to generate availability signals
    """
    
    def __init__(self, user_id: str):
        super().__init__(agent_type="personal", name=f"Personal Agent ({user_id})")
        self.user_id = user_id
        self.behavior_model = BehaviorLearningModel(user_id)
    
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Execute personal agent analysis
        
        Context expected:
            - request_type: "availability_check"
            - time_windows: List of candidate time windows
            - meeting_context: Meeting details (type, priority, etc.)
        """
        self.update_status(AgentStatus.ANALYZING, f"Analyzing availability for {self.user_id}...")
        
        try:
            request_type = context.get("request_type")
            time_windows = context.get("time_windows", [])
            meeting_context = context.get("meeting_context", {})
            
            if request_type == "availability_check":
                signals = await self._generate_availability_signals(
                    time_windows,
                    meeting_context
                )
                
                self.update_status(AgentStatus.COMPLETE, 
                                 f"Generated {len(signals)} availability signals")
                
                return self.create_result(
                    data={
                        "availability_signals": signals,
                        "user_id": self.user_id
                    },
                    message=f"Analyzed {len(time_windows)} time windows",
                    confidence=0.9
                )
            else:
                raise ValueError(f"Unknown request type: {request_type}")
                
        except Exception as e:
            self.update_status(AgentStatus.ERROR, f"Error: {str(e)}")
            return self.create_result(
                data={},
                message=f"Personal agent failed: {str(e)}",
                errors=[str(e)]
            )
    
    async def _generate_availability_signals(
        self,
        time_windows: List[Dict[str, Any]],
        meeting_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate availability signals for each time window
        """
        from database.connection import get_db_context
        from database.models import CalendarEvent, UserPreference, CalendarIntegration
        from integrations.google_calendar import GoogleCalendarIntegration
        
        signals = []
        
        # Fetch user's calendar events
        calendar_events = []
        with get_db_context() as db:
            # Try to get from database first
            if time_windows:
                # Handle both "start"/"end" and "start_time"/"end_time" formats
                start_time = min(w.get("start_time") or w.get("start") for w in time_windows)
                end_time = max(w.get("end_time") or w.get("end") for w in time_windows)
                
                calendar_events = db.query(CalendarEvent).filter(
                    CalendarEvent.user_id == self.user_id,
                    CalendarEvent.start_time <= end_time,
                    CalendarEvent.end_time >= start_time
                ).all()
                
                print(f"📅 [PersonalAgent] Found {len(calendar_events)} calendar events in database for {self.user_id}")
                
                # Convert to dict immediately while still in session
                calendar_events_dict = [
                    {
                        "start_time": event.start_time,
                        "end_time": event.end_time,
                        "title": event.title
                    }
                    for event in calendar_events
                ]
                
                print(f"📅 [PersonalAgent] Converted {len(calendar_events_dict)} events to dict")
                
                # Ensure all event times are timezone-aware
                # The database stores times in local timezone but without timezone info
                # We need to interpret them as EDT (America/New_York)
                import pytz
                edt = pytz.timezone('America/New_York')
                for evt in calendar_events_dict:
                    if evt['start_time'].tzinfo is None:
                        # Interpret naive datetime as EDT
                        evt['start_time'] = edt.localize(evt['start_time'])
                    if evt['end_time'].tzinfo is None:
                        # Interpret naive datetime as EDT
                        evt['end_time'] = edt.localize(evt['end_time'])
                    print(f"   - {evt['title']}: {evt['start_time']} to {evt['end_time']}")
                
                # If no events in database, try fetching from Google Calendar directly
                if not calendar_events_dict:
                    integration = db.query(CalendarIntegration).filter(
                        CalendarIntegration.user_id == self.user_id,
                        CalendarIntegration.is_active == True
                    ).first()
                    
                    if integration:
                        try:
                            google_cal = GoogleCalendarIntegration()
                            credentials = {
                                "access_token": integration.access_token,
                                "refresh_token": integration.refresh_token
                            }
                            
                            # Fetch events from Google Calendar
                            google_events = await google_cal.fetch_events(
                                credentials,
                                start_time,
                                end_time
                            )
                            
                            # Convert to our format
                            calendar_events_dict = [
                                {
                                    'start_time': event['start_time'],
                                    'end_time': event['end_time'],
                                    'title': event['title']
                                }
                                for event in google_events
                            ]
                            
                            print(f"✅ Fetched {len(calendar_events_dict)} events from Google Calendar for {self.user_id}")
                        except Exception as e:
                            print(f"❌ Failed to fetch from Google Calendar: {e}")
            
            # Get user preferences
            preferences = db.query(UserPreference).filter(
                UserPreference.user_id == self.user_id,
                UserPreference.active == True
            ).all()
        
        # calendar_events_dict is already created above
        # Analyze each time window
        for window in time_windows:
            signal = self._analyze_time_window(
                window,
                calendar_events_dict,
                meeting_context
            )
            signals.append(signal)
        
        return signals
    
    def _analyze_time_window(
        self,
        window: Dict[str, Any],
        calendar_events: List[Dict[str, Any]],
        meeting_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze a single time window and generate availability signal
        """
        import pytz
        
        # Handle both "start"/"end" and "start_time"/"end_time" formats
        start_time = window.get("start_time") or window.get("start")
        end_time = window.get("end_time") or window.get("end")
        
        # Ensure start_time and end_time are timezone-aware
        if start_time.tzinfo is None:
            start_time = pytz.UTC.localize(start_time)
        if end_time.tzinfo is None:
            end_time = pytz.UTC.localize(end_time)
        
        # Check for hard conflicts (existing meetings)
        hard_conflicts = []
        print(f"🔍 [PersonalAgent] Checking {len(calendar_events)} events for conflicts with {start_time} - {end_time}")
        for event in calendar_events:
            event_start = event["start_time"]
            event_end = event["end_time"]
            
            # Ensure event times are timezone-aware
            if event_start.tzinfo is None:
                event_start = pytz.UTC.localize(event_start)
            if event_end.tzinfo is None:
                event_end = pytz.UTC.localize(event_end)
            
            if self._times_overlap(start_time, end_time, event_start, event_end):
                print(f"   ⚠️  CONFLICT FOUND: {event['title']} ({event_start} - {event_end})")
                hard_conflicts.append({
                    "type": "hard",
                    "description": f"Conflicts with: {event['title']}",
                    "attendee_id": self.user_id
                })
        
        # If hard conflict exists, availability is 0
        if hard_conflicts:
            return {
                "time_window": {
                    "start_time": start_time,
                    "end_time": end_time
                },
                "availability_score": 0.0,
                "confidence": 1.0,
                "reasoning": f"Hard conflict: {hard_conflicts[0]['description']}",
                "conflicts": hard_conflicts,
                "user_id": self.user_id
            }
        
        # Check for soft conflicts
        soft_conflicts = []
        availability_score = 1.0
        
        # Check if outside working hours
        hour = start_time.hour
        if hour < 9 or hour >= 17:
            soft_conflicts.append({
                "type": "soft",
                "description": "Outside typical working hours",
                "attendee_id": self.user_id
            })
            availability_score *= 0.7
        
        # Check if back-to-back with another meeting
        for event in calendar_events:
            event_start = event["start_time"]
            event_end = event["end_time"]
            
            # Ensure event times are timezone-aware
            if event_start.tzinfo is None:
                event_start = pytz.UTC.localize(event_start)
            if event_end.tzinfo is None:
                event_end = pytz.UTC.localize(event_end)
            
            time_diff_before = abs((start_time - event_end).total_seconds() / 60)
            time_diff_after = abs((event_start - end_time).total_seconds() / 60)
            
            if time_diff_before < 15 or time_diff_after < 15:
                soft_conflicts.append({
                    "type": "soft",
                    "description": "Back-to-back with another meeting",
                    "attendee_id": self.user_id
                })
                availability_score *= 0.8
                break
        
        # Use ML model to predict preference
        try:
            ml_score = self.behavior_model.predict_preference(
                day_of_week=start_time.weekday(),
                hour_of_day=start_time.hour,
                meeting_type=meeting_context.get("type", "team_sync"),
                duration=meeting_context.get("duration", 30),
                priority=meeting_context.get("priority", "medium")
            )
            availability_score *= ml_score
        except Exception as e:
            print(f"ML prediction failed: {e}")
        
        reasoning = "Available"
        if soft_conflicts:
            reasoning = f"Available with {len(soft_conflicts)} soft conflict(s)"
        
        return {
            "time_window": {
                "start_time": start_time,
                "end_time": end_time
            },
            "availability_score": availability_score,
            "confidence": 0.9,
            "reasoning": reasoning,
            "conflicts": soft_conflicts,
            "user_id": self.user_id
        }
    
    def _times_overlap(
        self,
        start1: datetime,
        end1: datetime,
        start2: datetime,
        end2: datetime
    ) -> bool:
        """Check if two time ranges overlap"""
        # Make both timezone-aware or both naive for comparison
        if start1.tzinfo is not None and start2.tzinfo is None:
            # start1 is aware, start2 is naive - make start2 aware (assume UTC)
            import pytz
            start2 = pytz.UTC.localize(start2) if start2.tzinfo is None else start2
            end2 = pytz.UTC.localize(end2) if end2.tzinfo is None else end2
        elif start1.tzinfo is None and start2.tzinfo is not None:
            # start1 is naive, start2 is aware - make start1 aware (assume UTC)
            import pytz
            start1 = pytz.UTC.localize(start1) if start1.tzinfo is None else start1
            end1 = pytz.UTC.localize(end1) if end1.tzinfo is None else end1
        
        return start1 < end2 and end1 > start2
    
    def get_capabilities(self) -> List[str]:
        return [
            "Calendar analysis",
            "Preference learning",
            "Behavior prediction",
            "Privacy-preserving signals"
        ]
    
    def get_description(self) -> str:
        return f"Personal scheduling agent for user {self.user_id}"
