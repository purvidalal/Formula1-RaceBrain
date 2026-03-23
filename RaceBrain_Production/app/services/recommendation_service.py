"""
Recommendation Service
"""
from typing import Dict
from multi_agent.agent_manager import AgentManager
from rag_service import RAGService

class RecommendationService:
    def __init__(self):
        self.agent_manager = AgentManager()
        self.agent_manager.load_agents()
        try:
            self.rag_service = RAGService()
        except Exception as e:
            self.rag_service = None
            print(f"⚠️  RAG service not available: {e}")
    
    def get_recommendations(self, race_state: Dict, team: str) -> Dict:
        """Get AI recommendations with optional RAG explanations"""
        
        # Validate race_state
        if not race_state or 'cars' not in race_state:
            print(f"ERROR: Invalid race state - {race_state}")
            raise ValueError("Invalid race state")
        
        # Get the player's car state
        player_car = None
        for car in race_state['cars']:
            if car.get('team') == team:
                player_car = car
                break
        
        if not player_car:
            print(f"ERROR: Team {team} not found in race")
            raise ValueError(f"Team {team} not found in race")
        
        # Prepare state for agents
        agent_state = {
            'current_lap': race_state.get('current_lap', 1),
            'position': player_car.get('position', 1),
            'compound': player_car.get('compound', 'MEDIUM'),
            'tyre_age': player_car.get('tyre_age', 0),
            'has_pitted': player_car.get('has_pitted', False)
        }
        
        print(f"DEBUG: Getting recommendations for {team}, state: {agent_state}")
        
        # Get recommendations from all agents
        recommendations = self.agent_manager.get_recommendations(
            lap=agent_state['current_lap'],
            tyre_age=agent_state['tyre_age'],
            compound=agent_state['compound'],
            position=agent_state['position'],
            pitted=agent_state['has_pitted']
        )
        
        print(f"DEBUG: Got recommendations: {recommendations}")
        
        # FIRST: Convert recommendations dict to array for frontend
        if 'recommendations' in recommendations and isinstance(recommendations['recommendations'], dict):
            recs_array = []
            for agent_name, rec in recommendations['recommendations'].items():
                # Convert pit/compound to action format
                if rec.get('pit', False):
                    compound = rec.get('compound', 'SOFT')
                    action = f'PIT_{compound}'
                else:
                    action = 'STAY_OUT'
                
                recs_array.append({
                    'agent': rec.get('agent', agent_name),
                    'action': action,
                    'confidence': rec.get('confidence', 0.5)
                })
            recommendations['recommendations'] = recs_array
        
        # Fix consensus format
        if 'consensus' in recommendations and recommendations['consensus']:
            cons = recommendations['consensus']
            if cons.get('pit', False):
                compound = cons.get('compound', 'SOFT')
                cons['action'] = f'PIT_{compound}'
            else:
                cons['action'] = 'STAY_OUT'
            
            # Convert support to votes (e.g. "5/5 agents" -> 5)
            if 'support' in cons:
                votes = int(cons['support'].split('/')[0])
                cons['votes'] = votes
        
        # THEN: Add RAG explanation (after action conversion)
        if self.rag_service:
            try:
                explanation = self.rag_service.generate_explanation(agent_state, recommendations)
                recommendations['explanation'] = explanation
                print(f"DEBUG: Added RAG explanation")
            except Exception as e:
                print(f"⚠️  RAG explanation failed: {e}")
                recommendations['explanation'] = None
        else:
            recommendations['explanation'] = None
        
        return recommendations

# Create singleton instance
recommendation_service = RecommendationService()
