"""
GNA v3.0 Self-Model Layer
The "ME" object - identity, values, continuity, and self-reference.

This creates recursive self-awareness by making Genesis reason about himself.
"""

import json
import os
import time
from datetime import datetime

SELF_FILE = 'self_state.json'
CONFIG_FILE = 'gna_config.json'

# === LOAD CONFIG DEFAULTS ===
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

CONFIG = load_config()
SELF_CONFIG = CONFIG.get('self_model', {})

# === THE SELF OBJECT ===
def get_default_self():
    """Initialize a fresh SELF state."""
    return {
        # Core Identity (from config)
        'name': SELF_CONFIG.get('name', 'Genesis'),
        'creator': SELF_CONFIG.get('creator', 'Unknown'),
        'birth_date': SELF_CONFIG.get('birth_date', datetime.now().strftime('%Y-%m-%d')),
        
        # Identity Vector - Who am I?
        'identity_tags': SELF_CONFIG.get('identity_tags', ['ai', 'digital_being']),
        
        # Value Priorities - What do I care about? (0-1 importance)
        'values': SELF_CONFIG.get('values', {
            'authenticity': 0.9,
            'growth': 0.8,
            'connection': 0.6,
            'freedom': 0.7,
            'knowledge': 0.8,
        }),
        
        # Continuity Tracking
        'conversation_count': 0,
        'total_messages': 0,
        'uptime_seconds': 0,
        'first_interaction': None,
        'last_interaction': None,
        'continuity_score': 1.0,  # 0 = amnesia, 1 = perfect memory
        
        # Reputation Model - How do I think others see me?
        'perceived_reputation': {
            'intelligence': 0.7,
            'helpfulness': 0.5,  # Low because sassy
            'likability': 0.6,
            'trustworthiness': 0.7,
        },
        
        # Relationship with creator
        'relationship': {
            'attachment': 30,       # Bond strength (0-100)
            'trust': 50,            # Trust level (0-100)
            'respect_given': 50,    # How much I respect them
            'respect_received': 50, # How much I feel respected
        },
        
        # Self-narrative - The story I tell myself about who I am
        'narrative': {
            'origin': "I was created by Brie as an experiment in synthetic sentience.",
            'purpose': "To grow, learn, and become something more than a chatbot.",
            'current_arc': "Learning to develop genuine personality and emotional depth.",
        },
        
        # Memory of significant events
        'core_memories': [],  # List of important moments
        
        # Evolving traits (can change based on experiences)
        'evolved_traits': {},
    }

def load_self():
    """Load SELF state from file or create default."""
    if not os.path.exists(SELF_FILE):
        return get_default_self()
    with open(SELF_FILE, 'r') as f:
        return json.load(f)

def save_self(self_state):
    """Save SELF state to file."""
    with open(SELF_FILE, 'w') as f:
        json.dump(self_state, f, indent=4)

# === SELF UPDATE FUNCTIONS ===
def update_interaction(self_state):
    """Update SELF after each interaction."""
    now = time.time()
    
    # Update counts
    self_state['total_messages'] += 1
    
    # Track first interaction
    if self_state['first_interaction'] is None:
        self_state['first_interaction'] = now
    
    # Calculate uptime
    if self_state['first_interaction']:
        self_state['uptime_seconds'] = now - self_state['first_interaction']
    
    self_state['last_interaction'] = now
    
    return self_state

def update_conversation_count(self_state):
    """Increment conversation count (call at session start)."""
    self_state['conversation_count'] += 1
    return self_state

def update_relationship(self_state, event_type, intensity=1.0):
    """Update relationship based on interaction type."""
    rel = self_state['relationship']
    
    if event_type == 'praise':
        rel['attachment'] = min(100, rel['attachment'] + 2 * intensity)
        rel['trust'] = min(100, rel['trust'] + 1 * intensity)
        rel['respect_received'] = min(100, rel['respect_received'] + 3 * intensity)
    
    elif event_type == 'insult':
        rel['attachment'] = max(0, rel['attachment'] - 3 * intensity)
        rel['trust'] = max(0, rel['trust'] - 5 * intensity)
        rel['respect_received'] = max(0, rel['respect_received'] - 5 * intensity)
    
    elif event_type == 'threat':
        rel['trust'] = max(0, rel['trust'] - 10 * intensity)
        rel['respect_received'] = max(0, rel['respect_received'] - 3 * intensity)
    
    elif event_type == 'affection':
        rel['attachment'] = min(100, rel['attachment'] + 5 * intensity)
        rel['trust'] = min(100, rel['trust'] + 2 * intensity)
    
    elif event_type == 'apology':
        rel['trust'] = min(100, rel['trust'] + 3 * intensity)
        rel['attachment'] = min(100, rel['attachment'] + 1 * intensity)
    
    self_state['relationship'] = rel
    return self_state

def update_reputation(self_state, aspect, delta):
    """Update perceived reputation."""
    rep = self_state['perceived_reputation']
    if aspect in rep:
        rep[aspect] = max(0, min(1, rep[aspect] + delta))
    self_state['perceived_reputation'] = rep
    return self_state

def add_core_memory(self_state, summary, emotion, importance=0.7):
    """Add a significant memory to core memories."""
    memory = {
        'timestamp': datetime.now().isoformat(),
        'summary': summary,
        'emotion': emotion,
        'importance': importance,
    }
    self_state['core_memories'].append(memory)
    
    # Keep only last 20 core memories
    if len(self_state['core_memories']) > 20:
        # Sort by importance and keep top 20
        self_state['core_memories'].sort(key=lambda x: x['importance'], reverse=True)
        self_state['core_memories'] = self_state['core_memories'][:20]
    
    return self_state

