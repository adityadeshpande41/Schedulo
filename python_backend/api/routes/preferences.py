"""
User Preferences API endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import List

from api.models.responses import UserPreferenceResponse
from api.models.requests import UpdatePreferenceRequest
from services.preference_service import PreferenceService

router = APIRouter()
preference_service = PreferenceService()


@router.get("/{user_id}", response_model=List[UserPreferenceResponse])
async def get_user_preferences(user_id: str):
    """
    Get all preferences for a user
    """
    try:
        preferences = await preference_service.get_user_preferences(user_id)
        return preferences
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{preference_id}")
async def update_preference(
    preference_id: str,
    request: UpdatePreferenceRequest
):
    """
    Update a specific preference
    """
    try:
        updated = await preference_service.update_preference(
            preference_id,
            request.active,
            request.value
        )
        
        if not updated:
            raise HTTPException(status_code=404, detail="Preference not found")
        
        return {
            "preference_id": preference_id,
            "updated": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}")
async def create_preference(
    user_id: str,
    category: str,
    label: str,
    value: str,
    description: str = ""
):
    """
    Create a new preference for a user
    """
    try:
        preference = await preference_service.create_preference(
            user_id=user_id,
            category=category,
            label=label,
            value=value,
            description=description
        )
        
        return preference
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
