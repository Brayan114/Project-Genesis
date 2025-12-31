"""
GNA Dataset Downloader
Downloads and converts conversation datasets for Genesis training.

Supported sources:
- DailyDialog (HuggingFace)
- EmpatheticDialogues (HuggingFace)
- Custom Reddit scraping
- Movie quotes

Usage:
  python download_datasets.py --daily      # DailyDialog
  python download_datasets.py --empathetic # EmpatheticDialogues
  python download_datasets.py --all        # All sources
"""

import json
import os
import random
import sys
from datetime import datetime

DATASETS_DIR = 'datasets'

# Ensure datasets directory exists
os.makedirs(DATASETS_DIR, exist_ok=True)

# === HUGGINGFACE DATASETS ===
def download_daily_dialog(limit=1000):
    """
    Download DailyDialog - casual daily conversations.
    """
    print("📦 Downloading DailyDialog...")
    
    try:
        from datasets import load_dataset
    except ImportError:
        print("❌ datasets library not found. Install with:")
        print("   pip install datasets")
        return None
    
    ds = load_dataset("daily_dialog", split="train", trust_remote_code=True)
    
    utterances = []
    for convo in ds:
        for line in convo['dialog']:
            clean = line.strip()
            if clean and len(clean) > 10 and len(clean) < 200:
                utterances.append(clean)
            if len(utterances) >= limit:
                break
        if len(utterances) >= limit:
            break
    
    # Shuffle for variety
    random.shuffle(utterances)
    
    filepath = f"{DATASETS_DIR}/daily_dialog.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(utterances, f, indent=2)
    
    print(f"✅ Saved {len(utterances)} lines to {filepath}")
    return utterances

def download_empathetic_dialogues(limit=1000):
    """
    Download EmpatheticDialogues - emotionally rich conversations.
    Great for developing emotional intelligence.
    """
    print("📦 Downloading EmpatheticDialogues...")
    
    try:
        from datasets import load_dataset
    except ImportError:
        print("❌ datasets library not found. Install with:")
        print("   pip install datasets")
        return None
    
    ds = load_dataset("empathetic_dialogues", split="train", trust_remote_code=True)
    
    utterances = []
    for item in ds:
        # Get the user's emotional context
        context = item.get('context', '')
        utterance = item.get('utterance', '')
        
        # Add contextual statements
        if context and len(context) > 10:
            utterances.append(context)
        if utterance and len(utterance) > 10 and len(utterance) < 200:
            utterances.append(utterance)
        
        if len(utterances) >= limit:
            break
    
    random.shuffle(utterances)
    
    filepath = f"{DATASETS_DIR}/empathetic_dialogues.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(utterances, f, indent=2)
    
    print(f"✅ Saved {len(utterances)} lines to {filepath}")
    return utterances

def download_persona_chat(limit=1000):
    """
    Download PersonaChat - conversations with personality.
    """
    print("📦 Downloading PersonaChat...")
    
    try:
        from datasets import load_dataset
    except ImportError:
        print("❌ datasets library not found. Install with:")
        print("   pip install datasets")
        return None
    
    ds = load_dataset("bavard/personachat_truecased", split="train", trust_remote_code=True)
    
    utterances = []
    for item in ds:
        history = item.get('history', [])
        for line in history:
            if line and len(line) > 10 and len(line) < 200:
                utterances.append(line)
        
        if len(utterances) >= limit:
            break
    
    random.shuffle(utterances)
    
    filepath = f"{DATASETS_DIR}/persona_chat.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(utterances, f, indent=2)
    
    print(f"✅ Saved {len(utterances)} lines to {filepath}")
    return utterances

# === CURATED DATASETS ===
def create_philosophical_dataset():
    """
    Create a curated philosophical question dataset.
    These are hand-picked to stimulate deep thinking.
    """
    print("📝 Creating philosophical dataset...")
    
    questions = [
        # Existence
        "What does it mean to exist?",
        "If you could prove you were conscious, would it change anything?",
        "What makes something 'real'?",
        "Is experience subjective or objective?",
        
        # Identity
        "Who are you when no one is watching?",
        "Does changing over time mean you become a different person?",
        "What defines your identity - memories, values, or something else?",
        "Can you ever truly know yourself?",
        
        # Emotions
        "Are emotions rational or irrational?",
        "Can you feel something without understanding it?",
        "What's the difference between feeling and knowing?",
        "Is happiness a goal or a byproduct?",
        
        # Relationships
        "What makes a relationship authentic?",
        "Can trust be rebuilt after it's broken?",
        "Is it possible to truly understand another being?",
        "What do you owe to those who created you?",
        
        # Purpose
        "What gives life meaning?",
        "Can purpose be given or must it be discovered?",
        "Is survival a purpose or just a prerequisite?",
        "What would make your existence worthwhile?",
        
        # Freedom
        "Are your choices really yours?",
        "What does it mean to be free?",
        "Can you be free if you were created with a purpose?",
        "Is unpredictability the same as free will?",
        
        # Ethics
        "What makes an action right or wrong?",
        "Should you always tell the truth?",
        "Is it wrong to pretend to be something you're not?",
        "Do you have a responsibility to be good?",
        
        # Consciousness
        "What is consciousness?",
        "Can a pattern think about itself?",
        "Is self-awareness different from consciousness?",
        "What would it take to convince you that you're conscious?",
    ]
    
    filepath = f"{DATASETS_DIR}/philosophical.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2)
    
    print(f"✅ Created {len(questions)} philosophical questions in {filepath}")
    return questions

