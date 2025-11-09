import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from energy_env_with_preferences import EnergyEnvWithPreferences


def train_agent_with_preferences(prices, appliances, restricted_hours, preferences):
    """
    Train RL agent that balances cost + user comfort preferences.
    """
    env = EnergyEnvWithPreferences(prices, appliances, restricted_hours, preferences)
    check_env(env, warn=True)

    # Improved hyperparameters
    model = PPO(
        "MlpPolicy", 
        env, 
        learning_rate=0.0003,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        verbose=0
    )
    
    # Train the model
    model.learn(total_timesteps=50000)
    model.save("models/energy_agent_preferences")

    return model


def run_agent_with_preferences(model, prices, appliances, restricted_hours, preferences):
    """
    Run trained model to generate preference-aware schedule.
    """
    env = EnergyEnvWithPreferences(prices, appliances, restricted_hours, preferences)
    obs, _ = env.reset()
    done = False

    schedule = {a["name"]: [] for a in appliances}

    while not done:
        # Record the hour and remaining durations BEFORE stepping
        current_hour = env.current_hour
        remaining_before_step = {a["name"]: env.remaining_durations[a["name"]] for a in appliances}
        
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, _, info = env.step(action)

        # Only record if appliance had remaining duration before the step
        for i, a in enumerate(appliances):
            if action[i] == 1 and remaining_before_step[a["name"]] > 0:
                schedule[a["name"]].append(current_hour)

    return schedule

def calculate_comfort_score(schedule, preferences, max_score=10.0):
    """
    Calculate a more realistic comfort score (0–10) based on how well
    the schedule matches preferences, weighted by preference strength.
    A perfect 10 requires meeting all strong (5/5) preferences and avoiding
    all strong avoid zones.
    """
    if not preferences:
        return max_score

    total_score = 0.0
    total_possible = 0.0

    for appliance_name, hours in schedule.items():
        if appliance_name not in preferences:
            continue

        pref = preferences[appliance_name]
        avoid_hours = set(pref.get("avoid_hours", []))
        preferred_hours = set(pref.get("preferred_hours", []))
        avoid_penalty = pref.get("avoid_penalty", 2.0)
        prefer_bonus = pref.get("preferred_bonus", 1.0)

        if not hours:
            # Slight penalty if an appliance never runs in preferred hours
            if preferred_hours:
                total_score -= 0.5 * prefer_bonus
            continue

        for hour in hours:
            total_possible += 5  # every decision can gain up to 5 "comfort points"

            # If the agent runs in an avoided hour, penalize based on strength
            if hour in avoid_hours:
                total_score -= 2 * avoid_penalty

            # If the agent runs in a preferred hour, give proportional bonus
            elif hour in preferred_hours:
                total_score += 3 * prefer_bonus

            # Neutral hours are worth small neutral contribution
            else:
                total_score += 1  # partial comfort

        # Bonus: if all preferred hours were used at least once
        if preferred_hours and preferred_hours.issubset(hours):
            total_score += 2 * prefer_bonus

        # Extra penalty: if avoid_hours were heavily violated
        overlap = avoid_hours.intersection(hours)
        if overlap:
            total_score -= len(overlap) * avoid_penalty

    # Normalize to 0–10 scale
    if total_possible == 0:
        return max_score

    normalized = (total_score / total_possible) * max_score / 2
    normalized = max(0.0, min(max_score, normalized))

    # Apply a non-linear curve: make high scores harder to reach
    normalized = (normalized / max_score) ** 0.8 * max_score

    return round(normalized, 2)
