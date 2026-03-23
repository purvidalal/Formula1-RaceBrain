# 🏗️ RaceBrain Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────┐
│                     FRONTEND                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  game.html   │  │  test.html   │  │   assets/    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                         │ HTTP
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   FASTAPI SERVER                        │
│                     (main.py)                           │
└─────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ GAME ROUTES  │  │  API ROUTES  │  │ PAGE ROUTES  │
│              │  │              │  │              │
│ /api/game/*  │  │ /api/*       │  │ /, /game     │
└──────────────┘  └──────────────┘  └──────────────┘
        │                │
        ▼                ▼
┌──────────────┐  ┌──────────────────────────┐
│ GAME SERVICE │  │ RECOMMENDATION SERVICE   │
│              │  │                          │
│ - State      │  │ - AI Agents              │
│ - Validation │  │ - Multi-Agent Consensus  │
│ - Cleanup    │  │                          │
└──────────────┘  └──────────────────────────┘
        │                │
        ▼                ▼
┌──────────────┐  ┌──────────────────────────┐
│ RACE ENGINE  │  │ AGENT MANAGER            │
│              │  │                          │
│ - Physics    │  │ - DQN (Aggressive)       │
│ - State      │  │ - DQN (Conservative)     │
│ - Teams      │  │ - DQN (Balanced)         │
└──────────────┘  │ - Q-Learning             │
        │         │ - Heuristic              │
        ▼         └──────────────────────────┘
┌──────────────┐
│ LAP SIM      │
│              │
│ - Lap times  │
│ - Deg model  │
│ - Pit stops  │
└──────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│           CONFIGURATION              │
│                                      │
│ - Teams & Drivers                    │
│ - Compounds                          │
│ - Track Settings                     │
│ - Valid Actions                      │
└──────────────────────────────────────┘
```

---

## Request Flow

### Starting a Race

```
USER
  │
  │ POST /api/game/start
  │ {team: "Ferrari", difficulty: "normal"}
  ▼
GAME ROUTES
  │
  │ validate request
  ▼
GAME SERVICE
  │
  │ validate_team("Ferrari")
  │ check_race_limit()
  │ generate_uuid()
  ▼
RACE ENGINE
  │
  │ create_default_race("Ferrari")
  │ initialize 5 teams
  │ set starting positions
  ▼
RESPONSE
  │
  │ {
  │   race_id: "550e8400-...",
  │   state: {...},
  │   player_team: "Ferrari"
  │ }
  ▼
USER
```

### Taking an Action

```
USER
  │
  │ POST /api/game/action
  │ {race_id, team: "Ferrari", action: "PIT_SOFT"}
  ▼
GAME ROUTES
  │
  │ validate request
  ▼
GAME SERVICE
  │
  │ validate_action()
  │   ✓ race exists?
  │   ✓ team correct?
  │   ✓ not finished?
  │   ✓ valid action?
  │   ✓ can pit?
  ▼
LAP SIMULATOR
  │
  │ get_ai_actions() for 4 opponents
  │ simulate_lap(player_action, ai_actions)
  │   - calculate lap times
  │   - apply degradation
  │   - update positions
  │   - check pit stops
  ▼
RESPONSE
  │
  │ {
  │   race_id,
  │   state: {...updated...},
  │   finished: false
  │ }
  ▼
USER
```

### Getting Recommendations

```
USER
  │
  │ GET /api/game/recommendations/{race_id}/{team}
  ▼
GAME ROUTES
  │
  ▼
RECOMMENDATION SERVICE
  │
  │ get_race_state()
  │ extract: lap, tyre_age, compound, position
  ▼
AGENT MANAGER
  │
  ├─> DQN Aggressive    → action, confidence
  ├─> DQN Conservative  → action, confidence
  ├─> DQN Balanced      → action, confidence
  ├─> Q-Learning        → action, confidence
  └─> Heuristic         → action, confidence
  │
  │ calculate_consensus()
  │   weighted_voting(confidences)
  ▼
RESPONSE
  │
  │ {
  │   recommendations: {
  │     dqn_aggressive: {action, confidence, reasoning},
  │     ...
  │   },
  │   consensus: {action, confidence}
  │ }
  ▼
USER
```

---

## Data Flow

### Configuration → Services

```
config/settings.py
  │
  ├─> TEAM_DRIVERS        → game_service (validation)
  ├─> VALID_ACTIONS       → game_service (validation)
  ├─> BASE_PACE           → lap_simulator (physics)
  ├─> DEGRADATION         → lap_simulator (physics)
  └─> AI_DIFFICULTY       → game_service (AI offset)
```

### Race State Management

```
CREATE:
  game_service.create_race()
    → active_races[uuid] = RaceState
    → metadata[uuid] = {player_team, created_at, ...}

UPDATE:
  game_service.execute_action()
    → active_races[uuid] = simulate_lap(...)
    → metadata[uuid].last_action = now()

DELETE:
  game_service._cleanup_old_races()
    → if race.finished: delete
    → if inactive > 1hr: delete
```

---

## Validation Layers

### Layer 1: Pydantic (Request Schema)

```python
class GameActionRequest(BaseModel):
    race_id: str
    team: str
    action: str
```

### Layer 2: Game Service (Business Logic)

```python
def validate_action(race_id, team, action):
    ✓ race exists?
    ✓ team ownership?
    ✓ race not finished?
    ✓ valid action?
    ✓ can execute?
```

### Layer 3: Route Handler (HTTP)

```python
try:
    race = game_service.execute_action(...)
except ValueError as e:
    raise HTTPException(400, detail=str(e))
```

---

## Service Responsibilities

### Game Service
- ✅ Create races (with UUID)
- ✅ Validate all actions
- ✅ Execute lap simulation
- ✅ Manage race lifecycle
- ✅ Auto-cleanup stale races

### Recommendation Service
- ✅ Load AI agents
- ✅ Get agent recommendations
- ✅ Calculate consensus
- ✅ Extract race state for queries

### Race Engine
- ✅ Initialize race state
- ✅ Manage team profiles
- ✅ Track car positions
- ✅ Handle race finish

### Lap Simulator
- ✅ Calculate lap times
- ✅ Apply degradation
- ✅ Execute pit stops
- ✅ Update positions
- ✅ Get AI actions

---

## Error Handling Strategy

### Client Errors (400)
```python
# Invalid team
ValueError("Invalid team 'Toyota'")
  → HTTPException(400)

# Invalid action
ValueError("Invalid action 'JUMP'")
  → HTTPException(400)

# Race finished
ValueError("Race already finished")
  → HTTPException(400)
```

### Not Found (404)
```python
# Race doesn't exist
race = game_service.get_race(race_id)
if not race:
    → HTTPException(404)
```

### Server Errors (500)
```python
# Unexpected failures
except Exception as e:
    → HTTPException(500, detail=str(e))
```

---

## State Management

### Active Races

```python
{
  "550e8400-...": RaceState(
    current_lap=18,
    cars=[...],
    finished=False
  )
}
```

### Race Metadata

```python
{
  "550e8400-...": {
    "player_team": "Ferrari",
    "difficulty": "normal",
    "created_at": datetime(...),
    "last_action": datetime(...)
  }
}
```

### Cleanup Strategy

```
Every action:
  if race.finished:
    → mark for deletion
  
  if (now - last_action) > 1 hour:
    → mark for deletion

On create (if at limit):
  → cleanup_old_races()
  → delete marked races
```

---

## Performance Considerations

### Race Limit
- Max 1000 concurrent races
- Auto-cleanup prevents memory leaks

### UUID vs Integer IDs
- UUIDs: No collisions, distributed-safe
- Cost: 36 chars vs 4-8 chars
- Trade-off: Safety > Size

### In-Memory vs Database
- Current: In-memory (fast, simple)
- Future: Database (persistent, scalable)
- Trade-off: Speed vs Persistence

---

## Security Notes

### Input Validation
✅ Team must exist
✅ Action must be valid
✅ Race must belong to user
✅ Pydantic type checking

### Rate Limiting
⚠️ Not implemented yet
📝 Future: Add per-IP limits

### Authentication
⚠️ Not implemented yet
📝 Future: Add user accounts

---

## Extension Points

### Adding New Teams
```python
# config/settings.py
TEAM_DRIVERS["New Team"] = ["Driver1", "Driver2"]
```

### Adding New Actions
```python
# config/settings.py
VALID_ACTIONS.add("PUSH")
VALID_ACTIONS.add("CONSERVE")

# engine/lap_simulator.py
# Add action handling logic
```

### Adding New Tracks
```python
# config/settings.py
TRACKS["Monaco"] = {
    "name": "...",
    "total_laps": 78,
    ...
}
```

### Adding New AI Agents
```python
# multi_agent/agent_manager.py
self.agents.append(NewAgent())
```

---

## Monitoring & Debugging

### Check Active Races
```bash
curl http://localhost:8000/api/game/stats
```

### View Logs
```bash
python app/main.py
# Watch console output
```

### Test Endpoints
```bash
# Visit interactive docs
http://localhost:8000/docs
```

---

**This architecture is production-ready, maintainable, and extensible! 🏗️✨**