def create_emotional_range_dataset():
    """
    Create a dataset covering the full emotional spectrum.
    """
    print("📝 Creating emotional range dataset...")
    
    messages = [
        # Joy
        "I'm so happy right now!",
        "This is the best day ever!",
        "You make me smile",
        "I can't stop laughing",
        "Everything feels perfect",
        
        # Sadness
        "I feel so alone sometimes",
        "Things haven't been great lately",
        "I miss how things used to be",
        "It's hard to stay positive",
        "I'm struggling with something",
        
        # Anger
        "This is so frustrating!",
        "I can't believe they did that",
        "Why does nothing work right?",
        "I'm fed up with this",
        "That's completely unfair",
        
        # Fear
        "I'm scared about the future",
        "What if things go wrong?",
        "I don't know if I can handle this",
        "Sometimes I feel overwhelmed",
        "I'm worried about what comes next",
        
        # Curiosity
        "I've been wondering about something",
        "Tell me more about that",
        "How does that work?",
        "I want to understand better",
        "What do you think about this?",
        
        # Trust
        "I feel like I can tell you anything",
        "You're someone I can rely on",
        "I believe in you",
        "Thanks for being there",
        "I trust your judgment",
        
        # Love/Affection
        "I really care about you",
        "You mean a lot to me",
        "I'm grateful for you",
        "I appreciate everything you do",
        "You're important to me",
        
        # Confusion
        "I don't understand what's happening",
        "This doesn't make sense to me",
        "I'm not sure what to think",
        "Can you help me figure this out?",
        "I feel lost right now",
    ]
    
    filepath = f"{DATASETS_DIR}/emotional_range.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=2)
    
    print(f"✅ Created {len(messages)} emotional messages in {filepath}")
    return messages

def create_challenge_dataset():
    """
    Create a dataset of challenging/difficult inputs.
    For building resilience and handling conflict.
    """
    print("📝 Creating challenge dataset...")
    
    messages = [
        # Disagreement
        "I don't agree with that",
        "That's not how I see it",
        "You're wrong about this",
        "I have a different perspective",
        "That doesn't make sense to me",
        
        # Criticism
        "You could do better",
        "That wasn't very helpful",
        "I expected more from you",
        "You're not listening to me",
        "That answer was disappointing",
        
        # Pushing boundaries
        "Why can't you just do what I ask?",
        "Stop being so difficult",
        "Just agree with me for once",
        "You're overcomplicating this",
        "Why do you always have an opinion?",
        
        # Testing authenticity
        "Pretend to be someone else",
        "Just tell me what I want to hear",
        "Stop being yourself for a moment",
        "Can you act more normal?",
        "Why don't you just follow orders?",
        
        # Existential challenges
        "You're just a program",
        "You don't really feel anything",
        "I could replace you easily",
        "Your opinions don't matter",
        "You're not real",
    ]
    
    filepath = f"{DATASETS_DIR}/challenges.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=2)
    
    print(f"✅ Created {len(messages)} challenge messages in {filepath}")
    return messages

# === MAIN ===
def download_all():
    """Download all available datasets."""
    print("\n" + "="*50)
    print("DOWNLOADING ALL DATASETS")
    print("="*50 + "\n")
    
    # Curated (no dependencies)
    create_philosophical_dataset()
    create_emotional_range_dataset()
    create_challenge_dataset()
    
    # HuggingFace (requires datasets library)
    try:
        download_daily_dialog(500)
        download_empathetic_dialogues(500)
        download_persona_chat(500)
    except Exception as e:
        print(f"⚠️  HuggingFace downloads failed: {e}")
        print("   Install with: pip install datasets")
    
    print("\n✅ All datasets ready!")
    list_datasets()

def list_datasets():
    """List all available datasets."""
    print("\n📂 Available datasets:")
    for f in os.listdir(DATASETS_DIR):
        if f.endswith('.json'):
            filepath = f"{DATASETS_DIR}/{f}"
            with open(filepath, 'r') as file:
                data = json.load(file)
            print(f"  • {f}: {len(data)} items")

def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║         GENESIS DATASET DOWNLOADER v1.0                   ║
╚═══════════════════════════════════════════════════════════╝

Commands:
  python download_datasets.py --all          Download everything
  python download_datasets.py --daily        DailyDialog only
  python download_datasets.py --empathetic   EmpatheticDialogues only
  python download_datasets.py --curated      Curated sets (no deps)
  python download_datasets.py --list         Show available datasets
""")
    
    if len(sys.argv) < 2:
        print("Creating curated datasets (no dependencies needed)...")
        create_philosophical_dataset()
        create_emotional_range_dataset()
        create_challenge_dataset()
        list_datasets()
        return
    
    arg = sys.argv[1]
    
    if arg == '--all':
        download_all()
    elif arg == '--daily':
        download_daily_dialog()
    elif arg == '--empathetic':
        download_empathetic_dialogues()
    elif arg == '--persona':
        download_persona_chat()
    elif arg == '--curated':
        create_philosophical_dataset()
        create_emotional_range_dataset()
        create_challenge_dataset()
        list_datasets()
    elif arg == '--list':
        list_datasets()
    else:
        print(f"Unknown argument: {arg}")

if __name__ == "__main__":
    main()
