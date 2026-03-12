"""
Scheduling Link API Routes
Allows external users to view available times and book meetings
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any
from datetime import datetime, timedelta
import secrets

from database.connection import get_db
# from database.models import SchedulingLink, Meeting, User

router = APIRouter(prefix="/scheduling", tags=["scheduling"])


class CreateSchedulingLinkRequest(BaseModel):
    """Request to create a scheduling link"""
    organizer_id: str
    title: str
    duration: int = 30
    available_days: int = 14
    buffer_time: int = 0


class BookMeetingRequest(BaseModel):
    """Request to book a meeting via scheduling link"""
    attendee_name: str
    attendee_email: EmailStr
    selected_time: datetime
    notes: str = ""


@router.post("/link/create")
async def create_scheduling_link(
    request: CreateSchedulingLinkRequest,
    db: Session = Depends(get_db)
):
    """
    Create a scheduling link for external users
    Like Calendly - generates a unique URL
    """
    # Generate unique token
    token = secrets.token_urlsafe(16)
    
    # Create link (would save to database)
    link_data = {
        "token": token,
        "organizer_id": request.organizer_id,
        "title": request.title,
        "duration": request.duration,
        "available_days": request.available_days,
        "buffer_time": request.buffer_time,
        "url": f"https://schedulo.app/book/{token}",
        "created_at": datetime.utcnow()
    }
    
    return {
        "success": True,
        "link": link_data,
        "share_url": link_data["url"]
    }


@router.get("/link/{token}/availability")
async def get_available_slots(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Get available time slots for a scheduling link
    External users call this to see when organizer is free
    """
    # TODO: Look up link in database
    # For now, return mock data
    
    # Generate next 14 days of slots
    slots = []
    start_date = datetime.utcnow()
    
    for day_offset in range(14):
        date = start_date + timedelta(days=day_offset)
        
        # Skip weekends
        if date.weekday() >= 5:
            continue
        
        # Generate slots from 9 AM to 5 PM
        for hour in range(9, 17):
            slot_time = date.replace(hour=hour, minute=0, second=0, microsecond=0)
            
            # Check if organizer is available (would check calendar)
            is_available = True  # Mock
            
            if is_available:
                slots.append({
                    "time": slot_time.isoformat(),
                    "available": True
                })
    
    return {
        "token": token,
        "title": "Partnership Discussion",
        "duration": 30,
        "organizer": {
            "name": "Alex Rivera",
            "company": "Acme Corp"
        },
        "available_slots": slots[:20]  # Return first 20 slots
    }


@router.post("/link/{token}/book")
async def book_meeting_via_link(
    token: str,
    request: BookMeetingRequest,
    db: Session = Depends(get_db)
):
    """
    Book a meeting via scheduling link
    External user selects a time and confirms
    """
    # TODO: Validate token and check slot still available
    
    # Create meeting
    meeting_data = {
        "id": f"m_{secrets.token_hex(8)}",
        "title": "Partnership Discussion",
        "start_time": request.selected_time,
        "end_time": request.selected_time + timedelta(minutes=30),
        "organizer_email": "alex@acme.com",
        "attendee_name": request.attendee_name,
        "attendee_email": request.attendee_email,
        "notes": request.notes,
        "status": "confirmed"
    }
    
    # TODO: Save to database
    # TODO: Send confirmation emails
    # TODO: Add to calendars
    
    return {
        "success": True,
        "meeting": meeting_data,
        "message": "Meeting booked successfully! Check your email for confirmation."
    }
