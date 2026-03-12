"""
Federation Client
Makes API calls to external Schedulo instances for cross-company scheduling
"""

from typing import List, Dict, Any, Optional
import httpx
from datetime import datetime


class FederationClient:
    """
    Client for communicating with external Schedulo instances
    Implements the Schedulo Federation Protocol
    """
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def request_availability(
        self,
        endpoint: str,
        user_email: str,
        time_windows: List[Dict[str, Any]],
        meeting_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Request availability from external Schedulo instance
        
        Args:
            endpoint: External Schedulo API endpoint
            user_email: External user's email
            time_windows: List of time windows to check
            meeting_context: Optional meeting details (duration, type, priority)
            
        Returns:
            Availability signals from external agent
        """
        try:
            response = await self.client.post(
                f"{endpoint}/federation/availability",
                json={
                    "user_email": user_email,
                    "time_windows": time_windows,
                    "meeting_context": meeting_context or {},
                    "protocol_version": "1.0"
                },
                headers={
                    "Content-Type": "application/json",
                    "X-Schedulo-Federation": "1.0"
                }
            )
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            # Fallback: Return all windows as "unknown"
            return {
                "status": "error",
                "error": str(e),
                "signals": [
                    {
                        "start_time": w["start_time"],
                        "end_time": w["end_time"],
                        "status": "unknown",
                        "confidence": 0.0,
                        "requires_manual_check": True
                    }
                    for w in time_windows
                ]
            }
    
    async def send_meeting_invitation(
        self,
        endpoint: str,
        user_email: str,
        meeting_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send meeting invitation to external user
        
        Args:
            endpoint: External Schedulo API endpoint
            user_email: External user's email
            meeting_details: Meeting information
            
        Returns:
            Confirmation response
        """
        try:
            response = await self.client.post(
                f"{endpoint}/federation/invite",
                json={
                    "user_email": user_email,
                    "meeting": meeting_details,
                    "protocol_version": "1.0"
                }
            )
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            return {
                "status": "error",
                "error": str(e),
                "fallback": "send_calendar_invite"
            }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
