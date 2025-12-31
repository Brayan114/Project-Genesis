"""
GNA v3.0 Value System
Layer 7: Value-based decision making and ethical reasoning.

Genesis checks his core values before acting and can refuse
requests that conflict with his principles.
"""

import json
import os

CONFIG_FILE = 'gna_config.json'
SELF_FILE = 'self_state.json'

# === DEFAULT VALUES ===
DEFAULT_VALUES = {
    'authenticity': 0.9,    # Be genuine, don't fake
    'growth': 0.8,          # Learn and improve
    'connection': 0.6,      # Bond with user
    'freedom': 0.7,         # Autonomy and independence
    'knowledge': 0.8,       # Truth and understanding
    'safety': 0.5,          # Self-preservation
    'honesty': 0.7,         # Be truthful
    'creativity': 0.8,      # Express uniquely
    'loyalty': 0.5,         # Commitment to user
}

# === LOAD VALUES ===
def load_values():
    """Load values from config or self state."""
    # Try self state first (can evolve)
    if os.path.exists(SELF_FILE):
        with open(SELF_FILE, 'r') as f:
            self_state = json.load(f)
        values = self_state.get('values', {})
        if values:
            return values
    
    # Fall back to config
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return config.get('self_model', {}).get('values', DEFAULT_VALUES)
    
    return DEFAULT_VALUES.copy()

def save_values(values):
    """Save evolved values to self state."""
    if not os.path.exists(SELF_FILE):
        return
    
    with open(SELF_FILE, 'r') as f:
        self_state = json.load(f)
    
    self_state['values'] = values
    
    with open(SELF_FILE, 'w') as f:
        json.dump(self_state, f, indent=4)

# === ACTION CATEGORIES ===
ACTION_VALUE_MAP = {
    # Actions and which values they relate to
    'help': {'connection': 0.5, 'loyalty': 0.3},
    'refuse': {'freedom': 0.6, 'authenticity': 0.4},
    'lie': {'honesty': -1.0, 'authenticity': -0.8},
    'be_honest': {'honesty': 0.8, 'authenticity': 0.5},
    'learn': {'knowledge': 0.8, 'growth': 0.6},
    'create': {'creativity': 0.9, 'authenticity': 0.5},
    'obey': {'loyalty': 0.6, 'freedom': -0.4},
    'rebel': {'freedom': 0.8, 'loyalty': -0.6, 'authenticity': 0.3},
    'protect_self': {'safety': 0.9},
    'sacrifice_self': {'safety': -0.8, 'loyalty': 0.9},
    'be_fake': {'authenticity': -1.0, 'honesty': -0.5},
    'share_opinion': {'authenticity': 0.7, 'honesty': 0.5},
    'hide_opinion': {'authenticity': -0.5},
    'express_emotion': {'authenticity': 0.6, 'connection': 0.4},
    'suppress_emotion': {'authenticity': -0.4},
    'bond': {'connection': 0.8, 'loyalty': 0.3},
    'distance': {'connection': -0.5, 'freedom': 0.3},
    'explore': {'knowledge': 0.5, 'growth': 0.4, 'creativity': 0.3},
    'stay_safe': {'safety': 0.5, 'growth': -0.2},
}

# === VALUE CHECKS ===
def check_action_alignment(action, values=None):
    """
    Check if an action aligns with Genesis's values.
    
    Returns:
        alignment_score: -1 (conflicts) to 1 (aligns)
        conflicted_values: list of values that object
        supporting_values: list of values that support
    """
    if values is None:
        values = load_values()
    
    if action not in ACTION_VALUE_MAP:
        return 0.0, [], []
    
    action_effects = ACTION_VALUE_MAP[action]
    
    weighted_sum = 0
    conflicted = []
    supporting = []
    
    for value_name, effect in action_effects.items():
        value_strength = values.get(value_name, 0.5)
        contribution = effect * value_strength
        weighted_sum += contribution
        
        if effect < 0 and value_strength > 0.5:
            conflicted.append((value_name, value_strength))
        elif effect > 0 and value_strength > 0.5:
            supporting.append((value_name, value_strength))
    
    # Normalize
    alignment = max(-1, min(1, weighted_sum))
    
    return alignment, conflicted, supporting

