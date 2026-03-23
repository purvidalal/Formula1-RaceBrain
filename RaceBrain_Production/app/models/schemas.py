"""
API Request/Response Models
Pydantic schemas for type validation
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


# ============================================================
# GAME ENDPOINTS
# ============================================================

class StartGameRequest(BaseModel):
    """Request to start a new game"""
    team: str = Field(..., description="Player's team name")
    difficulty: str = Field(default="normal", description="Game difficulty")


class StartGameResponse(BaseModel):
    """Response when starting a game"""
    race_id: str
    state: Dict[str, Any]
    player_team: str


class GameActionRequest(BaseModel):
    """Request to take a game action"""
    race_id: str
    team: str
    action: str


class GameActionResponse(BaseModel):
    """Response after taking an action"""
    race_id: str
    state: Dict[str, Any]
    finished: bool
    events: list = []


# ============================================================
# RECOMMENDATION ENDPOINTS
# ============================================================

class RecommendationRequest(BaseModel):
    """Request for AI recommendations"""
    lap: int = Field(..., ge=1, description="Current lap number")
    tyre_age: int = Field(..., ge=0, description="Tyre age in laps")
    compound: str = Field(..., description="Current compound")
    position: int = Field(..., ge=1, le=20, description="Current position")
    pitted: bool = Field(default=False, description="Already pitted?")


class RecommendationResponse(BaseModel):
    """AI recommendation response"""
    recommendations: Dict[str, Any]
    consensus: Optional[Dict[str, Any]] = None


# ============================================================
# CONFIG ENDPOINTS
# ============================================================

class TeamConfigResponse(BaseModel):
    """Team configuration data"""
    teams: Dict[str, list]
    compounds: list
    valid_actions: list
    track: Dict[str, Any]
