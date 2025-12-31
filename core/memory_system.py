import json
import os
from datetime import datetime

MEMORY_FILE = 'brain.json'

def load_memory():
    """Reads the brain and returns a summary string."""
    if not os.path.exists(MEMORY_FILE):
        return ""
    
    try:
        with open(MEMORY_FILE, 'r') as f:
            memories = json.load(f)
        
        # Turn list of objects into a single text block
        memory_string = "\n".join([f"- [{m['date']}] {m['content']}" for m in memories])
        return memory_string
    except:
        return ""

def save_memory(content):
    """Saves a new fact to the brain."""
    # 1. Load existing
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            try:
                memories = json.load(f)
            except:
                memories = []
    else:
        memories = []

    # 2. Add new memory
    new_memory = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "content": content
    }
    memories.append(new_memory)

    # 3. Save back to file
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memories, f, indent=4)
    
    print(f"  [MEMORY STORED: {content}]")