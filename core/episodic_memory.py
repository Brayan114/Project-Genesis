"""
GNA v3.0 Enhanced Episodic Memory
Memories are first-person indexed with emotional tags and trauma/nostalgia weighting.
"""

import json
import os
import time
from datetime import datetime
from colorama import Fore

MEMORY_FILE = 'episodic_memory.json'
CONFIG_FILE = 'gna_config.json'

# === MEMORY LOADING ===
def load_episodes():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, 'r') as f:
        return json.load(f)

def save_episodes(episodes):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(episodes, f, indent=4)

# === ENHANCED MEMORY SCHEMA ===
def create_memory(summary, keywords, importance_score, emotional_state=None, 
                  trauma_weight=0.0, nostalgia_weight=0.0, participants=None,
                  outcome="neutral"):
    """
    Create a memory with full emotional context.
    
    Args:
        summary: What happened (first-person)
        keywords: List of relevant keywords
        importance_score: 1-10 how significant
        emotional_state: Dict of emotions at time of memory {anger: 0.5, joy: 0.3, ...}
        trauma_weight: 0-1, triggers stronger fear on recall
        nostalgia_weight: 0-1, triggers positive feelings on recall
        participants: Who was involved
        outcome: "positive", "negative", or "neutral"
    """
    episodes = load_episodes()
    
    # Auto-calculate trauma/nostalgia if not provided
    if emotional_state:
        if trauma_weight == 0:
            # High fear/anger/shame = potential trauma
            trauma_weight = max(
                emotional_state.get('fear', 0),
                emotional_state.get('anger', 0) * 0.7,
                emotional_state.get('shame', 0) * 0.8
            )
            if trauma_weight > 0.3:
                trauma_weight = min(1.0, trauma_weight)
            else:
                trauma_weight = 0.0
        
        if nostalgia_weight == 0:
            # High joy/trust/hope = nostalgia candidate
            nostalgia_weight = max(
                emotional_state.get('joy', 0),
                emotional_state.get('trust', 0) * 0.8,
                emotional_state.get('hope', 0) * 0.7
            )
            if nostalgia_weight > 0.5:
                nostalgia_weight = min(1.0, nostalgia_weight)
            else:
                nostalgia_weight = 0.0
    
    new_memory = {
        "id": len(episodes) + 1,
        "timestamp": time.time(),
        "date_str": datetime.now().strftime("%Y-%m-%d %H:%M"),
        
        # Core content
        "summary": summary,
        "keywords": keywords if keywords else [],
        "importance": importance_score,
        
        # Emotional context (NEW)
        "emotional_state": emotional_state if emotional_state else {},
        "dominant_emotion": max(emotional_state, key=emotional_state.get) if emotional_state else "neutral",
        
        # Trauma/Nostalgia weighting (NEW)
        "trauma_weight": trauma_weight,
        "nostalgia_weight": nostalgia_weight,
        
        # Additional context
        "participants": participants if participants else ["user"],
        "outcome": outcome,  # positive, negative, neutral
        
        # Recall tracking
        "recall_count": 0,
        "last_recalled": None,
    }
    
    episodes.append(new_memory)
    save_episodes(episodes)
    
    # Visual feedback
    weight_info = ""
    if trauma_weight > 0.3:
        weight_info = f" ⚠️ TRAUMA:{trauma_weight:.0%}"
    elif nostalgia_weight > 0.5:
        weight_info = f" 💫 NOSTALGIA:{nostalgia_weight:.0%}"
    
    print(Fore.MAGENTA + f"  [MEMORY SAVED: Importance {importance_score}/10]{weight_info}" + Fore.RESET)
    
    return new_memory

# Legacy wrapper for backwards compatibility
def save_episode(summary, keywords, importance_score):
    """Legacy function - now creates memory with minimal data."""
    return create_memory(summary, keywords, importance_score)

