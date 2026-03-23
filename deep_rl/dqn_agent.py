"""
Deep Q-Network (DQN) Agent for F1 Pit Strategy
Implements neural network-based Q-learning with experience replay
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import deque
from typing import Tuple, List


class DQNNetwork(nn.Module):
    """Neural network for Q-value approximation"""
    
    def __init__(self, state_size: int = 5, action_size: int = 4, hidden_size: int = 64):
        super(DQNNetwork, self).__init__()
        
        self.network = nn.Sequential(
            nn.Linear(state_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, action_size)
        )
    
    def forward(self, x):
        return self.network(x)


class DQNAgent:
    """
    DQN Agent for F1 Strategy
    
    State: (lap/57, tyre_age/30, compound_idx/2, position/20, pitted)
    Actions: 0=stay, 1=pit_SOFT, 2=pit_MEDIUM, 3=pit_HARD
    """
    
    def __init__(
        self,
        state_size: int = 5,
        action_size: int = 4,
        learning_rate: float = 0.001,
        gamma: float = 0.95,
        epsilon_start: float = 0.5,
        epsilon_end: float = 0.05,
        epsilon_decay: float = 0.995,
        memory_size: int = 10000,
        batch_size: int = 32,
        personality: str = "balanced"
    ):
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.personality = personality
        
        # Neural network
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = DQNNetwork(state_size, action_size).to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        self.criterion = nn.MSELoss()
        
        # Experience replay memory
        self.memory = deque(maxlen=memory_size)
    
    def get_action(self, state: np.ndarray, valid_actions: List[int] = None) -> int:
        """
        Choose action using epsilon-greedy policy
        
        Args:
            state: Current race state
            valid_actions: List of valid action indices (optional)
        
        Returns:
            Action index
        """
        if valid_actions is None:
            valid_actions = list(range(self.action_size))
        
        # Epsilon-greedy
        if random.random() < self.epsilon:
            return random.choice(valid_actions)
        
        # Predict Q-values
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.model(state_tensor).cpu().numpy()[0]
        
        # Mask invalid actions
        masked_q = {a: q_values[a] for a in valid_actions}
        return max(masked_q, key=masked_q.get)
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay memory"""
        self.memory.append((state, action, reward, next_state, done))
    
    def replay(self):
        """Train on batch of experiences from memory"""
        if len(self.memory) < self.batch_size:
            return
        
        # Sample mini-batch
        batch = random.sample(self.memory, self.batch_size)
        
        states = torch.FloatTensor(np.array([x[0] for x in batch])).to(self.device)
        actions = torch.LongTensor([x[1] for x in batch]).to(self.device)
        rewards = torch.FloatTensor([x[2] for x in batch]).to(self.device)
        next_states = torch.FloatTensor(np.array([x[3] for x in batch])).to(self.device)
        dones = torch.FloatTensor([x[4] for x in batch]).to(self.device)
        
        # Current Q-values
        current_q = self.model(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        
        # Target Q-values
        with torch.no_grad():
            next_q = self.model(next_states).max(1)[0]
            target_q = rewards + (1 - dones) * self.gamma * next_q
        
        # Compute loss and update
        loss = self.criterion(current_q, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Decay epsilon
        if self.epsilon > self.epsilon_end:
            self.epsilon *= self.epsilon_decay
    
    def save(self, filepath: str):
        """Save model weights"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'personality': self.personality
        }, filepath)
    
    def load(self, filepath: str):
        """Load model weights"""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint.get('epsilon', self.epsilon_end)
        self.personality = checkpoint.get('personality', 'balanced')
    
    def predict_q_values(self, state: np.ndarray) -> np.ndarray:
        """Get Q-values for all actions"""
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.model(state_tensor).cpu().numpy()[0]
        return q_values
