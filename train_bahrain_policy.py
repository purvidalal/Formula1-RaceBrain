# train_bahrain_policy.py (IMPROVED VERSION)
# Trains a comprehensive Bahrain Q-learning policy for ALL starting compounds
# Saves to models/rl_policy.pkl

import os, pickle, numpy as np
from collections import defaultdict

PARQUET_FILE = "bahrain_2025_clean.parquet"  # optional
DECAY_FILE   = "bahrain_2025_decay.pkl"      # optional
RL_FILE      = "models/rl_policy.pkl"        # FIX: This was missing!
os.makedirs("models", exist_ok=True)

BASE   = {"SOFT": 92.3, "MEDIUM": 93.2, "HARD": 94.1}
SLOPE  = {"SOFT": 0.11, "MEDIUM": 0.085, "HARD": 0.060}
PIT_LOSS = 22.5
RACE_LAPS = 57

# Try to load real data if available
try:
    import pandas as pd
    if os.path.exists(PARQUET_FILE):
        df = pd.read_parquet(PARQUET_FILE)
        lap_col  = "lap_time" if "lap_time" in df.columns else None
        comp_col = "compound" if "compound" in df.columns else None
        age_col  = "tyre_age" if "tyre_age" in df.columns else ("age" if "age" in df.columns else None)
        pit_col  = "pit_delta" if "pit_delta" in df.columns else None
        if lap_col and comp_col:
            fresh = df[df[age_col] <= 1] if age_col else df
            med = fresh.groupby(comp_col)[lap_col].median().to_dict()
            for k in ("SOFT","MEDIUM","HARD"):
                if k in med: BASE[k] = float(med[k])
        if pit_col and pit_col in df:
            PIT_LOSS = float(df[pit_col].clip(lower=0).median())
        print(f"✓ Loaded real data from {PARQUET_FILE}")
except Exception:
    print("ℹ Using default Bahrain pace data")

if os.path.exists(DECAY_FILE):
    try:
        with open(DECAY_FILE,"rb") as f: dec = pickle.load(f)
        if isinstance(dec, dict):
            if "slope" in dec and isinstance(dec["slope"], dict):
                for k in ("SOFT","MEDIUM","HARD"):
                    if k in dec["slope"]: SLOPE[k] = float(dec["slope"][k])
            else:
                for k in ("SOFT","MEDIUM","HARD"):
                    if k in dec: SLOPE[k] = float(dec[k])
        print(f"✓ Loaded degradation data from {DECAY_FILE}")
    except Exception:
        pass

def lap_time(comp: str, age: int) -> float:
    age = max(1, int(age))
    return BASE[comp] + SLOPE[comp] * age

ACTIONS = ["no_pit", "pit"]
STARTS  = ["SOFT","MEDIUM","HARD"]
COMP_IDX = {"SOFT":0,"MEDIUM":1,"HARD":2}
IDX_TO_COMP = {0:"SOFT", 1:"MEDIUM", 2:"HARD"}
BINS = {"lap":5,"age":5}

