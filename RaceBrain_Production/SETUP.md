# 🚀 SETUP INSTRUCTIONS

## ⚡ Quick Setup (5 minutes)

### Step 1: Download Production Files

1. Download the entire `RaceBrain_Production` folder from Claude
2. Save it to: `~/Downloads/RaceBrain_Production`

### Step 2: Copy Your Existing Files

Run the migration script to copy your working files:

```bash
cd ~/Downloads/RaceBrain_Production
python migrate.py
```

This copies:
- `engine/` (race engine)
- `multi_agent/` (AI agents)
- `models/` (trained models)
- `frontend/` (HTML files)

### Step 3: Start the Server

```bash
python app/main.py
```

You should see:

```
🤖 Loading AI agents...
  ✓ Loaded DQN (aggressive)
  ✓ Loaded DQN (conservative)
  ✓ Loaded DQN (balanced)
  ✓ Loaded Q-Learning policy
  ✓ Loaded Heuristic agent
✅ AI agents loaded successfully

============================================================
🏎️  RACEBRAIN PRODUCTION SERVER
============================================================
📍 URL: http://localhost:8000
📍 Game: http://localhost:8000/game
📍 Test: http://localhost:8000/test
📍 Docs: http://localhost:8000/docs
============================================================
```

### Step 4: Play!

Open in browser:
- **Main Game:** http://localhost:8000/game
- **Multi-Agent Test:** http://localhost:8000/test
- **API Documentation:** http://localhost:8000/docs

---

## 🎯 What You Get

### Professional Code Structure ✅

```
app/
├── main.py              ← Clean FastAPI app
├── services/            ← Business logic
├── routes/              ← API endpoints
└── models/              ← Type validation
```

### Single Source of Truth ✅

All configuration in one place:
```python
# config/settings.py
TEAM_DRIVERS = {
    "Ferrari": ["Charles Leclerc", "Lewis Hamilton"],
    ...
}
```

### Proper Validation ✅

```python
# Before action execution:
✓ Check race exists
✓ Check team ownership
✓ Check race not finished
✓ Check valid action
✓ Check can pit
```

### UUID Race IDs ✅

```python
# Globally unique, no collisions
race_id = "550e8400-e29b-41d4-a716-446655440000"
```

### Auto Cleanup ✅

```python
# Automatic memory management
- Delete finished races
- Delete inactive races (1 hour)
- Max 1000 concurrent races
```

---

## 🔧 Troubleshooting

### Problem: "Module not found"

**Solution:** Make sure you're in the right directory:
```bash
cd ~/Downloads/RaceBrain_Production
python app/main.py
```

### Problem: "File not found: game.html"

**Solution:** Run the migration script:
```bash
python migrate.py
```

### Problem: Port 8000 already in use

**Solution:** Stop your old server first:
```bash
# Press Ctrl+C in the old server terminal
# Then start the new one
python app/main.py
```

### Problem: AI agents not loading

**Solution:** Check models folder exists:
```bash
ls models/
# Should show: dqn_*.pkl, rl_policy.pkl
```

---

## 📊 Testing the API

### Test Game Creation

```bash
curl -X POST http://localhost:8000/api/game/start \
  -H "Content-Type: application/json" \
  -d '{"team": "Ferrari", "difficulty": "normal"}'
```

### Test Recommendations

```bash
curl -X POST http://localhost:8000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"lap": 18, "tyre_age": 13, "compound": "MEDIUM", "position": 4, "pitted": false}'
```

### Test Config

```bash
curl http://localhost:8000/api/config/teams
```

---

## 🎮 Using the Game

### 1. Start a Race

- Select team (e.g., Ferrari)
- Select difficulty
- Click "START RACE"

### 2. Make Decisions

Each lap you can:
- **STAY OUT** - Continue on current tyres
- **PIT → SOFT** - Pit for soft tyres
- **PIT → MEDIUM** - Pit for medium tyres  
- **PIT → HARD** - Pit for hard tyres

### 3. Get AI Help

Click "ASK AI AGENTS" to see:
- 5 agent recommendations
- Confidence scores
- Consensus decision

### 4. Race to the End

- Watch positions update
- See lap times
- Track events
- Win the race!

---

## 📈 API Documentation

Visit **http://localhost:8000/docs** for:
- Interactive API documentation
- Try endpoints directly
- See request/response schemas
- Test all features

---

## 🏆 Key Features

### Game Features
- ✅ Lap-by-lap racing
- ✅ 5 AI opponent teams
- ✅ 3 tyre compounds
- ✅ Realistic degradation
- ✅ Position-based racing
- ✅ Event tracking

### AI Features
- ✅ 5 trained agents
- ✅ DQN networks
- ✅ Q-Learning
- ✅ Rule-based
- ✅ Consensus system
- ✅ Confidence scores

### Technical Features
- ✅ UUID race IDs
- ✅ Automatic cleanup
- ✅ Proper validation
- ✅ Type safety
- ✅ Error handling
- ✅ Clean architecture

---

## 🎓 Code Quality

### What Changed

**Old:** 1800-line server.py with everything mixed
**New:** Clean separation:
- `config/` → Settings
- `services/` → Business logic
- `routes/` → API endpoints
- `models/` → Data validation

### Validation Examples

**Team validation:**
```python
if player_team not in TEAM_DRIVERS:
    raise ValueError("Invalid team")
```

**Action validation:**
```python
if action not in VALID_ACTIONS:
    raise ValueError("Invalid action")
```

**Race validation:**
```python
if race.finished:
    raise ValueError("Race already finished")
```

---

## 💡 Tips

1. **Use the API docs** - http://localhost:8000/docs is your friend
2. **Check logs** - Server prints helpful debug info
3. **Test endpoints** - Use curl or the docs interface
4. **Read the code** - It's clean and well-commented!

---

## 🚀 You're Ready!

Run these commands:

```bash
cd ~/Downloads/RaceBrain_Production
python migrate.py
python app/main.py
```

Then open: **http://localhost:8000/game**

**Enjoy your professional F1 strategy game! 🏎️✨**
