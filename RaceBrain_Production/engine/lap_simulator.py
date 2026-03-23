"""
Lap Simulator
"""
import random
from typing import Dict

BASE_LAP_TIME = 95.0

COMPOUND_PACE = {"SOFT": 0.0, "MEDIUM": 0.7, "HARD": 1.4}
COMPOUND_DEGRADATION = {"SOFT": 0.12, "MEDIUM": 0.085, "HARD": 0.06}


def calculate_lap_time(car, team_profile, traffic=0.0):
    lap_time = BASE_LAP_TIME * team_profile.base_pace
    lap_time += COMPOUND_PACE[car.compound]
    degradation = COMPOUND_DEGRADATION[car.compound] * team_profile.degradation_factor * car.tyre_age
    lap_time += degradation + traffic + random.uniform(-0.4, 0.4)
    return lap_time


def simulate_pit_stop(car, new_compound, team_profile):
    pit_time = team_profile.pit_stop_time + random.uniform(-0.5, 0.5)
    car.compound = new_compound
    car.tyre_age = 0
    car.pit_stops += 1
    car.has_pitted = True
    return pit_time


def simulate_lap(race, player_action, ai_actions):
    all_actions = {**ai_actions, player_action["team"]: player_action["action"]}
    
    for car in race.cars:
        team_profile = race.team_profiles[car.team]
        action = all_actions.get(car.team, "STAY_OUT")
        
        if action.startswith("PIT_"):
            compound = action.split("_")[1]
            pit_time = simulate_pit_stop(car, compound, team_profile)
            lap_time = calculate_lap_time(car, team_profile) + pit_time
            race.add_event(f"{car.team} pits for {compound}", "pit_stop", car.team)
        else:
            lap_time = calculate_lap_time(car, team_profile)
        
        car.last_lap_time = lap_time
        car.total_time += lap_time
        
        if not action.startswith("PIT_"):
            car.tyre_age += 1
    
    race.update_positions()
    race.update_gaps()
    race.advance_lap()
    return race


def get_ai_recommendation(car, race, ai_style):
    if car.has_pitted:
        return "STAY_OUT"
    
    age = car.tyre_age
    
    if ai_style == "aggressive":
        if car.compound == "SOFT" and age > 10:
            return "PIT_MEDIUM"
        elif age > 15:
            return "PIT_HARD"
    elif ai_style == "conservative":
        if age > 22:
            return "PIT_HARD"
    elif ai_style == "balanced":
        if car.compound == "SOFT" and age > 12:
            return "PIT_MEDIUM"
        elif age > 18:
            return "PIT_HARD"
    else:
        if age > 20:
            return "PIT_HARD"
    
    return "STAY_OUT"
