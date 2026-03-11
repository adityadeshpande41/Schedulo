"""
ML Behavior Learning Model
Learns user scheduling preferences from historical data
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np
from collections import defaultdict


class BehaviorLearningModel:
    """
    Machine Learning model for learning user scheduling behavior
    
    Learns:
    - Time of day preferences
    - Day of week preferences
    - Meeting type preferences
    - Reschedule patterns
    - Acceptance/decline patterns
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        
        # Learned patterns (will be populated from historical data)
        self.time_preferences = {}  # hour -> acceptance_rate
        self.day_preferences = {}   # day_of_week -> acceptance_rate
        self.type_preferences = {}  # meeting_type -> acceptance_rate
        self.reschedule_patterns = {}  # meeting_type -> reschedule_rate
        
        # Model state
        self.is_trained = False
        self.training_samples = 0
        
        # TODO: In production, use scikit-learn models
        # self.acceptance_model = RandomForestClassifier()
        # self.reschedule_model = XGBClassifier()
    
    def train(self, historical_data: List[Dict[str, Any]]):
        """
        Train model on historical meeting data
        
        Data format:
        {
            "meeting_id": "m1",
            "start_time": datetime,
            "duration": 60,
            "type": "team_sync",
            "priority": "medium",
            "was_accepted": True,
            "was_rescheduled": False,
            "response_time": 120  # seconds
        }
        """
        if not historical_data:
            return
        
        self.training_samples = len(historical_data)
        
        # Learn time of day preferences
        time_stats = defaultdict(lambda: {"accepted": 0, "total": 0})
        for meeting in historical_data:
            hour = meeting["start_time"].hour
            time_stats[hour]["total"] += 1
            if meeting["was_accepted"]:
                time_stats[hour]["accepted"] += 1
        
        self.time_preferences = {
            hour: stats["accepted"] / stats["total"]
            for hour, stats in time_stats.items()
        }
        
        # Learn day of week preferences
        day_stats = defaultdict(lambda: {"accepted": 0, "total": 0})
        for meeting in historical_data:
            day = meeting["start_time"].weekday()
            day_stats[day]["total"] += 1
            if meeting["was_accepted"]:
                day_stats[day]["accepted"] += 1
        
        self.day_preferences = {
            day: stats["accepted"] / stats["total"]
            for day, stats in day_stats.items()
        }
        
        # Learn meeting type preferences
        type_stats = defaultdict(lambda: {"accepted": 0, "total": 0})
        for meeting in historical_data:
            mtype = meeting["type"]
            type_stats[mtype]["total"] += 1
            if meeting["was_accepted"]:
                type_stats[mtype]["accepted"] += 1
        
        self.type_preferences = {
            mtype: stats["accepted"] / stats["total"]
            for mtype, stats in type_stats.items()
        }
        
        # Learn reschedule patterns
        reschedule_stats = defaultdict(lambda: {"rescheduled": 0, "total": 0})
        for meeting in historical_data:
            mtype = meeting["type"]
            reschedule_stats[mtype]["total"] += 1
            if meeting.get("was_rescheduled"):
                reschedule_stats[mtype]["rescheduled"] += 1
        
        self.reschedule_patterns = {
            mtype: stats["rescheduled"] / stats["total"]
            for mtype, stats in reschedule_stats.items()
        }
        
        self.is_trained = True
    
    def predict_acceptance(
        self,
        time_window: Dict[str, datetime],
        meeting_context: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> float:
        """
        Predict probability user will accept this meeting slot
        
        Returns: float between 0.0 and 1.0
        """
        if not self.is_trained and historical_data:
            self.train(historical_data)
        
        # Base probability
        prob = 0.5
        
        # Time of day factor
        hour = time_window["start"].hour
        if hour in self.time_preferences:
            prob = prob * 0.3 + self.time_preferences[hour] * 0.7
        
        # Day of week factor
        day = time_window["start"].weekday()
        if day in self.day_preferences:
            prob = prob * 0.5 + self.day_preferences[day] * 0.5
        
        # Meeting type factor
        mtype = meeting_context.get("type")
        if mtype in self.type_preferences:
            prob = prob * 0.6 + self.type_preferences[mtype] * 0.4
        
        # Priority boost
        if meeting_context.get("priority") == "high":
            prob = min(1.0, prob * 1.2)
        
        return prob
    
    def predict_reschedule_probability(
        self,
        time_window: Dict[str, datetime],
        meeting_context: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> float:
        """
        Predict probability user will reschedule existing meeting for this one
        """
        if not self.is_trained and historical_data:
            self.train(historical_data)
        
        mtype = meeting_context.get("type")
        base_rate = self.reschedule_patterns.get(mtype, 0.3)
        
        # High priority increases reschedule probability
        if meeting_context.get("priority") == "high":
            return min(1.0, base_rate * 1.5)
        
        # Client calls more likely to cause reschedules
        if mtype == "client_call":
            return min(1.0, base_rate * 1.3)
        
        return base_rate
    
    def prefers_time_of_day(self, hour: int) -> bool:
        """Check if user prefers this time of day"""
        if hour not in self.time_preferences:
            return False
        return self.time_preferences[hour] > 0.7
    
    def prefers_day_of_week(self, day: int) -> bool:
        """Check if user prefers this day of week"""
        if day not in self.day_preferences:
            return False
        return self.day_preferences[day] > 0.7
    
    def prefers_meeting_type(self, meeting_type: str, hour: int) -> bool:
        """Check if user prefers this meeting type at this time"""
        if meeting_type not in self.type_preferences:
            return False
        return self.type_preferences[meeting_type] > 0.7
    
    def get_reschedule_rate(self, meeting_type: str) -> float:
        """Get historical reschedule rate for meeting type"""
        return self.reschedule_patterns.get(meeting_type, 0.3)
    
    def get_learned_patterns(self) -> Dict[str, Any]:
        """Get all learned patterns for AI assistant"""
        return {
            "time_preferences": self.time_preferences,
            "day_preferences": self.day_preferences,
            "type_preferences": self.type_preferences,
            "reschedule_patterns": self.reschedule_patterns,
            "training_samples": self.training_samples
        }
    
    def update_from_feedback(self, feedback: Dict[str, Any]):
        """
        Update model based on user feedback
        
        Feedback format:
        {
            "proposed_slot": {...},
            "user_accepted": True/False,
            "user_choice": {...},
            "reason": "..."
        }
        """
        # Incremental learning
        slot = feedback.get("proposed_slot", {})
        accepted = feedback.get("user_accepted", False)
        
        if "start_time" in slot:
            hour = slot["start_time"].hour
            day = slot["start_time"].weekday()
            
            # Update time preferences
            if hour in self.time_preferences:
                # Exponential moving average
                alpha = 0.1
                self.time_preferences[hour] = (
                    alpha * (1.0 if accepted else 0.0) +
                    (1 - alpha) * self.time_preferences[hour]
                )
            
            # Update day preferences
            if day in self.day_preferences:
                alpha = 0.1
                self.day_preferences[day] = (
                    alpha * (1.0 if accepted else 0.0) +
                    (1 - alpha) * self.day_preferences[day]
                )
        
        self.training_samples += 1
