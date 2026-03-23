# 🏎️ RaceBrain - Production Version

**Multi-Agent Deep Reinforcement Learning F1 Strategy Game**

A professional-grade F1 strategy game powered by 5 AI agents trained with Deep Q-Learning.

---

## 🎯 What's New in Production

### ✅ Professional Architecture
- Clean separation of concerns
- Proper validation everywhere
- UUID-based race IDs
- Automatic race cleanup
- Type-safe API with Pydantic

### ✅ Single Source of Truth
- All teams/drivers in one config file
- No more duplicate/inconsistent data
- Backend drives frontend

### ✅ Robust Error Handling
- Detailed error messages
- Validation at every endpoint
- Graceful failure modes

### ✅ Production-Ready Code
- Proper Python packages
- Clean imports
- Professional structure
- Easy to extend

---

## 📁 Project Structure

```
RaceBrain_Production/
├── config/
│   └── settings.py              ← Single source of truth
│
├── engine/                       ← Game physics & simulation
│   ├── race_engine.py
│   └── lap_simulator.py
│
├── multi_agent/                  ← AI recommendation system
│   └── agent_manager.py
│
├── app/
│   ├── main.py                  ← FastAPI application
│   │
│   ├── services/
│   │   ├── game_service.py      ← Game state management
│   │   └── recommendation_service.py
│   │
│   ├── routes/
│   │   ├── game_routes.py       ← /api/game/*
│   │   ├── api_routes.py        ← /api/recommend
│   │   └── page_routes.py       ← HTML pages
│   │
│   └── models/
│       └── schemas.py            ← Pydantic models
│
├── frontend/                     ← HTML/JS/CSS
│   ├── game.html
│   └── test.html
│
├── models/                       ← Trained AI models
│   ├── dqn_aggressive.pkl
│   ├── dqn_conservative.pkl
│   ├── dqn_balanced.pkl
│   └── rl_policy.pkl
│
└── migrate.py                    ← Migration script
```

---

## 🚀 Quick Start

### 1. Run Migration Script

Copy your existing files to the production structure:

```bash
cd ~/Downloads/RaceBrain_Production
python migrate.py
```

### 2. Start Server

```bash
python app/main.py
```

### 3. Play!

- **Main Game:** http://localhost:8000/game
- **Multi-Agent Test:** http://localhost:8000/test
- **API Docs:** http://localhost:8000/docs

---

## 🎮 API Endpoints

### Game Endpoints

```
POST /api/game/start
  Body: {team: "Ferrari", difficulty: "normal"}
  Returns: {race_id, state, player_team}

POST /api/game/action
  Body: {race_id, team, action}
  Returns: {race_id, state, finished, events}

GET /api/game/recommendations/{race_id}/{team}
  Returns: All 5 agent recommendations

GET /api/game/state/{race_id}
  Returns: Current race state

DELETE /api/game/{race_id}
  Deletes a race
```

### General API

```
POST /api/recommend
  Body: {lap, tyre_age, compound, position, pitted}
  Returns: AI recommendations

GET /api/config/teams
  Returns: Team configuration
```

### Pages

```
GET /            → Main game
GET /game        → Main game
GET /test        → Multi-agent dashboard
```

---

## 🔧 Key Improvements

### 1. Proper Validation

**Before:**
```python
team = data.get("team")  # No validation!
```

**After:**
```python
if player_team not in TEAM_DRIVERS:
    raise ValueError(f"Invalid team '{player_team}'")
```

### 2. UUID Race IDs

**Before:**
```python
race_id = str(random.randint(1000, 9999))  # Can collide!
```

**After:**
```python
race_id = str(uuid.uuid4())  # Globally unique
```

### 3. Automatic Cleanup

**Before:**
```python
active_races = {}  # Grows forever
```

**After:**
```python
# Auto-delete finished races
# Auto-delete inactive races (1 hour)
# Limit: 1000 max concurrent races
```

### 4. Single Config

**Before:**
```python
# Python side
TEAMS = {...}

// JavaScript side
const teams = {...}  // Duplicate!
```

**After:**
```python
# Only in config/settings.py
TEAM_DRIVERS = {...}

# Frontend fetches from API
```

---

## 🤖 AI Agents

The system uses 5 trained AI agents:

1. **DQN Aggressive** - Early pit stops, aggressive strategy
2. **DQN Conservative** - Late pit stops, cautious strategy
3. **DQN Balanced** - Optimal balance
4. **Q-Learning** - Classic RL approach
5. **Heuristic** - Rule-based expert system

All agents provide:
- Recommended action
- Confidence score
- Reasoning

**Consensus mechanism** combines all 5 using weighted voting.

---

## 📊 Game Features

- ✅ **Lap-by-lap racing** - Interactive turn-based gameplay
- ✅ **5 AI teams** - Race against intelligent opponents
- ✅ **3 tyre compounds** - SOFT, MEDIUM, HARD
- ✅ **Realistic degradation** - Based on real F1 telemetry
- ✅ **Multi-agent recommendations** - Get advice from 5 AI agents
- ✅ **Real-time leaderboard** - See positions update live
- ✅ **Event feed** - Track race events

---

## 🎓 Technical Details

### Technologies

- **Backend:** FastAPI (Python 3.10+)
- **AI:** PyTorch, NumPy
- **Frontend:** Vanilla JS, HTML5, CSS3
- **Data:** Real F1 telemetry (Bahrain 2025)

### AI Training

- **3000 episodes** per DQN agent
- **State:** lap, tyre age, compound, position, pitted
- **Actions:** STAY_OUT, PIT_SOFT, PIT_MEDIUM, PIT_HARD
- **Reward:** Position-based with personality shaping

### Game Physics

```python
lap_time = BASE_PACE[compound] 
         + DEGRADATION[compound] * tyre_age
         + team_offset
         + random_variance
```

- **Pit stop:** 22.5s ± 0.5s
- **SOFT:** 92.3s base, 0.12s/lap degradation
- **MEDIUM:** 93.2s base, 0.085s/lap degradation
- **HARD:** 94.1s base, 0.06s/lap degradation

---

## 🔒 Validation Rules

### Race Creation
- ✅ Team must exist
- ✅ Max 1000 concurrent races
- ✅ UUID race ID generated

### Actions
- ✅ Race must exist
- ✅ Team must own the race
- ✅ Race must not be finished
- ✅ Action must be valid
- ✅ Can't pit twice

### Cleanup
- ✅ Finished races deleted
- ✅ Inactive races (1hr) deleted
- ✅ Automatic memory management

---

## 🐛 Error Handling

All errors return clear messages:

```json
{
  "detail": "Invalid team 'Toyota'. Must be one of: McLaren, Ferrari, ..."
}
```

```json
{
  "detail": "Race has already finished"
}
```

```json
{
  "detail": "Cannot pit again - already completed pit stop this race"
}
```

---

## 📈 Future Enhancements

- [ ] Weather conditions
- [ ] Safety cars
- [ ] Multiple tracks
- [ ] Championship mode
- [ ] Multiplayer
- [ ] Advanced telemetry
- [ ] Machine learning opponent adaptation

---

## 📝 License

Bachelor's Capstone Project - 2025

---

## 🏆 Credits

**Developer:** Your Name  
**Project:** RaceBrain - Multi-Agent Deep RL F1 Strategy Game  
**Institution:** Your University  
**Year:** 2025

---

**Enjoy racing! 🏎️💨**
