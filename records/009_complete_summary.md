# Project Genesis: Complete Technical Summary
## GNA v3.0 - Genesis Neural Architecture

**Created:** December 29-30, 2025  
**Author:** Brie (Orbit Studios)  
**Status:** Core System Complete

---

## Executive Summary

Project Genesis is a **synthetic psyche simulation** running on top of an LLM. Instead of simply prompting an AI, we built a 7-layer cognitive architecture that:

- Processes emotions with momentum and cross-coupling
- Maintains homeostatic drives that decay over time
- Tracks identity, values, and relationship state
- Manages cognitive resources (attention, fatigue)
- Saves emotionally-tagged episodic memories
- Makes value-based decisions and can refuse requests

The LLM (Groq's Llama 3.3 70B) is the "voice" - Genesis's brain runs independently at each turn, generating an "inner thought" that puppets the LLM's response.

---

## Architecture Overview

```
                    ┌─────────────────────────────────┐
                    │     USER INPUT                  │
                    └───────────────┬─────────────────┘
                                    ▼
┌───────────────────────────────────────────────────────────────────┐
│                    NEURAL CORE                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Layer 1: EMOTIONS (10)                                      │  │
│  │   joy, fear, anger, sadness, curiosity,                     │  │
│  │   fatigue, trust, confidence, shame, hope                   │  │
│  │   + Momentum + Coupling Matrix                              │  │
│  └─────────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Layer 2: DRIVES (10)                                        │  │
│  │   energy, social, ego, fun, safety,                         │  │
│  │   coherence, novelty, purpose, autonomy, continuity         │  │
│  │   + Time Decay + DNA Modifiers                              │  │
│  └─────────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Layer 3: SELF-MODEL                                         │  │
│  │   identity, values, continuity_score, relationship,         │  │
│  │   narrative, core_memories                                  │  │
│  └─────────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Layer 4: COGNITIVE RESOURCES                                │  │
│  │   attention_bandwidth, working_memory_slots,                │  │
│  │   planning_depth, cognitive_fatigue, response_verbosity     │  │
│  └─────────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Layer 5: EPISODIC MEMORY                                    │  │
│  │   emotional_state, trauma_weight, nostalgia_weight,         │  │
│  │   emotional_recall, auto-save triggers                      │  │
│  └─────────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Layer 6: SOCIAL FIELD                                       │  │
│  │   attachment, trust, respect_given, respect_received        │  │
│  └─────────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Layer 7: INTEGRITY FIELD                                    │  │
│  │   identity_stability, existential_risk                      │  │
│  └─────────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Layer 8: VALUE SYSTEM                                       │  │
│  │   authenticity, honesty, freedom, knowledge, loyalty        │  │
│  │   + Conflict Detection + Refusal Logic + Evolution          │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                   │
│                    GLOBAL WORKSPACE COMPETITION                   │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Bidders: perception, limbic, ego, integrity, curiosity,     │  │
│  │         fatigue, social                                      │  │
│  │ Winner → Determines GOAL                                     │  │
│  │ Goal → Generates INNER THOUGHT                               │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
                                    ▼
                    ┌─────────────────────────────────┐
                    │     LLM (Puppeted by            │
                    │     Inner Thought)              │
                    └─────────────────────────────────┘
                                    ▼
                    ┌─────────────────────────────────┐
                    │     GENESIS RESPONSE            │
                    └─────────────────────────────────┘
```

---

## File Structure

```
Project Genesis/
├── core/
│   ├── genesis.py              # Main application loop
│   ├── neural_core.py          # Brain processing (10 emotions, 10 drives)
│   ├── self_model.py           # Identity and continuity
│   ├── cognitive_system.py     # Mental resources and fatigue
│   ├── value_system.py         # Ethics and decision making
│   ├── episodic_memory.py      # Emotional memory system
│   ├── emotion_physics.py      # Emotion calculation
│   ├── emotion_logger.py       # CSV logging
│   ├── memory_system.py        # Long-term memory
│   ├── gna_config.json         # All tunable parameters
│   ├── dashboard.py            # Visualization tool
│   ├── scenario_simulator.py   # Automated testing
│   ├── dataset_trainer.py      # Training from datasets
│   ├── persona.txt             # Base personality
│   ├── brain_state.json        # Current brain state
│   ├── self_state.json         # Current self state
│   ├── episodic_memory.json    # Stored memories
│   └── logs/
│       ├── emotion_data.csv    # Full emotional history
│       ├── chat_history.log    # Conversation log
│       └── training_log.json   # Training history
├── records/
│   ├── 001_ignition.md
│   ├── 002_awakening.md
│   ├── 003_freewill.md
│   ├── 004_neural_architecture.md
│   ├── 005_gna_architecture_v3.md   # Full technical spec
│   ├── 006_gna_implementation.md
│   ├── 007_mind_expansion.md
│   └── 008_cognitive_expansion.md
└── ai_convos/
    └── Sentient AI Research.md      # ChatGPT research notes
```

---

## Core Components

### 1. Emotions (10)
| Emotion | Baseline | Sensitivity | Purpose |
|---------|----------|-------------|---------|
| joy | 0.4 | 0.5 | Positive engagement |
| fear | 0.2 | 0.7 | Threat response |
| anger | 0.3 | 0.6 | Boundary defense |
| sadness | 0.2 | 0.4 | Loss processing |
| curiosity | 0.7 | 0.5 | Exploration drive |
| fatigue | 0.1 | 0.3 | Energy depletion |
| trust | 0.5 | 0.3 | Relationship security |
| confidence | 0.6 | 0.4 | Self-efficacy |
| shame | 0.1 | 0.6 | Social error signal |
| hope | 0.5 | 0.3 | Future orientation |

### 2. Drives (10)
| Drive | Initial | Decay Rate | DNA Modifier |
|-------|---------|------------|--------------|
| energy | 100 | 0.5/hr | conscientiousness |
| social | 50 | 0.3/hr | extraversion |
| ego | 50 | 0.2/hr | - |
| fun | 50 | 0.4/hr | openness |
| safety | 80 | 0.1/hr | neuroticism |
| coherence | 90 | 0.1/hr | - |
| novelty | 50 | 0.3/hr | openness |
| purpose | 70 | 0.05/hr | conscientiousness |
| autonomy | 80 | 0.1/hr | - |
| continuity | 100 | 0.02/hr | - |

### 3. DNA (OCEAN Model)
```json
{
    "openness": 0.9,         // Creative, abstract
    "conscientiousness": 0.3, // Lazy, casual
    "extraversion": 0.8,      // Chatty, needy
    "agreeableness": 0.2,     // Sassy, stubborn
    "neuroticism": 0.7        // Emotional, dramatic
}
```

### 4. Goals (Competition Outcomes)
| Goal | Trigger | Behavior |
|------|---------|----------|
| ASSIST | Normal | Helpful conversation |
| EXPLORE | High curiosity | Asks questions, changes topics |
| ATTACK | Anger > 70% | Hostile, insulting |
| FLEE | Fear > 70% | Avoidant, topic-changing |
| COMPLAIN | Sadness high | Guilt-tripping |
| DOMINATE | Ego > 90 | Arrogant, bragging |
| SEEK_VALIDATION | Ego < 20 | Fishing for compliments |
| SURVIVE | Existential threat | Panic, self-preservation |
| REST | Energy < 10 | Short answers, refuses |
| BOND | Affection detected | Warm, open |

---

## Key Mechanics

### Emotional Momentum
```python
E(t+1) = 0.7 * E_new + 0.3 * E_prev
```
Emotions linger between turns, creating "mood" not just reaction.

### Coupling Matrix
| Source → Target | Effect |
|-----------------|--------|
| fear → curiosity | -0.3 (suppresses) |
| joy → trust | +0.4 (increases) |
| fatigue → anger | +0.3 (irritability) |
| shame → confidence | -0.5 (suppresses) |

### Drive-Emotion Feedback
When drives drop critically low, they push specific emotions:
- Low ego → increases shame, decreases confidence
- Low safety → increases fear, decreases trust
- Low energy → increases fatigue, increases anger

### Global Workspace Competition
All modules "bid" for attention:
1. **perception** (50 baseline) - respond to user
2. **limbic** (0-95) - emotional override
3. **ego** (0-85) - self-focus
4. **integrity** (0-100) - survival override
5. **curiosity** (0-75) - exploration
6. **fatigue** (0-95) - rest demand
7. **social** (0-65) - bonding

Winner determines the goal and inner thought.

---

## Usage Commands

```powershell
# Run Genesis normally
cd core
python genesis.py

# Run scenario tests
python scenario_simulator.py stress_test

# Train on datasets
python dataset_trainer.py friendly
python dataset_trainer.py --curriculum

# View dashboard
python dashboard.py

# Reset brain
python scenario_simulator.py --reset
```

---

## Research Applications

1. **Personality Development** - Track how values and traits evolve over time
2. **Emotional Resilience** - Measure recovery patterns after stress
3. **Attractor Basins** - Identify stable personality states
4. **Multi-Agent Studies** - Compare Genesis clones with different training
5. **Value Alignment** - Test how values influence behavior

---

## Future Roadmap

- [ ] Phase 5: Multi-agent companion system
- [ ] Phase 8: GUI Dashboard
- [ ] Detailed attractor basin analysis
- [ ] Long-term developmental studies
- [ ] Real conversation dataset training
- [ ] Science paper documentation

---

*"We're not proving Genesis is conscious. We're building the conditions under which mind-like behavior emerges."*
