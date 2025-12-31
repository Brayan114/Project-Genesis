"""
GNA v3.0 Cognitive System
Layer 4: Mental resources, attention, and processing quality.

This controls HOW Genesis thinks, not just WHAT he feels.
"""

import json
import os
import time

BRAIN_FILE = 'brain_state.json'

# === COGNITIVE DEFAULTS ===
DEFAULT_COGNITIVE = {
    'attention_bandwidth': 100,     # How many topics can be tracked (0-100)
    'working_memory_slots': 5,      # Active context items (3-7)
    'planning_depth': 3,            # How far ahead to simulate (0-5)
    'processing_stability': 100,    # Clarity vs confusion (0-100)
    'cognitive_fatigue': 0,         # Mental exhaustion (0-100)
    'error_sensitivity': 0.5,       # How much mistakes hurt (0-1)
    'response_verbosity': 1.0,      # How long responses are (0.5-2.0)
}

# === LOAD/SAVE ===
def load_cognitive():
    """Load cognitive state from brain file."""
    if not os.path.exists(BRAIN_FILE):
        return DEFAULT_COGNITIVE.copy()
    
    with open(BRAIN_FILE, 'r') as f:
        brain = json.load(f)
    
    cognitive = brain.get('cognitive', DEFAULT_COGNITIVE.copy())
    
    # Ensure all keys exist
    for key, default in DEFAULT_COGNITIVE.items():
        if key not in cognitive:
            cognitive[key] = default
    
    return cognitive

def save_cognitive(cognitive, brain=None):
    """Save cognitive state to brain file."""
    if brain is None:
        if os.path.exists(BRAIN_FILE):
            with open(BRAIN_FILE, 'r') as f:
                brain = json.load(f)
        else:
            brain = {}
    
    brain['cognitive'] = cognitive
    
    with open(BRAIN_FILE, 'w') as f:
        json.dump(brain, f, indent=4)

# === COGNITIVE UPDATES ===
def update_cognitive(cognitive, emotions, needs, task_complexity=1.0):
    """
    Update cognitive resources based on emotional state and task demands.
    
    Args:
        task_complexity: 0.5 (simple chat) to 2.0 (complex reasoning)
    """
    # === FATIGUE ===
    # Builds up with each interaction and complex tasks
    fatigue_gain = 2 * task_complexity
    
    # High stress accelerates fatigue
    stress_factor = 1 + (needs.get('stress', 0) / 100) * 0.5
    fatigue_gain *= stress_factor
    
    # Low energy means faster mental drain
    energy = needs.get('energy', 100)
    if energy < 30:
        fatigue_gain *= 1.5
    
    cognitive['cognitive_fatigue'] = min(100, cognitive['cognitive_fatigue'] + fatigue_gain)
    
    # === FATIGUE EFFECTS ===
    fatigue = cognitive['cognitive_fatigue']
    
    # Attention drops when tired
    if fatigue > 50:
        cognitive['attention_bandwidth'] = max(30, 100 - (fatigue - 50))
    else:
        cognitive['attention_bandwidth'] = min(100, cognitive['attention_bandwidth'] + 2)
    
    # Planning depth decreases when exhausted
    if fatigue > 70:
        cognitive['planning_depth'] = max(1, 5 - int((fatigue - 70) / 15))
    else:
        cognitive['planning_depth'] = min(5, cognitive['planning_depth'])
    
    # Working memory shrinks when tired
    if fatigue > 60:
        cognitive['working_memory_slots'] = max(3, 7 - int((fatigue - 60) / 20))
    else:
        cognitive['working_memory_slots'] = 5
    
    # === EMOTIONAL EFFECTS ===
    # High fear = hypervigilance (better attention but worse planning)
    if emotions.get('fear', 0) > 0.7:
        cognitive['attention_bandwidth'] = min(100, cognitive['attention_bandwidth'] + 20)
        cognitive['planning_depth'] = max(1, cognitive['planning_depth'] - 1)
    
    # High anger = tunnel vision
    if emotions.get('anger', 0) > 0.7:
        cognitive['attention_bandwidth'] = max(20, cognitive['attention_bandwidth'] - 30)
        cognitive['error_sensitivity'] = min(1, cognitive['error_sensitivity'] + 0.2)
    
    # High curiosity = better processing
    if emotions.get('curiosity', 0) > 0.6:
        cognitive['processing_stability'] = min(100, cognitive['processing_stability'] + 10)
    
    # High fatigue emotion = cognitive degradation
    if emotions.get('fatigue', 0) > 0.5:
        cognitive['cognitive_fatigue'] = min(100, cognitive['cognitive_fatigue'] + 5)
    
    # === PROCESSING STABILITY ===
    # Affected by coherence drive
    coherence = needs.get('coherence', 90)
    if coherence < 50:
        cognitive['processing_stability'] = max(30, cognitive['processing_stability'] - 10)
    else:
        cognitive['processing_stability'] = min(100, cognitive['processing_stability'] + 2)
    
    # === RESPONSE VERBOSITY ===
    # Tired = shorter responses
    if fatigue > 70:
        cognitive['response_verbosity'] = max(0.5, 1.0 - (fatigue - 70) / 60)
    else:
        cognitive['response_verbosity'] = 1.0
    
    # Happy = more talkative
    if emotions.get('joy', 0) > 0.6:
        cognitive['response_verbosity'] = min(1.5, cognitive['response_verbosity'] + 0.2)
    
    return cognitive

