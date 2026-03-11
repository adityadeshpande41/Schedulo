"""
LangGraph Orchestrator
State-based multi-agent orchestration with conditional routing
"""

from typing import TypedDict, Annotated, Sequence, Literal
from datetime import datetime
import operator

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from .personal_agent import PersonalAgent
from .multi_agent_coordinator import MultiAgentCoordinator
from .edge_case_handler import EdgeCaseHandler
from .openai_integration import OpenAIAssistant
from .time_window_generator import TimeWindowGenerator


class SchedulingState(TypedDict):
    """
    State that flows through the agent graph
    
    This is the shared state that all agents can read/write
    """
    # Input
    request: str  # Natural language request
    attendee_ids: list[str]
    duration: int
    meeting_context: dict
    
    # Agent outputs
    parsed_request: dict
    personal_agent_signals: dict  # user_id -> availability signals
    consensus_slots: list[dict]
    edge_cases_handled: list[str]
    ranked_recommendations: list[dict]
    
    # Decision tracking
    confidence: float
    escalation_needed: bool
    escalation_reason: str
    
    # Messages (for LangChain compatibility)
    messages: Annotated[Sequence[BaseMessage], operator.add]
    
    # Workflow control
    next_step: str
    iteration: int


class LangGraphOrchestrator:
    """
    LangGraph-based orchestrator for multi-agent scheduling
    
    Workflow:
    1. Parse Request (OpenAI)
    2. Personal Agents (Parallel)
    3. Coordination
    4. Edge Case Handling
    5. Ranking & Explanation
    6. Decision (Escalate or Complete)
    """
    
    def __init__(self):
        self.memory = MemorySaver()  # For checkpointing
        self.ai_assistant = OpenAIAssistant("orchestrator")
        self.time_generator = TimeWindowGenerator()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the agent workflow graph
        
        Graph structure:
        START → parse_request → personal_agents → coordinate → 
        edge_cases → rank → should_escalate? → [escalate | complete] → END
        """
        workflow = StateGraph(SchedulingState)
        
        # Add nodes (agent functions)
        workflow.add_node("parse_request", self.parse_request_node)
        workflow.add_node("personal_agents", self.personal_agents_node)
        workflow.add_node("coordinate", self.coordinate_node)
        workflow.add_node("edge_cases", self.edge_cases_node)
        workflow.add_node("rank", self.rank_node)
        workflow.add_node("escalate", self.escalate_node)
        workflow.add_node("complete", self.complete_node)
        
        # Define edges (workflow flow)
        workflow.set_entry_point("parse_request")
        
        workflow.add_edge("parse_request", "personal_agents")
        workflow.add_edge("personal_agents", "coordinate")
        workflow.add_edge("coordinate", "edge_cases")
        workflow.add_edge("edge_cases", "rank")
        
        # Conditional routing: escalate or complete?
        workflow.add_conditional_edges(
            "rank",
            self.should_escalate,
            {
                "escalate": "escalate",
                "complete": "complete"
            }
        )
        
        workflow.add_edge("escalate", END)
        workflow.add_edge("complete", END)
        
        return workflow.compile(checkpointer=self.memory)
    
    async def execute(self, request: str, attendee_ids: list[str], 
                     duration: int, meeting_context: dict) -> dict:
        """
        Execute the scheduling workflow
        
        Returns final state with recommendations or escalation
        """
        initial_state = SchedulingState(
            request=request,
            attendee_ids=attendee_ids,
            duration=duration,
            meeting_context=meeting_context,
            parsed_request={},
            personal_agent_signals={},
            consensus_slots=[],
            edge_cases_handled=[],
            ranked_recommendations=[],
            confidence=0.0,
            escalation_needed=False,
            escalation_reason="",
            messages=[HumanMessage(content=request)],
            next_step="parse_request",
            iteration=0
        )
        
        # Run the graph
        config = {"configurable": {"thread_id": "scheduling_session"}}
        final_state = await self.graph.ainvoke(initial_state, config)
        
        return final_state
    
    # ==================== AGENT NODES ====================
    
    async def parse_request_node(self, state: SchedulingState) -> SchedulingState:
        """
        Node 1: Parse natural language request using OpenAI
        
        Input: "Schedule 30-min sync with Sarah next week, afternoon"
        Output: {attendees: ["Sarah"], duration: 30, time_preference: "afternoon"}
        """
        print("🔍 [LangGraph] Parsing request...")
        
        parsed = await self.ai_assistant.parse_natural_language_request(
            state["request"]
        )
        
        state["parsed_request"] = parsed
        state["messages"].append(
            AIMessage(content=f"Parsed request: {parsed}")
        )
        state["iteration"] += 1
        
        return state
    
    async def personal_agents_node(self, state: SchedulingState) -> SchedulingState:
        """
        Node 2: Execute personal agents in parallel
        
        Each agent analyzes independently and returns availability signals
        """
        print(f"🤖 [LangGraph] Running {len(state['attendee_ids'])} personal agents...")
        
        # Generate candidate time windows from parsed request
        time_windows = self.time_generator.generate_windows(
            parsed_request=state["parsed_request"],
            duration=state["duration"],
            num_slots=20  # Generate 20 candidate slots
        )
        
        print(f"📅 [LangGraph] Generated {len(time_windows)} candidate time windows")
        
        signals = {}
        
        # Execute agents in parallel (in production, use asyncio.gather)
        for user_id in state["attendee_ids"]:
            agent = PersonalAgent(user_id)
            
            result = await agent.execute({
                "request_type": "availability_check",
                "time_windows": time_windows,
                "meeting_context": state["meeting_context"]
            })
            
            signals[user_id] = result.data.get("availability_signals", [])
        
        state["personal_agent_signals"] = signals
        state["messages"].append(
            AIMessage(content=f"Collected signals from {len(signals)} agents")
        )
        state["iteration"] += 1
        
        return state
    
    async def coordinate_node(self, state: SchedulingState) -> SchedulingState:
        """
        Node 3: Coordinate across agents to find consensus
        """
        print("🤝 [LangGraph] Coordinating agents...")
        
        # Get all agent signals
        all_signals = state["personal_agent_signals"]
        
        # Find slots where ALL agents are available or flexible
        consensus_slots = []
        
        # Get the first agent's signals to iterate through
        if not all_signals:
            state["consensus_slots"] = []
            state["confidence"] = 0.0
            return state
        
        first_user_signals = list(all_signals.values())[0]
        
        for i, signal_dict in enumerate(first_user_signals):
            # Check if this slot works for ALL attendees
            slot_works = True
            min_confidence = 1.0
            total_flexibility = 0.0
            
            for user_id, user_signals in all_signals.items():
                if i >= len(user_signals):
                    slot_works = False
                    break
                
                user_signal = user_signals[i]
                status = user_signal.get("status")
                confidence = user_signal.get("confidence", 0)
                flexibility = user_signal.get("flexibility", 0)
                
                # Slot doesn't work if anyone is busy (and not flexible)
                if status == "busy":
                    slot_works = False
                    break
                
                # Track minimum confidence and total flexibility
                min_confidence = min(min_confidence, confidence)
                total_flexibility += flexibility
            
            if slot_works:
                # Calculate overall score
                avg_flexibility = total_flexibility / len(all_signals)
                overall_confidence = min_confidence * 0.7 + avg_flexibility * 0.3
                
                consensus_slots.append({
                    "start_time": signal_dict["start_time"],
                    "end_time": signal_dict["end_time"],
                    "confidence": overall_confidence,
                    "attendee_count": len(all_signals),
                    "min_confidence": min_confidence,
                    "avg_flexibility": avg_flexibility
                })
        
        # Sort by confidence
        consensus_slots.sort(key=lambda x: x["confidence"], reverse=True)
        
        state["consensus_slots"] = consensus_slots
        state["confidence"] = consensus_slots[0]["confidence"] if consensus_slots else 0.0
        state["messages"].append(
            AIMessage(content=f"Found {len(consensus_slots)} consensus slots")
        )
        state["iteration"] += 1
        
        print(f"✅ [LangGraph] Found {len(consensus_slots)} consensus slots")
        
        return state
    
    async def edge_cases_node(self, state: SchedulingState) -> SchedulingState:
        """
        Node 4: Handle edge cases
        """
        print("⚠️  [LangGraph] Handling edge cases...")
        
        handler = EdgeCaseHandler()
        edge_cases = []
        
        # Check for timezone conflicts
        # TODO: Get actual timezones from user data
        attendee_timezones = {uid: "UTC" for uid in state["attendee_ids"]}
        
        fair_slots = handler.handle_timezone_conflicts(
            state["consensus_slots"],
            attendee_timezones
        )
        
        if len(fair_slots) < len(state["consensus_slots"]):
            edge_cases.append("timezone_conflicts")
        
        state["consensus_slots"] = fair_slots
        state["edge_cases_handled"] = edge_cases
        state["messages"].append(
            AIMessage(content=f"Handled {len(edge_cases)} edge cases")
        )
        state["iteration"] += 1
        
        return state
    
    async def rank_node(self, state: SchedulingState) -> SchedulingState:
        """
        Node 5: Rank slots and generate explanations
        """
        print("📊 [LangGraph] Ranking recommendations...")
        
        # Sort by confidence
        ranked = sorted(
            state["consensus_slots"],
            key=lambda s: s.get("confidence", 0),
            reverse=True
        )
        
        # Generate explanations for top 3
        for i, slot in enumerate(ranked[:3]):
            explanation = await self.ai_assistant.generate_explanation(
                recommendation=slot,
                context=state["meeting_context"]
            )
            slot["explanation"] = explanation
            slot["rank"] = i + 1
            slot["recommended"] = (i == 0)
        
        state["ranked_recommendations"] = ranked
        state["messages"].append(
            AIMessage(content=f"Ranked {len(ranked)} recommendations")
        )
        state["iteration"] += 1
        
        return state
    
    async def escalate_node(self, state: SchedulingState) -> SchedulingState:
        """
        Node 6a: Escalate to human
        """
        print("🚨 [LangGraph] Escalating to human...")
        
        state["escalation_needed"] = True
        state["messages"].append(
            AIMessage(content=f"Escalating: {state['escalation_reason']}")
        )
        
        return state
    
    async def complete_node(self, state: SchedulingState) -> SchedulingState:
        """
        Node 6b: Complete successfully
        """
        print("✅ [LangGraph] Workflow complete!")
        
        state["messages"].append(
            AIMessage(content="Scheduling recommendations ready")
        )
        
        return state
    
    # ==================== CONDITIONAL ROUTING ====================
    
    def should_escalate(self, state: SchedulingState) -> Literal["escalate", "complete"]:
        """
        Conditional edge: Decide whether to escalate or complete
        
        Escalate if:
        - No recommendations found
        - Low confidence (< 60%)
        - Requires approval
        - Edge cases unresolved
        """
        # No recommendations
        if not state["ranked_recommendations"]:
            state["escalation_reason"] = "No suitable time slots found"
            return "escalate"
        
        top_slot = state["ranked_recommendations"][0]
        
        # Low confidence
        if top_slot.get("confidence", 0) < 0.6:
            state["escalation_reason"] = f"Low confidence ({top_slot.get('confidence', 0):.0%})"
            return "escalate"
        
        # Requires approval
        if top_slot.get("requires_approval"):
            state["escalation_reason"] = "Requires rescheduling existing meetings"
            return "escalate"
        
        # Unresolved edge cases
        critical_edge_cases = ["all_busy", "conflicting_priorities"]
        if any(ec in state["edge_cases_handled"] for ec in critical_edge_cases):
            state["escalation_reason"] = "Critical edge cases detected"
            return "escalate"
        
        return "complete"
    
    # ==================== UTILITIES ====================
    
    def visualize_graph(self, output_path: str = "scheduling_graph.png"):
        """
        Visualize the agent workflow graph
        
        Requires: pip install pygraphviz
        """
        try:
            from IPython.display import Image, display
            display(Image(self.graph.get_graph().draw_mermaid_png()))
        except Exception as e:
            print(f"Could not visualize graph: {e}")
            print("Install pygraphviz: pip install pygraphviz")
    
    def get_graph_structure(self) -> dict:
        """Get graph structure as dictionary"""
        return {
            "nodes": [
                "parse_request",
                "personal_agents",
                "coordinate",
                "edge_cases",
                "rank",
                "escalate",
                "complete"
            ],
            "edges": [
                ("parse_request", "personal_agents"),
                ("personal_agents", "coordinate"),
                ("coordinate", "edge_cases"),
                ("edge_cases", "rank"),
                ("rank", "escalate (conditional)"),
                ("rank", "complete (conditional)"),
            ],
            "conditional_edges": {
                "rank": {
                    "condition": "should_escalate",
                    "routes": ["escalate", "complete"]
                }
            }
        }


# ==================== EXAMPLE USAGE ====================

async def example_usage():
    """Example of using LangGraph orchestrator"""
    
    orchestrator = LangGraphOrchestrator()
    
    # Execute scheduling workflow
    result = await orchestrator.execute(
        request="Schedule a 30-minute sync with Sarah and Marcus next week, preferably afternoon",
        attendee_ids=["u1", "u2", "u3"],
        duration=30,
        meeting_context={
            "type": "team_sync",
            "priority": "medium"
        }
    )
    
    # Check result
    if result["escalation_needed"]:
        print(f"⚠️  Escalation needed: {result['escalation_reason']}")
    else:
        print(f"✅ Found {len(result['ranked_recommendations'])} recommendations")
        print(f"Top slot: {result['ranked_recommendations'][0]}")
    
    # View workflow messages
    for msg in result["messages"]:
        print(f"{msg.type}: {msg.content}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
