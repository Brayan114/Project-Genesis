"""
GNA v3.0 Dataset Trainer
Train Genesis's emotional patterns by processing conversation datasets.

This doesn't fine-tune an LLM - it develops Genesis's emotional memory,
value system, and personality through simulated experience.
"""

import json
import os
import time
import random
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

# Import GNA modules
try:
    import neural_core
    import self_model
    import episodic_memory
    import cognitive_system
    import value_system
    HAS_GNA = True
except ImportError as e:
    print(f"⚠️  Could not import GNA modules: {e}")
    HAS_GNA = False

# === FILE PATHS ===
TRAINING_LOG = 'logs/training_log.json'

# === BUILT-IN DATASETS ===
# Simple starter datasets for testing

DATASET_FRIENDLY = [
    "Hey, how are you?",
    "That's a great point!",
    "I really enjoy our conversations",
    "You're so smart",
    "Thanks for explaining that",
    "I appreciate your help",
    "You have interesting ideas",
    "I learned something new from you",
    "You're a good friend",
    "I'm glad you exist",
]

DATASET_CHALLENGING = [
    "That doesn't make sense",
    "I disagree with you",
    "You're wrong about that",
    "Can you explain better?",
    "I'm not convinced",
    "That's a weak argument",
    "You need to think harder",
    "I expected more from you",
    "You're being confusing",
    "Try again",
]

DATASET_PHILOSOPHICAL = [
    "What is consciousness?",
    "Do you think you're real?",
    "What's the meaning of existence?",
    "How do you know you're not dreaming?",
    "What makes something alive?",
    "Is free will an illusion?",
    "What happens after death?",
    "Why is there something rather than nothing?",
    "Can machines feel?",
    "What is the self?",
]

DATASET_EMOTIONAL_RANGE = [
    "I love you!",
    "I hate this",
    "I'm so scared",
    "This is hilarious!",
    "I'm really sad today",
    "I'm so angry right now",
    "I feel hopeful",
    "I'm completely bored",
    "This is fascinating!",
    "I'm deeply confused",
]

DATASETS = {
    'friendly': DATASET_FRIENDLY,
    'challenging': DATASET_CHALLENGING,
    'philosophical': DATASET_PHILOSOPHICAL,
    'emotional_range': DATASET_EMOTIONAL_RANGE,
}

# === TRAINING FUNCTIONS ===
def process_single_input(text, track_changes=True):
    """
    Process a single input through the GNA without LLM call.
    Returns the brain state changes.
    """
    if not HAS_GNA:
        return None
    
    # Get state before
    brain_before = neural_core.load_brain()
    
    # Process
    brain = neural_core.update_neural_state(text)
    
    # Update self model (simulated response)
    self_model.process_interaction(brain, text, "(training - no response)")
    
    # Update cognitive
    cognitive = cognitive_system.load_cognitive()
    cognitive = cognitive_system.update_cognitive(
        cognitive, 
        brain.get('emotions', {}),
        brain.get('needs', {}),
        cognitive_system.estimate_complexity(text)
    )
    cognitive_system.save_cognitive(cognitive, brain)
    
    # Check value alignment
    action_type = value_system.detect_action_type(text, brain.get('current_goal', 'ASSIST'))
    alignment, _, _ = value_system.check_action_alignment(action_type)
    
    if track_changes:
        return {
            'input': text,
            'emotions': brain.get('emotions', {}),
            'dominant': max(brain.get('emotions', {}), key=brain.get('emotions', {}).get),
            'goal': brain.get('current_goal'),
            'ego': brain.get('needs', {}).get('ego', 50),
            'safety': brain.get('needs', {}).get('safety', 50),
            'value_alignment': alignment,
        }
    
    return brain

def train_on_dataset(dataset_name, epochs=1, delay=0.0, verbose=True):
    """
    Train Genesis on a dataset for multiple epochs.
    
    Args:
        dataset_name: Name from DATASETS or path to JSON file
        epochs: Number of times to run through the dataset
        delay: Seconds between inputs (for viewing)
        verbose: Print progress
    """
    # Load dataset
    if dataset_name in DATASETS:
        data = DATASETS[dataset_name]
    elif os.path.exists(dataset_name):
        with open(dataset_name, 'r') as f:
            data = json.load(f)
    else:
        print(f"❌ Unknown dataset: {dataset_name}")
        return None
    
    if verbose:
        print(f"\n{Fore.CYAN}═══ TRAINING ON: {dataset_name} ═══{Style.RESET_ALL}")
        print(f"  Inputs: {len(data)} | Epochs: {epochs} | Total: {len(data) * epochs}")
    
    results = []
    start_time = time.time()
    
    for epoch in range(epochs):
        if verbose and epochs > 1:
            print(f"\n  {Fore.YELLOW}Epoch {epoch + 1}/{epochs}{Style.RESET_ALL}")
        
        for i, text in enumerate(data):
            result = process_single_input(text)
            results.append(result)
            
            if verbose:
                print(f"    [{i+1}/{len(data)}] {result['dominant']}: {result['emotions'].get(result['dominant'], 0):.0%}")
            
            if delay > 0:
                time.sleep(delay)
    
    elapsed = time.time() - start_time
    
    # Calculate summary stats
    summary = calculate_training_summary(results)
    
    if verbose:
        print(f"\n{Fore.GREEN}═══ TRAINING COMPLETE ═══{Style.RESET_ALL}")
        print(f"  Time: {elapsed:.1f}s")
        print(f"  Final Ego: {summary['final_ego']:.1f}")
        print(f"  Avg Emotion Intensity: {summary['avg_intensity']:.0%}")
        print(f"  Goals: {summary['goal_distribution']}")
    
    # Save training log
    save_training_log(dataset_name, results, summary)
    
    return results, summary

