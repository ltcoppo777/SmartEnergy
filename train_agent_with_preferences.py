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

    # Train the model with more timesteps to ensure proper learning
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

def calculate_comfort_score(schedule, preferences):
    """
    Calculate comfort score (0-10) based on how well the schedule matches user preferences.
    """
    total_score = 0
    total_possible = 0

    for appliance_name, pref in preferences.items():
        if appliance_name not in schedule:
            continue

        hours = schedule[appliance_name]

        # If appliance is not scheduled at all, this is a major failure - return very low score
        if not hours or len(hours) == 0:
            return 0.5  # Low score but never exactly 0

        avoid_hours = set(pref.get("avoid_hours", []))
        preferred_hours = set(pref.get("preferred_hours", []))
        
        # Get user-defined importance weights
        avoid_penalty_weight = pref.get("avoid_penalty", 2.0)
        prefer_bonus_weight = pref.get("preferred_bonus", 1.0)

        # Count hours in each category
        hours_in_avoid = sum(1 for h in hours if h in avoid_hours)
        hours_in_prefer = sum(1 for h in hours if h in preferred_hours)
        hours_neutral = len(hours) - hours_in_avoid - hours_in_prefer

        # SCORING SYSTEM (per hour):
        # - Preferred hour: +10 points * preference weight
        # - Neutral hour: +5 points (baseline comfort)
        # - Avoided hour: -15 points * avoidance weight
        
        prefer_points = hours_in_prefer * 10.0 * prefer_bonus_weight
        neutral_points = hours_neutral * 5.0
        avoid_points = hours_in_avoid * (-15.0) * avoid_penalty_weight
        
        appliance_score = prefer_points + neutral_points + avoid_points
        
        # Best possible score: all hours in preferred
        best_possible = len(hours) * 10.0 * prefer_bonus_weight
        
        # Normalize to 0-10 scale for this appliance
        if best_possible > 0:
            appliance_normalized = max(0, min(10, (appliance_score / best_possible) * 10))
        else:
            appliance_normalized = 5.0  # Neutral if no preferences
        
        total_score += appliance_normalized
        total_possible += 10.0  # Each appliance can contribute max 10 points

    # Average across all appliances
    if total_possible == 0:
        return 5.0  # Neutral score if no preferences

    final_score = (total_score / total_possible) * 10

    # Ensure score stays in valid range (0.1, 9.9) and never exactly 0 or 10
    final_score = max(0.1, min(9.9, final_score))
    
    return round(final_score, 1)
