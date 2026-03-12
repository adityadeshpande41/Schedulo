"""
External User Service
Handles detection and routing of external users across company boundaries
"""

from typing import Optional, Dict, Any
import re


class ExternalUserService:
    """
    Determines if a user is internal or external and routes accordingly
    """
    
    def __init__(self, internal_domain: str = "acme.com"):
        """
        Args:
            internal_domain: Your company's email domain
        """
        self.internal_domain = internal_domain
    
    def is_external_user(self, user_identifier: str) -> bool:
        """
        Check if user is external based on email domain
        
        Args:
            user_identifier: Email or user ID
            
        Returns:
            True if external, False if internal
        """
        # If it's an email address
        if "@" in user_identifier:
            domain = user_identifier.split("@")[1]
            return domain != self.internal_domain
        
        # If it's a user ID (u1, u2, etc.), it's internal
        return False
    
    def get_external_domain(self, email: str) -> Optional[str]:
        """
        Extract domain from external email
        
        Args:
            email: External user's email
            
        Returns:
            Domain name or None
        """
        if "@" not in email:
            return None
        
        return email.split("@")[1]
    
    def get_schedulo_endpoint(self, domain: str) -> str:
        """
        Get Schedulo API endpoint for external domain
        
        In production, this would:
        1. Check DNS for _schedulo._tcp.domain.com SRV record
        2. Fall back to https://schedulo.domain.com
        3. Support custom endpoint registry
        
        Args:
            domain: External company domain
            
        Returns:
            API endpoint URL
        """
        # For demo, use a mapping
        domain_endpoints = {
            "bigcorp.com": "https://schedulo.bigcorp.com/api",
            "startup.io": "https://schedulo.startup.io/api",
            "enterprise.net": "https://schedulo.enterprise.net/api",
        }
        
        # Default pattern
        return domain_endpoints.get(
            domain,
            f"https://schedulo.{domain}/api"
        )
    
    def parse_user_identifier(self, identifier: str) -> Dict[str, Any]:
        """
        Parse user identifier into structured format
        
        Args:
            identifier: User ID or email
            
        Returns:
            Dict with type, domain, and routing info
        """
        if "@" in identifier:
            local, domain = identifier.split("@", 1)
            is_external = domain != self.internal_domain
            
            return {
                "type": "external" if is_external else "internal",
                "identifier": identifier,
                "email": identifier,
                "domain": domain,
                "endpoint": self.get_schedulo_endpoint(domain) if is_external else None,
                "is_external": is_external
            }
        else:
            # Internal user ID
            return {
                "type": "internal",
                "identifier": identifier,
                "user_id": identifier,
                "domain": self.internal_domain,
                "endpoint": None,
                "is_external": False
            }
    
    def categorize_attendees(
        self,
        attendee_identifiers: list[str]
    ) -> Dict[str, list[Dict[str, Any]]]:
        """
        Categorize attendees into internal and external
        
        Args:
            attendee_identifiers: List of user IDs or emails
            
        Returns:
            Dict with 'internal' and 'external' lists
        """
        internal = []
        external = []
        
        for identifier in attendee_identifiers:
            parsed = self.parse_user_identifier(identifier)
            
            if parsed["is_external"]:
                external.append(parsed)
            else:
                internal.append(parsed)
        
        return {
            "internal": internal,
            "external": external,
            "has_external": len(external) > 0
        }
