"""
Coordination Agent
Negotiates across attendees to resolve conflicts and find optimal times
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentStatus, AgentResult
from services.external_user_service import ExternalUserService
from services.federation_client import FederationClient


class CoordinationAgent(BaseAgent):
    """
    Negotiates across attendee preferences and constraints
    Resolves conflicts and balances priorities
    """
    
    def __init__(self):
        super().__init__(agent_type="coordination", name="Coordination Agent")
        self.external_service = ExternalUserService(internal_domain="acme.com")
        self.federation_client = FederationClient()
    
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Coordinate across attendees to resolve conflicts
        
        Context expected:
            - scored_windows: Windows with behavior scores
            - attendee_ids: List of user IDs or emails (internal or external)
            - priority: Meeting priority (high/medium/low)
            - preferences: User preferences from behavior agent
        """
        self.update_status(AgentStatus.NEGOTIATING, "Negotiating across attendees...")
        
        try:
            windows = context.get("scored_windows", [])
            attendee_ids = context.get("attendee_ids", [])
            priority = context.get("priority", "medium")
            preferences = context.get("preferences", {})
            
            # Categorize attendees (internal vs external)
            categorized = await self._categorize_attendees(attendee_ids)
            
            # Fetch external availability if needed
            if categorized["has_external"]:
                external_signals = await self._fetch_external_availability(
                    categorized["external"],
                    windows
                )
                # Merge external signals into windows
                windows = self._merge_external_signals(windows, external_signals)
            
            # Fetch attendee constraints
            constraints = await self._fetch_attendee_constraints(attendee_ids)
            
            # Resolve conflicts for each window
            resolved_windows = self._resolve_conflicts(
                windows,
                constraints,
                priority
            )
            
            # Balance priorities across attendees
            balanced_windows = self._balance_priorities(
                resolved_windows,
                preferences,
                priority
            )
            
            # Handle timezone negotiations
            timezone_optimized = self._optimize_for_timezones(
                balanced_windows,
                constraints
            )
            
            self.update_status(AgentStatus.COMPLETE,
                             f"Negotiated across {len(attendee_ids)} attendees")
            
            return self.create_result(
                data={
                    "coordinated_windows": timezone_optimized,
                    "conflicts_resolved": self._count_resolved_conflicts(windows, timezone_optimized),
                    "negotiation_summary": self._generate_summary(timezone_optimized)
                },
                message=f"Negotiated across {len(attendee_ids)} attendee preferences",
                confidence=0.82,
                metadata={
                    "priority": priority,
                    "total_constraints": len(constraints)
                }
            )
            
        except Exception as e:
            self.update_status(AgentStatus.ERROR, f"Error: {str(e)}")
            return self.create_result(
                data={},
                message=f"Coordination failed: {str(e)}",
                errors=[str(e)]
            )
    
    async def _fetch_attendee_constraints(
        self,
        attendee_ids: List[str]
    ) -> Dict[str, Any]:
        """Fetch constraints and preferences for each attendee"""
        constraints = {}
        
        for attendee_id in attendee_ids:
            # TODO: Fetch from database
            constraints[attendee_id] = {
                "timezone": "America/New_York",
                "working_hours": {"start": "09:00", "end": "17:00"},
                "hard_constraints": [],  # Absolute no-go times
                "soft_constraints": [],  # Preferences that can be overridden
                "priority_level": "normal",  # VIP status, etc.
                "flexibility_score": 0.7  # How flexible this person typically is
            }
        
        return constraints
    
    def _resolve_conflicts(
        self,
        windows: List[Dict[str, Any]],
        constraints: Dict[str, Any],
        priority: str
    ) -> List[Dict[str, Any]]:
        """
        Resolve conflicts for each window
        
        Strategies:
        - Hard conflicts: Mark as requiring approval or remove
        - Soft conflicts: Calculate resolution cost
        - Priority-based: High priority meetings can override soft conflicts
        """
        resolved = []
        
        for window in windows:
            window_copy = window.copy()
            conflicts = window_copy.get("conflicts", [])
            
            # Categorize conflicts
            hard_conflicts = [c for c in conflicts if c.get("type") == "hard"]
            soft_conflicts = [c for c in conflicts if c.get("type") == "soft"]
            
            # Handle hard conflicts
            if hard_conflicts:
                if priority == "high":
                    window_copy["requires_approval"] = True
                    window_copy["approval_reason"] = "High priority meeting with hard conflicts"
                else:
                    window_copy["coordination_score"] = window_copy.get("behavior_score", 50) * 0.3
                    window_copy["conflict_severity"] = "high"
                    resolved.append(window_copy)
                    continue
            
            # Handle soft conflicts
            if soft_conflicts:
                resolution_cost = self._calculate_resolution_cost(
                    soft_conflicts,
                    constraints,
                    priority
                )
                window_copy["resolution_cost"] = resolution_cost
                window_copy["resolutions"] = self._generate_resolutions(soft_conflicts)
            
            # Calculate coordination score
            window_copy["coordination_score"] = self._calculate_coordination_score(
                window_copy,
                constraints,
                priority
            )
            
            resolved.append(window_copy)
        
        return resolved
    
    def _balance_priorities(
        self,
        windows: List[Dict[str, Any]],
        preferences: Dict[str, Any],
        meeting_priority: str
    ) -> List[Dict[str, Any]]:
        """
        Balance priorities across attendees
        
        Considers:
        - Meeting priority (high/medium/low)
        - Attendee seniority/VIP status
        - Flexibility scores
        - Historical patterns
        """
        for window in windows:
            priority_score = self._calculate_priority_score(
                window,
                preferences,
                meeting_priority
            )
            window["priority_score"] = priority_score
            
            # Adjust coordination score based on priorities
            window["coordination_score"] = (
                window.get("coordination_score", 50) * 0.7 +
                priority_score * 0.3
            )
        
        return windows
    
    def _optimize_for_timezones(
        self,
        windows: List[Dict[str, Any]],
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Optimize for timezone fairness
        
        Ensures no single timezone is always disadvantaged
        """
        for window in windows:
            timezone_fairness = self._calculate_timezone_fairness(
                window,
                constraints
            )
            window["timezone_fairness"] = timezone_fairness
            
            # Penalize windows that are unfair to certain timezones
            if timezone_fairness < 0.5:
                window["coordination_score"] *= 0.8
                window["timezone_warning"] = "May be outside working hours for some attendees"
        
        return windows
    
    def _calculate_resolution_cost(
        self,
        conflicts: List[Dict[str, Any]],
        constraints: Dict[str, Any],
        priority: str
    ) -> float:
        """Calculate the cost of resolving conflicts (0-1, lower is better)"""
        if not conflicts:
            return 0.0
        
        total_cost = 0.0
        for conflict in conflicts:
            attendee_id = conflict.get("attendee_id")
            flexibility = constraints.get(attendee_id, {}).get("flexibility_score", 0.5)
            
            # Higher priority meetings have lower resolution cost
            priority_multiplier = {"high": 0.5, "medium": 1.0, "low": 1.5}.get(priority, 1.0)
            
            total_cost += (1 - flexibility) * priority_multiplier
        
        return min(1.0, total_cost / len(conflicts))
    
    def _generate_resolutions(
        self,
        conflicts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate resolution strategies for conflicts"""
        resolutions = []
        
        for conflict in conflicts:
            resolutions.append({
                "conflict_id": conflict.get("id"),
                "strategy": "reschedule_lower_priority",  # or "request_approval", "override"
                "estimated_success": 0.85,
                "alternative_action": "Move conflicting meeting to later slot"
            })
        
        return resolutions
    
    def _calculate_coordination_score(
        self,
        window: Dict[str, Any],
        constraints: Dict[str, Any],
        priority: str
    ) -> float:
        """Calculate coordination score (0-100)"""
        base_score = window.get("behavior_score", 50)
        
        # Adjust for conflicts
        conflicts = window.get("conflicts", [])
        conflict_penalty = len(conflicts) * 10
        
        # Adjust for resolution cost
        resolution_cost = window.get("resolution_cost", 0)
        cost_penalty = resolution_cost * 20
        
        # Priority bonus
        priority_bonus = {"high": 10, "medium": 5, "low": 0}.get(priority, 0)
        
        score = base_score - conflict_penalty - cost_penalty + priority_bonus
        
        return min(100.0, max(0.0, score))
    
    def _calculate_priority_score(
        self,
        window: Dict[str, Any],
        preferences: Dict[str, Any],
        meeting_priority: str
    ) -> float:
        """Calculate priority-based score (0-100)"""
        # TODO: Implement sophisticated priority calculation
        priority_values = {"high": 90, "medium": 60, "low": 30}
        return priority_values.get(meeting_priority, 60)
    
    def _calculate_timezone_fairness(
        self,
        window: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> float:
        """Calculate timezone fairness score (0-1)"""
        # TODO: Check if window falls within working hours for all timezones
        # 1.0 = fair for everyone, 0.0 = unfair for someone
        return 0.85
    
    def _count_resolved_conflicts(
        self,
        original_windows: List[Dict[str, Any]],
        resolved_windows: List[Dict[str, Any]]
    ) -> int:
        """Count how many conflicts were resolved"""
        original_conflicts = sum(len(w.get("conflicts", [])) for w in original_windows)
        remaining_conflicts = sum(len(w.get("conflicts", [])) for w in resolved_windows)
        return original_conflicts - remaining_conflicts
    
    def _generate_summary(
        self,
        windows: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate negotiation summary"""
        return {
            "total_windows": len(windows),
            "windows_with_conflicts": len([w for w in windows if w.get("conflicts")]),
            "avg_coordination_score": sum(w.get("coordination_score", 0) for w in windows) / len(windows) if windows else 0,
            "requires_approval": len([w for w in windows if w.get("requires_approval")])
        }
    
    async def _categorize_attendees(
        self,
        attendee_ids: List[str]
    ) -> Dict[str, Any]:
        """Categorize attendees into internal and external"""
        return self.external_service.categorize_attendees(attendee_ids)
    
    async def _fetch_external_availability(
        self,
        external_attendees: List[Dict[str, Any]],
        time_windows: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch availability from external Schedulo instances
        Falls back to email-based scheduling if federation fails
        
        Returns:
            Dict mapping email to availability signals
        """
        external_signals = {}
        
        for attendee in external_attendees:
            email = attendee["email"]
            endpoint = attendee["endpoint"]
            
            # Try federation first
            response = await self.federation_client.request_availability(
                endpoint=endpoint,
                user_email=email,
                time_windows=time_windows,
                meeting_context={}
            )
            
            # Check if federation succeeded
            if response.get("status") == "error":
                # Federation failed - mark for email fallback
                print(f"⚠️  Federation failed for {email}, will use email fallback")
                external_signals[email] = [
                    {
                        "start_time": w["start_time"],
                        "end_time": w["end_time"],
                        "status": "unknown",
                        "confidence": 0.0,
                        "requires_email_fallback": True,
                        "fallback_reason": response.get("error", "External Schedulo not available")
                    }
                    for w in time_windows
                ]
            else:
                # Federation succeeded
                external_signals[email] = response.get("signals", [])
        
        return external_signals
    
    def _merge_external_signals(
        self,
        windows: List[Dict[str, Any]],
        external_signals: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Merge external availability signals into time windows
        
        Treats external signals same as internal agent signals
        Handles fallback for users without Schedulo
        """
        for window in windows:
            window_start = window.get("start_time")
            
            # Track if any external user needs email fallback
            email_fallback_needed = []
            
            # Find matching signals for this window
            for email, signals in external_signals.items():
                for signal in signals:
                    if signal["start_time"] == window_start:
                        # Add external signal to window
                        if "external_signals" not in window:
                            window["external_signals"] = {}
                        
                        window["external_signals"][email] = {
                            "status": signal["status"],
                            "confidence": signal["confidence"],
                            "flexibility": signal.get("flexibility", 0.0),
                            "source": "external"
                        }
                        
                        # Check if email fallback needed
                        if signal.get("requires_email_fallback"):
                            email_fallback_needed.append({
                                "email": email,
                                "reason": signal.get("fallback_reason", "External system unavailable")
                            })
                        
                        # If external user is busy, mark window
                        elif signal["status"] == "busy":
                            if "conflicts" not in window:
                                window["conflicts"] = []
                            window["conflicts"].append({
                                "type": "hard",
                                "attendee": email,
                                "description": f"{email} is unavailable"
                            })
            
            # Mark window if email fallback needed
            if email_fallback_needed:
                window["requires_email_fallback"] = True
                window["email_fallback_users"] = email_fallback_needed
                window["fallback_message"] = (
                    f"Will send email invitation to {len(email_fallback_needed)} external user(s) "
                    f"who don't have Schedulo"
                )
        
        return windows
    
    def get_description(self) -> str:
        return "Negotiates across internal and external attendees to resolve conflicts and find mutually optimal times."
    
    def get_capabilities(self) -> List[str]:
        return [
            "Conflict resolution",
            "Priority balancing",
            "Cross-timezone negotiation",
            "Soft conflict handling",
            "Fairness optimization"
        ]
    
    def get_description(self) -> str:
        return "Negotiates across attendees to resolve conflicts and find mutually optimal times."
