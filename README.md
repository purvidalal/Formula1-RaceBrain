# RaceBrain: Multi-Agent Deep RL + RAG for F1 Strategy

## 🏎️ Complete F1 Pit Strategy Recommendation System

### Features:
1. **Multi-Agent Reinforcement Learning**
   - 3 Deep Q-Network agents (Aggressive, Conservative, Balanced)
   - Q-Learning baseline (your trained model)
   - Heuristic baseline
   - Consensus mechanism

2. **RAG Explanation Engine**
   - Natural language queries
   - Historical race analysis
   - Context-aware explanations
   - Evidence retrieval

3. **Production-Ready Interface**
   - F1 Official theme
   - Real-time recommendations
   - Interactive charts
   - Race simulation

### Quick Start:

```bash
# 1. Install dependencies
pip install -r requirements.txt --break-system-packages

# 2. Train DQN agents (~10 minutes)
python deep_rl/train_dqn.py

# 3. Build RAG knowledge base
python rag/build_knowledge.py

# 4. Start server
python server.py

# 5. Open browser
http://localhost:8000
```

### Project Structure:
- `deep_rl/` - Multi-agent DQN implementation
- `multi_agent/` - Agent coordination
- `rag/` - RAG explanation system
- `frontend/` - Web interface
- `models/` - Trained AI models
- `knowledge/` - RAG vector database

### Data:
- Bahrain 2025 F1 Grand Prix
- 1,006 lap records
- Real telemetry data
- Tyre degradation models

### Technologies:
- Python 3.10+
- PyTorch (Deep Learning)
- FastAPI (Backend)
- LangChain (RAG)
- ChromaDB (Vector Store)
- Chart.js (Visualization)
