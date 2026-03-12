"""
ML Behavior Learning Model
Learns user scheduling preferences from historical data using scikit-learn
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np
from collections import defaultdict
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import pickle
import os


class BehaviorLearningModel:
    """
    Machine Learning model for learning user scheduling behavior
    
    Uses Random Forest for acceptance prediction and Gradient Boosting for reschedule prediction
    
    Learns:
    - Time of day preferences
    - Day of week preferences  
    - Meeting type preferences
    - Reschedule patterns
    - Feature interactions (e.g., "prefers 2pm on Tuesdays")
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        
        # Statistical patterns (fast lookup)
        self.time_preferences = {}  # hour -> acceptance_rate
        self.day_preferences = {}   # day_of_week -> acceptance_rate
        self.type_preferences = {}  # meeting_type -> acceptance_rate
        self.reschedule_patterns = {}  # meeting_type -> reschedule_rate
        
        # ML Models (for complex patterns)
        self.acceptance_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42
        )
        self.reschedule_model = GradientBoostingClassifier(
            n_estimators=50,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        self.scaler = StandardScaler()
        
        # Model state
        self.is_trained = False
        self.training_samples = 0
        self.model_accuracy = 0.0
    
    def _extract_features(
        self,
        time_window: Dict[str, datetime],
        meeting_context: Dict[str, Any]
    ) -> np.ndarray:
        """
        Extract features for ML model
        
        Features:
        - Hour of day (0-23)
        - Day of week (0-6)
        - Is morning (0/1)
        - Is afternoon (0/1)
        - Is end of day (0/1)
        - Duration (minutes)
        - Priority (0=low, 1=medium, 2=high)
        - Meeting type (one-hot encoded)
        - Day of month
        - Week of year
        """
        start_time = time_window["start"]
        
        features = [
            start_time.hour,
            start_time.weekday(),
            1 if 6 <= start_time.hour < 12 else 0,  # morning
            1 if 12 <= start_time.hour < 17 else 0,  # afternoon
            1 if 17 <= start_time.hour < 20 else 0,  # end of day
            meeting_context.get("duration", 30),
            {"low": 0, "medium": 1, "high": 2}.get(meeting_context.get("priority", "medium"), 1),
            start_time.day,
            start_time.isocalendar()[1],  # week of year
        ]
        
        # One-hot encode meeting type
        meeting_types = ["team_sync", "one_on_one", "client_call", "standup", "workshop", "interview"]
        mtype = meeting_context.get("type", "team_sync")
        for mt in meeting_types:
            features.append(1 if mtype == mt else 0)
        
        return np.array(features).reshape(1, -1)
    
    def train(self, historical_data: List[Dict[str, Any]]):
        """
        Train both statistical patterns and ML models
        
        Data format:
        {
            "meeting_id": "m1",
            "start_time": datetime,
            "duration": 60,
            "type": "team_sync",
            "priority": "medium",
            "was_accepted": True,
            "was_rescheduled": False,
            "response_time": 120
        }
        """
        if not historical_data or len(historical_data) < 10:
            # Need at least 10 samples for ML
            return
        
        self.training_samples = len(historical_data)
        
        # Train statistical patterns (fast, interpretable)
        self._train_statistical_patterns(historical_data)
        
        # Train ML models (accurate, captures interactions)
        self._train_ml_models(historical_data)
        
        self.is_trained = True
    
    def _train_statistical_patterns(self, historical_data: List[Dict[str, Any]]):
        """Train simple statistical patterns"""
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
    
    def _train_ml_models(self, historical_data: List[Dict[str, Any]]):
        """Train ML models for complex pattern recognition"""
        # Prepare training data
        X = []
        y_acceptance = []
        y_reschedule = []
        
        for meeting in historical_data:
            features = self._extract_features(
                {"start": meeting["start_time"]},
                {
                    "duration": meeting.get("duration", 30),
                    "type": meeting.get("type", "team_sync"),
                    "priority": meeting.get("priority", "medium")
                }
            )
            X.append(features[0])
            y_acceptance.append(1 if meeting["was_accepted"] else 0)
            y_reschedule.append(1 if meeting.get("was_rescheduled", False) else 0)
        
        X = np.array(X)
        y_acceptance = np.array(y_acceptance)
        y_reschedule = np.array(y_reschedule)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train acceptance model
        self.acceptance_model.fit(X_scaled, y_acceptance)
        
        # Train reschedule model (if we have reschedule data)
        if sum(y_reschedule) > 0:
            self.reschedule_model.fit(X_scaled, y_reschedule)
        
        # Calculate accuracy
        self.model_accuracy = self.acceptance_model.score(X_scaled, y_acceptance)
    
    def predict_acceptance(
        self,
        time_window: Dict[str, datetime],
        meeting_context: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> float:
        """
        Predict probability user will accept this meeting slot
        
        Uses ML model if trained, falls back to statistical patterns
        
        Returns: float between 0.0 and 1.0
        """
        if not self.is_trained and historical_data:
            self.train(historical_data)
        
        # Use ML model if trained and accurate
        if self.is_trained and self.training_samples >= 20:
            try:
                features = self._extract_features(time_window, meeting_context)
                features_scaled = self.scaler.transform(features)
                prob = self.acceptance_model.predict_proba(features_scaled)[0][1]
                return float(prob)
            except Exception as e:
                print(f"ML prediction failed, using statistical fallback: {e}")
        
        # Fallback to statistical patterns
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
        
        # Use ML model if trained
        if self.is_trained and self.training_samples >= 20:
            try:
                features = self._extract_features(time_window, meeting_context)
                features_scaled = self.scaler.transform(features)
                prob = self.reschedule_model.predict_proba(features_scaled)[0][1]
                return float(prob)
            except Exception:
                pass
        
        # Fallback to statistical patterns
        mtype = meeting_context.get("type")
        base_rate = self.reschedule_patterns.get(mtype, 0.3)
        
        if meeting_context.get("priority") == "high":
            return min(1.0, base_rate * 1.5)
        
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
