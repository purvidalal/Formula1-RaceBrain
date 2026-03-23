"""
RaceBrain Configuration
Single source of truth for all game settings
"""

from typing import Dict, List
import os

# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# ============================================================
# TEAMS & DRIVERS (2025 Grid)
# ============================================================

TEAM_DRIVERS: Dict[str, List[str]] = {
    "McLaren": ["Lando Norris", "Oscar Piastri"],
    "Ferrari": ["Charles Leclerc", "Lewis Hamilton"],
    "Mercedes": ["George Russell", "Kimi Antonelli"],
    "Red Bull": ["Max Verstappen", "Sergio Perez"],
    "Aston Martin": ["Fernando Alonso", "Lance Stroll"],
    "Alpine": ["Pierre Gasly", "Esteban Ocon"],
    "Williams": ["Alex Albon", "Logan Sargeant"],
    "Haas": ["Nico Hulkenberg", "Kevin Magnussen"],
    "Sauber": ["Valtteri Bottas", "Zhou Guanyu"],
}

# Reverse mapping
DRIVER_TO_TEAM: Dict[str, str] = {
    driver: team 
    for team, drivers in TEAM_DRIVERS.items() 
    for driver in drivers
}

# ============================================================
# COMPOUNDS & ACTIONS
# ============================================================

COMPOUNDS = ["SOFT", "MEDIUM", "HARD"]

VALID_ACTIONS = {
    "STAY_OUT",
    "PIT_SOFT",
    "PIT_MEDIUM",
    "PIT_HARD",
}

# ============================================================
# TRACK SETTINGS (BAHRAIN)
# ============================================================

BASE_PACE: Dict[str, float] = {
    "SOFT": 92.3,
    "MEDIUM": 93.2,
    "HARD": 94.1,
}

DEGRADATION: Dict[str, float] = {
    "SOFT": 0.120,
    "MEDIUM": 0.085,
    "HARD": 0.060,
}

TRACK_CONFIG = {
    "name": "Bahrain International Circuit",
    "flag": "🇧🇭",
    "total_laps": 57,
    "pit_loss": 22.5,
}

# ============================================================
# AI DIFFICULTY
# ============================================================

AI_DIFFICULTY = {
    "easy": {
        "pace_offset": 1.0,
        "description": "AI is ~1.0s per lap slower on average.",
    },
    "normal": {
        "pace_offset": 0.4,
        "description": "AI is close to your pace with a small disadvantage.",
    },
    "hard": {
        "pace_offset": -0.2,
        "description": "AI is slightly faster - you need superior strategy.",
    }
}

DEFAULT_DIFFICULTY = "normal"

# ============================================================
# GAME LIMITS
# ============================================================

MAX_ACTIVE_RACES = 1000
RACE_CLEANUP_HOURS = 1
