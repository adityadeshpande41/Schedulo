"""
Schedule Service
Business logic for scheduling operations
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid

from api.models.requests import ScheduleRequest
from api.models.responses import (
    ScheduleResponse,
    TimeSlotResponse,
    ConflictResponse
)
from agents import AgentResult


class ScheduleService:
    """Service for handling scheduling logic"""
    
    def format_langgraph_response(
        self,
        final_state: Dict[str, Any],
        request: ScheduleRequest
    ) -> ScheduleResponse:
        """Format LangGraph final state into API response"""
        
        slots = self.format_time_slots(
            final_state.get("ranked_recommendations", [])
        )
        
        return ScheduleResponse(
            request_id=str(uuid.uuid4()),
            status="completed",
            recommended_slots=slots,
            approval_needed=final_state.get("escalation_needed", False),
            confidence=final_state.get("confidence", 0.0),
            message=final_state.get("messages", [])[-1].content if final_state.get("messages") else "Scheduling complete"
        )
    
    def format_schedule_response(
        self,
        agent_result: AgentResult,
        request: ScheduleRequest
    ) -> ScheduleResponse:
        """Format agent result into API response (legacy)"""
        
        slots = self.format_time_slots(
            agent_result.data["recommended_slots"]
        )
        
        return ScheduleResponse(
            request_id=str(uuid.uuid4()),
            status="completed",
            recommended_slots=slots,
            approval_needed=agent_result.data.get("approval_needed", False),
            confidence=agent_result.confidence,
            message=agent_result.message
        )
    
    def format_time_slots(
        self,
        slots: List[Dict[str, Any]]
    ) -> List[TimeSlotResponse]:
        """Format time slots for API response"""
        
        formatted_slots = []
        
        for slot in slots:
            formatted_slots.append(TimeSlotResponse(
                id=slot.get("id", str(uuid.uuid4())),
                start_time=slot["start_time"],
                end_time=slot["end_time"],
                score=slot.get("final_score", 0),
                confidence=slot.get("confidence", 0),
                rank=slot.get("rank", 0),
                reasoning=slot.get("reasoning", ""),
                conflicts=self._format_conflicts(slot.get("conflicts", [])),
                attendee_availability=slot.get("attendee_availability", []),
                requires_approval=slot.get("requires_approval", False),
                recommended=slot.get("recommended", False)
            ))
        
        return formatted_slots
    
    def _format_conflicts(
        self,
        conflicts: List[Dict[str, Any]]
    ) -> List[ConflictResponse]:
        """Format conflicts for API response"""
        
        return [
            ConflictResponse(
                type=c.get("type", "soft"),
                description=c.get("description", ""),
                attendee_id=c.get("attendee_id"),
                resolution=c.get("resolution")
            )
            for c in conflicts
        ]