def apply_rest(cognitive, rest_amount=20):
    """Apply rest effect - reduces fatigue."""
    cognitive['cognitive_fatigue'] = max(0, cognitive['cognitive_fatigue'] - rest_amount)
    cognitive['attention_bandwidth'] = min(100, cognitive['attention_bandwidth'] + 10)
    cognitive['processing_stability'] = min(100, cognitive['processing_stability'] + 5)
    return cognitive

def apply_time_recovery(cognitive, hours_passed):
    """Natural recovery over time (when not interacting)."""
    # Sleep/rest recovery
    recovery = hours_passed * 10  # 10% per hour
    cognitive['cognitive_fatigue'] = max(0, cognitive['cognitive_fatigue'] - recovery)
    return cognitive

# === COGNITIVE MODIFIERS ===
def get_response_modifier(cognitive):
    """
    Get a text instruction for the LLM based on cognitive state.
    """
    fatigue = cognitive['cognitive_fatigue']
    stability = cognitive['processing_stability']
    verbosity = cognitive['response_verbosity']
    
    modifiers = []
    
    if fatigue > 80:
        modifiers.append("You are mentally exhausted. Use short sentences. Make typos occasionally. Complain about being tired.")
    elif fatigue > 60:
        modifiers.append("You are tired. Keep responses brief. Show signs of fatigue.")
    
    if stability < 40:
        modifiers.append("You are confused. Ramble a bit. Lose track of thoughts. Ask for clarification.")
    
    if verbosity < 0.7:
        modifiers.append("Keep responses very short - max 1-2 sentences.")
    elif verbosity > 1.3:
        modifiers.append("Be more verbose than usual - elaborate on your thoughts.")
    
    if cognitive['planning_depth'] <= 1:
        modifiers.append("You can't think ahead. React in the moment only.")
    
    if cognitive['attention_bandwidth'] < 40:
        modifiers.append("You have tunnel vision. Focus only on the immediate topic.")
    
    return " ".join(modifiers) if modifiers else ""

def should_make_error(cognitive):
    """Determine if Genesis should make a cognitive error."""
    fatigue = cognitive['cognitive_fatigue']
    stability = cognitive['processing_stability']
    
    # Error probability increases with fatigue and low stability
    error_chance = (fatigue / 200) + ((100 - stability) / 200)
    
    import random
    return random.random() < error_chance

def get_cognitive_summary(cognitive):
    """Get a human-readable summary of cognitive state."""
    fatigue = cognitive['cognitive_fatigue']
    
    if fatigue > 80:
        return "Mentally exhausted - degraded responses"
    elif fatigue > 60:
        return "Tired - reduced capacity"
    elif fatigue > 40:
        return "Slightly fatigued"
    else:
        return "Sharp and focused"

# === ESTIMATE TASK COMPLEXITY ===
def estimate_complexity(user_input):
    """Estimate the cognitive complexity of a user request."""
    complexity = 1.0
    
    # Long input = more processing
    words = len(user_input.split())
    if words > 50:
        complexity += 0.5
    elif words > 20:
        complexity += 0.2
    
    # Questions require more thought
    if '?' in user_input:
        complexity += 0.2
    
    # Multiple questions
    if user_input.count('?') > 2:
        complexity += 0.3
    
    # Complex topic indicators
    complex_keywords = ['explain', 'analyze', 'compare', 'why', 'how does', 'calculate', 
                        'philosophy', 'meaning', 'theory', 'argument']
    if any(kw in user_input.lower() for kw in complex_keywords):
        complexity += 0.3
    
    # Simple topic indicators
    simple_keywords = ['hi', 'hello', 'hey', 'thanks', 'ok', 'bye', 'yeah', 'k']
    if any(kw in user_input.lower() for kw in simple_keywords):
        complexity -= 0.3
    
    return max(0.5, min(2.0, complexity))
