"""
API Routes
General API endpoints (recommendations, config)
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import RecommendationRequest, TeamConfigResponse
from app.services.recommendation_service import recommendation_service
from config.settings import TEAM_DRIVERS, COMPOUNDS, VALID_ACTIONS, TRACK_CONFIG

router = APIRouter(prefix="/api", tags=["api"])


@router.post("/recommend")
async def get_recommendations(request: RecommendationRequest):
    """
    Get AI recommendations for a given race state
    
    - **lap**: Current lap number
    - **tyre_age**: Tyre age in laps
    - **compound**: Current compound (SOFT/MEDIUM/HARD)
    - **position**: Current position (1-20)
    - **pitted**: Already completed pit stop?
    
    Returns recommendations from all 5 agents plus consensus
    """
    try:
        recommendations = recommendation_service.get_recommendations(
            lap=request.lap,
            tyre_age=request.tyre_age,
            compound=request.compound,
            position=request.position,
            pitted=request.pitted
        )
        
        return recommendations
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Recommendation failed: {str(e)}"
        )


@router.get("/config/teams", response_model=TeamConfigResponse)
async def get_team_config():
    """
    Get team and game configuration
    
    Returns:
    - teams: Team -> [Driver1, Driver2]
    - compounds: Available tyre compounds
    - valid_actions: Valid game actions
    - track: Track configuration
    """
    return TeamConfigResponse(
        teams=TEAM_DRIVERS,
        compounds=COMPOUNDS,
        valid_actions=list(VALID_ACTIONS),
        track=TRACK_CONFIG
    )
