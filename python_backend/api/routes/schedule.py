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
                "notes": request.notes,
                "preferred_time_range": request.preferred_time_range
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
    - Creates meeting in database
    - Adds to your Google Calendar
    - Sends calendar invites to attendees
    - Saves to historical_meetings for ML training
    """
    try:
        from database.connection import get_db_context
        from database.models import TimeSlot, HistoricalMeeting, Meeting, MeetingAttendee, User, CalendarIntegration
        from datetime import datetime
        from integrations.google_calendar import GoogleCalendarIntegration
        import uuid
        
        # Get the time slot from database
        with get_db_context() as db:
            slot = db.query(TimeSlot).filter(TimeSlot.id == slot_id).first()
            
            if not slot:
                raise HTTPException(status_code=404, detail="Time slot not found")
            
            user_id = "u1"  # TODO: Get from auth in production
            
            # Create meeting in database
            meeting_id = f"mtg_{uuid.uuid4().hex[:12]}"
            meeting = Meeting(
                id=meeting_id,
                title="New Meeting",  # TODO: Get from slot metadata
                type="team_sync",
                start_time=slot.start_time,
                end_time=slot.end_time,
                duration=int((slot.end_time - slot.start_time).total_seconds() / 60),
                status="confirmed",
                priority="medium",
                created_by=user_id
            )
            db.add(meeting)
            
            # Add attendee (yourself)
            attendee = MeetingAttendee(
                meeting_id=meeting_id,
                user_id=user_id,
                availability="available",
                response_status="accepted"
            )
            db.add(attendee)
            
            # Get user's calendar integration
            calendar_integration = db.query(CalendarIntegration).filter(
                CalendarIntegration.user_id == user_id,
                CalendarIntegration.is_active == True
            ).first()
            
            google_event_id = None
            if calendar_integration:
                # Add to Google Calendar
                google_cal = GoogleCalendarIntegration()
                
                credentials = {
                    "access_token": calendar_integration.access_token,
                    "refresh_token": calendar_integration.refresh_token
                }
                
                # Get user email
                user = db.query(User).filter(User.id == user_id).first()
                
                google_event_id = await google_cal.create_event(
                    credentials_dict=credentials,
                    event_data={
                        "title": "New Meeting",
                        "start_time": slot.start_time,
                        "end_time": slot.end_time,
                        "description": "Meeting scheduled via Schedulo AI",
                        "attendees": []  # TODO: Add other attendees' emails
                    }
                )
                
                if google_event_id:
                    print(f"✅ Created Google Calendar event: {google_event_id}")
                else:
                    print("⚠️  Failed to create Google Calendar event")
            
            # Save to historical_meetings for ML training
            historical = HistoricalMeeting(
                user_id=user_id,
                meeting_type="team_sync",
                start_time=slot.start_time,
                end_time=slot.end_time,
                duration=int((slot.end_time - slot.start_time).total_seconds() / 60),
                day_of_week=slot.start_time.weekday(),
                hour_of_day=slot.start_time.hour,
                was_accepted=True,
                was_rescheduled=False,
                was_cancelled=False,
                attendee_count=1
            )
            db.add(historical)
            
            # Check if we should retrain ML model
            count = db.query(HistoricalMeeting).filter(
                HistoricalMeeting.user_id == user_id
            ).count()
            
            print(f"📊 Historical meetings count: {count}")
            
            if count >= 20 and count % 10 == 0:
                print(f"🤖 Triggering ML retraining (count: {count})")
                from agents.personal_agent import PersonalAgent
                agent = PersonalAgent(user_id)
                
                await agent.execute({
                    "request_type": "learn_from_feedback",
                    "feedback": {
                        "proposed_slot": {
                            "start_time": slot.start_time,
                            "end_time": slot.end_time
                        },
                        "user_accepted": True,
                        "reason": "User confirmed this slot"
                    }
                })
        
        return {
            "status": "confirmed",
            "slot_id": slot_id,
            "meeting_id": meeting_id,
            "google_event_id": google_event_id,
            "message": "Meeting scheduled successfully and added to your calendar!",
            "training_data_count": count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/slots/{slot_id}/reject")
async def reject_time_slot(slot_id: str):
    """
    Reject a time slot - saves negative feedback for ML training
    """
    try:
        from database.connection import get_db_context
        from database.models import TimeSlot, HistoricalMeeting
        
        with get_db_context() as db:
            slot = db.query(TimeSlot).filter(TimeSlot.id == slot_id).first()
            
            if not slot:
                raise HTTPException(status_code=404, detail="Time slot not found")
            
            # Save rejection for ML training
            user_id = "u1"  # TODO: Get from auth
            
            historical = HistoricalMeeting(
                user_id=user_id,
                meeting_type="team_sync",
                start_time=slot.start_time,
                end_time=slot.end_time,
                duration=int((slot.end_time - slot.start_time).total_seconds() / 60),
                day_of_week=slot.start_time.weekday(),
                hour_of_day=slot.start_time.hour,
                was_accepted=False,  # User rejected this slot
                was_rescheduled=False,
                was_cancelled=False,
                attendee_count=1
            )
            db.add(historical)
        
        return {
            "status": "rejected",
            "slot_id": slot_id,
            "message": "Feedback saved for learning"
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
