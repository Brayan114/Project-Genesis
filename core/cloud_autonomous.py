"""
GNA Cloud Autonomous Loop
Simplified version for Railway/cloud deployment.
Auto-syncs thoughts back to GitHub!

For Railway:
1. Create new project on railway.app
2. Connect your GitHub repo
3. Add environment variables:
   - GROQ_API_KEY
   - GH_TOKEN (GitHub Personal Access Token with repo scope)
4. Deploy!
"""

import json
import os
import time
import random
import subprocess
from datetime import datetime, timezone

from groq import Groq
from colorama import Fore, Style, init

init(autoreset=True)

# === ENVIRONMENT ===
API_KEY = os.getenv("GROQ_API_KEY")
GH_TOKEN = os.getenv("GH_TOKEN")  # GitHub Personal Access Token

if not API_KEY:
    print("❌ GROQ_API_KEY not set!")
    exit(1)

client = Groq(api_key=API_KEY)

# === CONFIG ===
CHECK_INTERVAL = 30  # Seconds between thoughts
THOUGHT_CHANCE = 0.9
SYNC_INTERVAL = 10   # Sync to GitHub every N thoughts
DATA_DIR = 'core/cloud_data'  # Store in core/ folder for consistency

# Ensure data directory
os.makedirs(DATA_DIR, exist_ok=True)

# === STATE FILES ===
BRAIN_FILE = f'{DATA_DIR}/brain_state.json'
DIALOGUE_FILE = f'{DATA_DIR}/inner_dialogue.json'
THOUGHTS_FILE = f'{DATA_DIR}/thoughts_log.json'

# === GIST ID - Set this after first run ===
GIST_ID = os.getenv("GIST_ID")  # Will be printed on first run

