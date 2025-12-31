"""
GNA v3.0 Emotion Logger
Logs full brain state to CSV for analysis and visualization.
"""

import csv
import os
from datetime import datetime

LOG_FILE = 'logs/emotion_data.csv'

# All columns we want to track
EMOTION_COLUMNS = ['joy', 'fear', 'anger', 'sadness', 'curiosity', 
                   'fatigue', 'trust', 'confidence', 'shame', 'hope']
DRIVE_COLUMNS = ['energy', 'social', 'ego', 'fun', 'safety', 
                 'coherence', 'novelty', 'purpose', 'autonomy', 'continuity']

def init_log():
    """Creates the CSV file with headers if it doesn't exist."""
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Build header row
            headers = [
                "Timestamp", 
                "User_Input", 
                "Dominant_Emotion",
                "Current_Goal",
                "Winner",
            ]
            # Add emotion columns
            headers.extend([f"E_{e}" for e in EMOTION_COLUMNS])
            # Add drive columns
            headers.extend([f"D_{d}" for d in DRIVE_COLUMNS])
            
            writer.writerow(headers)

def log_state(user_input, brain_state, emotions, dominant_emotion):
    """Saves a snapshot of the brain to the CSV."""
    init_log()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    needs = brain_state.get('needs', {})
    
    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        row = [
            timestamp,
            user_input.replace(",", ";").replace("\n", " ")[:100],  # Truncate for sanity
            dominant_emotion,
            brain_state.get('current_goal', 'UNKNOWN'),
            brain_state.get('winner', 'perception'),
        ]
        
        # Add emotion values
        for emotion in EMOTION_COLUMNS:
            val = emotions.get(emotion, 0)
            row.append(f"{val:.3f}")
        
        # Add drive values  
        for drive in DRIVE_COLUMNS:
            val = needs.get(drive, 0)
            row.append(f"{val:.1f}")
        
        writer.writerow(row)

def get_recent_logs(n=10):
    """Returns the last N log entries for display/analysis."""
    if not os.path.exists(LOG_FILE):
        return []
    
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    return rows[-n:] if len(rows) > n else rows