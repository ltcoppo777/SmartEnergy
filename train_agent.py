import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from energy_env import EnergyEnv


def calculate_comfort_level(prices, appliances, avoid_hours, schedule=None, preferences=None):
    """
    Calculate comfort score using three-tier architecture:
    
    Tier 1 (Foundation): Cost Efficiency - how well schedule uses cheap hours
    Tier 2 (Adjustment): Avoid Hours - penalty for user comfort violations
    Tier 3 (Bonus): Preferred Hours - reward for ideal time windows
    
    Args:
        prices: List of 24 hourly electricity prices
        appliances: List of appliance dictionaries
        avoid_hours: List of hours to avoid (0-23) - legacy parameter
        schedule: Optional dict of appliance_name → list of scheduled hours
        preferences: Optional dict of preferences with avoid_hours, preferred_hours, preference_strength
    
    Returns:
        float: Comfort level from 0.0 to 10.0
    """
    if not prices:
        return 5.0
    
    prices_array = np.array(prices[:24])
    max_price = np.max(prices_array)
    min_price = np.min(prices_array)
    price_range = max_price - min_price
    
    if price_range == 0:
        return 5.0
    
    if schedule and preferences:
        total_score = 0
        total_max_score = 0

        for appliance_name, pref in preferences.items():
            if appliance_name not in schedule:
                continue

            hours = schedule[appliance_name]
            if not hours:
                continue

            app_avoid_hours = pref.get("avoid_hours", [])
            preferred_hours = pref.get("preferred_hours", [])
            preference_strength = pref.get("preference_strength", 3)

            avg_price_schedule = np.mean([prices_array[int(h) % 24] for h in hours])
            avg_price_day = np.mean(prices_array)
            
            cost_efficiency = (avg_price_day - avg_price_schedule) / price_range
            cost_score = max(0, min(10, 5 + cost_efficiency * 5))

            avoid_violations = sum(1 for h in hours if h in app_avoid_hours)
            violation_rate = avoid_violations / len(hours) if hours else 0
            penalty_weight = 2.0 * preference_strength
            avoid_adjustment = -(violation_rate * penalty_weight)

            preferred_hits = sum(1 for h in hours if h in preferred_hours)
            coverage = preferred_hits / len(hours) if hours else 0
            preferred_bonus = coverage * 0.5 * 10

            appliance_score = cost_score + avoid_adjustment + preferred_bonus
            appliance_score = min(10, max(0, appliance_score))

            total_score += appliance_score
            total_max_score += 10

        if total_max_score > 0:
            return round(min(10, max(0, (total_score / total_max_score) * 10)), 1)
    
    if not avoid_hours or not schedule:
        if schedule:
            all_hours = []
            for hours_list in schedule.values():
                all_hours.extend(hours_list)
            
            if all_hours:
                avg_price_schedule = np.mean([prices_array[int(h) % 24] for h in all_hours])
                avg_price_day = np.mean(prices_array)
                cost_efficiency = (avg_price_day - avg_price_schedule) / price_range
                cost_score = max(0, min(10, 5 + cost_efficiency * 5))
                return round(cost_score, 1)
        
        return 5.0
    
    avoid_hours_prices = [prices_array[h] for h in avoid_hours if 0 <= h < len(prices_array)]
    work_hours = [h for h in range(24) if h not in avoid_hours]
    work_hours_prices = [prices_array[h] for h in work_hours if 0 <= h < len(prices_array)]
    
    if not avoid_hours_prices or not work_hours_prices:
        return 5.0
    
    avg_avoid_price = np.mean(avoid_hours_prices)
    avg_work_price = np.mean(work_hours_prices)
    
    price_diff = avg_avoid_price - avg_work_price
    max_possible_diff = max_price - min_price
    
    comfort_ratio = price_diff / max_possible_diff if max_possible_diff > 0 else 0
    comfort_level = 5.0 + (comfort_ratio * 5.0)
    comfort_level = max(0.0, min(10.0, comfort_level))
    
    return round(comfort_level, 1)


def generate_optimization_advice(prices, appliances, avoid_hours, schedule=None):
    """
    Generate optimization advice based on prices and avoid hours.
    
    Args:
        prices: List of 24 hourly electricity prices
        appliances: List of appliance dictionaries
        avoid_hours: List of hours to avoid
        schedule: Optional schedule dictionary (not used in this version)
    
    Returns:
        str: Optimization advice text
    """
    if not prices:
        return "No price data available for advice generation."
    
    prices_array = np.array(prices)
    max_price_hour = np.argmax(prices_array)
    min_price_hour = np.argmin(prices_array)
    max_price = prices_array[max_price_hour]
    min_price = prices_array[min_price_hour]
    
    advice_parts = []
    
    if avoid_hours:
        avoid_hours_prices = [prices[h] for h in avoid_hours if 0 <= h < len(prices)]
        avg_avoid_price = np.mean(avoid_hours_prices)
        
        if avg_avoid_price > np.mean(prices_array):
            advice_parts.append(f"✓ Excellent! Your avoid hours ({', '.join(map(str, sorted(avoid_hours)))}) align with peak prices (avg ${avg_avoid_price:.4f}/kWh).")
        else:
            advice_parts.append(f"• Your avoid hours include some lower-price periods. Consider adjusting to capture more savings.")
    else:
        advice_parts.append("No avoid hours set. Set avoid hours to align with peak pricing periods for better comfort.")
    
    advice_parts.append(f"\n🔍 Peak price: ${max_price:.4f}/kWh at hour {max_price_hour:02d}:00")
    advice_parts.append(f"🔍 Lowest price: ${min_price:.4f}/kWh at hour {min_price_hour:02d}:00")
    
    if appliances:
        advice_parts.append(f"\n💡 Schedule your {len(appliances)} appliance(s) during low-price hours for maximum savings.")
    
    return "\n".join(advice_parts)


def train_agent(prices, appliances, restricted_hours):
    """
    Train the PPO reinforcement learning agent using the given price data and restricted hours.
    """
    env = EnergyEnv(prices, appliances, restricted_hours)
    check_env(env, warn=True)

    # Improved hyperparameters for better learning
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
    
    # More timesteps for better learning
    model.learn(total_timesteps=50000)
    model.save("models/energy_agent")

    return model


def run_agent(model, prices, appliances, restricted_hours):
    """
    Run the trained model to generate an optimized schedule.
    """
    env = EnergyEnv(prices, appliances, restricted_hours)
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

    # Format hours into human-readable ranges
    readable_schedule = {}
    for name, hours in schedule.items():
        if not hours:
            readable_schedule[name] = "Not scheduled"
            continue

        hours = sorted(set(hours))
        ranges = []
        start = prev = hours[0]
        for h in hours[1:]:
            if h != prev + 1:
                ranges.append(f"{start}:00–{prev+1}:00")
                start = h
            prev = h
        ranges.append(f"{start}:00–{prev+1}:00")
        readable_schedule[name] = ", ".join(ranges)

    return readable_schedule