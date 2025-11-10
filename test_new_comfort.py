#!/usr/bin/env python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from train_agent import calculate_comfort_level
from train_agent_with_preferences import calculate_comfort_score
import numpy as np

prices = [0.10, 0.12, 0.15, 0.18, 0.20, 0.22, 0.25, 0.24, 0.20, 0.15, 0.12, 0.10,
          0.09, 0.08, 0.12, 0.15, 0.18, 0.20, 0.22, 0.25, 0.24, 0.20, 0.15, 0.12]

print("=" * 60)
print("TEST 1: Cost Efficiency (Tier 1) - NO preferences")
print("=" * 60)

schedule = {"dishwasher": [2, 3, 4]}
preferences = {"dishwasher": {"avoid_hours": [], "preferred_hours": [], "preference_strength": 3}}

score = calculate_comfort_level(prices, [], [], schedule, preferences)
print(f"Schedule: dishwasher at hours 2-4 (cheap hours, avg $0.15)")
print(f"Result: {score}/10 - should be HIGH (>7)")
print()

schedule = {"dishwasher": [18, 19, 20]}
score = calculate_comfort_level(prices, [], [], schedule, preferences)
print(f"Schedule: dishwasher at hours 18-20 (expensive hours, avg $0.20)")
print(f"Result: {score}/10 - should be LOW (<4)")
print()

print("=" * 60)
print("TEST 2: Avoid Hours Penalty (Tier 2)")
print("=" * 60)

schedule = {"dishwasher": [2, 3, 4]}
preferences = {
    "dishwasher": {
        "avoid_hours": [2],
        "preferred_hours": [],
        "preference_strength": 3
    }
}

score = calculate_comfort_level(prices, [], [], schedule, preferences)
print(f"Schedule: hours 2-4 (cheap) but hour 2 is avoided")
print(f"Violation rate: 33% (1 of 3 hours)")
print(f"Expected penalty: -2.0 (0.33 * 2.0 * 3)")
print(f"Result: {score}/10")
print()

print("=" * 60)
print("TEST 3: Preferred Hours Bonus (Tier 3)")
print("=" * 60)

schedule = {"dishwasher": [10, 11, 12]}
preferences = {
    "dishwasher": {
        "avoid_hours": [],
        "preferred_hours": [10, 11, 12],
        "preference_strength": 3
    }
}

score = calculate_comfort_level(prices, [], [], schedule, preferences)
print(f"Schedule: hours 10-12 (all preferred)")
print(f"Coverage: 100% in preferred hours")
print(f"Expected bonus: +5.0 (1.0 * 0.5 * 10)")
print(f"Result: {score}/10")
print()

print("=" * 60)
print("TEST 4: Combined - All Three Tiers")
print("=" * 60)

schedule = {"dishwasher": [10, 11, 12]}
preferences = {
    "dishwasher": {
        "avoid_hours": [20, 21, 22],
        "preferred_hours": [10, 11, 12],
        "preference_strength": 3
    }
}

score = calculate_comfort_level(prices, [], [], schedule, preferences)
print(f"Schedule: hours 10-12")
print(f"- Cost: moderate (avg $0.12)")
print(f"- Avoid: ZERO violations")
print(f"- Preferred: 100% coverage")
print(f"Result: {score}/10 - should be HIGH (8-9)")
print()

print("=" * 60)
print("TEST 5: calculate_comfort_score() function")
print("=" * 60)

schedule = {"washer": [15, 16, 17]}
preferences = {
    "washer": {
        "avoid_hours": [0, 1, 18, 19, 20],
        "preferred_hours": [10, 11, 12, 13],
        "preference_strength": 3
    }
}

score = calculate_comfort_score(schedule, preferences, prices)
print(f"Washer scheduled at hours 15-17 (moderate price, no avoid/preferred)")
print(f"Result: {score}/10")
print()

print("[OK] All tests completed!")
