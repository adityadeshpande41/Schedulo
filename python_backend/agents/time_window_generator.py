"""
Time Window Generator
Generates candidate time slots based on parsed request and constraints
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import pytz


class TimeWindowGenerator:
    """
    Generates candidate time windows for scheduling
    
    Takes parsed request (date range, time preference, duration)
    and generates potential meeting slots
    """
    
    def __init__(self):
        self.default_work_hours = (9, 17)  # 9 AM to 5 PM
        self.slot_interval = 30  # Generate slots every 30 minutes
    
    def generate_windows(
        self,
        parsed_request: Dict[str, Any],
        duration: int,
        num_slots: int = 20,
        preferred_time_range: Dict[str, str] = None
    ) -> List[Dict[str, datetime]]:
        """
        Generate candidate time windows
        
        Args:
            parsed_request: Parsed natural language request
            duration: Meeting duration in minutes
            num_slots: Number of candidate slots to generate
            preferred_time_range: Optional dict with 'start' and 'end' ISO strings
            
        Returns:
            List of time windows with start/end times
        """
        # Use preferred time range if provided, otherwise parse from request
        if preferred_time_range and preferred_time_range.get("start") and preferred_time_range.get("end"):
            user_tz = preferred_time_range.get("timezone", "UTC")
            print(f"📅 Using preferred time range in timezone: {user_tz}")
            print(f"📅 Range: {preferred_time_range['start']} to {preferred_time_range['end']}")
            
            # Parse dates in user's timezone
            tz = pytz.timezone(user_tz)
            start_dt = tz.localize(datetime.fromisoformat(preferred_time_range["start"]))
            end_dt = tz.localize(datetime.fromisoformat(preferred_time_range["end"]))
            
            date_range = {
                "start": start_dt,
                "end": end_dt,
                "timezone": tz
            }
            print(f"📅 Parsed date range: {date_range['start']} to {date_range['end']}")
        else:
            print(f"⚠️  No preferred time range, using default")
            date_range = self._parse_date_range(parsed_request.get("date_range", "next_week"))
            date_range["timezone"] = pytz.UTC
        
        time_preference = parsed_request.get("time_preference", "anytime")
        user_tz = date_range.get("timezone", pytz.UTC)
        
        # Generate candidate slots
        windows = []
        current_date = date_range["start"]
        
        while current_date <= date_range["end"] and len(windows) < num_slots:
            # Skip weekends (optional - could be configurable)
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                # Generate slots for this day based on time preference
                day_slots = self._generate_day_slots(
                    current_date,
                    duration,
                    time_preference,
                    user_tz
                )
                windows.extend(day_slots)
            
            current_date += timedelta(days=1)
        
        # Return requested number of slots
        return windows[:num_slots]
    
    def _parse_date_range(self, date_range_str: str) -> Dict[str, datetime]:
        """
        Parse date range string into start/end dates
        
        Supports: today, tomorrow, this_week, next_week, specific_date
        """
        now = datetime.utcnow().replace(tzinfo=pytz.UTC)
        
        if date_range_str == "today":
            start = now
            end = now
        elif date_range_str == "tomorrow":
            start = now + timedelta(days=1)
            end = start
        elif date_range_str == "this_week":
            # Rest of this week
            start = now
            end = now + timedelta(days=(6 - now.weekday()))
        elif date_range_str == "next_week":
            # Next Monday to Friday
            days_until_monday = (7 - now.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            start = now + timedelta(days=days_until_monday)
            end = start + timedelta(days=4)  # Monday to Friday
        else:
            # Default: next 7 days
            start = now + timedelta(days=1)
            end = now + timedelta(days=7)
        
        return {"start": start, "end": end}
    
    def _generate_day_slots(
        self,
        date: datetime,
        duration: int,
        time_preference: str,
        user_tz: pytz.timezone = pytz.UTC
    ) -> List[Dict[str, datetime]]:
        """
        Generate time slots for a specific day in user's timezone
        
        Args:
            date: The date to generate slots for (timezone-aware)
            duration: Meeting duration in minutes
            time_preference: morning, afternoon, evening, or anytime
            user_tz: User's timezone
        """
        slots = []
        
        # Determine hour range based on preference (8am-5pm for work hours)
        if time_preference == "morning":
            start_hour, end_hour = 8, 12
        elif time_preference == "afternoon":
            start_hour, end_hour = 13, 17
        elif time_preference == "evening":
            start_hour, end_hour = 17, 20
        else:  # anytime - use 8am-5pm
            start_hour, end_hour = 8, 17
        
        # Generate slots at intervals
        current_hour = start_hour
        current_minute = 0
        
        while current_hour < end_hour:
            # Create slot in user's timezone
            start_time = date.replace(
                hour=current_hour,
                minute=current_minute,
                second=0,
                microsecond=0
            )
            end_time = start_time + timedelta(minutes=duration)
            
            # Only add if end time is within working hours
            if end_time.hour < end_hour or (end_time.hour == end_hour and end_time.minute == 0):
                slots.append({
                    "start": start_time,
                    "end": end_time
                })
            
            # Move to next interval
            current_minute += self.slot_interval
            if current_minute >= 60:
                current_hour += 1
                current_minute = 0
        
        return slots
    
    def filter_by_constraints(
        self,
        windows: List[Dict[str, datetime]],
        constraints: Dict[str, Any]
    ) -> List[Dict[str, datetime]]:
        """
        Filter windows by additional constraints
        
        Constraints can include:
        - specific_date: Only slots on this date
        - exclude_dates: Dates to exclude
        - min_time: Earliest time of day
        - max_time: Latest time of day
        """
        filtered = windows
        
        # Filter by specific date
        if "specific_date" in constraints:
            target_date = constraints["specific_date"]
            filtered = [
                w for w in filtered
                if w["start"].date() == target_date.date()
            ]
        
        # Filter by time range
        if "min_time" in constraints:
            min_hour = constraints["min_time"]
            filtered = [
                w for w in filtered
                if w["start"].hour >= min_hour
            ]
        
        if "max_time" in constraints:
            max_hour = constraints["max_time"]
            filtered = [
                w for w in filtered
                if w["start"].hour < max_hour
            ]
        
        return filtered