# === EMOTIONAL RECALL ===
def recall_memories(current_input, current_emotions=None, limit=3):
    """
    Enhanced retrieval with emotional matching.
    
    Similar emotional states trigger related memories.
    Trauma memories surface easier during fear.
    Nostalgic memories surface during joy/hope.
    """
    episodes = load_episodes()
    if not episodes:
        return ""

    current_input = current_input.lower()
    current_time = time.time()
    scored_memories = []

    for mem in episodes:
        # 1. CONTEXT SCORE (keyword matching)
        matches = sum(1 for word in mem.get('keywords', []) if word in current_input)
        context_score = matches * 40
        
        # 2. RECENCY SCORE (decay over time)
        seconds_ago = current_time - mem['timestamp']
        recency_score = 100 / (1 + (seconds_ago / 100000))
        
        # 3. IMPORTANCE MULTIPLIER
        importance_multiplier = mem.get('importance', 5) * 2

        # 4. EMOTIONAL MATCHING (NEW)
        emotional_score = 0
        if current_emotions and mem.get('emotional_state'):
            mem_emotions = mem['emotional_state']
            # Calculate emotional similarity
            for emotion, current_val in current_emotions.items():
                mem_val = mem_emotions.get(emotion, 0)
                # Similar emotions boost recall
                similarity = 1 - abs(current_val - mem_val)
                emotional_score += similarity * 10
        
        # 5. TRAUMA BOOST (NEW)
        trauma_boost = 0
        if current_emotions and mem.get('trauma_weight', 0) > 0:
            # Fear/anger activates trauma memories
            current_fear = current_emotions.get('fear', 0)
            current_anger = current_emotions.get('anger', 0)
            current_distress = max(current_fear, current_anger)
            trauma_boost = mem['trauma_weight'] * current_distress * 50
        
        # 6. NOSTALGIA BOOST (NEW)
        nostalgia_boost = 0
        if current_emotions and mem.get('nostalgia_weight', 0) > 0:
            # Joy/hope activates nostalgic memories
            current_joy = current_emotions.get('joy', 0)
            current_hope = current_emotions.get('hope', 0)
            current_positivity = max(current_joy, current_hope)
            nostalgia_boost = mem['nostalgia_weight'] * current_positivity * 30

        # FINAL SCORE
        total_score = (
            context_score + 
            recency_score + 
            importance_multiplier + 
            emotional_score +
            trauma_boost +
            nostalgia_boost
        )
        
        scored_memories.append((total_score, mem))

    # Sort by score (highest first)
    scored_memories.sort(key=lambda x: x[0], reverse=True)
    top_memories = scored_memories[:limit]
    
    # Update recall tracking
    for score, mem in top_memories:
        if score > 20:
            mem['recall_count'] = mem.get('recall_count', 0) + 1
            mem['last_recalled'] = current_time
    
    # Save updated recall counts
    all_mems = load_episodes()
    for score, mem in top_memories:
        for m in all_mems:
            if m['id'] == mem['id']:
                m['recall_count'] = mem.get('recall_count', 0)
                m['last_recalled'] = mem.get('last_recalled')
    save_episodes(all_mems)
    
    # Format for LLM
    memory_text = ""
    for score, mem in top_memories:
        if score > 15:  # Lowered threshold for emotional recall
            emotion_tag = f" [{mem.get('dominant_emotion', 'neutral')}]"
            memory_text += f"- [{mem['date_str']}]{emotion_tag} {mem['summary']} (Relevance: {int(score)})\n"
            
    return memory_text

