"""
Game Routes
Endpoints for the interactive F1 strategy game
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    StartGameRequest, 
    StartGameResponse,
    GameActionRequest,
    GameActionResponse
)
from app.services.game_service import game_service
from app.services.recommendation_service import recommendation_service

router = APIRouter(prefix="/api/game", tags=["game"])


@router.post("/start", response_model=StartGameResponse)
async def start_game(request: StartGameRequest):
    """
    Start a new race
    
    - **team**: Player's team name (e.g., "Ferrari")
    - **difficulty**: Game difficulty (easy/normal/hard)
    
    Returns race_id and initial state
    """
    try:
        race_id, race = game_service.create_race(
            player_team=request.team,
            difficulty=request.difficulty
        )
        
        return StartGameResponse(
            race_id=race_id,
            state=race.to_dict(),
            player_team=request.team
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create race: {str(e)}")


@router.post("/action", response_model=GameActionResponse)
async def take_action(request: GameActionRequest):
    """
    Execute a race action
    
    - **race_id**: Race identifier
    - **team**: Player's team
    - **action**: Action to take (STAY_OUT, PIT_SOFT, PIT_MEDIUM, PIT_HARD)
    
    Returns updated race state
    """
    try:
        race = game_service.execute_action(
            race_id=request.race_id,
            player_team=request.team,
            action=request.action
        )
        
        return GameActionResponse(
            race_id=request.race_id,
            state=race.to_dict(),
            finished=race.finished,
            events=[]  # TODO: Add event tracking
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Action failed: {str(e)}")


@router.get("/state/{race_id}")
async def get_race_state(race_id: str):
    """Get current race state"""
    race = game_service.get_race(race_id)
    
    if not race:
        raise HTTPException(status_code=404, detail=f"Race '{race_id}' not found")
    
    return {
        "race_id": race_id,
        "state": race.to_dict(),
        "finished": race.finished
    }


@router.get("/recommendations/{race_id}/{team}")
async def get_recommendations(race_id: str, team: str):
    """Get AI recommendations"""
    try:
        print(f"\n{'='*60}")
        print(f"🔍 GET RECOMMENDATIONS REQUEST")
        print(f"Race ID: {race_id}")
        print(f"Team: {team}")
        
        race_state = game_service.get_race_state(race_id)
        print(f"✅ Got race state: {type(race_state)}")
        print(f"Race state keys: {race_state.keys() if isinstance(race_state, dict) else 'NOT A DICT'}")
        
        recommendations = recommendation_service.get_recommendations(race_state, team)
        print(f"✅ Got recommendations: {type(recommendations)}")
        print(f"{'='*60}\n")
        
        return recommendations
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ ERROR IN GET_RECOMMENDATIONS:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")
        raise
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


@router.delete("/{race_id}")
async def delete_race(race_id: str):
    """Delete a race"""
    deleted = game_service.delete_race(race_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Race '{race_id}' not found")
    
    return {"message": "Race deleted", "race_id": race_id}


@router.get("/stats")
async def get_stats():
    """Get game service statistics"""
    return game_service.get_stats()