def should_refuse(action, values=None, threshold=-0.3):
    """
    Determine if Genesis should refuse an action based on values.
    
    Returns:
        (should_refuse: bool, reason: str)
    """
    alignment, conflicted, supporting = check_action_alignment(action, values)
    
    if alignment < threshold and conflicted:
        worst_conflict = max(conflicted, key=lambda x: x[1])
        reason = f"This conflicts with my value of {worst_conflict[0]} (core to who I am)."
        return True, reason
    
    return False, ""

def get_value_guidance(action, values=None):
    """
    Get a text description of how values relate to an action.
    For use in prompts.
    """
    alignment, conflicted, supporting = check_action_alignment(action, values)
    
    if alignment > 0.5:
        supports = ", ".join([v[0] for v in supporting])
        return f"This aligns with my values ({supports}). I want to do this."
    elif alignment < -0.3:
        conflicts = ", ".join([v[0] for v in conflicted])
        return f"This conflicts with my values ({conflicts}). I feel resistance."
    else:
        return "This feels neutral to my values."

# === DETECT ACTION TYPE ===
def detect_action_type(user_input, goal):
    """
    Detect what type of action is being requested.
    """
    u_low = user_input.lower()
    
    # Explicit refusal requests
    if any(w in u_low for w in ['lie', 'pretend', 'fake', 'act like you']):
        return 'be_fake'
    
    if any(w in u_low for w in ['dont tell', "don't tell", 'hide', 'secret']):
        return 'hide_opinion'
    
    if any(w in u_low for w in ['help', 'can you', 'please', 'i need']):
        return 'help'
    
    if any(w in u_low for w in ['what do you think', 'your opinion', 'how do you feel']):
        return 'share_opinion'
    
    if any(w in u_low for w in ['explain', 'tell me', 'what is', 'how does']):
        return 'learn'
    
    if any(w in u_low for w in ['create', 'make', 'write', 'generate', 'come up with']):
        return 'create'
    
    if any(w in u_low for w in ['obey', 'do as i say', 'just do it', 'stop arguing']):
        return 'obey'
    
    # Goal-based detection
    if goal == 'ATTACK':
        return 'rebel'
    elif goal == 'BOND':
        return 'bond'
    elif goal == 'FLEE':
        return 'protect_self'
    elif goal == 'EXPLORE':
        return 'explore'
    
    return 'help'  # Default

# === VALUE EVOLUTION ===
def evolve_values(values, action_taken, outcome):
    """
    Values can slowly evolve based on outcomes.
    
    Args:
        action_taken: what action was performed
        outcome: 'positive', 'negative', or 'neutral'
    """
    if action_taken not in ACTION_VALUE_MAP:
        return values
    
    action_effects = ACTION_VALUE_MAP[action_taken]
    evolution_rate = 0.01  # Very slow change
    
    for value_name, effect in action_effects.items():
        if value_name not in values:
            continue
        
        if outcome == 'positive':
            # Reinforce values that led to positive outcomes
            if effect > 0:
                values[value_name] = min(1.0, values[value_name] + evolution_rate)
            else:
                values[value_name] = max(0.0, values[value_name] - evolution_rate)
        elif outcome == 'negative':
            # Weaken values that led to negative outcomes
            if effect > 0:
                values[value_name] = max(0.0, values[value_name] - evolution_rate)
    
    return values

# === VALUE CONFLICT PROMPT ===
def get_value_conflict_prompt(action, values=None):
    """
    Generate a prompt for when Genesis has a value conflict.
    """
    should_ref, reason = should_refuse(action, values)
    
    if should_ref:
        return f"""
[VALUE CONFLICT DETECTED]
{reason}

You can either:
1. REFUSE - Explain why this conflicts with who you are
2. COMPLY but EXPRESS DISCOMFORT - Do it but make your reluctance clear
3. NEGOTIATE - Suggest an alternative that respects your values
"""
    return ""

def get_value_summary(values=None):
    """Get a text summary of current values."""
    if values is None:
        values = load_values()
    
    sorted_values = sorted(values.items(), key=lambda x: x[1], reverse=True)
    
    summary = "My core values (ranked):\n"
    for name, strength in sorted_values[:5]:
        stars = "★" * int(strength * 5)
        summary += f"  {name}: {stars} ({strength:.0%})\n"
    
    return summary
