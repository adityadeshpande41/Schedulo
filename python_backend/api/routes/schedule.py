"""
Schedule API endpoints
Main scheduling request handling
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from datetime import datetime, timedelta
import uuid

from api.models.requests import ScheduleRequest
from api.models.responses import ScheduleResponse, TimeSlotResponse
from agents.langgraph_orchestrator import LangGraphOrchestrator
from services.schedule_service import ScheduleService

router = APIRouter()
schedule_service = ScheduleService()
orchestrator = LangGraphOrchestrator()


@router.post("/request", response_model=ScheduleResponse)
async def create_schedule_request(
    request: ScheduleRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a new scheduling request using LangGraph orchestration
    
    The LangGraph orchestrator coordinates all agents through a state-based workflow
    """
    try:
        # Build natural language request
        nl_request = f"Schedule {request.title or 'a meeting'}"
        if request.duration:
            nl_request += f" for {request.duration} minutes"
        if request.notes:
            nl_request += f". {request.notes}"
        
        # Execute LangGraph workflow
        final_state = await orchestrator.execute(
            request=nl_request,
            attendee_ids=request.attendee_ids,
            duration=request.duration or 60,
            meeting_context={
                "type": request.meeting_type or "team_sync",
                "priority": request.priority or "medium",
                "title": request.title,
                "notes": request.notes
            }
        )
        
        # Check if escalation is needed
        if final_state.get("escalation_needed"):
            return ScheduleResponse(
                request_id=str(uuid.uuid4()),
                status="escalated",
                recommended_slots=[],
                approval_needed=True,
                confidence=final_state.get("confidence", 0.0),
                message=f"Escalated: {final_state.get('escalation_reason', 'Manual review needed')}"
            )
        
        # Convert to response format
        response = schedule_service.format_langgraph_response(final_state, request)
        
        return response
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/slots/recommendations", response_model=List[TimeSlotResponse])
async def get_recommended_slots(
    attendee_ids: str,  # Comma-separated
    duration: int = 60,
    meeting_type: str = "team_sync",
    priority: str = "medium"
):
    """
    Get recommended time slots for a meeting using LangGraph
    
    Query parameters:
    - attendee_ids: Comma-separated user IDs
    - duration: Meeting duration in minutes
    - meeting_type: Type of meeting
    - priority: Meeting priority (high/medium/low)
    """
    try:
        attendee_list = [a.strip() for a in attendee_ids.split(",")]
        
        # Execute LangGraph workflow
        final_state = await orchestrator.execute(
            request=f"Find time slots for {meeting_type}",
            attendee_ids=attendee_list,
            duration=duration,
            meeting_context={
                "type": meeting_type,
                "priority": priority
            }
        )
        
        if final_state.get("escalation_needed"):
            raise HTTPException(
                status_code=400,
                detail=final_state.get("escalation_reason", "No suitable slots found")
            )
        
        # Format recommendations
        slots = schedule_service.format_time_slots(
            final_state.get("ranked_recommendations", [])
        )
        
        return slots
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/slots/{slot_id}/confirm")
async def confirm_time_slot(slot_id: str):
    """
    Confirm a selected time slot and create the meeting
    """
    try:
        # TODO: Create meeting in database
        # TODO: Send calendar invites
        # TODO: Update attendee calendars
        
        return {
            "status": "confirmed",
            "slot_id": slot_id,
            "message": "Meeting scheduled successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
