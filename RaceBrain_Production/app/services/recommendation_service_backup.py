"""
Recommendation Service with RAG Integration
"""

from typing import Dict, List
from multi_agent.agent_manager import AgentManager
from rag_service import RAGService

class RecommendationService:
    def __init__(self):
        self.agent_manager = AgentManager()
        self.rag_service = RAGService()
    
    def get_recommendations(self, race_state: Dict, team: str) -> Dict:
        """Get AI recommendations with RAG explanations"""
        
        # Get the player's car state
        player_car = next((car for car in race_state['cars'] if car['team'] == team), None)
        if not player_car:
            raise ValueError(f"Team {team} not found in race")
        
        # Prepare state for agents
        agent_state = {
            'current_lap': race_state['current_lap'],
            'position': player_car['position'],
            'compound': player_car['compound'],
            'tyre_age': player_car['tyre_age'],
            'has_pitted': player_car['has_pitted']
        }
        
        # Get recommendations from all agents
        recommendations = self.agent_manager.get_recommendations(agent_state)
        
        # Generate RAG explanation
        explanation = self.rag_service.generate_explanation(agent_state, recommendations)
        
        # Add explanation to response
        recommendations['explanation'] = explanation
        
        return recommendations
