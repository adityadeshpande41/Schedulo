"""
Agent Service
Business logic for agent operations and WebSocket management
"""

from typing import List, Set
from datetime import datetime
from fastapi import WebSocket

from api.models.responses import AgentActivityResponse, AgentInfoResponse
from agents import CalendarAgent, BehaviorAgent, CoordinationAgent, OrchestratorAgent


class AgentService:
    """Service for handling agent operations"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.calendar_agent = CalendarAgent()
        self.behavior_agent = BehaviorAgent()
        self.coordination_agent = CoordinationAgent()
        self.orchestrator_agent = OrchestratorAgent()
    
    async def get_current_activity(self) -> List[AgentActivityResponse]:
        """Get current activity status of all agents"""
        
        # TODO: Get real-time status from agents
        return self._get_mock_activity()
    
    def get_agents_info(self) -> List[AgentInfoResponse]:
        """Get information about all agents"""
        
        agents = [
            self.calendar_agent,
            self.behavior_agent,
            self.coordination_agent,
            self.orchestrator_agent
        ]
        
        return [
            AgentInfoResponse(
                type=agent.agent_type,
                name=agent.name,
                description=agent.get_description(),
                capabilities=agent.get_capabilities(),
                icon=self._get_agent_icon(agent.agent_type),
                color=self._get_agent_color(agent.agent_type)
            )
            for agent in agents
        ]
    
    async def connect_websocket(self, websocket: WebSocket):
        """Add WebSocket connection"""
        self.active_connections.add(websocket)
    
    async def disconnect_websocket(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.discard(websocket)
    
    async def broadcast_activity(self, activity: AgentActivityResponse):
        """Broadcast activity update to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(activity.model_dump())
            except Exception as e:
                print(f"Error broadcasting to client: {e}")
                await self.disconnect_websocket(connection)
    
    def _get_mock_activity(self) -> List[AgentActivityResponse]:
        """Mock agent activity"""
        return [
            AgentActivityResponse(
                id="a1",
                agent_type="calendar",
                status="complete",
                message="Scanned 4 calendars across 3 timezones",
                timestamp=datetime.utcnow(),
                progress=100
            )
        ]
    
    def _get_agent_icon(self, agent_type: str) -> str:
        """Get icon for agent type"""
        icons = {
            "calendar": "calendar-search",
            "behavior": "brain",
            "coordination": "users",
            "orchestrator": "cpu"
        }
        return icons.get(agent_type, "settings")
    
    def _get_agent_color(self, agent_type: str) -> str:
        """Get color gradient for agent type"""
        colors = {
            "calendar": "from-blue-500 to-cyan-500",
            "behavior": "from-purple-500 to-pink-500",
            "coordination": "from-amber-500 to-orange-500",
            "orchestrator": "from-emerald-500 to-teal-500"
        }
        return colors.get(agent_type, "from-gray-500 to-gray-600")
