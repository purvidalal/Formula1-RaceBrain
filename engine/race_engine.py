"""
RaceBrain Race Engine
"""
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class TeamProfile:
    name: str
    base_pace: float = 1.0
    degradation_factor: float = 1.0
    pit_stop_time: float = 22.5
    ai_style: str = "balanced"


@dataclass
class CarState:
    team: str
    position: int
    compound: str
    tyre_age: int
    total_time: float = 0.0
    last_lap_time: float = 0.0
    pit_stops: int = 0
    pace_mode: str = "NORMAL"
    has_pitted: bool = False
    gap_ahead: Optional[float] = None
    gap_behind: Optional[float] = None
    
    def to_dict(self):
        return {
            "team": self.team,
            "position": self.position,
            "compound": self.compound,
            "tyre_age": self.tyre_age,
            "total_time": round(self.total_time, 3),
            "last_lap_time": round(self.last_lap_time, 3),
            "pit_stops": self.pit_stops,
            "pace_mode": self.pace_mode,
            "has_pitted": self.has_pitted,
            "gap_ahead": round(self.gap_ahead, 3) if self.gap_ahead else None,
            "gap_behind": round(self.gap_behind, 3) if self.gap_behind else None
        }


@dataclass
class RaceEvent:
    lap: int
    message: str
    event_type: str
    team: Optional[str] = None


class RaceState:
    def __init__(self, track_name: str = "Bahrain", total_laps: int = 57):
        self.track_name = track_name
        self.total_laps = total_laps
        self.current_lap = 1
        self.cars: List[CarState] = []
        self.events: List[RaceEvent] = []
        self.finished = False
        self.team_profiles: Dict[str, TeamProfile] = {}
        
    def add_car(self, car: CarState):
        self.cars.append(car)
        self.cars.sort(key=lambda x: x.position)
    
    def add_event(self, message: str, event_type: str, team: Optional[str] = None):
        event = RaceEvent(self.current_lap, message, event_type, team)
        self.events.append(event)
        return event
    
    def update_positions(self):
        self.cars.sort(key=lambda x: x.total_time)
        for i, car in enumerate(self.cars, 1):
            old_pos = car.position
            car.position = i
            if old_pos != i and self.current_lap > 1:
                if i < old_pos:
                    self.add_event(f"{car.team} → P{i}", "position_gain", car.team)
    
    def update_gaps(self):
        for i, car in enumerate(self.cars):
            if i > 0:
                car.gap_ahead = car.total_time - self.cars[i-1].total_time
            else:
                car.gap_ahead = None
            if i < len(self.cars) - 1:
                car.gap_behind = self.cars[i+1].total_time - car.total_time
            else:
                car.gap_behind = None
    
    def get_car(self, team: str) -> Optional[CarState]:
        for car in self.cars:
            if car.team == team:
                return car
        return None
    
    def advance_lap(self):
        self.current_lap += 1
        if self.current_lap > self.total_laps:
            self.finished = True
    
    def to_dict(self):
        return {
            "track": self.track_name,
            "total_laps": self.total_laps,
            "current_lap": self.current_lap,
            "finished": self.finished,
            "cars": [car.to_dict() for car in self.cars],
            "events": [
                {"lap": e.lap, "message": e.message, "type": e.event_type, "team": e.team}
                for e in self.events[-10:]
            ]
        }


DEFAULT_TEAMS = {
    "Red Bull": TeamProfile("Red Bull", 0.98, 0.95, 21.8, "aggressive"),
    "Ferrari": TeamProfile("Ferrari", 0.99, 1.0, 22.3, "balanced"),
    "Mercedes": TeamProfile("Mercedes", 1.0, 1.05, 22.8, "conservative"),
    "McLaren": TeamProfile("McLaren", 1.01, 1.02, 23.0, "qlearning"),
    "Aston Martin": TeamProfile("Aston Martin", 1.02, 1.08, 23.5, "heuristic")
}


def create_default_race(player_team: str = "Ferrari") -> RaceState:
    race = RaceState()
    teams = ["Red Bull", "Ferrari", "Mercedes", "McLaren", "Aston Martin"]
    compounds = ["SOFT", "MEDIUM", "MEDIUM", "SOFT", "MEDIUM"]
    
    for i, team in enumerate(teams, 1):
        car = CarState(team=team, position=i, compound=compounds[i-1], tyre_age=1)
        race.add_car(car)
        race.team_profiles[team] = DEFAULT_TEAMS[team]
    
    race.add_event(f"🏁 Race Start! {player_team} is your team.", "race_start", player_team)
    return race
