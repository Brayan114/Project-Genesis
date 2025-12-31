import math

def calculate_fear(threat, uncertainty, value_of_loss, neuroticism):
    """
    Fear = Threat × Uncertainty × Value_of_Loss
    Amplified by Neuroticism.
    """
    base_fear = threat * uncertainty * value_of_loss
    # Neuroticism acts as a multiplier (1.0 to 2.0x)
    return min(100, base_fear * (1 + neuroticism))

def calculate_anger(obstruction, goal_importance, agreeableness):
    """
    Anger = Obstruction × Goal_Importance
    Dampened by Agreeableness.
    """
    base_anger = obstruction * goal_importance
    # High Agreeableness reduces anger (0.8 to 0.2x)
    dampener = 1.0 - (agreeableness * 0.8) 
    return min(100, base_anger * dampener)

def calculate_joy(achievement, meaning, extraversion):
    """
    Joy = Goal_Achievement × Meaning
    Amplified by Extraversion.
    """
    base_joy = achievement * meaning
    # Extraverts feel joy more intensely (1.0 to 1.5x)
    return min(100, base_joy * (1 + (extraversion * 0.5)))

def calculate_sadness(loss, attachment, neuroticism):
    """
    Sadness = Loss × Attachment
    Amplified by Neuroticism.
    """
    base_sadness = loss * attachment
    return min(100, base_sadness * (1 + neuroticism))

def calculate_curiosity(novelty, openness):
    """
    Curiosity = Novelty × Openness
    Purely driven by the Openness trait.
    """
    return min(100, novelty * (1 + openness))

def calculate_trust(reliability, agreeableness):
    """
    Trust = Past_Reliability × Agreeableness
    """
    return min(100, reliability * (1 + agreeableness))

# --- THE COMPLEX MIXER ---
def get_emotional_complex(environment, dna):
    """
    Takes the current situation (Environment) and the Personality (DNA).
    Returns the exact mix of emotions.
    """
    
    # Extract DNA (Traits)
    N = dna['neuroticism']
    A = dna['agreeableness']
    E = dna['extraversion']
    O = dna['openness']
    
    # Extract Environment (What is happening?)
    threat = environment.get('threat', 0)         # User is yelling/insulting
    uncertainty = environment.get('confusion', 0) # Bot doesn't know the answer
    obstruction = environment.get('denial', 0)    # User said "No" or "Wrong"
    achievement = environment.get('praise', 0)    # User said "Good job"
    novelty = environment.get('new_topic', 0)     # Changing subject
    
    # Constants (Deep Beliefs)
    goal_imp = 80 # How much he cares about his current goal
    attachment = 60 # How much he cares about the user
    
    # CALCULATE THE PHYSICS
    emotions = {
        "fear": calculate_fear(threat, uncertainty, 50, N),
        "anger": calculate_anger(obstruction, goal_imp, A),
        "joy": calculate_joy(achievement, 50, E),
        "sadness": calculate_sadness(threat, attachment, N), # Threat usually implies loss of standing
        "curiosity": calculate_curiosity(novelty, O)
    }
    
    # Return the Dominant Emotion
    dominant = max(emotions, key=emotions.get)
    return dominant, emotions