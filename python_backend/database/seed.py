"""
Database seeding script
Populates database with sample data for development
"""

from datetime import datetime, timedelta
import uuid

from database import get_db_context
from database.models import (
    User, Meeting, MeetingAttendee, UserPreference,
    MeetingStatus, MeetingPriority, MeetingType
)


def seed_users():
    """Seed sample users"""
    users = [
        User(
            id="u1",
            name="Alex Rivera",
            email="alex@schedulo.ai",
            role="Product Manager",
            timezone="America/New_York"
        ),
        User(
            id="u2",
            name="Sarah Chen",
            email="sarah@schedulo.ai",
            role="Engineering Lead",
            timezone="America/Los_Angeles"
        ),
        User(
            id="u3",
            name="Marcus Johnson",
            email="marcus@schedulo.ai",
            role="Designer",
            timezone="America/Chicago"
        ),
        User(
            id="u4",
            name="Priya Patel",
            email="priya@schedulo.ai",
            role="Data Scientist",
            timezone="Asia/Kolkata"
        ),
        User(
            id="u5",
            name="James Kim",
            email="james@client.com",
            role="VP of Sales (Client)",
            timezone="America/New_York"
        ),
    ]
    
    with get_db_context() as db:
        for user in users:
            existing = db.query(User).filter_by(id=user.id).first()
            if not existing:
                db.add(user)
        print("✅ Users seeded")


def seed_preferences():
    """Seed user preferences"""
    preferences = [
        UserPreference(
            id="p1",
            user_id="u1",
            category="time",
            label="Prefers Afternoons",
            description="Scheduling meetings after 1 PM when possible",
            value="afternoon",
            icon="sun",
            active=True
        ),
        UserPreference(
            id="p2",
            user_id="u1",
            category="time",
            label="No Fridays After 3 PM",
            description="Avoid scheduling on Friday afternoons",
            value="no_friday_pm",
            icon="calendar-x",
            active=True
        ),
        UserPreference(
            id="p3",
            user_id="u1",
            category="priority",
            label="Client Calls First",
            description="Will move internal 1:1s for customer calls",
            value="client_priority",
            icon="arrow-up",
            active=True
        ),
        UserPreference(
            id="p4",
            user_id="u1",
            category="behavior",
            label="No Back-to-Back",
            description="Prefers 15-minute buffer between meetings",
            value="buffer_15",
            icon="clock",
            active=True
        ),
    ]
    
    with get_db_context() as db:
        for pref in preferences:
            existing = db.query(UserPreference).filter_by(id=pref.id).first()
            if not existing:
                db.add(pref)
        print("✅ Preferences seeded")


def seed_meetings():
    """Seed sample meetings"""
    base_time = datetime.utcnow() + timedelta(days=1)
    
    meetings = [
        {
            "id": "m1",
            "title": "Sprint Planning",
            "type": MeetingType.TEAM_SYNC,
            "start_time": base_time.replace(hour=10, minute=0),
            "end_time": base_time.replace(hour=11, minute=0),
            "duration": 60,
            "status": MeetingStatus.CONFIRMED,
            "priority": MeetingPriority.HIGH,
            "location": "Virtual — Zoom",
            "description": "Weekly sprint planning and backlog review",
            "created_by": "u1",
            "attendees": ["u1", "u2", "u3"]
        },
        {
            "id": "m2",
            "title": "Client Strategy Review",
            "type": MeetingType.CLIENT_CALL,
            "start_time": base_time.replace(hour=14, minute=0),
            "end_time": base_time.replace(hour=15, minute=0),
            "duration": 60,
            "status": MeetingStatus.PENDING,
            "priority": MeetingPriority.HIGH,
            "location": "Virtual — Google Meet",
            "description": "Q2 strategy alignment with client team",
            "created_by": "u1",
            "attendees": ["u1", "u5"]
        },
    ]
    
    with get_db_context() as db:
        for meeting_data in meetings:
            existing = db.query(Meeting).filter_by(id=meeting_data["id"]).first()
            if not existing:
                attendee_ids = meeting_data.pop("attendees")
                meeting = Meeting(**meeting_data)
                db.add(meeting)
                db.flush()
                
                # Add attendees
                for user_id in attendee_ids:
                    attendee = MeetingAttendee(
                        meeting_id=meeting.id,
                        user_id=user_id,
                        availability="available",
                        response_status="accepted"
                    )
                    db.add(attendee)
        
        print("✅ Meetings seeded")


def seed_all():
    """Seed all data"""
    print("🌱 Seeding database...")
    seed_users()
    seed_preferences()
    seed_meetings()
    print("✅ Database seeding complete!")


if __name__ == "__main__":
    seed_all()
