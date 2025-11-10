#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from train_agent import calculate_comfort_level
import numpy as np

print("=" * 70)
print("COMFORT LEVEL SENSITIVITY TEST - SHOWING MARGIN CHANGES")
print("=" * 70)

sample_prices = [
    0.0279, 0.034, 0.0529, 0.0409, 0.055, 0.0745,
    0.0813, 0.0602, 0.0564, 0.0797, 0.1079, 0.1138,
    0.0949, 0.1071, 0.0922, 0.0926, 0.0515, 0.0484,
    0.0641, 0.0447, 0.0357, 0.0469, 0.0328, 0.0282
]

sample_appliances = [
    {"name": "Washer", "power": 0.5, "duration": 3},
    {"name": "Dryer", "power": 2.5, "duration": 2}
]

print("\n[SCENARIO 1] Avoid EARLY MORNING (low cost hours)")
print("-" * 70)
avoid_early = [0, 1, 2, 3, 4, 5]
comfort_early = calculate_comfort_level(sample_prices, sample_appliances, avoid_early)
print(f"Avoid hours: {avoid_early}")
print(f"Comfort Level: {comfort_early}")

print("\n[SCENARIO 2] Avoid MID-DAY (high cost hours)")
print("-" * 70)
avoid_midday = [9, 10, 11, 12, 13, 14, 15]
comfort_midday = calculate_comfort_level(sample_prices, sample_appliances, avoid_midday)
print(f"Avoid hours: {avoid_midday}")
print(f"Comfort Level: {comfort_midday}")

print("\n[SCENARIO 3] Avoid EVENING (medium cost hours)")
print("-" * 70)
avoid_evening = [17, 18, 19, 20]
comfort_evening = calculate_comfort_level(sample_prices, sample_appliances, avoid_evening)
print(f"Avoid hours: {avoid_evening}")
print(f"Comfort Level: {comfort_evening}")

print("\n[SCENARIO 4] Avoid LATE NIGHT (low cost hours)")
print("-" * 70)
avoid_night = [21, 22, 23]
comfort_night = calculate_comfort_level(sample_prices, sample_appliances, avoid_night)
print(f"Avoid hours: {avoid_night}")
print(f"Comfort Level: {comfort_night}")

print("\n" + "=" * 70)
print("SENSITIVITY ANALYSIS - MARGIN CHANGES")
print("=" * 70)
print(f"\nEarly Morning (cheap): {comfort_early:.2f}")
print(f"Mid-Day (expensive):  {comfort_midday:.2f}")
print(f"Evening (medium):     {comfort_evening:.2f}")
print(f"Late Night (cheap):   {comfort_night:.2f}")

print(f"\nMargin between BEST and WORST: {max(comfort_early, comfort_midday, comfort_evening, comfort_night) - min(comfort_early, comfort_midday, comfort_evening, comfort_night):.2f}")
print(f"This shows how much the comfort level changes based on schedule!")

if max(comfort_early, comfort_midday, comfort_evening, comfort_night) - min(comfort_early, comfort_midday, comfort_evening, comfort_night) > 1.5:
    print("\n[OK] Sensitivity is HIGH - comfort changes significantly with schedule")
else:
    print("\n[WARNING] Sensitivity may still be low - consider further tuning")
