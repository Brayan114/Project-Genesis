"""
GNA v3.0 Dashboard
Visualization tool for Genesis's emotional and cognitive data.

Run with: python dashboard.py
Requires: matplotlib, pandas (pip install matplotlib pandas)
"""

import csv
import os
import json
from datetime import datetime

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Patch
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("⚠️  matplotlib not found. Install with: pip install matplotlib")

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("⚠️  pandas not found. Install with: pip install pandas")

# === FILE PATHS ===
LOG_FILE = 'logs/emotion_data.csv'
BRAIN_FILE = 'brain_state.json'
SELF_FILE = 'self_state.json'
MEMORY_FILE = 'episodic_memory.json'

# === COLORS ===
EMOTION_COLORS = {
    'joy': '#FFD700',       # Gold
    'fear': '#8B0000',      # Dark Red
    'anger': '#FF4500',     # Orange Red
    'sadness': '#4169E1',   # Royal Blue
    'curiosity': '#32CD32', # Lime Green
    'fatigue': '#808080',   # Gray
    'trust': '#9370DB',     # Medium Purple
    'confidence': '#FF69B4', # Hot Pink
    'shame': '#8B4513',     # Saddle Brown
    'hope': '#00CED1',      # Dark Turquoise
}

DRIVE_COLORS = {
    'energy': '#FFD700',
    'social': '#FF69B4',
    'ego': '#9370DB',
    'fun': '#32CD32',
    'safety': '#4169E1',
    'coherence': '#00CED1',
    'novelty': '#FF4500',
    'purpose': '#8B0000',
    'autonomy': '#808080',
    'continuity': '#8B4513',
}

# === DATA LOADING ===
def load_csv_data():
    """Load emotion log data from CSV."""
    if not os.path.exists(LOG_FILE):
        print(f"❌ No data file found at {LOG_FILE}")
        return None
    
    if not HAS_PANDAS:
        print("❌ pandas required for data analysis")
        return None
    
    df = pd.read_csv(LOG_FILE)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    return df

def load_brain_state():
    """Load current brain state."""
    if not os.path.exists(BRAIN_FILE):
        return None
    with open(BRAIN_FILE, 'r') as f:
        return json.load(f)

def load_self_state():
    """Load self state."""
    if not os.path.exists(SELF_FILE):
        return None
    with open(SELF_FILE, 'r') as f:
        return json.load(f)

def load_memories():
    """Load episodic memories."""
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, 'r') as f:
        return json.load(f)

# === VISUALIZATION FUNCTIONS ===
def plot_emotion_timeline(df, emotions=None):
    """Plot emotion values over time."""
    if df is None or not HAS_MATPLOTLIB:
        return
    
    if emotions is None:
        emotions = ['joy', 'fear', 'anger', 'sadness', 'curiosity']
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for emotion in emotions:
        col = f'E_{emotion}'
        if col in df.columns:
            ax.plot(df['Timestamp'], df[col].astype(float), 
                   label=emotion.capitalize(), 
                   color=EMOTION_COLORS.get(emotion, '#000000'),
                   linewidth=2)
    
    ax.set_xlabel('Time')
    ax.set_ylabel('Intensity (0-1)')
    ax.set_title('Genesis Emotional Timeline')
    ax.legend(loc='upper right')
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('logs/emotion_timeline.png', dpi=150)
    print("✅ Saved: logs/emotion_timeline.png")
    plt.show()

def plot_drive_timeline(df, drives=None):
    """Plot drive values over time."""
    if df is None or not HAS_MATPLOTLIB:
        return
    
    if drives is None:
        drives = ['energy', 'social', 'ego', 'safety']
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for drive in drives:
        col = f'D_{drive}'
        if col in df.columns:
            ax.plot(df['Timestamp'], df[col].astype(float), 
                   label=drive.capitalize(), 
                   color=DRIVE_COLORS.get(drive, '#000000'),
                   linewidth=2)
    
    ax.set_xlabel('Time')
    ax.set_ylabel('Level (0-100)')
    ax.set_title('Genesis Drive Levels Over Time')
    ax.legend(loc='upper right')
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('logs/drive_timeline.png', dpi=150)
    print("✅ Saved: logs/drive_timeline.png")
    plt.show()

