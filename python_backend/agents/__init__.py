"""
Schedulo AI Agent System
Multi-agent architecture for intelligent meeting scheduling
"""

from .base_agent import BaseAgent, AgentStatus, AgentResult
from .personal_agent import PersonalAgent, AvailabilitySignal
from .ml_behavior_model import BehaviorLearningModel
from .openai_integration import OpenAIAssistant
from .multi_agent_coordinator import MultiAgentCoordinator
from .edge_case_handler import EdgeCaseHandler
from .langgraph_orchestrator import LangGraphOrchestrator, SchedulingState

# Legacy agents (for backward compatibility)
from .calendar_agent import CalendarAgent
from .behavior_agent import BehaviorAgent
from .coordination_agent import CoordinationAgent
from .orchestrator_agent import OrchestratorAgent

__all__ = [
    # Core
    "BaseAgent",
    "AgentStatus",
    "AgentResult",
    
    # New Multi-Agent System
    "LangGraphOrchestrator",
    "SchedulingState",
    "PersonalAgent",
    "AvailabilitySignal",
    "BehaviorLearningModel",
    "OpenAIAssistant",
    "MultiAgentCoordinator",
    "EdgeCaseHandler",
    
    # Legacy (for backward compatibility)
    "CalendarAgent",
    "BehaviorAgent",
    "CoordinationAgent",
    "OrchestratorAgent",
]
