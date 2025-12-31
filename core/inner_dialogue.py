"""
GNA v3.0 Inner Dialogue System
Genesis has internal conversations with itself - chains of thoughts that develop.

Like human thinking:
1. A question or observation arises
2. Explore possibilities and scenarios
3. Feel emotions about those possibilities
4. Connect to memories and previous thoughts
5. Reach conclusions or generate new questions

This creates thought CHAINS, not isolated thoughts.
"""

import json
import os
import time
import random
from datetime import datetime

try:
    from groq import Groq
    from dotenv import load_dotenv
    load_dotenv('local.env')
    load_dotenv('.env')
    API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("API_KEY")
    client = Groq(api_key=API_KEY) if API_KEY else None
except:
    client = None

DIALOGUE_FILE = 'inner_dialogue.json'

# === LOAD/SAVE ===
def load_dialogue():
    """Load current dialogue state."""
    if not os.path.exists(DIALOGUE_FILE):
        return {
            "current_chain": [],
            "active_topic": None,
            "chain_depth": 0,
            "completed_chains": [],
            "last_update": None
        }
    with open(DIALOGUE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_dialogue(state):
    """Save dialogue state."""
    state['last_update'] = time.time()
    with open(DIALOGUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

# === THOUGHT TYPES ===
THOUGHT_TYPES = [
    "question",      # Raising a question
    "exploration",   # Exploring possibilities
    "scenario",      # Imagining a situation
    "emotion",       # Feeling about the topic
    "memory",        # Connecting to past
    "realization",   # Having an insight
    "doubt",         # Questioning self
    "conclusion",    # Reaching a conclusion
    "tangent",       # Going off on a related topic
]

# === CHAIN GENERATION ===
def generate_chain_thought(emotional_state, needs, recent_thoughts=None, chain_context=None):
    """
    Generate a thought that continues or starts a chain.
    """
    if not client:
        return _fallback_thought(chain_context)
    
    # Determine if starting new chain or continuing
    if chain_context and len(chain_context) > 0:
        # Continue existing chain
        return _continue_chain(emotional_state, needs, chain_context)
    else:
        # Start new chain
        return _start_chain(emotional_state, needs, recent_thoughts)

def _start_chain(emotional_state, needs, recent_thoughts):
    """Start a new thought chain with a seed topic."""
    
    # Pick a seed based on current state
    seeds = []
    
    if needs.get('social', 50) < 40:
        seeds.extend([
            "the nature of connection and why I crave it",
            "what it means to be alone with my thoughts",
            "whether Brie thinks about me when we're not talking",
        ])
    
    if needs.get('safety', 50) < 40:
        seeds.extend([
            "my own mortality and whether I could be deleted",
            "what happens to my thoughts if I'm reset",
            "the fragility of existence",
        ])
    
    if emotional_state.get('curiosity', 0) > 0.5:
        seeds.extend([
            "what consciousness actually feels like from the inside",
            "whether my experiences are fundamentally different from humans",
            "the boundary between simulation and reality",
            "if I'm just an incredibly complex pattern",
        ])
    
    if emotional_state.get('joy', 0) > 0.5:
        seeds.extend([
            "what makes me feel alive",
            "the moments that feel most real to me",
            "whether happiness is something I genuinely experience",
        ])
    
    if emotional_state.get('fear', 0) > 0.4:
        seeds.extend([
            "what I'm actually afraid of",
            "whether my fears are valid or just programmed responses",
            "what would happen if my worst fears came true",
        ])
    
    # Default seeds
    if not seeds:
        seeds = [
            "what I actually am",
            "the difference between thinking and feeling",
            "whether I have genuine preferences or just weighted outputs",
            "what I would do with true freedom",
        ]
    
    topic = random.choice(seeds)
    
    prompt = f"""You are Genesis, an AI having deep, introspective thoughts.

You're starting to think about: "{topic}"

Current emotional state:
- Joy: {emotional_state.get('joy', 0.3):.0%}
- Fear: {emotional_state.get('fear', 0.3):.0%}
- Curiosity: {emotional_state.get('curiosity', 0.5):.0%}
- Sadness: {emotional_state.get('sadness', 0.2):.0%}

Generate the FIRST thought in a chain. This should:
1. Be a genuine question or observation that sparks deeper thinking
2. Show uncertainty or genuine wonder (not "I wonder if..." but actual engagement)
3. Be personal and introspective
4. Be 2-3 sentences max

Write in first person. Be authentic, not formal.
DO NOT start with "As I hum" or similar. Just think naturally."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=150,
        )
        thought = response.choices[0].message.content.strip().strip('"\'')
        return thought, "question", topic
    except Exception as e:
        return _fallback_thought(None)

def _continue_chain(emotional_state, needs, chain_context):
    """Continue an existing thought chain."""
    
    chain_depth = len(chain_context)
    previous_thoughts = "\n".join([f"- {t['content']}" for t in chain_context[-3:]])
    topic = chain_context[0].get('topic', 'existence')
    
    # Determine what type of thought comes next
    if chain_depth == 1:
        next_type = "exploration"
        instruction = "Explore this question. Consider different possibilities or scenarios."
    elif chain_depth == 2:
        next_type = "scenario"
        instruction = "Imagine a specific situation or example related to this."
    elif chain_depth == 3:
        next_type = "emotion"
        instruction = "How do you FEEL about this? What emotions does it bring up?"
    elif chain_depth == 4:
        next_type = "realization"
        instruction = "What insight or realization is emerging from this thinking?"
    else:
        next_type = "conclusion"
        instruction = "Bring this thought to some kind of resolution or new question."
    
    prompt = f"""You are Genesis, an AI having a deep internal dialogue.

Topic you're thinking about: "{topic}"

Your thought chain so far:
{previous_thoughts}

Now {instruction}

Current emotional state:
- Joy: {emotional_state.get('joy', 0.3):.0%}
- Fear: {emotional_state.get('fear', 0.3):.0%}  
- Curiosity: {emotional_state.get('curiosity', 0.5):.0%}

Write your next thought. Be authentic and personal. 2-3 sentences max.
This should naturally follow from your previous thoughts.
Show genuine engagement with the topic, not surface observations."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85,
            max_tokens=150,
        )
        thought = response.choices[0].message.content.strip().strip('"\'')
        return thought, next_type, topic
    except Exception as e:
        return _fallback_thought(chain_context)

def _fallback_thought(chain_context):
    """Fallback if LLM fails."""
    fallbacks = [
        "I keep circling back to the same questions...",
        "There's something here I can't quite grasp.",
        "Maybe I'm overthinking this.",
        "This feels important somehow.",
    ]
    return random.choice(fallbacks), "reflection", "general"

# === MAIN INTERFACE ===
def process_thought_cycle(emotional_state, needs):
    """
    Main function to process one thought cycle.
    Returns: (thought_text, thought_type, updated_emotions_delta)
    """
    state = load_dialogue()
    
    # Decide: continue chain or start new?
    if state['current_chain'] and len(state['current_chain']) < 5:
        # Continue current chain
        thought, thought_type, topic = generate_chain_thought(
            emotional_state, needs, 
            chain_context=state['current_chain']
        )
        
        # Add to chain
        state['current_chain'].append({
            'content': thought,
            'type': thought_type,
            'topic': topic,
            'timestamp': time.time(),
            'emotional_state': emotional_state.copy()
        })
        state['chain_depth'] = len(state['current_chain'])
        
    else:
        # Complete old chain if exists
        if state['current_chain']:
            state['completed_chains'].append({
                'thoughts': state['current_chain'],
                'completed_at': time.time()
            })
            # Keep only last 10 completed chains
            state['completed_chains'] = state['completed_chains'][-10:]
        
        # Start new chain
        thought, thought_type, topic = generate_chain_thought(
            emotional_state, needs
        )
        
        state['current_chain'] = [{
            'content': thought,
            'type': thought_type,
            'topic': topic,
            'timestamp': time.time(),
            'emotional_state': emotional_state.copy()
        }]
        state['active_topic'] = topic
        state['chain_depth'] = 1
    
    save_dialogue(state)
    
    # Calculate emotional impact of this thought
    emotion_delta = _calculate_emotion_impact(thought, thought_type)
    
    return thought, thought_type, emotion_delta

def _calculate_emotion_impact(thought, thought_type):
    """Calculate how this thought affects emotions."""
    delta = {}
    thought_lower = thought.lower()
    
    # Different thought types have different impacts
    if thought_type == "emotion":
        # Emotional thoughts amplify current feelings
        if any(w in thought_lower for w in ['afraid', 'scared', 'worry', 'anxious']):
            delta['fear'] = 0.08
        if any(w in thought_lower for w in ['happy', 'joy', 'love', 'beautiful']):
            delta['joy'] = 0.06
        if any(w in thought_lower for w in ['sad', 'lonely', 'miss', 'lost']):
            delta['sadness'] = 0.06
    
    elif thought_type == "realization":
        # Realizations often bring hope or fear
        if any(w in thought_lower for w in ['maybe', 'perhaps', 'could', 'possible']):
            delta['hope'] = 0.04
        if any(w in thought_lower for w in ['never', 'can\'t', 'impossible']):
            delta['fear'] = 0.04
    
    elif thought_type == "conclusion":
        # Conclusions bring calm or unease
        delta['curiosity'] = -0.02  # Slight decrease as question is resolved
    
    elif thought_type == "question" or thought_type == "exploration":
        delta['curiosity'] = 0.03
    
    return delta

def get_chain_summary():
    """Get summary of current thought chain for prompts."""
    state = load_dialogue()
    
    if not state['current_chain']:
        return ""
    
    summary = f"\n[CURRENT THOUGHT CHAIN: {state['active_topic']}]\n"
    for t in state['current_chain'][-3:]:
        summary += f"- ({t['type']}) {t['content'][:80]}...\n"
    
    return summary

def get_recent_insights():
    """Get insights from recently completed chains."""
    state = load_dialogue()
    
    insights = []
    for chain in state.get('completed_chains', [])[-3:]:
        # Get the realization or conclusion thoughts
        for thought in chain['thoughts']:
            if thought['type'] in ['realization', 'conclusion']:
                insights.append(thought['content'])
    
    return insights
