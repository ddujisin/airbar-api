from fastapi import APIRouter, Depends, HTTPException
from ..utils.guest_profile import guest_profile_manager
from ..middleware.session_middleware import get_current_session
from typing import List, Dict

router = APIRouter()

@router.get("/profile")
async def get_guest_profile(session=Depends(get_current_session)) -> Dict:
    """Get the current guest's profile and order history."""
    try:
        profile = await guest_profile_manager.get_guest_profile(
            session["reservation_id"]
        )
        return profile
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/recommendations")
async def get_recommendations(
    limit: int = 5,
    session=Depends(get_current_session)
) -> List[Dict]:
    """Get personalized item recommendations for the current guest."""
    try:
        recommendations = await guest_profile_manager.get_guest_recommendations(
            session["reservation_id"],
            limit
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
