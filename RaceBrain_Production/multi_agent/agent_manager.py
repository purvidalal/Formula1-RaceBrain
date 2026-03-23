"""
Multi-Agent Manager
Coordinates 5 agents: 3 DQN + Q-Learning + Heuristic
"""

import os
import sys
import pickle
import numpy as np
from typing import Dict, List, Tuple, Optional

# Add deep_rl to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'deep_rl'))

try:
    from dqn_agent import DQNAgent
except ImportError:
    DQNAgent = None


class AgentManager:
    """Manages multiple agents and aggregates their recommendations"""
    
    def __init__(self):
        self.agents = {}
        self.compounds = ["SOFT", "MEDIUM", "HARD"]
        
    def load_agents(self, models_dir: str = "models"):
        """Load all available agents"""
        print("🤖 Loading AI agents...")
        
        # Load DQN agents
        if DQNAgent is not None:
            for personality in ["aggressive", "conservative", "balanced"]:
                path = os.path.join(models_dir, f"dqn_{personality}.pkl")
                if os.path.exists(path):
                    try:
                        agent = DQNAgent(personality=personality)
                        agent.load(path)
                        agent.epsilon = 0.0  # No exploration during inference
                        self.agents[f"dqn_{personality}"] = agent
                        print(f"  ✓ Loaded DQN ({personality})")
                    except Exception as e:
                        print(f"  ⚠ Failed to load DQN ({personality}): {e}")
        
        # Load Q-Learning agent
        ql_path = os.path.join(models_dir, "rl_policy.pkl")
        if os.path.exists(ql_path):
            try:
                with open(ql_path, "rb") as f:
                    policy_data = pickle.load(f)
                self.agents["q_learning"] = policy_data
                print(f"  ✓ Loaded Q-Learning policy: {len(policy_data.get('q_table', {}))} entries")
            except Exception as e:
                print(f"  ⚠ Failed to load Q-Learning: {e}")
        
        # Heuristic agent (always available)
        self.agents["heuristic"] = "heuristic"
        print(f"  ✓ Loaded Heuristic agent")
        
        print(f"\n✓ Loaded {len(self.agents)} agents total")
        return len(self.agents)
    
    def get_recommendations(
        self,
        lap: int,
        tyre_age: int,
        compound: str,
        position: int = 10,
        pitted: bool = False
    ) -> Dict:
        """
        Get recommendations from all agents
        
        Returns:
            {
                "recommendations": {agent_name: recommendation_dict},
                "consensus": consensus_dict
            }
        """
        recommendations = {}
        
        # Get recommendation from each agent
        for agent_name, agent in self.agents.items():
            try:
                if agent_name.startswith("dqn_"):
                    rec = self._get_dqn_recommendation(
                        agent, agent_name, lap, tyre_age, compound, position, pitted
                    )
                elif agent_name == "q_learning":
                    rec = self._get_qlearning_recommendation(
                        agent, lap, tyre_age, compound, position, pitted
                    )
                elif agent_name == "heuristic":
                    rec = self._get_heuristic_recommendation(
                        lap, tyre_age, compound, position, pitted
                    )
                else:
                    continue
                
                recommendations[agent_name] = rec
            except Exception as e:
                print(f"⚠ Error getting recommendation from {agent_name}: {e}")
        
        # Calculate consensus
        consensus = self._calculate_consensus(recommendations)
        
        return {
            "recommendations": recommendations,
            "consensus": consensus
        }
    
    def _get_dqn_recommendation(
        self, agent, agent_name, lap, tyre_age, compound, position, pitted
    ) -> Dict:
        """Get recommendation from DQN agent"""
        # Normalize state
        comp_idx = self.compounds.index(compound)
        state = np.array([
            lap / 57,
            tyre_age / 30,
            comp_idx / 2,
            position / 20,
            1.0 if pitted else 0.0
        ])
        
        # Get Q-values
        q_values = agent.predict_q_values(state)
        
        # Get best action
        valid_actions = [0] if pitted else [0, 1, 2, 3]
        best_action = max(valid_actions, key=lambda a: q_values[a])
        
        # Convert to recommendation
        if best_action == 0:
            return {
                "agent": f"DQN ({agent.personality.title()})",
                "pit": False,
                "compound": None,
                "confidence": float(self._softmax_confidence(q_values, best_action)),
                "q_value": float(q_values[best_action])
            }
        else:
            return {
                "agent": f"DQN ({agent.personality.title()})",
                "pit": True,
                "compound": self.compounds[best_action - 1],
                "confidence": float(self._softmax_confidence(q_values, best_action)),
                "q_value": float(q_values[best_action])
            }
    
    def _get_qlearning_recommendation(
        self, policy_data, lap, tyre_age, compound, position, pitted
    ) -> Dict:
        """Get recommendation from Q-Learning agent"""
        q_table = policy_data.get("q_table", {})
        bins = policy_data.get("bins", {"lap": 5, "age": 5})
        
        # Bin state
        lap_bin = (lap // bins["lap"]) * bins["lap"]
        age_bin = (tyre_age // bins["age"]) * bins["age"]
        comp_idx = self.compounds.index(compound)
        
        # Get Q-values for all actions
        q_values = []
        for action in range(4):
            key = (lap_bin, age_bin, comp_idx, action)
            q_values.append(q_table.get(key, -1e6))
        
        # Get best action
        valid_actions = [0] if pitted else [0, 1, 2, 3]
        best_action = max(valid_actions, key=lambda a: q_values[a])
        
        if best_action == 0:
            return {
                "agent": "Q-Learning (Baseline)",
                "pit": False,
                "compound": None,
                "confidence": 0.5,  # Q-Learning doesn't provide confidence
                "q_value": float(q_values[best_action]) if q_values[best_action] > -1e5 else None
            }
        else:
            return {
                "agent": "Q-Learning (Baseline)",
                "pit": True,
                "compound": self.compounds[best_action - 1],
                "confidence": 0.5,
                "q_value": float(q_values[best_action]) if q_values[best_action] > -1e5 else None
            }
    
    def _get_heuristic_recommendation(
        self, lap, tyre_age, compound, position, pitted
    ) -> Dict:
        """Get recommendation from heuristic agent"""
        # Simple heuristic: pit if tyres are old or on wrong compound
        
        should_pit = False
        target_compound = None
        confidence = 0.5
        
        if not pitted:
            # Pit if tyres are very old
            if tyre_age > 20:
                should_pit = True
                target_compound = "HARD"  # Conservative choice
                confidence = min(0.9, 0.5 + (tyre_age - 20) * 0.02)
            
            # Or if on softs for too long
            elif compound == "SOFT" and tyre_age > 12:
                should_pit = True
                target_compound = "MEDIUM"
                confidence = 0.7
        
        if should_pit:
            return {
                "agent": "Heuristic (Rule-Based)",
                "pit": True,
                "compound": target_compound,
                "confidence": confidence,
                "q_value": None
            }
        else:
            return {
                "agent": "Heuristic (Rule-Based)",
                "pit": False,
                "compound": None,
                "confidence": 0.65,
                "q_value": None
            }
    
    def _softmax_confidence(self, q_values: np.ndarray, action: int) -> float:
        """Calculate confidence using softmax"""
        # Shift values to avoid overflow
        shifted = q_values - np.max(q_values)
        exp_vals = np.exp(shifted / 100)  # Temperature = 100
        probs = exp_vals / np.sum(exp_vals)
        return probs[action]
    
    def _calculate_consensus(self, recommendations: Dict) -> Dict:
        """Calculate consensus from all agent recommendations"""
        if not recommendations:
            return None
        
        # Count votes
        pit_votes = sum(1 for rec in recommendations.values() if rec["pit"])
        stay_votes = len(recommendations) - pit_votes
        
        # Majority decision
        consensus_pit = pit_votes > stay_votes
        
        if consensus_pit:
            # Find most common compound among pit recommendations
            compounds = [rec["compound"] for rec in recommendations.values() if rec["pit"]]
            if compounds:
                from collections import Counter
                most_common = Counter(compounds).most_common(1)[0][0]
                
                # Average confidence of agreeing agents
                agreeing_confidences = [
                    rec["confidence"] for rec in recommendations.values()
                    if rec["pit"] and rec["compound"] == most_common
                ]
                avg_confidence = np.mean(agreeing_confidences) if agreeing_confidences else 0.5
                
                return {
                    "pit": True,
                    "compound": most_common,
                    "support": f"{pit_votes}/{len(recommendations)} agents",
                    "confidence": float(avg_confidence)
                }
        
        # Consensus: stay out
        agreeing_confidences = [
            rec["confidence"] for rec in recommendations.values() if not rec["pit"]
        ]
        avg_confidence = np.mean(agreeing_confidences) if agreeing_confidences else 0.5
        
        return {
            "pit": False,
            "compound": None,
            "support": f"{stay_votes}/{len(recommendations)} agents",
            "confidence": float(avg_confidence)
        }
