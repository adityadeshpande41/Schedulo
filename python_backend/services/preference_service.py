"""
Preference Service
Business logic for user preferences
"""

from typing import List, Optional

from api.models.responses import UserPreferenceResponse


class PreferenceService:
    """Service for handling user preferences"""
    
    async def get_user_preferences(
        self,
        user_id: str
    ) -> List[UserPreferenceResponse]:
        """Get all preferences for a user"""
        
        # TODO: Query database
        return self._get_mock_preferences(user_id)
    
    async def update_preference(
        self,
        preference_id: str,
        active: Optional[bool],
        value: Optional[str]
    ) -> bool:
        """Update a preference"""
        
        # TODO: Update database
        return True
    
    async def create_preference(
        self,
        user_id: str,
        category: str,
        label: str,
        value: str,
        description: str
    ) -> UserPreferenceResponse:
        """Create a new preference"""
        
        # TODO: Insert into database
        return UserPreferenceResponse(
            id="p_new",
            user_id=user_id,
            category=category,
            label=label,
            description=description,
            value=value,
            icon="settings",
            active=True
        )
    
    def _get_mock_preferences(
        self,
        user_id: str
    ) -> List[UserPreferenceResponse]:
        """Mock preferences data"""
        
        return [
            UserPreferenceResponse(
                id="p1",
                user_id=user_id,
                category="time",
                label="Prefers Afternoons",
                description="Scheduling meetings after 1 PM when possible",
                value="afternoon",
                icon="sun",
                active=True
            ),
            UserPreferenceResponse(
                id="p2",
                user_id=user_id,
                category="behavior",
                label="No Back-to-Back",
                description="Prefers 15-minute buffer between meetings",
                value="buffer_15",
                icon="clock",
                active=True
            )
        ]
