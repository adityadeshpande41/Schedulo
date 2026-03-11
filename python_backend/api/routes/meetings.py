"""
Meetings API endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime, timedelta

from api.models.responses import MeetingResponse, DecisionExplanationResponse
from services.meeting_service import MeetingService

router = APIRouter()
meeting_service = MeetingService()


@router.get("/upcoming", response_model=List[MeetingResponse])
async def get_upcoming_meetings(
    user_id: str,
    days: int = 7
):
    """
    Get upcoming meetings for a user
    
    Parameters:
    - user_id: User ID
    - days: Number of days to look ahead (default 7)
    """
    try:
        meetings = await meeting_service.get_upcoming_meetings(user_id, days)
        return meetings
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(meeting_id: str):
    """Get meeting details by ID"""
    try:
        meeting = await meeting_service.get_meeting_by_id(meeting_id)
        
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        return meeting
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{meeting_id}/decision", response_model=DecisionExplanationResponse)
async def get_meeting_decision(meeting_id: str):
    """
    Get AI decision explanation for a meeting
    
    Explains why specific time slots were recommended
    """
    try:
        decision = await meeting_service.get_decision_explanation(meeting_id)
        
        if not decision:
            raise HTTPException(
                status_code=404,
                detail="Decision explanation not found"
            )
        
        return decision
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{meeting_id}/status")
async def update_meeting_status(
    meeting_id: str,
    status: str
):
    """
    Update meeting status
    
    Status values: confirmed, pending, rescheduled, cancelled
    """
    try:
        valid_statuses = ["confirmed", "pending", "rescheduled", "cancelled"]
        
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        updated = await meeting_service.update_meeting_status(meeting_id, status)
        
        return {
            "meeting_id": meeting_id,
            "status": status,
            "updated": updated
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{meeting_id}")
async def cancel_meeting(meeting_id: str):
    """Cancel a meeting"""
    try:
        cancelled = await meeting_service.cancel_meeting(meeting_id)
        
        if not cancelled:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        return {
            "meeting_id": meeting_id,
            "status": "cancelled",
            "message": "Meeting cancelled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