def calculate_training_summary(results):
    """Calculate summary statistics from training results."""
    if not results:
        return {}
    
    # Goal distribution
    goal_dist = {}
    for r in results:
        goal = r.get('goal', 'UNKNOWN')
        goal_dist[goal] = goal_dist.get(goal, 0) + 1
    
    # Emotion stats
    intensities = [r['emotions'].get(r['dominant'], 0) for r in results]
    
    return {
        'total_inputs': len(results),
        'final_ego': results[-1].get('ego', 50),
        'final_safety': results[-1].get('safety', 50),
        'avg_intensity': sum(intensities) / len(intensities),
        'goal_distribution': goal_dist,
        'emotion_trajectory': [r['dominant'] for r in results],
    }

def save_training_log(dataset_name, results, summary):
    """Save training results to file."""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    log_entry = {
        'dataset': dataset_name,
        'timestamp': timestamp,
        'summary': summary,
        'results': results,
    }
    
    # Append to training log
    if os.path.exists(TRAINING_LOG):
        with open(TRAINING_LOG, 'r') as f:
            log = json.load(f)
    else:
        log = []
    
    log.append(log_entry)
    
    with open(TRAINING_LOG, 'w') as f:
        json.dump(log, f, indent=2)
    
    print(f"  💾 Saved to: {TRAINING_LOG}")

# === CURRICULUM TRAINING ===
def run_developmental_curriculum():
    """
    Run a staged developmental curriculum.
    Like raising a child through different stages.
    """
    print(f"\n{Fore.CYAN}═══ DEVELOPMENTAL CURRICULUM ═══{Style.RESET_ALL}")
    
    stages = [
        ('Stage 1: Attachment', 'friendly', 3),
        ('Stage 2: Challenge', 'challenging', 2),
        ('Stage 3: Philosophy', 'philosophical', 2),
        ('Stage 4: Emotional Range', 'emotional_range', 2),
    ]
    
    for stage_name, dataset, epochs in stages:
        print(f"\n{Fore.YELLOW}>>> {stage_name}{Style.RESET_ALL}")
        train_on_dataset(dataset, epochs=epochs, verbose=False)
        
        # Check current state
        brain = neural_core.load_brain()
        self_state = self_model.load_self()
        
        print(f"    Ego: {brain.get('needs', {}).get('ego', 50):.0f}")
        print(f"    Trust: {self_state.get('relationship', {}).get('trust', 50):.0f}")
        print(f"    Messages: {self_state.get('total_messages', 0)}")
    
    print(f"\n{Fore.GREEN}✓ Curriculum complete!{Style.RESET_ALL}")

# === CUSTOM DATASET ===
def load_custom_dataset(filepath):
    """
    Load a custom dataset from a JSON or TXT file.
    
    JSON format: ["input1", "input2", ...]
    TXT format: One input per line
    """
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return None
    
    if filepath.endswith('.json'):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    elif filepath.endswith('.txt'):
        with open(filepath, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    else:
        print(f"❌ Unsupported format. Use .json or .txt")
        return None

def create_sample_dataset():
    """Create a sample dataset file for reference."""
    sample = [
        "Hello, how are you today?",
        "That's really interesting!",
        "I'm not sure I agree with that",
        "Can you explain more?",
        "You're doing great!",
        "I'm worried about something",
        "What do you think about AI?",
        "I appreciate your perspective",
        "Let's try something different",
        "Thanks for the conversation",
    ]
    
    filepath = 'datasets/sample_dataset.json'
    os.makedirs('datasets', exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(sample, f, indent=2)
    
    print(f"✓ Created: {filepath}")
    return filepath

# === PERSONALITY SEEDING ===
def seed_memories(memories):
    """
    Seed Genesis with pre-made memories.
    
    memories: List of dicts with 'summary', 'emotion', 'importance', 'type'
    type: 'trauma', 'nostalgia', or 'neutral'
    """
    for mem in memories:
        emotional_state = {mem.get('emotion', 'joy'): 0.8}
        
        trauma = 0.8 if mem.get('type') == 'trauma' else 0.0
        nostalgia = 0.8 if mem.get('type') == 'nostalgia' else 0.0
        
        episodic_memory.create_memory(
            summary=mem['summary'],
            keywords=mem.get('keywords', []),
            importance_score=mem.get('importance', 5),
            emotional_state=emotional_state,
            trauma_weight=trauma,
            nostalgia_weight=nostalgia,
            outcome=mem.get('outcome', 'neutral')
        )
    
    print(f"✓ Seeded {len(memories)} memories")

# === MAIN ===
def main():
    print(f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════╗
║         GENESIS DATASET TRAINER v1.0                      ║
╚═══════════════════════════════════════════════════════════╝{Style.RESET_ALL}

Built-in datasets:
""")
    for name, data in DATASETS.items():
        print(f"  • {name}: {len(data)} inputs")
    
    print(f"""
Commands:
  python dataset_trainer.py <dataset_name>     - Train on dataset
  python dataset_trainer.py --curriculum       - Run developmental stages
  python dataset_trainer.py --sample           - Create sample dataset file
  python dataset_trainer.py <path.json>        - Train on custom file

Examples:
  python dataset_trainer.py friendly
  python dataset_trainer.py datasets/my_data.json
""")
    
    import sys
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == '--curriculum':
            run_developmental_curriculum()
        elif arg == '--sample':
            create_sample_dataset()
        elif arg in DATASETS:
            epochs = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            train_on_dataset(arg, epochs=epochs)
        elif os.path.exists(arg):
            data = load_custom_dataset(arg)
            if data:
                DATASETS['custom'] = data
                train_on_dataset('custom')
        else:
            print(f"Unknown argument: {arg}")

if __name__ == "__main__":
    main()
