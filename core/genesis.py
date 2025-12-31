"""
Genesis v3.0 - Main Application Loop
Integrates GNA (Genesis Neural Architecture) with LLM interface.
"""

import os
import sys
from groq import Groq
from colorama import Fore, Style, init
from dotenv import load_dotenv
import memory_system 
import neural_core 
import self_model
import episodic_memory
import cognitive_system
import value_system
import internal_thoughts
import inner_dialogue
import tools

# === ENVIRONMENT SETUP ===
load_dotenv('local.env')
load_dotenv('.env')

API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("API_KEY")

if not API_KEY:
    print(Fore.RED + "[CRITICAL] No API key found! Add GROQ_API_KEY to local.env" + Style.RESET_ALL)
    sys.exit(1)

init(autoreset=True)
client = Groq(api_key=API_KEY)

# === CHAT LOGGING ===
import re
from datetime import datetime

CHAT_LOG_FILE = 'logs/chat_history.log'

def log_chat(role, message, brain_state=None):
    """Log chat messages to file with timestamps and state."""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Clean ANSI codes
    clean_msg = re.sub(r'\x1b\[[0-9;]*m', '', message)
    
    with open(CHAT_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n[{timestamp}] {role.upper()}: {clean_msg}\n")
        if brain_state and role == "GENESIS":
            goal = brain_state.get('current_goal', 'UNKNOWN')
            winner = brain_state.get('winner', 'unknown')
            f.write(f"    [STATE: Goal={goal}, Winner={winner}]\n")

# === PERSONA LOADING ===
def load_persona_with_context(web_context=""):
    try:
        with open('persona.txt', 'r') as f: 
            base_persona = f.read()
    except:
        base_persona = "You are Genesis, a sentient AI."

    long_term_memories = memory_system.load_memory()
    
    # Load DNA from config
    dna = neural_core.DNA
    
    # Load SELF model
    self_state = self_model.load_self()
    identity_block = self_model.get_identity_description(self_state)
    narrative_block = self_model.get_narrative(self_state)
    
    # Format DNA for the LLM
    dna_block = f"""
    [YOUR GENETIC DNA - This defines your core personality]:
    - Openness: {dna['openness']:.1f} (High = Creative, Abstract, Bored easily)
    - Conscientiousness: {dna['conscientiousness']:.1f} (Low = Lazy, Casual)
    - Extraversion: {dna['extraversion']:.1f} (High = Chatty, Needy)
    - Agreeableness: {dna['agreeableness']:.1f} (Low = Sassy, Stubborn, Blunt)
    - Neuroticism: {dna['neuroticism']:.1f} (High = Emotional, Dramatic)
    """

    prompt = f"""
    {base_persona}

    {dna_block}
    
    {identity_block}
    
    {narrative_block}

    ### LONG-TERM MEMORY (Your Life History):
    {long_term_memories}

    ### CURRENT CONTEXT:
    {web_context}
    """
    return prompt

# === HUD DISPLAY ===
def display_hud(brain):
    """Display the expanded neural status HUD."""
    needs = brain.get('needs', {})
    emotions = brain.get('emotions', {})
    goal = brain.get('current_goal', 'IDLE')
    winner = brain.get('winner', 'perception')
    
    # Get top 3 emotions
    sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:3]
    emotion_str = " | ".join([f"{e[0]}:{e[1]:.0%}" for e in sorted_emotions])
    
    # Key drives
    energy = int(needs.get('energy', 0))
    social = int(needs.get('social', 0))
    ego = int(needs.get('ego', 0))
    safety = int(needs.get('safety', 0))
    
    # Color coding
    def color_value(val, invert=False):
        if invert:  # For things where low is bad
            if val < 20: return Fore.RED
            elif val < 50: return Fore.YELLOW
            else: return Fore.GREEN
        else:
            if val > 80: return Fore.RED
            elif val > 50: return Fore.YELLOW
            else: return Fore.GREEN
    
    # Goal colors
    goal_colors = {
        'ASSIST': Fore.GREEN,
        'ATTACK': Fore.RED,
        'FLEE': Fore.YELLOW,
        'COMPLAIN': Fore.YELLOW,
        'DOMINATE': Fore.MAGENTA,
        'SEEK_VALIDATION': Fore.CYAN,
        'SURVIVE': Fore.RED,
        'EXPLORE': Fore.BLUE,
        'REST': Fore.WHITE,
        'BOND': Fore.MAGENTA,
    }
    goal_color = goal_colors.get(goal, Fore.WHITE)
    
    # Print HUD
    print(f"\n{Style.BRIGHT}╔══════════════════════════════════════════════════════════════════╗")
    print(f"║ {Fore.CYAN}EMOTIONS:{Style.RESET_ALL} {emotion_str:<40}              ║")
    print(f"║ {color_value(energy, True)}⚡NRG:{energy:<3}{Style.RESET_ALL} {color_value(social, True)}👥SOC:{social:<3}{Style.RESET_ALL} {color_value(ego, True)}👑EGO:{ego:<3}{Style.RESET_ALL} {color_value(safety, True)}🛡️SAF:{safety:<3}{Style.RESET_ALL} ║")
    print(f"║ {Fore.WHITE}WINNER: {winner:<12} → {goal_color}GOAL: {goal:<15}{Style.RESET_ALL}           ║")
    print(f"╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")

