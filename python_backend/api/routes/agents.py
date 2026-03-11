"""
Agent Activity API endpoints
Real-time agent status and activity monitoring
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import List
import json

from api.models.responses import AgentActivityResponse, AgentInfoResponse
from services.agent_service import AgentService

router = APIRouter()
agent_service = AgentService()


@router.get("/activity", response_model=List[AgentActivityResponse])
async def get_agent_activity():
    """
    Get current agent activity status
    
    Returns real-time status of all agents
    """
    try:
        activities = await agent_service.get_current_activity()
        return activities
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info", response_model=List[AgentInfoResponse])
async def get_agent_info():
    """
    Get information about all available agents
    
    Returns capabilities, descriptions, and metadata
    """
    try:
        agents_info = agent_service.get_agents_info()
        return agents_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/activity")
async def agent_activity_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time agent activity updates
    
    Clients can subscribe to receive live updates as agents execute
    """
    await websocket.accept()
    
    try:
        # Add client to active connections
        await agent_service.connect_websocket(websocket)
        
        # Keep connection alive and send updates
        while True:
            # Wait for messages from client (ping/pong)
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_text("pong")
            
    except WebSocketDisconnect:
        await agent_service.disconnect_websocket(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        await agent_service.disconnect_websocket(websocket)
