#!/usr/bin/env python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from train_agent import calculate_comfort_level
from train_agent_with_preferences import calculate_comfort_score
import numpy as np

prices = [0.10, 0.12, 0.15, 0.18, 0.20, 0.22, 0.25, 0.24, 0.20, 0.15, 0.12, 0.10,
          0.09, 0.08, 0.12, 0.15, 0.18, 0.20, 0.22, 0.25, 0.24, 0.20, 0.15, 0.12]

schedule = {
    "dishwasher": [2, 3, 4],
    "washer": [15, 16, 17]
}

preferences = {
    "dishwasher": {
        "avoid_hours": [0, 1, 2, 22, 23],
        "preferred_hours": [10, 11, 12],
        "preference_strength": 3
    },
    "washer": {
        "avoid_hours": [0, 1, 18, 19, 20],
        "preferred_hours": [10, 11, 12, 13],
        "preference_strength": 3
    }
}

score1 = calculate_comfort_level(prices, [], [0, 1, 2, 22, 23])
print(f"[OK] calculate_comfort_level basic: {score1}")

score2 = calculate_comfort_level(prices, [], [0, 1, 2, 22, 23], schedule, preferences)
print(f"[OK] calculate_comfort_level with preferences: {score2}")

score3 = calculate_comfort_score(schedule, preferences, prices, [])
print(f"[OK] calculate_comfort_score: {score3}")

print("\n[OK] All comfort score calculations working!")
