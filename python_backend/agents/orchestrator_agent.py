"""
Orchestrator Agent
Synthesizes all agent outputs into ranked recommendations
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentStatus, AgentResult
from .calendar_agent import CalendarAgent
from .behavior_agent import BehaviorAgent
from .coordination_agent import CoordinationAgent


class OrchestratorAgent(BaseAgent):
    """
    Orchestrates all agents and produces final ranked recommendations
    Combines signals from calendar, behavior, and coordination agents
    """
    
    def __init__(self):
        super().__init__(agent_type="orchestrator", name="Orchestrator")
        self.calendar_agent = CalendarAgent()
        self.behavior_agent = BehaviorAgent()
        self.coordination_agent = CoordinationAgent()
    
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Orchestrate all agents and produce final recommendations
        
        Context expected:
            - attendee_ids: List of user IDs
            - duration: Meeting duration in minutes
            - meeting_type: Type of meeting
            - priority: Meeting priority
            - date_range: Optional date range
        """
        self.update_status(AgentStatus.RANKING, "Orchestrating agents...")
        
        try:
            # Step 1: Calendar Agent - Find available windows
            calendar_result = await self.calendar_agent.execute(context)
            if calendar_result.errors:
                return self._handle_agent_failure("calendar", calendar_result)
            
            # Step 2: Behavior Agent - Score windows based on patterns
            behavior_context = {
                **context,
                "available_windows": calendar_result.data["available_windows"]
            }
            behavior_result = await self.behavior_agent.execute(behavior_context)
            if behavior_result.errors:
                return self._handle_agent_failure("behavior", behavior_result)
            
            # Step 3: Coordination Agent - Resolve conflicts and negotiate
            coordination_context = {
                **context,
                "scored_windows": behavior_result.data["scored_windows"],
                "preferences": behavior_result.data["preferences"]
            }
            coordination_result = await self.coordination_agent.execute(coordination_context)
            if coordination_result.errors:
                return self._handle_agent_failure("coordination", coordination_result)
            
            # Step 4: Synthesize and rank final recommendations
            final_slots = self._synthesize_recommendations(
                calendar_result,
                behavior_result,
                coordination_result,
                context
            )
            
            # Step 5: Generate explanations
            explanations = self._generate_explanations(
                final_slots,
                calendar_result,
                behavior_result,
                coordination_result
            )
            
            # Step 6: Determine if human approval needed
            approval_needed = self._check_approval_needed(final_slots, context)
            
            self.update_status(AgentStatus.COMPLETE,
                             f"Ranked {len(final_slots)} recommendations")
            
            return self.create_result(
                data={
                    "recommended_slots": final_slots,
                    "explanations": explanations,
                    "approval_needed": approval_needed,
                    "agent_insights": self._collect_agent_insights(
                        calendar_result,
                        behavior_result,
                        coordination_result
                    )
                },
                message=f"Generated {len(final_slots)} ranked recommendations",
                confidence=self._calculate_overall_confidence(final_slots),
                metadata={
                    "agents_executed": 3,
                    "top_score": final_slots[0]["final_score"] if final_slots else 0
                }
            )
            
        except Exception as e:
            self.update_status(AgentStatus.ERROR, f"Error: {str(e)}")
            return self.create_result(
                data={},
                message=f"Orchestration failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _synthesize_recommendations(
        self,
        calendar_result: AgentResult,
        behavior_result: AgentResult,
        coordination_result: AgentResult,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Synthesize all agent outputs into final ranked recommendations
        
        Combines:
        - Calendar availability
        - Behavior patterns
        - Coordination scores
        - Priority and constraints
        """
        windows = coordination_result.data["coordinated_windows"]
        
        # Calculate final score for each window
        for window in windows:
            final_score = self._calculate_final_score(window, context)
            window["final_score"] = final_score
            window["rank"] = 0  # Will be set after sorting
            window["recommended"] = False  # Will be set for top choice
        
        # Sort by final score
        sorted_windows = sorted(windows, key=lambda w: w["final_score"], reverse=True)
        
        # Assign ranks and mark top recommendation
        for i, window in enumerate(sorted_windows):
            window["rank"] = i + 1
            if i == 0:
                window["recommended"] = True
        
        return sorted_windows[:10]  # Return top 10
    
    def _calculate_final_score(
        self,
        window: Dict[str, Any],
        context: Dict[str, Any]
    ) -> float:
        """
        Calculate final score combining all agent signals
        
        Weights:
        - Calendar availability: 20%
        - Behavior patterns: 35%
        - Coordination: 35%
        - Priority boost: 10%
        """
        # Base scores from agents
        behavior_score = window.get("behavior_score", 50)
        coordination_score = window.get("coordination_score", 50)
        
        # Calendar score (inverse of conflicts)
        conflicts = len(window.get("conflicts", []))
        calendar_score = max(0, 100 - (conflicts * 20))
        
        # Weighted combination
        final_score = (
            calendar_score * 0.20 +
            behavior_score * 0.35 +
            coordination_score * 0.35
        )
        
        # Priority boost
        priority = context.get("priority", "medium")
        priority_boost = {"high": 10, "medium": 5, "low": 0}.get(priority, 0)
        final_score += priority_boost
        
        return min(100.0, max(0.0, final_score))
    
    def _generate_explanations(
        self,
        slots: List[Dict[str, Any]],
        calendar_result: AgentResult,
        behavior_result: AgentResult,
        coordination_result: AgentResult
    ) -> Dict[str, Any]:
        """Generate human-readable explanations for recommendations"""
        if not slots:
            return {}
        
        top_slot = slots[0]
        
        return {
            "top_recommendation": {
                "slot_id": top_slot.get("id", "unknown"),
                "reasoning": self._generate_reasoning(top_slot),
                "confidence": self._calculate_slot_confidence(top_slot),
                "tradeoffs": self._identify_tradeoffs(slots)
            },
            "alternatives": [
                {
                    "slot_id": slot.get("id", "unknown"),
                    "reasoning": self._generate_reasoning(slot),
                    "why_not_top": self._explain_ranking(slot, top_slot)
                }
                for slot in slots[1:4]  # Top 3 alternatives
            ]
        }
    
    def _generate_reasoning(self, slot: Dict[str, Any]) -> str:
        """Generate reasoning for why this slot was recommended"""
        reasons = []
        
        if not slot.get("conflicts"):
            reasons.append("All attendees free")
        
        if slot.get("behavior_score", 0) > 80:
            reasons.append("Optimal time based on preferences")
        
        if slot.get("coordination_score", 0) > 80:
            reasons.append("High attendee alignment")
        
        if slot.get("timezone_fairness", 0) > 0.8:
            reasons.append("Fair across timezones")
        
        return ". ".join(reasons) if reasons else "Available time slot"
    
    def _calculate_slot_confidence(self, slot: Dict[str, Any]) -> float:
        """Calculate confidence score for a slot (0-100)"""
        score = slot.get("final_score", 50)
        conflicts = len(slot.get("conflicts", []))
        
        # High score + no conflicts = high confidence
        confidence = score * (1 - (conflicts * 0.1))
        
        return min(100.0, max(0.0, confidence))
    
    def _identify_tradeoffs(self, slots: List[Dict[str, Any]]) -> List[str]:
        """Identify tradeoffs in the recommendations"""
        tradeoffs = []
        
        if not slots:
            return tradeoffs
        
        top_slot = slots[0]
        
        if top_slot.get("conflicts"):
            tradeoffs.append("Top slot has minor conflicts that can be resolved")
        
        if top_slot.get("timezone_fairness", 1.0) < 0.7:
            tradeoffs.append("May be outside preferred hours for some timezones")
        
        return tradeoffs
    
    def _explain_ranking(
        self,
        slot: Dict[str, Any],
        top_slot: Dict[str, Any]
    ) -> str:
        """Explain why this slot wasn't ranked first"""
        score_diff = top_slot.get("final_score", 0) - slot.get("final_score", 0)
        
        if score_diff < 5:
            return "Very close alternative with similar quality"
        elif slot.get("conflicts"):
            return "Has more scheduling conflicts"
        elif slot.get("behavior_score", 0) < top_slot.get("behavior_score", 0):
            return "Less aligned with historical preferences"
        else:
            return "Lower overall score across multiple factors"
    
    def _check_approval_needed(
        self,
        slots: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> bool:
        """Determine if human approval is needed"""
        if not slots:
            return True
        
        top_slot = slots[0]
        
        # Require approval if:
        # - Low confidence
        if self._calculate_slot_confidence(top_slot) < 60:
            return True
        
        # - Hard conflicts present
        if any(c.get("type") == "hard" for c in top_slot.get("conflicts", [])):
            return True
        
        # - Explicitly marked as requiring approval
        if top_slot.get("requires_approval"):
            return True
        
        return False
    
    def _calculate_overall_confidence(self, slots: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence in recommendations"""
        if not slots:
            return 0.0
        
        top_confidence = self._calculate_slot_confidence(slots[0])
        
        # Boost confidence if we have multiple good options
        if len(slots) > 1 and slots[1].get("final_score", 0) > 70:
            top_confidence = min(100.0, top_confidence * 1.1)
        
        return top_confidence
    
    def _collect_agent_insights(
        self,
        calendar_result: AgentResult,
        behavior_result: AgentResult,
        coordination_result: AgentResult
    ) -> List[Dict[str, str]]:
        """Collect insights from all agents"""
        return [
            {
                "agent": "calendar",
                "insight": calendar_result.message
            },
            {
                "agent": "behavior",
                "insight": behavior_result.message
            },
            {
                "agent": "coordination",
                "insight": coordination_result.message
            }
        ]
    
    def _handle_agent_failure(
        self,
        agent_name: str,
        result: AgentResult
    ) -> AgentResult:
        """Handle failure of a sub-agent"""
        return self.create_result(
            data={},
            message=f"{agent_name} agent failed: {result.message}",
            errors=result.errors
        )
    
    def get_capabilities(self) -> List[str]:
        return [
            "Multi-signal ranking",
            "Confidence scoring",
            "Explainable decisions",
            "Human escalation",
            "Agent coordination"
        ]
    
    def get_description(self) -> str:
        return "Synthesizes all agent outputs into a ranked list of slot recommendations with explanations."
