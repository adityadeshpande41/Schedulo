"""
Calendar Integration API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from database.connection import get_db
from database.models import CalendarIntegration, User
from integrations.google_calendar import GoogleCalendarIntegration

router = APIRouter(prefix="/calendar", tags=["calendar"])
auth_router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/connect/google")
async def connect_google_calendar(
    user_id: str = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Initiate Google Calendar OAuth flow
    Returns authorization URL to redirect user to
    """
    try:
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Generate OAuth URL
        google_cal = GoogleCalendarIntegration()
        auth_url = google_cal.get_authorization_url(user_id)
        
        return {"authorization_url": auth_url}
    except Exception as e:
        # Fallback if database not available - generate OAuth URL anyway
        print(f"Database error in connect: {e}")
        try:
            google_cal = GoogleCalendarIntegration()
            auth_url = google_cal.get_authorization_url(user_id)
            return {"authorization_url": auth_url}
        except Exception as oauth_error:
            print(f"OAuth error: {oauth_error}")
            raise HTTPException(status_code=500, detail="Failed to generate OAuth URL")


@auth_router.get("/google/callback")
async def google_calendar_callback(
    code: str = Query(...),
    state: str = Query(...),  # state contains user_id
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback
    Exchange code for tokens and store in database
    """
    try:
        google_cal = GoogleCalendarIntegration()
        
        # Exchange code for tokens
        token_data = await google_cal.handle_oauth_callback(code, state)
        user_id = token_data["user_id"]
        
        # Check if integration already exists
        existing = db.query(CalendarIntegration).filter(
            CalendarIntegration.user_id == user_id
        ).first()
        
        if existing:
            # Update existing
            existing.access_token = token_data["access_token"]
            existing.refresh_token = token_data.get("refresh_token")
            existing.token_expires_at = token_data.get("expires_at")
            existing.is_active = True
            existing.updated_at = datetime.utcnow()
        else:
            # Create new
            integration = CalendarIntegration(
                user_id=user_id,
                provider="google",
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                token_expires_at=token_data.get("expires_at"),
                is_active=True
            )
            db.add(integration)
        
        db.commit()
        
        # Redirect back to frontend
        return RedirectResponse(url=f"http://localhost:5173/dashboard?calendar_connected=true")
        
    except Exception as e:
        print(f"OAuth callback error: {e}")
        return RedirectResponse(url=f"http://localhost:5173/dashboard?calendar_error=true")


@router.get("/status/{user_id}")
async def get_calendar_status(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Check if user has connected calendar
    """
    try:
        integration = db.query(CalendarIntegration).filter(
            CalendarIntegration.user_id == user_id,
            CalendarIntegration.is_active == True
        ).first()
        
        if not integration:
            return {
                "connected": False,
                "provider": None
            }
        
        return {
            "connected": True,
            "provider": integration.provider,
            "last_synced": integration.last_synced_at.isoformat() if integration.last_synced_at else None
        }
    except Exception as e:
        # Fallback if database not available
        print(f"Database error: {e}")
        return {
            "connected": False,
            "provider": None
        }


@router.post("/sync/{user_id}")
async def sync_calendar(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Manually trigger calendar sync
    Fetches events from Google Calendar and stores in database
    """
    # Get integration
    integration = db.query(CalendarIntegration).filter(
        CalendarIntegration.user_id == user_id,
        CalendarIntegration.is_active == True
    ).first()
    
    if not integration:
        raise HTTPException(status_code=404, detail="Calendar not connected")
    
    try:
        google_cal = GoogleCalendarIntegration()
        
        # Fetch events for next 30 days
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)
        
        credentials = {
            "access_token": integration.access_token,
            "refresh_token": integration.refresh_token
        }
        
        events = await google_cal.fetch_events(credentials, start_date, end_date)
        
        # Save events to database
        from database.models import CalendarEvent
        
        # Delete old events for this user in this date range
        db.query(CalendarEvent).filter(
            CalendarEvent.user_id == user_id,
            CalendarEvent.start_time >= start_date,
            CalendarEvent.end_time <= end_date
        ).delete()
        
        # Insert new events
        import uuid
        for event in events:
            calendar_event = CalendarEvent(
                id=str(uuid.uuid4()),
                user_id=user_id,
                external_id=event["external_id"],
                calendar_provider="google",
                title=event["title"],
                start_time=event["start_time"],
                end_time=event["end_time"],
                location=event.get("location"),
                attendees=event.get("attendees", [])
            )
            db.add(calendar_event)
        
        db.commit()
        
        # Update last synced time
        integration.last_synced_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "events_fetched": len(events),
            "synced_at": integration.last_synced_at.isoformat()
        }
        
    except Exception as e:
        print(f"Calendar sync error: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.delete("/disconnect/{user_id}")
async def disconnect_calendar(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Disconnect calendar integration
    """
    integration = db.query(CalendarIntegration).filter(
        CalendarIntegration.user_id == user_id
    ).first()
    
    if not integration:
        raise HTTPException(status_code=404, detail="Calendar not connected")
    
    # Soft delete - just mark as inactive
    integration.is_active = False
    db.commit()
    
    return {"success": True, "message": "Calendar disconnected"}
