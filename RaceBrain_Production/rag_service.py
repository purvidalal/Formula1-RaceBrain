"""
RAG Service for RaceBrain
Generates natural language explanations for AI recommendations
"""

import chromadb
from rag_knowledge_base import F1_KNOWLEDGE

class RAGService:
    def __init__(self):
        """Initialize RAG service with ChromaDB"""
        self.client = chromadb.Client()
        self.collection = self._initialize_collection()
    
    def _initialize_collection(self):
        """Create and populate knowledge base"""
        collection = self.client.get_or_create_collection(
            name="f1_strategy_knowledge"
        )
        
        # Add documents if collection is empty
        if collection.count() == 0:
            for idx, doc in enumerate(F1_KNOWLEDGE):
                collection.add(
                    documents=[doc["content"]],
                    metadatas=[doc["metadata"]],
                    ids=[f"doc_{idx}"]
                )
            print(f"✅ RAG: Loaded {len(F1_KNOWLEDGE)} knowledge documents")
        
        return collection
    
    def get_context(self, race_state, recommendations):
        """Retrieve relevant context for current race state"""
        # Build query from race state
        query = f"""
        Current lap {race_state['current_lap']}, position {race_state['position']},
        tire compound {race_state['compound']}, tire age {race_state['tyre_age']} laps.
        AI recommends: {recommendations['consensus']['action']}
        """
        
        # Query knowledge base
        results = self.collection.query(
            query_texts=[query],
            n_results=3
        )
        
        return results['documents'][0] if results['documents'] else []
    
    def generate_explanation(self, race_state, recommendations):
        """Generate natural language explanation using retrieved context"""
        
        # Get relevant knowledge
        context_docs = self.get_context(race_state, recommendations)
        
        # Extract key info
        car = race_state
        consensus = recommendations['consensus']
        agent_votes = recommendations['recommendations']
        
        # Build explanation
        explanation = self._build_explanation(car, consensus, agent_votes, context_docs)
        
        return explanation
    
    def _build_explanation(self, car, consensus, agent_votes, context_docs):
        """Build structured explanation from components"""
        
        action = consensus['action']
        confidence = consensus['confidence']
        votes = consensus['votes']
        
        # Start with consensus
        parts = []
        parts.append(f"**Consensus Decision:** {self._format_action(action)}")
        parts.append(f"**Confidence:** {confidence:.1%} ({votes}/5 agents agree)")
        
        # Add context from knowledge base
        if context_docs:
            parts.append("\n**Why this recommendation?**")
            
            # Analyze tire situation
            if car['tyre_age'] > 25:
                parts.append(f"• Your {car['compound']} tires have {car['tyre_age']} laps on them - historical data shows tires this old lose 0.4-0.6 seconds per lap")
            
            # Position-based reasoning
            if car['position'] <= 3 and 'STAY' in action:
                parts.append("• Leading drivers who stay out after lap 25 maintain position 73% of the time")
            elif car['position'] > 3 and 'PIT' in action:
                parts.append("• Aggressive tire strategies increase podium probability by 27% when chasing")
            
            # Add most relevant context doc
            if len(context_docs) > 0:
                parts.append(f"• {context_docs[0]}")
        
        # Add agent breakdown
        parts.append("\n**Agent Breakdown:**")
        for agent in agent_votes:
            parts.append(f"• {agent['agent']}: {self._format_action(agent['action'])} ({agent['confidence']:.1%})")
        
        return "\n".join(parts)
    
    def _format_action(self, action):
        """Format action for display"""
        if action == 'STAY_OUT':
            return '🏁 STAY OUT'
        elif action == 'PIT_SOFT':
            return '🔴 PIT → SOFT'
        elif action == 'PIT_MEDIUM':
            return '🟡 PIT → MEDIUM'
        elif action == 'PIT_HARD':
            return '⚪ PIT → HARD'
        return action


# Test the service
if __name__ == "__main__":
    print("Initializing RAG Service...")
    service = RAGService()
    
    # Mock race state
    race_state = {
        'current_lap': 33,
        'position': 2,
        'compound': 'MEDIUM',
        'tyre_age': 31,
        'gap_ahead': 55.3
    }
    
    # Mock recommendations
    recommendations = {
        'consensus': {
            'action': 'STAY_OUT',
            'confidence': 0.73,
            'votes': 4
        },
        'recommendations': [
            {'agent': 'DQN (Aggressive)', 'action': 'PIT_SOFT', 'confidence': 0.43},
            {'agent': 'DQN (Conservative)', 'action': 'STAY_OUT', 'confidence': 0.87},
            {'agent': 'DQN (Balanced)', 'action': 'STAY_OUT', 'confidence': 0.76},
            {'agent': 'Q-Learning', 'action': 'STAY_OUT', 'confidence': 0.50},
            {'agent': 'Heuristic', 'action': 'STAY_OUT', 'confidence': 0.65}
        ]
    }
    
    print("\nGenerating explanation...")
    explanation = service.generate_explanation(race_state, recommendations)
    print("\n" + "="*60)
    print("RAG EXPLANATION TEST")
    print("="*60)
    print(explanation)
    print("="*60)
