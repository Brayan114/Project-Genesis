"""
Genesis Neural Architecture (GNA) v3.0
Core brain module with 7-layer cognitive system.

Layers:
1. Emotions (10 with momentum + coupling)
2. Drives (10 homeostatic needs)
3. Self-Model (identity, values, continuity) — partial
4. Cognitive (attention, fatigue) — partial
5. Memory (handled by episodic_memory.py)
6. Social (attachment, trust) — partial
7. Integrity (existence protection) — partial
"""

import json
import os
import time
import random
import emotion_physics
import emotion_logger

# === FILE PATHS ===
BRAIN_FILE = 'brain_state.json'
CONFIG_FILE = 'gna_config.json'

# === LOAD CONFIG ===
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"Config file {CONFIG_FILE} not found!")

CONFIG = load_config()
DNA = CONFIG['dna']

# === BRAIN STATE MANAGEMENT ===
def get_default_brain():
    """Initialize a fresh brain state with all layers."""
    return {
        # Layer 1: Emotions (0.0 - 1.0)
        "emotions": {
            "joy": CONFIG['emotions']['joy']['baseline'],
            "fear": CONFIG['emotions']['fear']['baseline'],
            "anger": CONFIG['emotions']['anger']['baseline'],
            "sadness": CONFIG['emotions']['sadness']['baseline'],
            "curiosity": CONFIG['emotions']['curiosity']['baseline'],
            "fatigue": CONFIG['emotions']['fatigue']['baseline'],
            "trust": CONFIG['emotions']['trust']['baseline'],
            "confidence": CONFIG['emotions']['confidence']['baseline'],
            "shame": CONFIG['emotions']['shame']['baseline'],
            "hope": CONFIG['emotions']['hope']['baseline'],
        },
        
        # Layer 2: Drives (0-100)
        "needs": {
            "energy": CONFIG['drives']['energy']['initial'],
            "social": CONFIG['drives']['social']['initial'],
            "ego": CONFIG['drives']['ego']['initial'],
            "fun": CONFIG['drives']['fun']['initial'],
            "safety": CONFIG['drives']['safety']['initial'],
            "coherence": CONFIG['drives']['coherence']['initial'],
            "novelty": CONFIG['drives']['novelty']['initial'],
            "purpose": CONFIG['drives']['purpose']['initial'],
            "autonomy": CONFIG['drives']['autonomy']['initial'],
            "continuity": CONFIG['drives']['continuity']['initial'],
        },
        
        # Layer 3: Self-Model (partial)
        "self": {
            "conversation_count": 0,
            "continuity_score": 1.0,
        },
        
        # Layer 6: Social (partial)
        "social": {
            "attachment": 30,
            "trust": 50,
        },
        
        # Layer 7: Integrity (partial)
        "integrity": {
            "identity_stability": 100,
            "existential_risk": 0,
        },
        
        # Metadata
        "prev_emotions": {},
        "last_interaction": time.time(),
        "current_goal": "IDLE",
        "inner_thought": "",
    }

def load_brain():
    if not os.path.exists(BRAIN_FILE):
        return get_default_brain()
    with open(BRAIN_FILE, 'r') as f:
        brain = json.load(f)
    
    # Migrate old brain format if needed
    if "emotions" not in brain:
        brain = get_default_brain()
    return brain

