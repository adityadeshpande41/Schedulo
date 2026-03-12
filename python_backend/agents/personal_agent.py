"""
Personal Agent - Privacy-Preserving Individual Scheduling Agent
Each user has their own agent that learns their preferences
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from .base_agent import BaseAgent, AgentStatus, AgentResult
from .ml_behavior_model import BehaviorLearningModel
from .openai_integration import OpenAIAssistant


class AvailabilitySignal:
    """Privacy-preserving availability signal"""
    
    def __init__(
        self,
        time_slot: Dict[str, datetime],
        status: str,  # "available", "busy", "flexible", "prefer_not"
        confidence: float,
        flexibility_score: float = 0.0,
        priority_override: Optional[str] = None
    ):
        self.time_slot = time_slot
        self.status = status
        self.confidence = confidence
        self.flexibility_score = flexibility_score
        self.priority_override = priority_override
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (for sharing with coordination layer)"""
        return {
            "start_time": self.time_slot["start"].isoformat(),
            "end_time": self.time_slot["end"].isoformat(),
            "status": self.status,
            "confidence": self.confidence,
            "flexibility": self.flexibility_score,
            "priority_override": self.priority_override
        }


class PersonalAgent(BaseAgent):
    """
    Privacy-preserving personal scheduling agent
    
    Key Features:
    - Only accesses owner's private calendar
    - Learns owner's preferences via ML
    - Shares minimal information (availability signals only)
    - Escalates to human when uncertain
    """
    
    def __init__(self, user_id: str):
        super().__init__(agent_type="personal", name=f"Personal Agent ({user_id})")
        self.user_id = user_id
        
        # ML model for behavior learning
        self.behavior_model = BehaviorLearningModel(user_id)
        
        # OpenAI assistant for natural language understanding
        self.ai_assistant = OpenAIAssistant(user_id)
        
        # Privacy: This agent ONLY accesses this user's data
        self.private_calendar = None  # Will be loaded from DB
        self.private_preferences = None
        self.historical_data = None
    
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Main execution: Analyze request and provide availability signals
        
        Context:
            - request_type: "availability_check" | "preference_query" | "conflict_resolution"
            - time_windows: List of potential time slots
            - meeting_context: Meeting details (type, priority, attendees)
        """
        self.update_status(AgentStatus.ANALYZING, f"Analyzing for {self.user_id}...")
        
        try:
            request_type = context.get("request_type")
            
            if request_type == "availability_check":
                return await self._check_availability(context)
            
            elif request_type == "preference_query":
                return await self._query_preferences(context)
            
            elif request_type == "conflict_resolution":
                return await self._resolve_conflict(context)
            
            elif request_type == "learn_from_feedback":
                return await self._learn_from_feedback(context)
            
            else:
                raise ValueError(f"Unknown request type: {request_type}")
                
        except Exception as e:
            self.update_status(AgentStatus.ERROR, f"Error: {str(e)}")
            return self.create_result(
                data={},
                message=f"Personal agent failed: {str(e)}",
                errors=[str(e)]
            )
    
    async def _check_availability(self, context: Dict[str, Any]) -> AgentResult:
        """
        Check availability for proposed time windows
        Returns privacy-preserving availability signals
        """
        time_windows = context.get("time_windows", [])
        meeting_context = context.get("meeting_context", {})
        
        # Load private data (only this user's data)
        await self._load_private_data()
        
        availability_signals = []
        
        for window in time_windows:
            # 1. Check calendar (private)
            is_busy = self._check_calendar_busy(window)
            
            # 2. ML prediction: Will user accept this slot?
            # This is the key ML integration!
            acceptance_prob = self.behavior_model.predict_acceptance(
                window,
                meeting_context,
                self.historical_data
            )
            
            # 3. Check learned preferences
            preference_score = self._evaluate_preferences(window, meeting_context)
            
            # 4. Determine status
            if is_busy:
                # Check if user would reschedule
                reschedule_prob = self.behavior_model.predict_reschedule_probability(
                    window,
                    meeting_context,
                    self.historical_data
                )
                
                if reschedule_prob > 0.7 and meeting_context.get("priority") == "high":
                    status = "flexible"
                    confidence = reschedule_prob
                else:
                    status = "busy"
                    confidence = 1.0
            else:
                # Use ML prediction to determine confidence
                # This makes each slot have different scores based on learned patterns!
                if acceptance_prob > 0.8:
                    status = "available"
                    confidence = acceptance_prob
                elif acceptance_prob > 0.5:
                    status = "flexible"
                    confidence = acceptance_prob
                else:
                    status = "prefer_not"
                    confidence = 1.0 - acceptance_prob
            
            # 5. Calculate flexibility score
            flexibility = self._calculate_flexibility(window, meeting_context)
            
            # 6. Create privacy-preserving signal
            signal = AvailabilitySignal(
                time_slot=window,
                status=status,
                confidence=confidence,  # Now varies based on ML predictions!
                flexibility_score=flexibility,
                priority_override=self._check_priority_override(window, meeting_context)
            )
            
            availability_signals.append(signal)
        
        self.update_status(AgentStatus.COMPLETE, f"Analyzed {len(time_windows)} windows")
        
        return self.create_result(
            data={
                "user_id": self.user_id,
                "availability_signals": [s.to_dict() for s in availability_signals],
                "overall_confidence": sum(s.confidence for s in availability_signals) / len(availability_signals) if availability_signals else 0,
                "ml_model_trained": self.behavior_model.is_trained,
                "training_samples": self.behavior_model.training_samples
            },
            message=f"Availability analysis complete for {self.user_id} (ML: {self.behavior_model.is_trained})",
            confidence=sum(s.confidence for s in availability_signals) / len(availability_signals) if availability_signals else 0
        )
    
    async def _query_preferences(self, context: Dict[str, Any]) -> AgentResult:
        """
        Query learned preferences using OpenAI
        """
        query = context.get("query", "")
        
        # Use OpenAI to understand and answer preference queries
        response = await self.ai_assistant.query_preferences(
            query=query,
            learned_patterns=self.behavior_model.get_learned_patterns(),
            user_preferences=self.private_preferences
        )
        
        return self.create_result(
            data={"response": response},
            message="Preference query answered",
            confidence=0.9
        )
    
    async def _resolve_conflict(self, context: Dict[str, Any]) -> AgentResult:
        """
        Resolve scheduling conflict using AI reasoning
        """
        conflict = context.get("conflict", {})
        
        # Use OpenAI to reason about conflict resolution
        resolution = await self.ai_assistant.resolve_conflict(
            conflict=conflict,
            user_patterns=self.behavior_model.get_learned_patterns(),
            historical_decisions=self.historical_data
        )
        
        # Check if escalation is needed
        if resolution["confidence"] < 0.6:
            resolution["escalate_to_human"] = True
            resolution["escalation_reason"] = "Low confidence in conflict resolution"
        
        return self.create_result(
            data=resolution,
            message="Conflict resolution proposed",
            confidence=resolution["confidence"]
        )
    
    async def _learn_from_feedback(self, context: Dict[str, Any]) -> AgentResult:
        """
        Learn from user feedback to improve predictions
        """
        feedback = context.get("feedback", {})
        
        # Update ML model with new data
        self.behavior_model.update_from_feedback(feedback)
        
        # Update OpenAI context
        await self.ai_assistant.update_context(feedback)
        
        return self.create_result(
            data={"updated": True},
            message="Learned from feedback",
            confidence=1.0
        )
    
    async def _load_private_data(self):
        """Load user's private data (calendar, preferences, history)"""
        from services.user_data_service import UserDataService
        from datetime import datetime, timedelta
        
        # Initialize data service
        data_service = UserDataService()
        
        try:
            # Load preferences
            self.private_preferences = data_service.get_user_preferences(self.user_id)
            
            # Load calendar (next 30 days)
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=30)
            self.private_calendar = data_service.get_user_calendar(
                self.user_id,
                start_date,
                end_date
            )
            
            # Load historical data for ML training
            self.historical_data = data_service.get_historical_meetings(
                self.user_id,
                lookback_days=90
            )
            
            # Train ML model ONLY if not already trained
            # This prevents retraining on every request (huge performance boost!)
            if self.historical_data and not self.behavior_model.is_trained:
                print(f"🤖 Training ML model for {self.user_id} with {len(self.historical_data)} samples...")
                self.behavior_model.train(self.historical_data)
                print(f"✅ ML model trained (accuracy: {self.behavior_model.model_accuracy:.2%})")
            
        finally:
            data_service.close()
    
    def _check_calendar_busy(self, window: Dict[str, datetime]) -> bool:
        """Check if time window conflicts with calendar"""
        if not self.private_calendar:
            return False
        
        from datetime import timezone
        
        start = window["start"]
        end = window["end"]
        
        # Ensure start and end are timezone-aware
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        
        # Check for conflicts
        for event in self.private_calendar:
            event_start = event["start_time"]
            event_end = event["end_time"]
            
            # Ensure event times are timezone-aware
            if event_start.tzinfo is None:
                event_start = event_start.replace(tzinfo=timezone.utc)
            if event_end.tzinfo is None:
                event_end = event_end.replace(tzinfo=timezone.utc)
            
            # Skip if not marked as busy
            if not event.get("is_busy", True):
                continue
            
            # Check for overlap
            if (event_start < end and event_end > start):
                return True
        
        return False
    
    def _evaluate_preferences(
        self,
        window: Dict[str, datetime],
        meeting_context: Dict[str, Any]
    ) -> float:
        """Evaluate how well window matches learned preferences"""
        score = 0.5  # Base score
        
        # Time of day preference
        hour = window["start"].hour
        if self.behavior_model.prefers_time_of_day(hour):
            score += 0.2
        
        # Day of week preference
        day = window["start"].weekday()
        if self.behavior_model.prefers_day_of_week(day):
            score += 0.15
        
        # Meeting type preference
        meeting_type = meeting_context.get("type")
        if self.behavior_model.prefers_meeting_type(meeting_type, hour):
            score += 0.15
        
        return min(1.0, score)
    
    def _calculate_flexibility(
        self,
        window: Dict[str, datetime],
        meeting_context: Dict[str, Any]
    ) -> float:
        """
        Calculate how flexible user is for this slot
        0.0 = inflexible, 1.0 = very flexible
        """
        flexibility = 0.5
        
        # High priority meetings reduce flexibility
        if meeting_context.get("priority") == "high":
            flexibility += 0.3
        
        # Internal meetings are more flexible
        if meeting_context.get("type") in ["one_on_one", "team_sync"]:
            flexibility += 0.2
        
        # Historical reschedule rate
        reschedule_rate = self.behavior_model.get_reschedule_rate(meeting_context.get("type"))
        flexibility += reschedule_rate * 0.3
        
        return min(1.0, flexibility)
    
    def _check_priority_override(
        self,
        window: Dict[str, datetime],
        meeting_context: Dict[str, Any]
    ) -> Optional[str]:
        """
        Check if this meeting type should override existing meetings
        """
        meeting_type = meeting_context.get("type")
        priority = meeting_context.get("priority")
        
        # Client calls can override internal meetings
        if meeting_type == "client_call" and priority == "high":
            return "can_reschedule_internal"
        
        # Urgent meetings can override low-priority meetings
        if priority == "high":
            return "can_reschedule_low_priority"
        
        return None
    
    def get_capabilities(self) -> List[str]:
        return [
            "Privacy-preserving availability checking",
            "ML-based behavior prediction",
            "Preference learning",
            "Conflict resolution",
            "Smart escalation",
            "Continuous learning"
        ]
    
    def get_description(self) -> str:
        return f"Personal scheduling agent for {self.user_id}. Learns preferences, protects privacy, and makes intelligent scheduling decisions."