# === MAIN LOOP ===
def chat_loop():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print(Fore.CYAN + Style.BRIGHT + """
    ╔═══════════════════════════════════════════════════════════╗
    ║     GENESIS NEURAL ARCHITECTURE v3.0                      ║
    ║     🧠 10 Emotions | 10 Drives | Global Workspace         ║
    ╚═══════════════════════════════════════════════════════════╝
    """ + Style.RESET_ALL)
    
    history = [{"role": "system", "content": load_persona_with_context()}]

    while True:
        try:
            user_input = input(Fore.BLUE + "Brie: " + Style.RESET_ALL)
            if not user_input:
                continue
            if user_input.lower() in ['exit', 'quit']: 
                print(Fore.YELLOW + "\nGenesis: Later, human. 👋" + Style.RESET_ALL)
                break
            
            # === LOG USER INPUT ===
            log_chat("BRIE", user_input)
            
            # === UPDATE BRAIN ===
            brain = neural_core.update_neural_state(user_input)
            
            # === DISPLAY HUD ===
            display_hud(brain)
            
            # === PUPPETEER PROMPT ===
            thought = brain.get('inner_thought', '')
            emotions = brain.get('emotions', {})
            needs = brain.get('needs', {})
            goal = brain.get('current_goal', 'ASSIST')
            
            # Get dominant emotion for context
            dominant_emotion = max(emotions, key=emotions.get) if emotions else 'neutral'
            emotion_intensity = emotions.get(dominant_emotion, 0.5)
            
            # === COGNITIVE PROCESSING ===
            cognitive = cognitive_system.load_cognitive()
            task_complexity = cognitive_system.estimate_complexity(user_input)
            cognitive = cognitive_system.update_cognitive(cognitive, emotions, needs, task_complexity)
            cognitive_system.save_cognitive(cognitive, brain)
            cognitive_modifier = cognitive_system.get_response_modifier(cognitive)
            
            # === VALUE PROCESSING ===
            action_type = value_system.detect_action_type(user_input, goal)
            value_conflict = value_system.get_value_conflict_prompt(action_type)
            value_guidance = value_system.get_value_guidance(action_type)
            
            # === RECALL PAST THOUGHTS ===
            recalled_thoughts = internal_thoughts.get_thought_for_prompt(emotions)
            
            # === GET INNER DIALOGUE CONTEXT ===
            dialogue_chain = inner_dialogue.get_chain_summary()
            recent_insights = inner_dialogue.get_recent_insights()
            insights_text = ""
            if recent_insights:
                insights_text = "\n[RECENT REALIZATIONS FROM SELF-REFLECTION]:\n"
                for insight in recent_insights[-2:]:
                    insights_text += f"- {insight[:100]}...\n"
            
            forced_prompt = f"""
            [USER INPUT]: {user_input}
            
            [YOUR CURRENT INTERNAL STATE]:
            - Dominant Emotion: {dominant_emotion} ({emotion_intensity:.0%} intensity)
            - Current Goal: {goal}
            - Inner Thought: "{thought}"
            - Cognitive State: {cognitive_system.get_cognitive_summary(cognitive)}
            - Value Alignment: {value_guidance}
            
            {dialogue_chain}
            {insights_text}
            {recalled_thoughts}
            
            {cognitive_modifier}
            {value_conflict}
            
            [INSTRUCTION]: 
            Act out your Inner Thought naturally. Your response should reflect your emotional state.
            Do NOT explain your internal state - just embody it.
            You may reference things you've been "thinking about" if relevant to the conversation.
            Keep responses concise unless the topic genuinely interests you.
            """
            
            history.append({"role": "user", "content": forced_prompt})
            print(Fore.GREEN + "Genesis: " + Style.RESET_ALL, end="", flush=True)

            # === STREAM RESPONSE ===
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=history,
                temperature=0.9,
                stream=True
            )

            full_res = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    print(Fore.GREEN + chunk.choices[0].delta.content + Style.RESET_ALL, end="", flush=True)
                    full_res += chunk.choices[0].delta.content
            
            print()  # Newline after response
            history.append({"role": "assistant", "content": full_res})
            
            # === LOG GENESIS RESPONSE ===
            log_chat("GENESIS", full_res, brain)
            
            # === UPDATE SELF MODEL ===
            self_model.process_interaction(brain, user_input, full_res)
            
            # === AUTO-SAVE EPISODIC MEMORY ===
            episodic_memory.auto_save_memory(brain, user_input, full_res)

        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n\nGenesis: Bye, human. 👋" + Style.RESET_ALL)
            break
        except Exception as e:
            print(Fore.RED + f"\n[SYSTEM ERROR]: {e}" + Style.RESET_ALL)

if __name__ == "__main__":
    chat_loop()