"""
Game Service
Manages game state, validation, and race lifecycle
"""

import uuid
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

from config.settings import VALID_ACTIONS, TEAM_DRIVERS, MAX_ACTIVE_RACES, RACE_CLEANUP_HOURS


class GameService:
    """Professional game state management"""
    
    def __init__(self):
        self.active_races: Dict[str, any] = {}  # race_id -> RaceState
        self.metadata: Dict[str, dict] = {}     # race_id -> metadata
    
    def create_race(
        self, 
        player_team: str,
        difficulty: str = "normal"
    ) -> Tuple[str, any]:
        """
        Create a new race with validation
        
        Args:
            player_team: Team for the player
            difficulty: Game difficulty level
            
        Returns:
            (race_id, race_state)
            
        Raises:
            ValueError: If validation fails
        """
        # Validate team
        if player_team not in TEAM_DRIVERS:
            valid_teams = list(TEAM_DRIVERS.keys())
            raise ValueError(
                f"Invalid team '{player_team}'. "
                f"Must be one of: {', '.join(valid_teams)}"
            )
        
        # Cleanup old races if needed
        if len(self.active_races) >= MAX_ACTIVE_RACES:
            self._cleanup_old_races()
            if len(self.active_races) >= MAX_ACTIVE_RACES:
                raise ValueError(
                    "Server at capacity. Please try again in a moment."
                )
        
        # Import here to avoid circular dependency
        from engine.race_engine import create_default_race
        
        # Create race
        race_id = str(uuid.uuid4())
        race = create_default_race(player_team)
        
        # Store race and metadata
        self.active_races[race_id] = race
        self.metadata[race_id] = {
            "player_team": player_team,
            "difficulty": difficulty,
            "created_at": datetime.now(),
            "last_action": datetime.now(),
        }
        
        return race_id, race
    
    def get_race(self, race_id: str) -> Optional[any]:
        """Get race by ID"""
        return self.active_races.get(race_id)
    
    def validate_action(
        self,
        race_id: str,
        team: str,
        action: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a game action
        
        Returns:
            (is_valid, error_message)
        """
        # Check race exists
        if race_id not in self.active_races:
            return False, f"Race '{race_id}' not found"
        
        race = self.active_races[race_id]
        meta = self.metadata[race_id]
        
        # Check team ownership
        if team != meta["player_team"]:
            return False, f"Team '{team}' is not the player in this race"
        
        # Check race not finished
        if race.finished:
            return False, "Race has already finished"
        
        # Check valid action
        if action not in VALID_ACTIONS:
            valid = ", ".join(sorted(VALID_ACTIONS))
            return False, f"Invalid action '{action}'. Valid: {valid}"
        
        # Check if can pit (not if already pitted)
        car = race.get_car(team)
        if car and car.has_pitted and action.startswith("PIT_"):
            return False, "Cannot pit again - already completed pit stop this race"
        
        return True, None
    
    def execute_action(
        self,
        race_id: str,
        player_team: str,
        action: str
    ) -> any:
        """
        Execute a validated action
        
        Args:
            race_id: Race identifier
            player_team: Player's team
            action: Action to execute
            
        Returns:
            Updated race state
            
        Raises:
            ValueError: If validation fails
        """
        # Validate
        is_valid, error = self.validate_action(race_id, player_team, action)
        if not is_valid:
            raise ValueError(error)
        
        race = self.active_races[race_id]
        
        # Import simulation
        from engine.lap_simulator import simulate_lap, get_ai_recommendation
        
        # Get AI actions
        ai_actions = {}
        for car in race.cars:
            if car.team != player_team:
                profile = race.team_profiles[car.team]
                ai_action = get_ai_recommendation(car, race, profile.ai_style)
                ai_actions[car.team] = ai_action
        
        # Simulate lap
        player_action = {"team": player_team, "action": action}
        race = simulate_lap(race, player_action, ai_actions)
        
        # Update metadata
        self.metadata[race_id]["last_action"] = datetime.now()
        
        return race
    
    def delete_race(self, race_id: str) -> bool:
        """Delete a race"""
        if race_id in self.active_races:
            del self.active_races[race_id]
            del self.metadata[race_id]
            return True
        return False
    
    def get_stats(self) -> dict:
        """Get service statistics"""
        return {
            "active_races": len(self.active_races),
            "finished_races": sum(
                1 for r in self.active_races.values() if r.finished
            ),
        }
    
    def _cleanup_old_races(self):
        """Remove stale races"""
        now = datetime.now()
        cutoff = timedelta(hours=RACE_CLEANUP_HOURS)
        to_delete = []
        
        for race_id, meta in self.metadata.items():
            race = self.active_races[race_id]
            
            # Delete finished races
            if race.finished:
                to_delete.append(race_id)
            # Delete inactive races
            elif (now - meta["last_action"]) > cutoff:
                to_delete.append(race_id)
        
        for race_id in to_delete:
            self.delete_race(race_id)
        
        return len(to_delete)


    def get_race_state(self, race_id: str):
        """Get race state - compatibility wrapper"""
        race = self.get_race(race_id)
        if not race:
            raise ValueError(f"Race {race_id} not found")
        # Convert race object to dict for frontend
        if hasattr(race, 'to_dict'):
            return race.to_dict()
        return race
    

# Global service instance
game_service = GameService()
