"""
Federation API Routes
Exposes endpoints for external Schedulo instances to query availability
"""

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
from datetime import datetime

router = APIRouter(prefix="/federation", tags=["federation"])


class AvailabilityRequest(BaseModel):
    """Request from external Schedulo instance"""
    user_email: EmailStr
    time_windows: List[Dict[str, Any]]
    meeting_context: Optional[Dict[str, Any]] = None
    protocol_version: str = "1.0"


class AvailabilityResponse(BaseModel):
    """Response with availability signals"""
    status: str
    signals: List[Dict[str, Any]]
    protocol_version: str = "1.0"


@router.post("/availability", response_model=AvailabilityResponse)
async def get_external_availability(
    request: AvailabilityRequest,
    x_schedulo_federation: Optional[str] = Header(None)
):
    """
    External endpoint for other Schedulo instances to query availability
    
    This is called by external companies when scheduling with your users.
    Returns only availability signals, never calendar details.
    """
    # Verify federation protocol version
    if x_schedulo_federation != "1.0":
        raise HTTPException(
            status_code=400,
            detail="Unsupported federation protocol version"
        )
    
    # TODO: Authenticate external request (API key, OAuth, etc.)
    
    # Find user by email
    user_email = request.user_email
    
    # TODO: Look up user in database
    # For demo, simulate user lookup
    if not user_email.endswith("@acme.com"):
        raise HTTPException(
            status_code=404,
            detail="User not found in this organization"
        )
    
    # Run personal agent for this user (privacy-isolated)
    # TODO: Import and use actual PersonalAgent
    from ...agents.personal_agent import PersonalAgent
    
    agent = PersonalAgent(user_id="u1")  # Map email to user_id
    
    # Check availability for each time window
    signals = []
    for window in request.time_windows:
        # Agent checks private calendar and returns only signal
        result = await agent.execute({
            "time_windows": [window],
            "meeting_context": request.meeting_context
        })
        
        # Extract signal (no calendar details!)
        if result.success:
            agent_signals = result.data.get("availability_signals", [])
            if agent_signals:
                signal = agent_signals[0]
                signals.append({
                    "start_time": window["start_time"],
                    "end_time": window["end_time"],
                    "status": signal.get("status", "unknown"),
                    "confidence": signal.get("confidence", 0.0),
                    "flexibility": signal.get("flexibility", 0.0)
                })
        else:
            # Fallback
            signals.append({
                "start_time": window["start_time"],
                "end_time": window["end_time"],
                "status": "unknown",
                "confidence": 0.0,
                "requires_manual_check": True
            })
    
    return AvailabilityResponse(
        status="success",
        signals=signals,
        protocol_version="1.0"
    )


@router.post("/invite")
async def receive_external_invitation(
    meeting: Dict[str, Any],
    x_schedulo_federation: Optional[str] = Header(None)
):
    """
    Receive meeting invitation from external Schedulo instance
    """
    # TODO: Create meeting in local database
    # TODO: Send notification to user
    
    return {
        "status": "accepted",
        "message": "Meeting invitation received"
    }
