"""
Comprehensive Edge Case Handler
Handles all edge cases in multi-agent scheduling
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pytz


class EdgeCaseHandler:
    """
    Handles edge cases in scheduling:
    1. Timezone conflicts
    2. All attendees busy
    3. Conflicting priorities
    4. Last-minute requests
    5. Recurring meeting conflicts
    6. Holiday/vacation conflicts
    7. Working hours violations
    8. Back-to-back meeting limits
    9. Meeting duration constraints
    10. Attendee availability gaps
    """
    
    @staticmethod
    def handle_timezone_conflicts(
        slots: List[Dict[str, Any]],
        attendee_timezones: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Edge Case: International teams across multiple timezones
        
        Ensures:
        - No one has meetings outside working hours
        - Fair distribution of inconvenient times
        - Timezone-aware recommendations
        """
        from datetime import datetime
        
        fair_slots = []
        
        for slot in slots:
            # Handle different slot structures
            if "window" in slot and "start" in slot["window"]:
                start_time = slot["window"]["start"]
            elif "start_time" in slot:
                start_time = slot["start_time"]
            else:
                # Skip slots without time information
                continue
            
            # Convert string to datetime if needed
            if isinstance(start_time, str):
                try:
                    start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                except:
                    continue
                
            fairness_scores = []
            
            for user_id, tz_str in attendee_timezones.items():
                try:
                    tz = pytz.timezone(tz_str)
                    local_time = start_time.astimezone(tz)
                    hour = local_time.hour
                    
                    # Score based on local time
                    if 9 <= hour <= 17:  # Normal working hours
                        fairness_scores.append(1.0)
                    elif 8 <= hour < 9 or 17 < hour <= 18:  # Slightly outside
                        fairness_scores.append(0.7)
                    elif 7 <= hour < 8 or 18 < hour <= 19:  # Early/late
                        fairness_scores.append(0.4)
                    else:  # Outside reasonable hours
                        fairness_scores.append(0.0)
                except:
                    # Skip if timezone conversion fails
                    continue
            
            # Calculate overall fairness
            if fairness_scores:
                avg_fairness = sum(fairness_scores) / len(fairness_scores)
                min_fairness = min(fairness_scores)
                
                # Penalize if anyone has very unfair time
                if min_fairness < 0.3:
                    slot["timezone_warning"] = "Outside working hours for some attendees"
                    if "confidence" in slot:
                        slot["confidence"] *= 0.5
                
                slot["timezone_fairness"] = avg_fairness
                
                # Only include if reasonably fair
                if avg_fairness > 0.5:
                    fair_slots.append(slot)
            else:
                # No timezone info, include slot anyway
                fair_slots.append(slot)
        
        return fair_slots
    
    @staticmethod
    def handle_all_busy(
        proposals: Dict[str, List[Dict[str, Any]]],
        meeting_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Edge Case: All attendees are busy
        
        Strategies:
        1. Find who can reschedule
        2. Suggest alternative dates
        3. Propose splitting the meeting
        4. Escalate to human
        """
        # Find most flexible attendees
        flexibility_scores = {}
        for user_id, signals in proposals.items():
            avg_flexibility = sum(
                s.get("flexibility", 0) for s in signals
            ) / len(signals) if signals else 0
            flexibility_scores[user_id] = avg_flexibility
        
        # Sort by flexibility
        sorted_attendees = sorted(
            flexibility_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            "strategy": "request_reschedule",
            "most_flexible": sorted_attendees[0][0] if sorted_attendees else None,
            "suggestion": "Consider rescheduling lower-priority meetings",
            "escalate": True
        }
    
    @staticmethod
    def handle_conflicting_priorities(
        slot: Dict[str, Any],
        conflicts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Edge Case: High-priority meeting conflicts with another high-priority meeting
        
        Resolution:
        1. Compare priorities
        2. Check historical patterns
        3. Suggest alternatives
        4. Escalate if needed
        """
        high_priority_conflicts = [
            c for c in conflicts
            if c.get("priority") == "high"
        ]
        
        if high_priority_conflicts:
            return {
                "resolution": "escalate",
                "reason": "Multiple high-priority conflicts",
                "conflicts": high_priority_conflicts,
                "suggestion": "Human decision required"
            }
        
        # Medium/low priority conflicts can be auto-resolved
        return {
            "resolution": "auto_reschedule",
            "reason": "Lower priority conflicts can be rescheduled",
            "conflicts": conflicts
        }
    
    @staticmethod
    def handle_last_minute_request(
        request_time: datetime,
        proposed_time: datetime,
        meeting_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Edge Case: Meeting requested with < 24 hours notice
        
        Considerations:
        - Attendees may not see invite in time
        - May need to override existing meetings
        - Higher escalation threshold
        """
        time_until_meeting = (proposed_time - request_time).total_seconds() / 3600
        
        if time_until_meeting < 2:  # Less than 2 hours
            return {
                "warning": "Very short notice",
                "recommendation": "Call attendees directly",
                "confidence_penalty": 0.5,
                "escalate": True
            }
        elif time_until_meeting < 24:  # Less than 24 hours
            return {
                "warning": "Short notice",
                "recommendation": "Confirm attendee availability",
                "confidence_penalty": 0.8,
                "escalate": meeting_context.get("priority") == "high"
            }
        
        return {"warning": None}
    
    @staticmethod
    def handle_recurring_conflicts(
        slot: Dict[str, Any],
        recurring_meetings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Edge Case: Proposed time conflicts with recurring meeting
        
        Considerations:
        - One-time override vs permanent change
        - Impact on future occurrences
        - Attendee notification
        """
        conflicts = []
        
        for recurring in recurring_meetings:
            if EdgeCaseHandler._times_overlap(slot["window"], recurring):
                conflicts.append({
                    "meeting": recurring,
                    "type": "recurring",
                    "suggestion": "Skip this occurrence or reschedule series"
                })
        
        if conflicts:
            return {
                "has_recurring_conflicts": True,
                "conflicts": conflicts,
                "escalate": True,
                "reason": "Recurring meeting conflicts require human decision"
            }
        
        return {"has_recurring_conflicts": False}
    
    @staticmethod
    def handle_vacation_conflicts(
        slot: Dict[str, Any],
        vacation_periods: Dict[str, List[tuple[datetime, datetime]]]
    ) -> Dict[str, Any]:
        """
        Edge Case: Attendee is on vacation
        
        Resolution:
        - Exclude vacation periods
        - Suggest alternative attendees
        - Reschedule meeting
        """
        conflicts = []
        
        for user_id, periods in vacation_periods.items():
            slot_time = slot["window"]["start"]
            
            for vacation_start, vacation_end in periods:
                if vacation_start <= slot_time <= vacation_end:
                    conflicts.append({
                        "user_id": user_id,
                        "vacation_period": (vacation_start, vacation_end)
                    })
        
        if conflicts:
            return {
                "has_vacation_conflicts": True,
                "conflicts": conflicts,
                "suggestion": "Reschedule or find alternative attendee",
                "escalate": True
            }
        
        return {"has_vacation_conflicts": False}
    
    @staticmethod
    def handle_working_hours_violation(
        slot: Dict[str, Any],
        working_hours: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Edge Case: Proposed time outside working hours
        
        Considerations:
        - Company policy
        - Individual preferences
        - Timezone differences
        """
        violations = []
        
        slot_time = slot["window"]["start"]
        hour = slot_time.hour
        day = slot_time.weekday()
        
        for user_id, hours in working_hours.items():
            start_hour = hours.get("start", 9)
            end_hour = hours.get("end", 17)
            working_days = hours.get("days", [0, 1, 2, 3, 4])  # Mon-Fri
            
            if day not in working_days:
                violations.append({
                    "user_id": user_id,
                    "reason": "Outside working days"
                })
            elif hour < start_hour or hour >= end_hour:
                violations.append({
                    "user_id": user_id,
                    "reason": f"Outside working hours ({start_hour}-{end_hour})"
                })
        
        if violations:
            return {
                "has_violations": True,
                "violations": violations,
                "confidence_penalty": 0.6,
                "requires_approval": True
            }
        
        return {"has_violations": False}
    
    @staticmethod
    def handle_back_to_back_limit(
        slot: Dict[str, Any],
        existing_meetings: Dict[str, List[Dict[str, Any]]],
        max_consecutive: int = 3
    ) -> Dict[str, Any]:
        """
        Edge Case: Too many back-to-back meetings
        
        Considerations:
        - User fatigue
        - Buffer time preferences
        - Meeting type
        """
        warnings = []
        
        slot_start = slot["window"]["start"]
        slot_end = slot["window"]["end"]
        
        for user_id, meetings in existing_meetings.items():
            consecutive_count = 0
            
            # Check meetings before
            for meeting in meetings:
                if meeting["end_time"] == slot_start:
                    consecutive_count += 1
            
            # Check meetings after
            for meeting in meetings:
                if meeting["start_time"] == slot_end:
                    consecutive_count += 1
            
            if consecutive_count >= max_consecutive:
                warnings.append({
                    "user_id": user_id,
                    "consecutive_meetings": consecutive_count + 1,
                    "suggestion": "Add buffer time"
                })
        
        if warnings:
            return {
                "has_back_to_back_warning": True,
                "warnings": warnings,
                "confidence_penalty": 0.9
            }
        
        return {"has_back_to_back_warning": False}
    
    @staticmethod
    def handle_duration_constraints(
        requested_duration: int,
        available_gaps: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Edge Case: Requested duration doesn't fit available gaps
        
        Solutions:
        - Suggest shorter duration
        - Find longer gaps
        - Split into multiple meetings
        """
        fitting_gaps = []
        
        for gap in available_gaps:
            gap_duration = (gap["end"] - gap["start"]).total_seconds() / 60
            
            if gap_duration >= requested_duration:
                fitting_gaps.append(gap)
            elif gap_duration >= requested_duration * 0.75:
                # Close enough - suggest adjusted duration
                fitting_gaps.append({
                    **gap,
                    "suggested_duration": int(gap_duration),
                    "note": f"Suggest {int(gap_duration)} min instead of {requested_duration} min"
                })
        
        return fitting_gaps
    
    @staticmethod
    def handle_availability_gaps(
        attendee_signals: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Edge Case: Large gaps in attendee availability
        
        Analysis:
        - Identify patterns in unavailability
        - Suggest optimal time ranges
        - Detect systematic conflicts
        """
        # Find common unavailable periods
        unavailable_patterns = {}
        
        for user_id, signals in attendee_signals.items():
            busy_times = [
                s for s in signals
                if s["status"] == "busy"
            ]
            
            if len(busy_times) > len(signals) * 0.7:
                unavailable_patterns[user_id] = "mostly_busy"
        
        if unavailable_patterns:
            return {
                "has_availability_gaps": True,
                "patterns": unavailable_patterns,
                "suggestion": "Consider extending date range or async communication"
            }
        
        return {"has_availability_gaps": False}
    
    @staticmethod
    def _times_overlap(
        window1: Dict[str, datetime],
        window2: Dict[str, datetime]
    ) -> bool:
        """Check if two time windows overlap"""
        return (
            window1["start"] < window2["end"] and
            window1["end"] > window2["start"]
        )
