import sys
from pathlib import Path
import numpy as np
from stable_baselines3 import PPO

# Add root directory to path to import ML modules
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

from energy_env_with_preferences import EnergyEnvWithPreferences
from optimizer import optimize_schedule_lp, format_schedule_readable
from train_agent_with_preferences import calculate_comfort_score

class EnergyAgentService:
    def __init__(self):
        self.models = {}
        self.load_models()
    
    def load_models(self):
        """Load trained RL models"""
        try:
            # Look for models in root directory
            root_dir = Path(__file__).parent.parent.parent.parent
            model_path = root_dir / "backend" / "models" / "energy_agent_preferences.zip"
            if model_path.exists():
                self.models['preferences'] = PPO.load(str(model_path))
                print(f"✓ Loaded ML model from {model_path}")
            else:
                print(f"ℹ ML model not found at {model_path} - using LP optimization fallback")
        except Exception as e:
            print(f"Model loading warning: {e}")
    
    def optimize_with_preferences(self, prices, appliances, restricted_hours, preferences):
        """
        Run RL optimization with user preferences
        """
        try:
            if 'preferences' in self.models:
                # Use trained RL model
                env = EnergyEnvWithPreferences(prices, appliances, restricted_hours, preferences)
                model = self.models['preferences']
                
                obs, _ = env.reset()
                done = False
                schedule = {a["name"]: [] for a in appliances}
                
                while not done:
                    current_hour = env.current_hour
                    remaining_before_step = {
                        a["name"]: env.remaining_durations[a["name"]] for a in appliances
                    }
                    
                    action, _ = model.predict(obs, deterministic=True)
                    obs, reward, done, _, _ = env.step(action)
                    
                    for i, a in enumerate(appliances):
                        if action[i] == 1 and remaining_before_step[a["name"]] > 0:
                            schedule[a["name"]].append(current_hour)
                
                # Calculate results
                total_cost = self.calculate_schedule_cost(schedule, prices, appliances)
                comfort_score = calculate_comfort_score(schedule, preferences, prices, appliances)
                
            else:
                # Fallback to LP with preference weighting
                schedule, total_cost = optimize_schedule_lp(prices, appliances, restricted_hours)
                comfort_score = calculate_comfort_score(schedule, preferences, prices, appliances)
            
            return {
                'schedule': schedule,
                'total_cost': total_cost,
                'comfort_score': comfort_score
            }
            
        except Exception as e:
            raise Exception(f"RL optimization failed: {str(e)}")
    
    def calculate_schedule_cost(self, schedule, prices, appliances):
        """Calculate total cost of a schedule"""
        total_cost = 0.0
        for appliance in appliances:
            name = appliance["name"]
            power = appliance["power"]
            for hour in schedule.get(name, []):
                if 0 <= hour < len(prices):
                    total_cost += prices[int(hour)] * power
        return total_cost