def plot_goal_distribution(df):
    """Plot distribution of goals."""
    if df is None or not HAS_MATPLOTLIB:
        return
    
    goal_counts = df['Current_Goal'].value_counts()
    
    colors = {
        'ASSIST': '#32CD32',
        'EXPLORE': '#00CED1',
        'ATTACK': '#FF4500',
        'FLEE': '#FFD700',
        'COMPLAIN': '#4169E1',
        'SEEK_VALIDATION': '#9370DB',
        'DOMINATE': '#FF69B4',
        'BOND': '#FF1493',
        'SURVIVE': '#8B0000',
        'REST': '#808080',
    }
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(goal_counts.index, goal_counts.values,
                  color=[colors.get(g, '#000000') for g in goal_counts.index])
    
    ax.set_xlabel('Goal State')
    ax.set_ylabel('Frequency')
    ax.set_title('Genesis Goal Distribution')
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig('logs/goal_distribution.png', dpi=150)
    print("✅ Saved: logs/goal_distribution.png")
    plt.show()

def plot_current_state():
    """Plot current brain state as radar chart."""
    if not HAS_MATPLOTLIB:
        return
    
    brain = load_brain_state()
    if brain is None:
        print("❌ No brain state found")
        return
    
    emotions = brain.get('emotions', {})
    
    # Prepare radar chart
    categories = list(emotions.keys())
    values = [emotions[c] for c in categories]
    values += [values[0]]  # Close the polygon
    categories += [categories[0]]
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
    
    angles = [n / float(len(categories[:-1])) * 2 * 3.14159 for n in range(len(categories))]
    
    ax.plot(angles, values, 'o-', linewidth=2, color='#FF69B4')
    ax.fill(angles, values, alpha=0.25, color='#FF69B4')
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([c.capitalize() for c in categories[:-1]])
    ax.set_ylim(0, 1)
    ax.set_title('Current Emotional State', size=14, y=1.1)
    
    plt.tight_layout()
    plt.savefig('logs/current_state.png', dpi=150)
    print("✅ Saved: logs/current_state.png")
    plt.show()

def plot_memory_analysis():
    """Analyze and plot memory data."""
    if not HAS_MATPLOTLIB:
        return
    
    memories = load_memories()
    if not memories:
        print("❌ No memories found")
        return
    
    # Extract data
    trauma_weights = [m.get('trauma_weight', 0) for m in memories]
    nostalgia_weights = [m.get('nostalgia_weight', 0) for m in memories]
    importances = [m.get('importance', 5) for m in memories]
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Trauma vs Nostalgia scatter
    axes[0].scatter(trauma_weights, nostalgia_weights, 
                   c=importances, cmap='RdYlGn', s=100, alpha=0.7)
    axes[0].set_xlabel('Trauma Weight')
    axes[0].set_ylabel('Nostalgia Weight')
    axes[0].set_title('Memory Emotional Distribution')
    axes[0].set_xlim(0, 1)
    axes[0].set_ylim(0, 1)
    
    # Importance histogram
    axes[1].hist(importances, bins=10, color='#9370DB', edgecolor='black')
    axes[1].set_xlabel('Importance Score')
    axes[1].set_ylabel('Frequency')
    axes[1].set_title('Memory Importance Distribution')
    
    # Memory types pie chart
    trauma_count = sum(1 for m in memories if m.get('trauma_weight', 0) > 0.3)
    nostalgia_count = sum(1 for m in memories if m.get('nostalgia_weight', 0) > 0.5)
    neutral_count = len(memories) - trauma_count - nostalgia_count
    
    if trauma_count + nostalgia_count + neutral_count > 0:
        axes[2].pie([trauma_count, nostalgia_count, max(0, neutral_count)],
                   labels=['Trauma', 'Nostalgia', 'Neutral'],
                   colors=['#8B0000', '#FFD700', '#808080'],
                   autopct='%1.1f%%')
        axes[2].set_title('Memory Type Distribution')
    
    plt.tight_layout()
    plt.savefig('logs/memory_analysis.png', dpi=150)
    print("✅ Saved: logs/memory_analysis.png")
    plt.show()