def binv(v,step): return (int(v)//step)*step

rng = np.random.default_rng(2025)

def valid_actions(pitted: bool): 
    return ["no_pit"] if pitted else ["no_pit","pit"]

def step(state, action, target_after_pit):
    lap, age, comp, pitted = state
    reward = -lap_time(comp, age)
    next_comp, next_pitted, next_age = comp, pitted, age + 1
    if (action=="pit") and (not pitted) and (6 <= lap <= RACE_LAPS-6):
        reward -= PIT_LOSS
        next_comp = target_after_pit
        next_age = 1
        next_pitted = True
    next_lap = lap + 1
    return (next_lap, next_age, next_comp, next_pitted), reward, (next_lap > RACE_LAPS)

def train_for_compound(start_compound, target_compound, episodes=5000, alpha=0.15, gamma=0.95, eps0=0.25, eps_end=0.02):
    """Train Q-learning for a specific start→target compound strategy"""
    print(f"\n  Training {start_compound} → {target_compound}")
    Q = defaultdict(float)
    
    for ep in range(episodes):
        epsilon = float(eps_end + (eps0-eps_end)*np.exp(-ep/(episodes/4)))
        s = (1, 1, start_compound, False)
        done = False
        total_reward = 0
        
        while not done:
            acts = valid_actions(s[3])
            a = acts[rng.integers(len(acts))] if (rng.random()<epsilon) else max(acts, key=lambda x: Q[(s,x)])
            ns, r, done = step(s, a, target_compound)
            total_reward += r
            
            next_acts = valid_actions(ns[3])
            next_max = max(Q[(ns, na)] for na in next_acts) if next_acts else 0.0
            Q[(s,a)] += alpha*(r + gamma*next_max - Q[(s,a)])
            s = ns
        
        if (ep + 1) % 1000 == 0:
            print(f"    Ep {ep+1}/{episodes}: Total time = {-total_reward:.1f}s, ε = {epsilon:.3f}")
    
    return Q

print("="*60)
print("F1 BAHRAIN RL TRAINING - COMPREHENSIVE")
print("="*60)
print(f"\nBase pace: SOFT={BASE['SOFT']:.1f}s, MEDIUM={BASE['MEDIUM']:.1f}s, HARD={BASE['HARD']:.1f}s")
print(f"Degradation: SOFT={SLOPE['SOFT']:.3f}, MEDIUM={SLOPE['MEDIUM']:.3f}, HARD={SLOPE['HARD']:.3f}")
print(f"Pit loss: {PIT_LOSS:.1f}s")

# Train for all meaningful compound combinations
all_Q = {}
strategies = [
    ("SOFT", "MEDIUM"),
    ("SOFT", "HARD"),
    ("MEDIUM", "SOFT"),
    ("MEDIUM", "HARD"),
    ("HARD", "SOFT"),
    ("HARD", "MEDIUM"),
]

print(f"\nTraining {len(strategies)} strategies with 5000 episodes each...")

for start, target in strategies:
    Q = train_for_compound(start, target, episodes=5000)
    # Merge into master Q-table
    all_Q.update(Q)
    print(f"  ✓ {start}→{target} complete ({len(Q)} states learned)")

print(f"\n✓ Total unique states in Q-table: {len(all_Q)}")

# Convert to server action space: keys (lap_bin, age_bin, comp_idx, action)
print("\nConverting to server format...")
q_table = {}
NEG = -1e6

for state_action, q_val in all_Q.items():
    # state_action is ((lap, age, comp, pitted), "no_pit" or "pit")
    state, action_str = state_action
    lap, age, comp, pitted = state
    
    lb, ab, ci = binv(lap, BINS["lap"]), binv(age, BINS["age"]), COMP_IDX[comp]
    
    if action_str == "no_pit":
        # Action 0 = stay
        q_table[(lb, ab, ci, 0)] = float(q_val)
    elif action_str == "pit":
        # Actions 1-3 = pit to SOFT/MEDIUM/HARD
        if not pitted:
            # Store pit value for all compounds
            for a in (1, 2, 3):
                key = (lb, ab, ci, a)
                # Keep best Q-value if multiple entries
                if key not in q_table or q_val > q_table[key]:
                    q_table[key] = float(q_val)
        else:
            # Already pitted - penalize
            for a in (1, 2, 3):
                q_table[(lb, ab, ci, a)] = NEG

print(f"✓ Converted to {len(q_table)} server Q-table entries")

# Save to file
policy_data = {"q_table": q_table, "bins": BINS}
with open(RL_FILE, "wb") as f:
    pickle.dump(policy_data, f, protocol=pickle.HIGHEST_PROTOCOL)

print(f"\n{'='*60}")
print(f"✓ SAVED TO: {RL_FILE}")
print(f"  Q-table entries: {len(q_table)}")
print(f"  State bins: lap={BINS['lap']}, age={BINS['age']}")
print(f"{'='*60}")
print("\n🏁 TRAINING COMPLETE!")
print("   Restart your server to use the new RL policy.")
print(f"{'='*60}\n")