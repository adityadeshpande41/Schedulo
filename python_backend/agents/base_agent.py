"""
Base Agent Class
Foundation for all Schedulo AI agents
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    SCANNING = "scanning"
    ANALYZING = "analyzing"
    NEGOTIATING = "negotiating"
    RANKING = "ranking"
    COMPLETE = "complete"
    WAITING = "waiting"
    ERROR = "error"


@dataclass
class AgentResult:
    """Standard result format for all agents"""
    agent_type: str
    status: AgentStatus
    data: Any
    message: str
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


class BaseAgent(ABC):
    """
    Abstract base class for all Schedulo agents
    Provides common functionality and interface
    """
    
    def __init__(self, agent_type: str, name: str):
        self.agent_type = agent_type
        self.name = name
        self.status = AgentStatus.IDLE
        self.last_result: Optional[AgentResult] = None
        
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Execute the agent's primary function
        
        Args:
            context: Execution context with request data and dependencies
            
        Returns:
            AgentResult with execution outcome
        """
        pass
    
    def update_status(self, status: AgentStatus, message: str = ""):
        """Update agent status"""
        self.status = status
        if message:
            print(f"[{self.name}] {message}")
    
    def create_result(
        self,
        data: Any,
        message: str,
        confidence: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
        errors: Optional[List[str]] = None
    ) -> AgentResult:
        """Create a standardized result object"""
        result = AgentResult(
            agent_type=self.agent_type,
            status=self.status,
            data=data,
            message=message,
            confidence=confidence,
            metadata=metadata or {},
            errors=errors or []
        )
        self.last_result = result
        return result
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return []
    
    def get_description(self) -> str:
        """Return agent description"""
        return ""