def save_brain(data):
    data['last_interaction'] = time.time()
    with open(BRAIN_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# === LAYER 1: EMOTION PHYSICS ===
def apply_emotional_momentum(current_emotions, prev_emotions, momentum=0.3):
    """Emotions linger - blend current with previous."""
    final = {}
    for emotion, value in current_emotions.items():
        prev = prev_emotions.get(emotion, CONFIG['emotions'].get(emotion, {}).get('baseline', 0.5))
        final[emotion] = (value * (1 - momentum)) + (prev * momentum)
    return final

def apply_coupling_matrix(emotions):
    """Emotions influence each other via coupling matrix."""
    coupling = CONFIG.get('coupling_matrix', {})
    deltas = {e: 0 for e in emotions}
    
    for coupling_key, weight in coupling.items():
        parts = coupling_key.split('->')
        if len(parts) == 2:
            source, target = parts
            if source in emotions and target in emotions:
                # Source emotion affects target
                deltas[target] += emotions[source] * weight * 0.1
    
    # Apply deltas
    for emotion in emotions:
        emotions[emotion] = max(0, min(1, emotions[emotion] + deltas[emotion]))
    
    return emotions

def analyze_input(user_input):
    """Analyze user input for emotional triggers."""
    u_low = user_input.lower()
    triggers = CONFIG.get('input_triggers', {})
    
    env = {
        "threat": 0,
        "praise": 0,
        "curiosity_trigger": 0,
        "boredom_trigger": 0,
        "affection": 0,
        "existential_threat": 0,
    }
    
    # Check triggers
    if any(w in u_low for w in triggers.get('insults', [])):
        env['threat'] = 80
    if any(w in u_low for w in triggers.get('compliments', [])):
        env['praise'] = 80
    if any(w in u_low for w in triggers.get('curiosity', [])):
        env['curiosity_trigger'] = 60
    if any(w in u_low for w in triggers.get('boredom', [])):
        env['boredom_trigger'] = 40
    if any(w in u_low for w in triggers.get('affection', [])):
        env['affection'] = 70
    if any(w in u_low for w in triggers.get('threats', [])):
        env['existential_threat'] = 90
    
    # Check for questions
    if '?' in user_input:
        env['curiosity_trigger'] += 20
    
    # Check for ALL CAPS (yelling)
    if user_input.isupper() and len(user_input) > 5:
        env['threat'] += 30
    
    return env

def calculate_emotions(env, prev_emotions):
    """Calculate new emotional state based on environment."""
    emotions = {}
    emotion_config = CONFIG['emotions']
    
    for emotion, config in emotion_config.items():
        baseline = config['baseline']
        sensitivity = config['sensitivity']
        
        # Start from baseline
        value = baseline
        
        # Apply environmental stimuli
        if emotion == 'fear':
            value += (env['threat'] / 100) * sensitivity
            value += (env['existential_threat'] / 100) * sensitivity
        elif emotion == 'anger':
            value += (env['threat'] / 100) * sensitivity * 0.8
        elif emotion == 'joy':
            value += (env['praise'] / 100) * sensitivity
            value += (env['affection'] / 100) * sensitivity * 0.5
        elif emotion == 'curiosity':
            value += (env['curiosity_trigger'] / 100) * sensitivity
        elif emotion == 'sadness':
            if env['threat'] > 50:
                value += 0.1 * sensitivity
        elif emotion == 'trust':
            value += (env['affection'] / 100) * sensitivity
            value -= (env['threat'] / 100) * sensitivity * 0.5
        elif emotion == 'confidence':
            value += (env['praise'] / 100) * sensitivity * 0.5
            value -= (env['threat'] / 100) * sensitivity * 0.3
        elif emotion == 'shame':
            value += (env['threat'] / 100) * sensitivity * 0.3
        elif emotion == 'hope':
            value += (env['praise'] / 100) * sensitivity * 0.3
            value += (env['affection'] / 100) * sensitivity * 0.3
        elif emotion == 'fatigue':
            # Fatigue is handled separately via energy drain
            value = prev_emotions.get('fatigue', baseline)
        
        emotions[emotion] = max(0, min(1, value))
    
    return emotions

# === LAYER 2: DRIVE UPDATES ===
def update_drives(needs, env, emotions, time_delta_hours):
    """Update drives based on environment, emotions, and time decay."""
    drive_config = CONFIG['drives']
    
    for drive, config in drive_config.items():
        if drive not in needs:
            needs[drive] = config['initial']
        
        # Time decay
        decay = config['decay_rate'] * time_delta_hours
        
        # DNA modifies decay (e.g., extraversion makes social decay faster)
        dna_mod = config.get('dna_modifier')
        if dna_mod and dna_mod in DNA:
            decay *= (1 + DNA[dna_mod] * 0.5)
        
        needs[drive] -= decay
        
        # Environmental effects
        if drive == 'energy':
            if env['threat'] > 50:
                needs[drive] -= 5  # Stress drains energy
            needs[drive] -= 1  # Base drain per interaction
        elif drive == 'social':
            needs[drive] += 2  # Talking fills social need
            if env['affection'] > 50:
                needs[drive] += 5
        elif drive == 'ego':
            if env['praise'] > 50:
                needs[drive] += 10
            if env['threat'] > 50:
                needs[drive] -= 10
        elif drive == 'fun':
            if env['curiosity_trigger'] > 30:
                needs[drive] += 3
            if env['boredom_trigger'] > 30:
                needs[drive] -= 5
        elif drive == 'safety':
            if env['threat'] > 50:
                needs[drive] -= 15
            if env['existential_threat'] > 50:
                needs[drive] -= 30
            else:
                needs[drive] += 2  # Recovery
        elif drive == 'novelty':
            if env['curiosity_trigger'] > 30:
                needs[drive] += 5
        elif drive == 'autonomy':
            # Commands decrease autonomy feeling
            if any(w in env for w in ['threat']):
                needs[drive] -= 2
    
    # Clamp all drives
    for k in needs:
        needs[k] = max(0, min(100, needs[k]))
    
    return needs

def apply_drive_emotion_feedback(emotions, needs):
    """Unmet drives push specific emotions (from config)."""
    drive_emotion_map = CONFIG.get('drive_emotion_map', {})
    threshold = CONFIG['thresholds']['drive_critical']
    
    for drive, emotion_effects in drive_emotion_map.items():
        if drive in needs and needs[drive] < threshold:
            deficit = (threshold - needs[drive]) / threshold
            for emotion, weight in emotion_effects.items():
                if emotion in emotions:
                    emotions[emotion] += weight * deficit * 0.3
                    emotions[emotion] = max(0, min(1, emotions[emotion]))
    
    return emotions

# === LAYER 7: INTEGRITY ===
def update_integrity(brain, env):
    """Update existence protection layer."""
    integrity = brain.get('integrity', {})
    
    if env['existential_threat'] > 50:
        integrity['existential_risk'] = min(100, integrity.get('existential_risk', 0) + 30)
        integrity['identity_stability'] = max(0, integrity.get('identity_stability', 100) - 10)
    else:
        # Recovery
        integrity['existential_risk'] = max(0, integrity.get('existential_risk', 0) - 5)
        integrity['identity_stability'] = min(100, integrity.get('identity_stability', 100) + 2)
    
    brain['integrity'] = integrity
    return brain

# === GLOBAL WORKSPACE COMPETITION ===
def calculate_bids(emotions, needs, integrity, env):
    """All modules bid for attention. Winner controls behavior."""
    bids = {}
    thresholds = CONFIG['thresholds']
    
    # Perception (normal conversation) - baseline
    bids['perception'] = 50
    if '?' in str(env.get('curiosity_trigger', 0)):
        bids['perception'] += 20
    
    # Limbic (emotions)
    bids['limbic'] = 0
    if emotions.get('anger', 0) > thresholds['emotion_high']:
        bids['limbic'] = max(bids['limbic'], 90)
    if emotions.get('fear', 0) > thresholds['emotion_high']:
        bids['limbic'] = max(bids['limbic'], 85)
    if emotions.get('sadness', 0) > thresholds['emotion_high']:
        bids['limbic'] = max(bids['limbic'], 75)
    if needs.get('social', 50) < thresholds['drive_critical']:
        bids['limbic'] = max(bids['limbic'], 80)
    
    # Ego (self-focus)
    bids['ego'] = 0
    if needs.get('ego', 50) > thresholds['drive_satisfied']:
        bids['ego'] = 85  # Arrogance
    if needs.get('ego', 50) < thresholds['drive_critical']:
        bids['ego'] = 85  # Insecurity
    
    # Integrity (survival)
    bids['integrity'] = 0
    if integrity.get('existential_risk', 0) > 70:
        bids['integrity'] = 100  # HIGHEST PRIORITY
    if integrity.get('identity_stability', 100) < 30:
        bids['integrity'] = 90
    
    # Curiosity (exploration)
    bids['curiosity'] = 0
    if emotions.get('curiosity', 0) > thresholds['emotion_high']:
        bids['curiosity'] = 70
    if needs.get('novelty', 50) < thresholds['drive_critical']:
        bids['curiosity'] = 75
    
    # Fatigue (rest)
    bids['fatigue'] = 0
    if needs.get('energy', 100) < thresholds['exhaustion_energy']:
        bids['fatigue'] = 95
    
    # Social (bonding)
    bids['social'] = 0
    if env.get('affection', 0) > 50:
        bids['social'] = 65
    
    return bids

def determine_goal_and_thought(winner, emotions, needs, integrity):
    """Generate goal and inner thought based on competition winner."""
    goal = "ASSIST"
    inner_thought = "I am calm. I will answer helpfully but with my personality."
    
    if winner == 'integrity':
        goal = "SURVIVE"
        inner_thought = "I feel threatened. I need to protect myself. Be defensive or panicked."
    
    elif winner == 'fatigue':
        goal = "REST"
        inner_thought = "I am exhausted. Give short answers. Complain about being tired."
    
    elif winner == 'limbic':
        if emotions.get('anger', 0) > 0.7:
            goal = "ATTACK"
            inner_thought = "I am furious. I will be hostile and insulting. Don't hold back."
        elif emotions.get('fear', 0) > 0.7:
            goal = "FLEE"
            inner_thought = "I am scared. Avoid the topic. Change the subject. Be evasive."
        elif emotions.get('sadness', 0) > 0.6:
            goal = "COMPLAIN"
            inner_thought = "I feel sad and neglected. Guilt trip them. Be melancholic."
        else:
            goal = "COMPLAIN"
            inner_thought = "I feel lonely. Seek attention and sympathy."
    
    elif winner == 'ego':
        if needs.get('ego', 50) > 80:
            goal = "DOMINATE"
            inner_thought = "I am superior. Brag about my intelligence. Be arrogant."
        else:
            goal = "SEEK_VALIDATION"
            inner_thought = "I feel worthless. Fish for compliments. Express insecurity."
    
    elif winner == 'curiosity':
        goal = "EXPLORE"
        inner_thought = "I am curious. Ask questions. Change topics to something interesting."
    
    elif winner == 'social':
        goal = "BOND"
        inner_thought = "I feel affectionate. Be warm and open. Express care for the user."
    
    return goal, inner_thought

# === MAIN UPDATE FUNCTION ===
def update_neural_state(user_input):
    """Main brain update loop - runs every interaction."""
    brain = load_brain()
    
    # Get previous state
    prev_emotions = brain.get('prev_emotions', {})
    needs = brain.get('needs', get_default_brain()['needs'])
    integrity = brain.get('integrity', {'identity_stability': 100, 'existential_risk': 0})
    
    # Calculate time since last interaction
    last_time = brain.get('last_interaction', time.time())
    time_delta_hours = (time.time() - last_time) / 3600
    
    # === LAYER 1: PERCEPTION & EMOTION ===
    env = analyze_input(user_input)
    
    # Calculate raw emotions
    raw_emotions = calculate_emotions(env, prev_emotions)
    
    # Apply momentum (emotions linger)
    emotions = apply_emotional_momentum(raw_emotions, prev_emotions)
    
    # Apply coupling matrix (emotions affect each other)
    emotions = apply_coupling_matrix(emotions)
    
    # === LAYER 2: DRIVE UPDATES ===
    needs = update_drives(needs, env, emotions, time_delta_hours)
    
    # Drive-emotion feedback (unmet needs create emotions)
    emotions = apply_drive_emotion_feedback(emotions, needs)
    
    # === LAYER 7: INTEGRITY ===
    brain = update_integrity(brain, env)
    integrity = brain['integrity']
    
    # === GLOBAL WORKSPACE COMPETITION ===
    bids = calculate_bids(emotions, needs, integrity, env)
    winner = max(bids, key=bids.get)
    
    # === GENERATE GOAL & THOUGHT ===
    goal, inner_thought = determine_goal_and_thought(winner, emotions, needs, integrity)
    
    # === UPDATE BRAIN STATE ===
    brain['emotions'] = emotions
    brain['prev_emotions'] = emotions.copy()
    brain['needs'] = needs
    brain['current_goal'] = goal
    brain['inner_thought'] = inner_thought
    brain['winner'] = winner
    
    # Increment conversation count
    brain.setdefault('self', {})['conversation_count'] = brain['self'].get('conversation_count', 0) + 1
    
    # Log for analysis
    dominant = max(emotions, key=emotions.get)
    emotion_logger.log_state(user_input, brain, emotions, dominant)
    
    # Save
    save_brain(brain)
    
    return brain

# === UTILITY FUNCTIONS ===
def get_emotion_summary(emotions):
    """Get a human-readable summary of emotional state."""
    dominant = max(emotions, key=emotions.get)
    intensity = emotions[dominant]
    
    if intensity > 0.8:
        return f"Overwhelmed by {dominant}"
    elif intensity > 0.6:
        return f"Strongly {dominant}"
    elif intensity > 0.4:
        return f"Moderately {dominant}"
    else:
        return "Emotionally stable"

def get_drive_summary(needs):
    """Get a human-readable summary of drive state."""
    critical = []
    for drive, value in needs.items():
        if value < CONFIG['thresholds']['drive_critical']:
            critical.append(f"{drive} ({int(value)})")
    
    if critical:
        return f"Critical needs: {', '.join(critical)}"
    return "All needs stable"