def print_status_report():
    """Print a text-based status report."""
    print("\n" + "="*60)
    print("         GENESIS STATUS REPORT")
    print("="*60)
    
    # Brain state
    brain = load_brain_state()
    if brain:
        emotions = brain.get('emotions', {})
        needs = brain.get('needs', {})
        
        print("\n📊 CURRENT EMOTIONS:")
        sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
        for emotion, value in sorted_emotions[:5]:
            bar = "█" * int(value * 20)
            print(f"  {emotion:12} {bar:20} {value:.0%}")
        
        print("\n⚡ CURRENT DRIVES:")
        for drive in ['energy', 'social', 'ego', 'safety']:
            value = needs.get(drive, 0)
            bar = "█" * int(value / 5)
            print(f"  {drive:12} {bar:20} {value:.0f}/100")
        
        print(f"\n🎯 Current Goal: {brain.get('current_goal', 'UNKNOWN')}")
        print(f"🏆 Winner: {brain.get('winner', 'unknown')}")
    
    # Self state
    self_state = load_self_state()
    if self_state:
        print("\n👤 SELF MODEL:")
        print(f"  Messages: {self_state.get('total_messages', 0)}")
        print(f"  Continuity: {self_state.get('continuity_score', 1):.0%}")
        rel = self_state.get('relationship', {})
        print(f"  Attachment: {rel.get('attachment', 0):.0f}/100")
        print(f"  Trust: {rel.get('trust', 0):.0f}/100")
    
    # Memories
    memories = load_memories()
    if memories:
        trauma_count = sum(1 for m in memories if m.get('trauma_weight', 0) > 0.3)
        nostalgia_count = sum(1 for m in memories if m.get('nostalgia_weight', 0) > 0.5)
        print(f"\n💾 MEMORIES: {len(memories)} total")
        print(f"  ⚠️  Trauma: {trauma_count}")
        print(f"  💫 Nostalgia: {nostalgia_count}")
    
    print("\n" + "="*60)

# === MAIN ===
def main():
    """Main dashboard entry point."""
    print("\n🧠 GENESIS NEURAL DASHBOARD v1.0\n")
    
    # Check dependencies
    if not HAS_MATPLOTLIB or not HAS_PANDAS:
        print("⚠️  Some features disabled. Install dependencies with:")
        print("   pip install matplotlib pandas")
        print()
    
    # Always show text report
    print_status_report()
    
    if not HAS_MATPLOTLIB or not HAS_PANDAS:
        return
    
    # Load data
    df = load_csv_data()
    
    if df is None or len(df) < 2:
        print("\n⚠️  Not enough data for charts. Chat with Genesis more!")
        return
    
    print("\n📈 Generating visualizations...\n")
    
    # Generate all charts
    try:
        plot_emotion_timeline(df)
    except Exception as e:
        print(f"⚠️  Emotion timeline failed: {e}")
    
    try:
        plot_drive_timeline(df)
    except Exception as e:
        print(f"⚠️  Drive timeline failed: {e}")
    
    try:
        plot_goal_distribution(df)
    except Exception as e:
        print(f"⚠️  Goal distribution failed: {e}")
    
    try:
        plot_current_state()
    except Exception as e:
        print(f"⚠️  Current state failed: {e}")
    
    try:
        plot_memory_analysis()
    except Exception as e:
        print(f"⚠️  Memory analysis failed: {e}")
    
    print("\n✅ Dashboard complete! Charts saved to logs/")

if __name__ == "__main__":
    main()
