"""
Behavior Agent
Learns scheduling patterns and preferences from historical data
"""

from typing import Dict, Any, List
from datetime import datetime, time
from .base_agent import BaseAgent, AgentStatus, AgentResult


class BehaviorAgent(BaseAgent):
    """
    Analyzes historical scheduling patterns to optimize recommendations
    Learns user preferences and meeting type patterns
    """
    
    def __init__(self):
        super().__init__(agent_type="behavior", name="Behavior Agent")
    
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Analyze behavior patterns and score time windows
        
        Context expected:
            - attendee_ids: List of user IDs
            - meeting_type: Type of meeting
            - available_windows: Windows from calendar agent
            - lookback_days: Days of history to analyze (default 90)
        """
        self.update_status(AgentStatus.ANALYZING, "Analyzing scheduling patterns...")
        
        try:
            attendee_ids = context.get("attendee_ids", [])
            meeting_type = context.get("meeting_type", "team_sync")
            windows = context.get("available_windows", [])
            lookback_days = context.get("lookback_days", 90)
            
            # Fetch historical data
            historical_data = await self._fetch_historical_data(
                attendee_ids,
                lookback_days
            )
            
            # Learn preferences
            preferences = self._learn_preferences(historical_data, attendee_ids)
            
            # Analyze meeting type patterns
            type_patterns = self._analyze_meeting_type_patterns(
                historical_data,
                meeting_type
            )
            
            # Score each window based on learned behavior
            scored_windows = self._score_windows(
                windows,
                preferences,
                type_patterns
            )
            
            self.update_status(AgentStatus.COMPLETE,
                             f"Analyzed {lookback_days} days of patterns")
            
            return self.create_result(
                data={
                    "scored_windows": scored_windows,
                    "preferences": preferences,
                    "patterns": type_patterns
                },
                message=f"Analyzed {lookback_days} days of scheduling patterns",
                confidence=0.88,
                metadata={
                    "attendees_analyzed": len(attendee_ids),
                    "historical_meetings": len(historical_data)
                }
            )
            
        except Exception as e:
            self.update_status(AgentStatus.ERROR, f"Error: {str(e)}")
            return self.create_result(
                data={},
                message=f"Behavior analysis failed: {str(e)}",
                errors=[str(e)]
            )
    
    async def _fetch_historical_data(
        self,
        attendee_ids: List[str],
        lookback_days: int
    ) -> List[Dict[str, Any]]:
        """Fetch historical meeting data for pattern analysis"""
        # TODO: Query database for past meetings
        # Include: meeting times, types, attendees, acceptance rates, reschedules
        return []
    
    def _learn_preferences(
        self,
        historical_data: List[Dict[str, Any]],
        attendee_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Learn scheduling preferences from historical data
        
        Learns:
        - Preferred time of day
        - Preferred days of week
        - Meeting duration preferences
        - Buffer time patterns
        - Acceptance/decline patterns
        """
        preferences = {}
        
        for attendee_id in attendee_ids:
            attendee_meetings = [
                m for m in historical_data
                if attendee_id in m.get("attendee_ids", [])
            ]
            
            preferences[attendee_id] = {
                "preferred_time_of_day": self._calculate_preferred_time(attendee_meetings),
                "preferred_days": self._calculate_preferred_days(attendee_meetings),
                "avg_meeting_duration": self._calculate_avg_duration(attendee_meetings),
                "acceptance_rate": self._calculate_acceptance_rate(attendee_meetings),
                "prefers_buffer": self._detect_buffer_preference(attendee_meetings),
                "avoid_back_to_back": self._detect_back_to_back_avoidance(attendee_meetings)
            }
        
        return preferences
    
    def _analyze_meeting_type_patterns(
        self,
        historical_data: List[Dict[str, Any]],
        meeting_type: str
    ) -> Dict[str, Any]:
        """Analyze patterns specific to meeting type"""
        type_meetings = [
            m for m in historical_data
            if m.get("type") == meeting_type
        ]
        
        if not type_meetings:
            return {"has_data": False}
        
        return {
            "has_data": True,
            "typical_duration": self._calculate_avg_duration(type_meetings),
            "typical_time_of_day": self._calculate_preferred_time(type_meetings),
            "typical_attendee_count": sum(len(m.get("attendee_ids", [])) for m in type_meetings) / len(type_meetings),
            "success_rate": self._calculate_success_rate(type_meetings)
        }
    
    def _score_windows(
        self,
        windows: List[Dict[str, Any]],
        preferences: Dict[str, Any],
        patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Score each window based on learned behavior
        Higher score = better fit with historical patterns
        """
        for window in windows:
            window["behavior_score"] = self._calculate_behavior_score(
                window,
                preferences,
                patterns
            )
            window["behavior_insights"] = self._generate_insights(
                window,
                preferences,
                patterns
            )
        
        return sorted(windows, key=lambda w: w["behavior_score"], reverse=True)
    
    def _calculate_behavior_score(
        self,
        window: Dict[str, Any],
        preferences: Dict[str, Any],
        patterns: Dict[str, Any]
    ) -> float:
        """Calculate behavior-based score for a window (0-100)"""
        score = 50.0  # Base score
        
        window_time = window["start_time"]
        
        # TODO: Implement sophisticated scoring algorithm
        # Factors:
        # - Time of day alignment with preferences
        # - Day of week preferences
        # - Meeting type patterns
        # - Historical acceptance rates
        # - Buffer time preferences
        
        # Mock scoring
        hour = window_time.hour
        if 9 <= hour <= 11:  # Morning preference
            score += 20
        elif 14 <= hour <= 16:  # Afternoon preference
            score += 15
        
        return min(100.0, max(0.0, score))
    
    def _generate_insights(
        self,
        window: Dict[str, Any],
        preferences: Dict[str, Any],
        patterns: Dict[str, Any]
    ) -> List[str]:
        """Generate human-readable insights about the window"""
        insights = []
        
        # TODO: Generate contextual insights based on patterns
        # Example: "Sarah historically accepts morning meetings 85% of the time"
        
        return insights
    
    # Helper methods for pattern analysis
    def _calculate_preferred_time(self, meetings: List[Dict[str, Any]]) -> str:
        """Calculate preferred time of day (morning/afternoon/evening)"""
        # TODO: Implement time preference calculation
        return "morning"
    
    def _calculate_preferred_days(self, meetings: List[Dict[str, Any]]) -> List[str]:
        """Calculate preferred days of week"""
        # TODO: Implement day preference calculation
        return ["Monday", "Tuesday", "Wednesday", "Thursday"]
    
    def _calculate_avg_duration(self, meetings: List[Dict[str, Any]]) -> int:
        """Calculate average meeting duration"""
        if not meetings:
            return 60
        return sum(m.get("duration", 60) for m in meetings) // len(meetings)
    
    def _calculate_acceptance_rate(self, meetings: List[Dict[str, Any]]) -> float:
        """Calculate meeting acceptance rate"""
        # TODO: Calculate from response status
        return 0.85
    
    def _detect_buffer_preference(self, meetings: List[Dict[str, Any]]) -> bool:
        """Detect if user prefers buffer time between meetings"""
        # TODO: Analyze gaps between meetings
        return True
    
    def _detect_back_to_back_avoidance(self, meetings: List[Dict[str, Any]]) -> bool:
        """Detect if user avoids back-to-back meetings"""
        # TODO: Analyze meeting spacing
        return True
    
    def _calculate_success_rate(self, meetings: List[Dict[str, Any]]) -> float:
        """Calculate success rate (not rescheduled/cancelled)"""
        # TODO: Calculate from meeting status
        return 0.92
    
    def get_capabilities(self) -> List[str]:
        return [
            "Pattern recognition",
            "Preference learning",
            "Time-of-day optimization",
            "Meeting type analysis",
            "Acceptance rate prediction"
        ]
    
    def get_description(self) -> str:
        return "Learns scheduling patterns and preferences from historical data to optimize recommendations."
