"""
Seed historical meeting data for ML training
Run this to populate initial training data
"""

from database.connection import get_db_context
from database.models import HistoricalMeeting
from datetime import datetime, timedelta
import random

def seed_historical_meetings(user_id: str = "u1", count: int = 30):
    """
    Seed historical meeting data with realistic patterns
    
    Patterns to simulate:
    - Prefers mornings (9-11am) for focused work meetings
    - Prefers afternoons (2-4pm) for team syncs
    - Avoids early mornings (before 9am) and late evenings (after 5pm)
    - More flexible on Tuesdays and Thursdays
    - Less flexible on Mondays (busy day)
    """
    
    with get_db_context() as db:
        # Clear existing data
        db.query(HistoricalMeeting).filter(
            HistoricalMeeting.user_id == user_id
        ).delete()
        
        # Generate historical meetings
        base_date = datetime.now() - timedelta(days=90)
        
        meeting_types = ["team_sync", "one_on_one", "client_call", "standup", "workshop"]
        
        for i in range(count):
            # Random day in past 90 days
            days_offset = random.randint(0, 89)
            meeting_date = base_date + timedelta(days=days_offset)
            
            # Determine meeting type
            meeting_type = random.choice(meeting_types)
            
            # Determine hour based on preferences
            day_of_week = meeting_date.weekday()
            
            # Simulate preferences
            if meeting_type == "one_on_one":
                # Prefers mornings
                hour = random.choice([9, 10, 11] * 3 + [14, 15, 16])
            elif meeting_type == "team_sync":
                # Prefers afternoons
                hour = random.choice([14, 15, 16] * 3 + [10, 11])
            elif meeting_type == "client_call":
                # Flexible but not too early/late
                hour = random.choice([10, 11, 14, 15, 16])
            else:
                # Random within working hours
                hour = random.choice([9, 10, 11, 14, 15, 16, 17])
            
            start_time = meeting_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            
            # Duration
            duration = random.choice([30, 60, 90])
            end_time = start_time + timedelta(minutes=duration)
            
            # Acceptance patterns
            # More likely to accept if it matches preferences
            was_accepted = True
            if hour < 9 or hour > 17:
                was_accepted = random.random() > 0.7  # 30% acceptance for bad times
            elif day_of_week == 0:  # Monday
                was_accepted = random.random() > 0.3  # 70% acceptance
            elif day_of_week in [1, 3]:  # Tuesday, Thursday
                was_accepted = random.random() > 0.1  # 90% acceptance
            else:
                was_accepted = random.random() > 0.2  # 80% acceptance
            
            # Reschedule patterns
            was_rescheduled = False
            if was_accepted and random.random() < 0.15:  # 15% reschedule rate
                was_rescheduled = True
            
            # Create historical meeting
            historical = HistoricalMeeting(
                user_id=user_id,
                meeting_type=meeting_type,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                day_of_week=day_of_week,
                hour_of_day=hour,
                was_accepted=was_accepted,
                was_rescheduled=was_rescheduled,
                was_cancelled=False,
                attendee_count=random.randint(2, 5)
            )
            
            db.add(historical)
        
        db.commit()
        print(f"✅ Seeded {count} historical meetings for user {user_id}")
        
        # Print summary
        accepted = db.query(HistoricalMeeting).filter(
            HistoricalMeeting.user_id == user_id,
            HistoricalMeeting.was_accepted == True
        ).count()
        
        print(f"   - {accepted} accepted ({accepted/count*100:.0f}%)")
        print(f"   - {count - accepted} rejected ({(count-accepted)/count*100:.0f}%)")
        
        # Print time preferences
        morning_count = db.query(HistoricalMeeting).filter(
            HistoricalMeeting.user_id == user_id,
            HistoricalMeeting.hour_of_day >= 9,
            HistoricalMeeting.hour_of_day < 12,
            HistoricalMeeting.was_accepted == True
        ).count()
        
        afternoon_count = db.query(HistoricalMeeting).filter(
            HistoricalMeeting.user_id == user_id,
            HistoricalMeeting.hour_of_day >= 14,
            HistoricalMeeting.hour_of_day < 17,
            HistoricalMeeting.was_accepted == True
        ).count()
        
        print(f"   - Morning meetings (9-12): {morning_count}")
        print(f"   - Afternoon meetings (2-5): {afternoon_count}")


if __name__ == "__main__":
    print("🌱 Seeding historical meeting data for ML training...")
    seed_historical_meetings("u1", 30)
    print("✅ Done! ML model will now have training data.")
