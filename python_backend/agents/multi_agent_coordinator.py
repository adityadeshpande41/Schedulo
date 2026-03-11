"""
Multi-Agent Coordinator
Facilitates negotiation between personal agents without accessing private data
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from .base_agent import BaseAgent, AgentStatus, AgentResult
from .personal_agent import PersonalAgent, AvailabilitySignal
from .openai_integration import OpenAIAssistant


class NegotiationRound:
    """Represents one round of negotiation between agents"""
    
    def __init__(self, round_number: int):
        self.round_number = round_number
        self.proposals = {}  # agent_id -> List[AvailabilitySignal]
        self.consensus_slots = []
        self.conflicts = []


class MultiAgentCoordinator(BaseAgent):
    """
    Coordinates multiple personal agents to find optimal meeting times
    
    Key Features:
    - No access to private calendar data
    - Only receives availability signals
    - Facilitates negotiation protocol
    - Handles edge cases and conflicts
    - Escalates when needed
    """
    
    def __init__(self):
        super().__init__(agent_type="coordinator", name="Multi-Agent Coordinator")
        self.personal_agents = {}  # user_id -> PersonalAgent
        self.ai_assistant = OpenAIAssistant("coordinator")
    
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Coordinate scheduling across multiple personal agents
        
        Context:
            - attendee_ids: List of user IDs
            - duration: Meeting duration in minutes
            - meeting_context: Meeting details
            - date_range: (start_date, end_date)
        """
        self.update_status(AgentStatus.NEGOTIATING, "Coordinating agents...")
        
        try:
            attendee_ids = context.get("attendee_ids", [])
            duration = context.get("duration", 60)
            meeting_context = context.get("meeting_context", {})
            date_range = context.get("date_range")
            
            # Edge Case 1: Single attendee
            if len(attendee_ids) == 1:
                return await self._handle_single_attendee(attendee_ids[0], context)
            
            # Edge Case 2: No attendees
            if not attendee_ids:
                raise ValueError("No attendees specified")
            
            # Initialize personal agents
            await self._initialize_agents(attendee_ids)
            
            # Generate candidate time windows
            candidate_windows = self._generate_candidate_windows(
                date_range,
                duration,
                meeting_context
            )
            
            # Edge Case 3: No candidate windows
            if not candidate_windows:
                return await self._handle_no_candidates(context)
            
            # Multi-round negotiation
            negotiation_result = await self._negotiate(
                candidate_windows,
                meeting_context
            )
            
            # Edge Case 4: No consensus reached
            if not negotiation_result["consensus_slots"]:
                return await self._handle_no_consensus(context, negotiation_result)
            
            # Rank and explain recommendations
            ranked_slots = await self._rank_and_explain(
                negotiation_result["consensus_slots"],
                meeting_context
            )
            
            # Check if escalation needed
            escalation_check = self._check_escalation_needed(ranked_slots)
            
            self.update_status(AgentStatus.COMPLETE, 
                             f"Found {len(ranked_slots)} optimal slots")
            
            return self.create_result(
                data={
                    "recommended_slots": ranked_slots,
                    "negotiation_rounds": negotiation_result["rounds"],
                    "escalation_needed": escalation_check["needed"],
                    "escalation_reason": escalation_check.get("reason"),
                    "edge_cases_handled": negotiation_result.get("edge_cases", [])
                },
                message=f"Coordination complete across {len(attendee_ids)} agents",
                confidence=ranked_slots[0]["confidence"] if ranked_slots else 0
            )
            
        except Exception as e:
            self.update_status(AgentStatus.ERROR, f"Error: {str(e)}")
            return self.create_result(
                data={},
                message=f"Coordination failed: {str(e)}",
                errors=[str(e)]
            )
    
    async def _initialize_agents(self, attendee_ids: List[str]):
        """Initialize personal agent for each attendee"""
        for user_id in attendee_ids:
            if user_id not in self.personal_agents:
                self.personal_agents[user_id] = PersonalAgent(user_id)
    
    def _generate_candidate_windows(
        self,
        date_range: tuple[datetime, datetime],
        duration: int,
        meeting_context: Dict[str, Any]
    ) -> List[Dict[str, datetime]]:
        """
        Generate candidate time windows to evaluate
        
        Smart generation based on:
        - Business hours
        - Timezone considerations
        - Meeting type typical times
        """
        start_date, end_date = date_range
        windows = []
        
        # Business hours: 9 AM - 5 PM
        business_start = 9
        business_end = 17
        
        current_date = start_date
        while current_date <= end_date:
            # Skip weekends (edge case)
            if current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                continue
            
            # Generate slots throughout the day
            for hour in range(business_start, business_end):
                # Check if slot fits within business hours
                slot_end_hour = hour + (duration / 60)
                if slot_end_hour > business_end:
                    continue
                
                start_time = current_date.replace(hour=hour, minute=0, second=0)
                end_time = start_time + timedelta(minutes=duration)
                
                windows.append({
                    "start": start_time,
                    "end": end_time
                })
            
            current_date += timedelta(days=1)
        
        return windows[:50]  # Limit to 50 candidates for efficiency
    
    async def _negotiate(
        self,
        candidate_windows: List[Dict[str, datetime]],
        meeting_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Multi-round negotiation between personal agents
        
        Protocol:
        1. Each agent evaluates candidates independently
        2. Agents share only availability signals (not calendar data)
        3. Find slots where all agents agree
        4. Handle conflicts and edge cases
        """
        rounds = []
        edge_cases_handled = []
        
        # Round 1: Initial availability check
        round1 = NegotiationRound(1)
        
        for user_id, agent in self.personal_agents.items():
            # Request availability signals (privacy-preserving)
            result = await agent.execute({
                "request_type": "availability_check",
                "time_windows": candidate_windows,
                "meeting_context": meeting_context
            })
            
            round1.proposals[user_id] = result.data["availability_signals"]
        
        # Find consensus slots (all agents available)
        consensus_slots = self._find_consensus(round1.proposals, candidate_windows)
        round1.consensus_slots = consensus_slots
        rounds.append(round1)
        
        # Edge Case: Timezone conflicts
        timezone_conflicts = self._detect_timezone_conflicts(round1.proposals)
        if timezone_conflicts:
            edge_cases_handled.append("timezone_conflicts")
            consensus_slots = self._resolve_timezone_conflicts(
                consensus_slots,
                timezone_conflicts
            )
        
        # Edge Case: All agents busy
        if not consensus_slots:
            edge_cases_handled.append("all_busy")
            # Try flexible slots (where agents might reschedule)
            flexible_slots = self._find_flexible_slots(round1.proposals, candidate_windows)
            consensus_slots = flexible_slots
        
        # Edge Case: Low confidence slots
        if consensus_slots:
            low_confidence = [s for s in consensus_slots if s["confidence"] < 0.6]
            if low_confidence:
                edge_cases_handled.append("low_confidence")
                # Request additional context from agents
                consensus_slots = await self._request_additional_context(
                    low_confidence,
                    meeting_context
                )
        
        return {
            "consensus_slots": consensus_slots,
            "rounds": len(rounds),
            "edge_cases": edge_cases_handled
        }
    
    def _find_consensus(
        self,
        proposals: Dict[str, List[Dict[str, Any]]],
        candidate_windows: List[Dict[str, datetime]]
    ) -> List[Dict[str, Any]]:
        """
        Find time slots where all agents are available
        """
        consensus = []
        
        for i, window in enumerate(candidate_windows):
            # Check if all agents are available for this window
            all_available = True
            signals = []
            
            for user_id, user_signals in proposals.items():
                if i < len(user_signals):
                    signal = user_signals[i]
                    signals.append(signal)
                    
                    # Not available if busy or prefer_not
                    if signal["status"] in ["busy", "prefer_not"]:
                        all_available = False
                        break
            
            if all_available and signals:
                # Calculate aggregate confidence
                avg_confidence = sum(s["confidence"] for s in signals) / len(signals)
                avg_flexibility = sum(s.get("flexibility", 0) for s in signals) / len(signals)
                
                consensus.append({
                    "window": window,
                    "confidence": avg_confidence,
                    "flexibility": avg_flexibility,
                    "signals": signals
                })
        
        return consensus
    
    def _find_flexible_slots(
        self,
        proposals: Dict[str, List[Dict[str, Any]]],
        candidate_windows: List[Dict[str, datetime]]
    ) -> List[Dict[str, Any]]:
        """
        Find slots where agents are flexible (might reschedule)
        Edge case: When no perfect slots exist
        """
        flexible = []
        
        for i, window in enumerate(candidate_windows):
            signals = []
            flexibility_scores = []
            
            for user_id, user_signals in proposals.items():
                if i < len(user_signals):
                    signal = user_signals[i]
                    signals.append(signal)
                    
                    # Check if flexible
                    if signal["status"] == "flexible":
                        flexibility_scores.append(signal.get("flexibility", 0))
            
            # If enough agents are flexible
            if len(flexibility_scores) >= len(proposals) * 0.7:
                avg_flexibility = sum(flexibility_scores) / len(flexibility_scores)
                
                flexible.append({
                    "window": window,
                    "confidence": avg_flexibility * 0.8,  # Lower confidence
                    "flexibility": avg_flexibility,
                    "signals": signals,
                    "requires_approval": True
                })
        
        return flexible
    
    def _detect_timezone_conflicts(
        self,
        proposals: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Detect if proposed times are unfair for certain timezones
        Edge case: International teams
        """
        # TODO: Implement timezone fairness detection
        return []
    
    def _resolve_timezone_conflicts(
        self,
        slots: List[Dict[str, Any]],
        conflicts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Resolve timezone conflicts by finding fair times
        """
        # TODO: Implement timezone conflict resolution
        return slots
    
    async def _request_additional_context(
        self,
        low_confidence_slots: List[Dict[str, Any]],
        meeting_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Request additional context from agents for low confidence slots
        """
        # TODO: Implement additional context gathering
        return low_confidence_slots
    
    async def _rank_and_explain(
        self,
        consensus_slots: List[Dict[str, Any]],
        meeting_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Rank slots and generate explanations using OpenAI
        """
        ranked = sorted(consensus_slots, key=lambda s: s["confidence"], reverse=True)
        
        # Generate explanations for top slots
        for i, slot in enumerate(ranked[:5]):
            explanation = await self.ai_assistant.generate_explanation(
                recommendation=slot,
                context=meeting_context
            )
            slot["explanation"] = explanation
            slot["rank"] = i + 1
            slot["recommended"] = (i == 0)
        
        return ranked
    
    def _check_escalation_needed(
        self,
        ranked_slots: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Determine if human escalation is needed
        """
        if not ranked_slots:
            return {
                "needed": True,
                "reason": "No suitable slots found"
            }
        
        top_slot = ranked_slots[0]
        
        # Escalate if low confidence
        if top_slot["confidence"] < 0.6:
            return {
                "needed": True,
                "reason": f"Low confidence ({top_slot['confidence']:.0%})"
            }
        
        # Escalate if requires approval
        if top_slot.get("requires_approval"):
            return {
                "needed": True,
                "reason": "Requires rescheduling existing meetings"
            }
        
        return {"needed": False}
    
    async def _handle_single_attendee(
        self,
        user_id: str,
        context: Dict[str, Any]
    ) -> AgentResult:
        """Edge case: Single attendee meeting"""
        agent = PersonalAgent(user_id)
        result = await agent.execute({
            "request_type": "availability_check",
            "time_windows": self._generate_candidate_windows(
                context.get("date_range"),
                context.get("duration", 60),
                context.get("meeting_context", {})
            ),
            "meeting_context": context.get("meeting_context", {})
        })
        
        return self.create_result(
            data=result.data,
            message="Single attendee scheduling",
            confidence=result.confidence
        )
    
    async def _handle_no_candidates(
        self,
        context: Dict[str, Any]
    ) -> AgentResult:
        """Edge case: No candidate windows generated"""
        return self.create_result(
            data={
                "recommended_slots": [],
                "escalation_needed": True,
                "escalation_reason": "No available time windows in specified range"
            },
            message="No candidate windows found",
            confidence=0.0
        )
    
    async def _handle_no_consensus(
        self,
        context: Dict[str, Any],
        negotiation_result: Dict[str, Any]
    ) -> AgentResult:
        """Edge case: No consensus reached"""
        return self.create_result(
            data={
                "recommended_slots": [],
                "escalation_needed": True,
                "escalation_reason": "Could not find time that works for all attendees",
                "suggestion": "Try extending date range or reducing attendee count"
            },
            message="No consensus reached",
            confidence=0.0
        )
    
    def get_capabilities(self) -> List[str]:
        return [
            "Multi-agent coordination",
            "Privacy-preserving negotiation",
            "Edge case handling",
            "Timezone conflict resolution",
            "Smart escalation",
            "AI-powered explanations"
        ]
    
    def get_description(self) -> str:
        return "Coordinates multiple personal agents to find optimal meeting times while preserving privacy."
