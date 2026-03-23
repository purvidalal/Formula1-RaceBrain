"""
Train DQN Agents with Different Personalities
- Aggressive: Early pit bias
- Conservative: Late pit bias  
- Balanced: No bias
"""

import os
import sys
import numpy as np
import pandas as pd
import pickle
from dqn_agent import DQNAgent

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Constants
RACE_LAPS = 57
PIT_LOSS = 22.5
BASE_PACE = {"SOFT": 92.3, "MEDIUM": 93.2, "HARD": 94.1}
DEGRADATION = {"SOFT": 0.120, "MEDIUM": 0.085, "HARD": 0.060}
COMPOUNDS = ["SOFT", "MEDIUM", "HARD"]

# Load real data if available
DATA_FILE = "bahrain_2025_clean.parquet"
if os.path.exists(DATA_FILE):
    try:
        df = pd.read_parquet(DATA_FILE)
        print(f"✓ Loaded {len(df)} rows from {DATA_FILE}")
        
        # Update pace from real data
        for comp in COMPOUNDS:
            comp_data = df[df['compound'] == comp]
            if len(comp_data) > 0:
                fresh_laps = comp_data[comp_data['tyre_age'] <= 2]
                if len(fresh_laps) > 0:
                    BASE_PACE[comp] = float(fresh_laps['lap_time'].median())
        
        print(f"Base pace: SOFT={BASE_PACE['SOFT']:.1f}, MEDIUM={BASE_PACE['MEDIUM']:.1f}, HARD={BASE_PACE['HARD']:.1f}")
    except Exception as e:
        print(f"⚠ Could not load data: {e}")


def lap_time(compound: str, tyre_age: int) -> float:
    """Calculate lap time based on compound and tyre age"""
    base = BASE_PACE[compound]
    deg = DEGRADATION[compound]
    return base + deg * max(1, tyre_age)


def normalize_state(lap, tyre_age, compound, position, pitted):
    """
    Normalize state to [0, 1] range
    
    Returns: np.array of shape (5,)
    """
    comp_idx = COMPOUNDS.index(compound)
    return np.array([
        lap / RACE_LAPS,              # 0-1
        tyre_age / 30,                # 0-1 (max realistic tyre age)
        comp_idx / 2,                 # 0-1 (SOFT=0, MEDIUM=0.5, HARD=1)
        position / 20,                # 0-1 (P1=0.05, P20=1)
        1.0 if pitted else 0.0        # Binary
    ])


class F1Environment:
    """F1 Race Environment for DQN Training"""
    
    def __init__(self, personality: str = "balanced"):
        self.personality = personality
        self.reset()
    
    def reset(self):
        """Reset to start of race"""
        self.lap = 1
        self.tyre_age = 1
        self.compound = np.random.choice(COMPOUNDS)
        self.position = np.random.randint(1, 21)
        self.pitted = False
        self.total_time = 0
        return self.get_state()
    
    def get_state(self):
        """Get normalized state"""
        return normalize_state(
            self.lap, self.tyre_age, self.compound, 
            self.position, self.pitted
        )
    
    def step(self, action: int):
        """
        Execute action
        
        Actions:
        0 = stay out
        1 = pit for SOFT
        2 = pit for MEDIUM
        3 = pit for HARD
        
        Returns: (next_state, reward, done)
        """
        # Calculate current lap time
        current_lap_time = lap_time(self.compound, self.tyre_age)
        
        # Personality-based reward shaping
        reward = -current_lap_time
        
        # Execute action
        if action == 0:
            # Stay out
            self.tyre_age += 1
        else:
            # Pit stop
            new_compound = COMPOUNDS[action - 1]
            
            # Only pit if not already pitted or changing compound
            if not self.pitted or new_compound != self.compound:
                reward -= PIT_LOSS
                self.compound = new_compound
                self.tyre_age = 1
                self.pitted = True
                
                # Personality-based rewards
                if self.personality == "aggressive":
                    # Reward early pits
                    if self.lap < 20:
                        reward += 5  # Bonus for early pit
                elif self.personality == "conservative":
                    # Reward late pits
                    if self.lap > 35:
                        reward += 5  # Bonus for late pit
            else:
                # Penalty for invalid pit (same compound)
                reward -= 50
        
        self.total_time += current_lap_time
        self.lap += 1
        done = self.lap > RACE_LAPS
        
        next_state = self.get_state()
        return next_state, reward, done
    
    def get_valid_actions(self):
        """Get list of valid actions"""
        if self.pitted:
            return [0]  # Can only stay out after pitting
        return [0, 1, 2, 3]  # All actions valid


def train_dqn_agent(
    personality: str,
    episodes: int = 3000,
    save_path: str = None
):
    """
    Train a DQN agent with specific personality
    
    Args:
        personality: "aggressive", "conservative", or "balanced"
        episodes: Number of training episodes
        save_path: Path to save trained model
    """
    print(f"\n{'='*60}")
    print(f"Training DQN Agent - {personality.upper()}")
    print(f"{'='*60}")
    
    env = F1Environment(personality=personality)
    agent = DQNAgent(
        state_size=5,
        action_size=4,
        epsilon_start=0.5,
        epsilon_end=0.05,
        personality=personality
    )
    
    best_time = float('inf')
    
    for episode in range(episodes):
        state = env.reset()
        done = False
        episode_reward = 0
        
        while not done:
            valid_actions = env.get_valid_actions()
            action = agent.get_action(state, valid_actions)
            next_state, reward, done = env.step(action)
            
            agent.remember(state, action, reward, next_state, done)
            agent.replay()
            
            episode_reward += reward
            state = next_state
        
        # Track best performance
        if env.total_time < best_time:
            best_time = env.total_time
        
        # Progress logging
        if (episode + 1) % 500 == 0:
            print(f"  Episode {episode + 1}/{episodes}: "
                  f"Best={best_time:.1f}s, ε={agent.epsilon:.3f}")
    
    # Save model
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        agent.save(save_path)
        print(f"✓ Saved to {save_path}")
    
    return agent


if __name__ == "__main__":
    print("="*60)
    print("DQN AGENT TRAINING - MULTI-PERSONALITY")
    print("="*60)
    
    # Create models directory
    os.makedirs("models", exist_ok=True)
    
    # Train all three personalities
    personalities = [
        ("aggressive", "models/dqn_aggressive.pkl"),
        ("conservative", "models/dqn_conservative.pkl"),
        ("balanced", "models/dqn_balanced.pkl")
    ]
    
    for personality, save_path in personalities:
        train_dqn_agent(
            personality=personality,
            episodes=3000,
            save_path=save_path
        )
    
    print("\n" + "="*60)
    print("✓ ALL AGENTS TRAINED SUCCESSFULLY")
    print("="*60)
    print("\nTrained models:")
    for _, path in personalities:
        print(f"  • {path}")
    print("\n" + "="*60)