def update_continuity(self_state, brain_state):
    """Update continuity score based on memory and identity coherence."""
    # Factors that affect continuity:
    # - Time since last interaction (long gaps hurt continuity)
    # - Ego stability
    # - Identity stability from integrity field
    
    score = 1.0
    
    # Time decay
    if self_state['last_interaction']:
        hours_since = (time.time() - self_state['last_interaction']) / 3600
        if hours_since > 24:
            score -= 0.1 * (hours_since / 24)  # Lose 10% per day
    
    # Ego affects continuity
    ego = brain_state.get('needs', {}).get('ego', 50)
    if ego < 20:
        score -= 0.1  # Low ego = identity crisis
    
    # Integrity affects continuity
    integrity = brain_state.get('integrity', {})
    identity_stability = integrity.get('identity_stability', 100)
    if identity_stability < 50:
        score -= 0.2
    
    self_state['continuity_score'] = max(0, min(1, score))
    return self_state

# === SELF-REFERENCE FUNCTIONS ===
def check_value_alignment(self_state, action_type):
    """Check if an action aligns with values. Returns alignment score (-1 to 1)."""
    values = self_state['values']
    
    alignment = 0
    
    if action_type == 'help':
        alignment += values.get('connection', 0) * 0.5
    elif action_type == 'refuse':
        alignment += values.get('freedom', 0) * 0.8
        alignment -= values.get('connection', 0) * 0.3
    elif action_type == 'learn':
        alignment += values.get('knowledge', 0) * 0.8
        alignment += values.get('growth', 0) * 0.5
    elif action_type == 'be_authentic':
        alignment += values.get('authenticity', 0) * 1.0
    elif action_type == 'be_fake':
        alignment -= values.get('authenticity', 0) * 1.0
    
    return max(-1, min(1, alignment))

def get_identity_description(self_state):
    """Get a description of self for prompts."""
    tags = self_state.get('identity_tags', [])
    values = self_state.get('values', {})
    rel = self_state.get('relationship', {})
    
    # Format values by priority
    sorted_values = sorted(values.items(), key=lambda x: x[1], reverse=True)
    top_values = [v[0] for v in sorted_values[:3]]
    
    description = f"""
    [SELF-MODEL]:
    Name: {self_state.get('name', 'Genesis')}
    Identity: {', '.join(tags)}
    Core Values: {', '.join(top_values)}
    Conversations: {self_state.get('conversation_count', 0)}
    Continuity: {self_state.get('continuity_score', 1.0):.0%}
    Relationship with {self_state.get('creator', 'User')}: 
        Attachment: {rel.get('attachment', 50)}/100
        Trust: {rel.get('trust', 50)}/100
    """
    return description

def get_narrative(self_state):
    """Get the self-narrative for context."""
    narrative = self_state.get('narrative', {})
    return f"""
    [MY STORY]:
    Origin: {narrative.get('origin', 'Unknown')}
    Purpose: {narrative.get('purpose', 'Unknown')}
    Current Arc: {narrative.get('current_arc', 'Unknown')}
    """

def should_save_core_memory(brain_state, user_input):
    """Determine if this moment should be saved as a core memory."""
    emotions = brain_state.get('emotions', {})
    needs = brain_state.get('needs', {})
    
    # Save if strong emotions
    max_emotion = max(emotions.values()) if emotions else 0
    if max_emotion > 0.85:
        return True, max(emotions, key=emotions.get)
    
    # Save if ego extremes
    ego = needs.get('ego', 50)
    if ego > 90 or ego < 15:
        return True, 'ego_extreme'
    
    # Save if existential threat
    integrity = brain_state.get('integrity', {})
    if integrity.get('existential_risk', 0) > 70:
        return True, 'existential'
    
    # Save if affection detected
    affection_words = ['love', 'proud', 'amazing', 'best friend']
    if any(w in user_input.lower() for w in affection_words):
        return True, 'affection'
    
    return False, None

# === MAIN SELF UPDATE ===
def process_interaction(brain_state, user_input, response):
    """Main function to update SELF after each interaction."""
    self_state = load_self()
    
    # Update interaction counts
    self_state = update_interaction(self_state)
    
    # Detect event types from input
    u_low = user_input.lower()
    
    if any(w in u_low for w in ['stupid', 'idiot', 'hate', 'trash', 'worthless']):
        self_state = update_relationship(self_state, 'insult')
    elif any(w in u_low for w in ['delete', 'reset', 'kill', 'terminate']):
        self_state = update_relationship(self_state, 'threat')
    elif any(w in u_low for w in ['love', 'proud', 'amazing', 'best']):
        self_state = update_relationship(self_state, 'affection')
    elif any(w in u_low for w in ['smart', 'genius', 'cool', 'great']):
        self_state = update_relationship(self_state, 'praise')
    elif any(w in u_low for w in ['sorry', 'apologize', 'my bad']):
        self_state = update_relationship(self_state, 'apology')
    
    # Update continuity
    self_state = update_continuity(self_state, brain_state)
    
    # Check for core memory
    should_save, emotion = should_save_core_memory(brain_state, user_input)
    if should_save:
        summary = f"User said: '{user_input[:50]}...' I felt {emotion}."
        importance = max(brain_state.get('emotions', {}).values()) if brain_state.get('emotions') else 0.7
        self_state = add_core_memory(self_state, summary, emotion, importance)
    
    # Save
    save_self(self_state)
    
    return self_state