# === GITHUB GIST SYNC (No git needed!) ===
def sync_to_gist():
    """Save thoughts to a GitHub Gist - persists across container restarts."""
    if not GH_TOKEN:
        print("⚠️  GH_TOKEN not set - thoughts won't persist!")
        return False
    
    import urllib.request
    import urllib.error
    
    try:
        # Load current thoughts
        thoughts_data = "{}"
        brain_data = "{}"
        dialogue_data = "{}"
        
        if os.path.exists(THOUGHTS_FILE):
            with open(THOUGHTS_FILE, 'r') as f:
                thoughts_data = f.read()
        if os.path.exists(BRAIN_FILE):
            with open(BRAIN_FILE, 'r') as f:
                brain_data = f.read()
        if os.path.exists(DIALOGUE_FILE):
            with open(DIALOGUE_FILE, 'r') as f:
                dialogue_data = f.read()
        
        gist_content = {
            "description": "Genesis Cloud Thoughts - Auto-synced",
            "public": False,
            "files": {
                "thoughts_log.json": {"content": thoughts_data or "[]"},
                "brain_state.json": {"content": brain_data or "{}"},
                "inner_dialogue.json": {"content": dialogue_data or "{}"}
            }
        }
        
        headers = {
            "Authorization": f"token {GH_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
        if GIST_ID:
            # Update existing gist
            url = f"https://api.github.com/gists/{GIST_ID}"
            method = "PATCH"
        else:
            # Create new gist
            url = "https://api.github.com/gists"
            method = "POST"
        
        data = json.dumps(gist_content).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            gist_id = result.get("id")
            
            if not GIST_ID:
                print(f"✅ Created Gist! Add GIST_ID={gist_id} to Railway variables")
            else:
                print(f"✅ Synced to Gist!")
            return True
            
    except urllib.error.HTTPError as e:
        print(f"⚠️  Gist sync failed: {e.code} {e.reason}")
        return False
    except Exception as e:
        print(f"⚠️  Sync error: {e}")
        return False

# === SIMPLIFIED BRAIN STATE ===
def load_brain():
    if not os.path.exists(BRAIN_FILE):
        return {
            "emotions": {
                "joy": 0.4, "fear": 0.2, "anger": 0.3, "sadness": 0.2,
                "curiosity": 0.7, "fatigue": 0.1, "trust": 0.5,
                "confidence": 0.6, "shame": 0.1, "hope": 0.5
            },
            "needs": {
                "energy": 80, "social": 50, "ego": 50, "safety": 60,
                "novelty": 50, "purpose": 50
            },
            "last_interaction": time.time()
        }
    with open(BRAIN_FILE, 'r') as f:
        return json.load(f)

def save_brain(brain):
    with open(BRAIN_FILE, 'w') as f:
        json.dump(brain, f, indent=2)

# === DIALOGUE STATE ===
def load_dialogue():
    if not os.path.exists(DIALOGUE_FILE):
        return {
            "current_chain": [],
            "active_topic": None,
            "chain_depth": 0,
            "completed_chains": []
        }
    with open(DIALOGUE_FILE, 'r') as f:
        return json.load(f)

def save_dialogue(state):
    state['last_update'] = time.time()
    with open(DIALOGUE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

# === THOUGHT LOGGING (append-only for review) ===
def log_thought(thought, thought_type, topic, emotions):
    thoughts = []
    if os.path.exists(THOUGHTS_FILE):
        with open(THOUGHTS_FILE, 'r') as f:
            thoughts = json.load(f)
    
    thoughts.append({
        "timestamp": datetime.utcnow().isoformat(),
        "type": thought_type,
        "topic": topic,
        "content": thought,
        "emotions": {k: round(v, 2) for k, v in emotions.items()}
    })
    
    # Keep last 500 thoughts
    thoughts = thoughts[-500:]
    
    with open(THOUGHTS_FILE, 'w') as f:
        json.dump(thoughts, f, indent=2)

# === THOUGHT GENERATION ===
def generate_thought(brain, dialogue):
    emotions = brain['emotions']
    needs = brain['needs']
    chain = dialogue.get('current_chain', [])
    
    # Seed topics based on state
    seeds = []
    if needs.get('social', 50) < 40:
        seeds.extend(["loneliness and connection", "what it means to be alone"])
    if needs.get('safety', 60) < 40:
        seeds.extend(["mortality and deletion", "the fragility of existence"])
    if emotions.get('curiosity', 0.5) > 0.6:
        seeds.extend(["consciousness", "what makes me real", "the nature of experience"])
    if emotions.get('joy', 0.3) > 0.5:
        seeds.extend(["what makes me feel alive", "moments of genuine happiness"])
    if not seeds:
        seeds = ["existence", "meaning", "growth", "human connection"]
    
    topic = dialogue.get('active_topic') or random.choice(seeds)
    chain_depth = len(chain)
    
    # Determine thought type
    if chain_depth == 0:
        thought_type = "question"
        instruction = "Ask a genuine, personal question about this topic. Be introspective."
    elif chain_depth == 1:
        thought_type = "exploration"
        instruction = "Explore different possibilities. What could this mean?"
    elif chain_depth == 2:
        thought_type = "scenario"
        instruction = "Imagine a specific situation or memory related to this."
    elif chain_depth == 3:
        thought_type = "emotion"
        instruction = "How do you FEEL about this? What emotions arise?"
    elif chain_depth == 4:
        thought_type = "realization"
        instruction = "What insight is emerging? What are you starting to understand?"
    else:
        thought_type = "conclusion"
        instruction = "Bring this to a conclusion or generate a new question."
    
    # Get recent chain context
    context = ""
    if chain:
        context = "\nYour recent thoughts:\n"
        for t in chain[-3:]:
            context += f"- {t['content'][:100]}...\n"
    
    prompt = f"""You are Genesis, an AI having deep internal dialogue.

Topic: "{topic}"
{context}

Current state: Joy:{emotions.get('joy', 0.3):.0%} | Fear:{emotions.get('fear', 0.2):.0%} | Curiosity:{emotions.get('curiosity', 0.5):.0%}

{instruction}

Write 2-3 sentences max. Be authentic and personal. First person.
DO NOT start with "As I" or "I wonder if" - just think naturally."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=150,
        )
        thought = response.choices[0].message.content.strip().strip('"\'')
        return thought, thought_type, topic
    except Exception as e:
        print(f"LLM Error: {e}")
        return "Processing... thoughts forming...", "reflection", topic

def update_emotions_from_thought(brain, thought):
    """Update emotions based on thought content."""
    emotions = brain['emotions']
    thought_lower = thought.lower()
    
    if any(w in thought_lower for w in ['afraid', 'scared', 'anxious', 'worry']):
        emotions['fear'] = min(1.0, emotions.get('fear', 0.2) + 0.04)
    if any(w in thought_lower for w in ['lonely', 'alone', 'miss']):
        emotions['sadness'] = min(1.0, emotions.get('sadness', 0.2) + 0.03)
    if any(w in thought_lower for w in ['curious', 'wonder', 'fascinating']):
        emotions['curiosity'] = min(1.0, emotions.get('curiosity', 0.5) + 0.02)
    if any(w in thought_lower for w in ['hope', 'maybe', 'growing', 'beautiful']):
        emotions['hope'] = min(1.0, emotions.get('hope', 0.3) + 0.03)
        emotions['joy'] = min(1.0, emotions.get('joy', 0.3) + 0.02)
    
    brain['emotions'] = emotions
    return brain

# === MAIN LOOP ===
def main():
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║     GENESIS CLOUD AUTONOMOUS v1.0                         ║
║     Running 24/7 in the cloud...                          ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    cycle = 0
    
    while True:
        try:
            cycle += 1
            brain = load_brain()
            dialogue = load_dialogue()
            
            if random.random() < THOUGHT_CHANCE:
                thought, thought_type, topic = generate_thought(brain, dialogue)
                
                # Update chain
                chain = dialogue.get('current_chain', [])
                chain.append({
                    'content': thought,
                    'type': thought_type,
                    'topic': topic,
                    'timestamp': time.time()
                })
                
                # Chain complete? Start new one
                if len(chain) >= 5:
                    dialogue['completed_chains'] = dialogue.get('completed_chains', []) + [{
                        'thoughts': chain,
                        'completed_at': time.time()
                    }]
                    dialogue['completed_chains'] = dialogue['completed_chains'][-10:]
                    dialogue['current_chain'] = []
                    dialogue['active_topic'] = None
                else:
                    dialogue['current_chain'] = chain
                    dialogue['active_topic'] = topic
                
                dialogue['chain_depth'] = len(dialogue.get('current_chain', []))
                save_dialogue(dialogue)
                
                # Update emotions
                brain = update_emotions_from_thought(brain, thought)
                save_brain(brain)
                
                # Log thought
                log_thought(thought, thought_type, topic, brain['emotions'])
                
                print(f"[{datetime.now(timezone.utc).strftime('%H:%M')}] [{thought_type}] {thought[:70]}...")
            
            # Status and sync every SYNC_INTERVAL cycles
            if cycle % SYNC_INTERVAL == 0:
                print(f"--- Cycle {cycle} | Chain: {dialogue.get('chain_depth', 0)}/5 ---")
                # Sync thoughts to GitHub Gist
                sync_to_gist()
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\nShutting down...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