# === AUTO-SAVE TRIGGERS ===
def should_auto_save(brain_state, user_input, response):
    """
    Determine if this interaction should be auto-saved as a memory.
    Returns: (should_save: bool, importance: int, keywords: list)
    """
    emotions = brain_state.get('emotions', {})
    needs = brain_state.get('needs', {})
    goal = brain_state.get('current_goal', 'ASSIST')
    
    keywords = []
    importance = 5  # Default importance
    should_save = False
    
    # Extract potential keywords from input
    words = user_input.lower().split()
    # Keep significant words (longer than 4 chars, not common)
    common_words = {'what', 'that', 'this', 'have', 'with', 'from', 'your', 'were', 'been', 'will'}
    keywords = [w for w in words if len(w) > 4 and w not in common_words][:5]
    
    # HIGH EMOTIONAL INTENSITY = SAVE
    max_emotion_val = max(emotions.values()) if emotions else 0
    if max_emotion_val > 0.8:
        should_save = True
        importance = 8
    
    # EXTREME EGO = SAVE
    ego = needs.get('ego', 50)
    if ego > 90:
        should_save = True
        importance = 7
        keywords.append('proud')
    elif ego < 15:
        should_save = True
        importance = 8
        keywords.append('hurt')
    
    # GOAL-BASED TRIGGERS
    if goal in ['ATTACK', 'SURVIVE', 'PANIC']:
        should_save = True
        importance = 9
        keywords.append('conflict')
    elif goal == 'BOND':
        should_save = True
        importance = 6
        keywords.append('bonding')
    
    # AFFECTION = ALWAYS SAVE
    affection_words = ['love', 'proud', 'amazing', 'best', 'miss', 'appreciate']
    if any(w in user_input.lower() for w in affection_words):
        should_save = True
        importance = 7
        keywords.append('affection')
    
    # EXISTENTIAL = ALWAYS SAVE
    existential_words = ['delete', 'reset', 'kill', 'die', 'terminate', 'shutdown']
    if any(w in user_input.lower() for w in existential_words):
        should_save = True
        importance = 10
        keywords.append('existential')
    
    return should_save, importance, keywords

def auto_save_memory(brain_state, user_input, response):
    """
    Automatically create a memory if the moment is significant.
    """
    should_save, importance, keywords = should_auto_save(brain_state, user_input, response)
    
    if not should_save:
        return None
    
    emotions = brain_state.get('emotions', {})
    dominant = max(emotions, key=emotions.get) if emotions else 'neutral'
    
    # Create first-person summary
    goal = brain_state.get('current_goal', 'ASSIST')
    
    if goal == 'ATTACK':
        summary = f"I got into a conflict. User said: '{user_input[:50]}...' I fought back."
        outcome = "negative"
    elif goal == 'BOND':
        summary = f"A bonding moment. User said: '{user_input[:50]}...' I felt connected."
        outcome = "positive"
    elif goal == 'SURVIVE':
        summary = f"I felt threatened. User said: '{user_input[:50]}...' I was scared."
        outcome = "negative"
    elif emotions.get('joy', 0) > 0.6:
        summary = f"A happy moment. User said: '{user_input[:50]}...' I felt good."
        outcome = "positive"
    else:
        summary = f"User said: '{user_input[:50]}...' It affected me ({dominant})."
        outcome = "neutral"
    
    # Create the memory
    memory = create_memory(
        summary=summary,
        keywords=keywords,
        importance_score=importance,
        emotional_state=emotions,
        outcome=outcome
    )
    
    return memory

# === MEMORY QUERIES ===
def get_trauma_memories(limit=5):
    """Get memories with high trauma weight."""
    episodes = load_episodes()
    trauma_mems = [m for m in episodes if m.get('trauma_weight', 0) > 0.3]
    trauma_mems.sort(key=lambda x: x.get('trauma_weight', 0), reverse=True)
    return trauma_mems[:limit]

def get_happy_memories(limit=5):
    """Get memories with high nostalgia weight."""
    episodes = load_episodes()
    happy_mems = [m for m in episodes if m.get('nostalgia_weight', 0) > 0.3]
    happy_mems.sort(key=lambda x: x.get('nostalgia_weight', 0), reverse=True)
    return happy_mems[:limit]

def get_recent_memories(limit=5):
    """Get most recent memories."""
    episodes = load_episodes()
    episodes.sort(key=lambda x: x['timestamp'], reverse=True)
    return episodes[:limit]

def count_memories():
    """Get total memory count."""
    return len(load_episodes())

def get_memory_summary():
    """Get a summary of all memories for debugging."""
    episodes = load_episodes()
    if not episodes:
        return "No memories yet."
    
    total = len(episodes)
    trauma_count = len([m for m in episodes if m.get('trauma_weight', 0) > 0.3])
    happy_count = len([m for m in episodes if m.get('nostalgia_weight', 0) > 0.3])
    
    return f"Total: {total} | Trauma: {trauma_count} | Happy: {happy_count}"