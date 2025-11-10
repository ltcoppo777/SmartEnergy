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

def calculate_comfort_score(schedule, preferences, prices=None, appliances=None):
    """
    Calculate comfort score using three-tier architecture:
    
    Tier 1 (Foundation): Cost Efficiency - how well schedule uses cheap hours
    Tier 2 (Adjustment): Avoid Hours - penalty for user comfort violations  
    Tier 3 (Bonus): Preferred Hours - reward for ideal time windows
    
    Args:
        schedule: dict of appliance_name → list of scheduled hours
        preferences: dict of appliance_name → {avoid_hours, preferred_hours, preference_strength}
        prices: optional list of 24 hourly prices
        appliances: optional list of appliances with power info
    
    Returns:
        float: comfort score 0-10
    """
    if not schedule or not preferences:
        return 0.0
    
    total_score = 0
    total_count = 0

    for appliance_name, pref in preferences.items():
        if appliance_name not in schedule:
            continue

        hours = schedule[appliance_name]
        if not hours:
            continue

        avoid_hours = pref.get("avoid_hours", [])
        preferred_hours = pref.get("preferred_hours", [])
        preference_strength = pref.get("preference_strength", 3)

        cost_score = 5.0
        if prices and len(prices) >= 24:
            prices_array = np.array(prices[:24])
            price_range = np.max(prices_array) - np.min(prices_array)
            
            if price_range > 0:
                avg_price_schedule = np.mean([prices_array[int(h) % 24] for h in hours])
                avg_price_day = np.mean(prices_array)
                cost_efficiency = (avg_price_day - avg_price_schedule) / price_range
                cost_score = max(0, min(10, 5 + cost_efficiency * 5))

        avoid_violations = sum(1 for h in hours if h in avoid_hours)
        violation_rate = avoid_violations / len(hours) if hours else 0
        penalty_weight = 2.0 * preference_strength
        avoid_adjustment = -(violation_rate * penalty_weight)

        preferred_hits = sum(1 for h in hours if h in preferred_hours)
        coverage = preferred_hits / len(hours) if hours else 0
        preferred_bonus = coverage * 0.5 * 10

        appliance_score = cost_score + avoid_adjustment + preferred_bonus
        appliance_score = min(10, max(0, appliance_score))

        total_score += appliance_score
        total_count += 1

    if total_count == 0:
        return 0.0

    final_score = total_score / total_count
    return round(min(10, max(0, final_score)), 2)
