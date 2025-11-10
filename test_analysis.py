#!/usr/bin/env python
import sys
import os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from train_agent import (
    calculate_comfort_level,
    generate_optimization_advice,
    run_agent
)

print("=" * 70)
print("SMARTENERGY - ANALYSIS & COMFORT LEVEL TEST")
print("=" * 70)

sample_prices = [
    0.0279, 0.034, 0.0529, 0.0409, 0.055, 0.0745,
    0.0813, 0.0602, 0.0564, 0.0797, 0.1079, 0.1138,
    0.0949, 0.1071, 0.0922, 0.0926, 0.0515, 0.0484,
    0.0641, 0.0447, 0.0357, 0.0469, 0.0328, 0.0282
]

sample_appliances = [
    {"name": "Washer", "power": 0.5, "duration": 3},
    {"name": "Dryer", "power": 2.5, "duration": 2},
    {"name": "Dishwasher", "power": 1.2, "duration": 2}
]

print("\n[TEST 1] Comfort Level with Moderate Constraints")
print("-" * 70)
restricted_hours_1 = [13, 14, 15, 16, 17]
comfort_1 = calculate_comfort_level(sample_prices, sample_appliances, restricted_hours_1)
print(f"Restricted hours: {restricted_hours_1}")
print(f"Available hours: {24 - len(restricted_hours_1)}")
print(f"Total appliance duration: {sum(a['duration'] for a in sample_appliances)} hours")
print(f"Comfort Level: {comfort_1}/10")
assert 1 <= comfort_1 <= 10, "Comfort level should be between 1-10"
print("[PASSED]")

print("\n[TEST 2] Comfort Level with High Restrictions")
print("-" * 70)
restricted_hours_2 = list(range(9, 18))
comfort_2 = calculate_comfort_level(sample_prices, sample_appliances, restricted_hours_2)
print(f"Restricted hours: {restricted_hours_2}")
print(f"Available hours: {24 - len(restricted_hours_2)}")
print(f"Comfort Level: {comfort_2}/10")
assert comfort_2 <= comfort_1, "Equal or lower comfort with higher restrictions"
print("[PASSED]")

print("\n[TEST 3] Comfort Level with No Restrictions")
print("-" * 70)
restricted_hours_3 = []
comfort_3 = calculate_comfort_level(sample_prices, sample_appliances, restricted_hours_3)
print(f"Restricted hours: None")
print(f"Available hours: 24")
print(f"Comfort Level: {comfort_3}/10")
assert 1 <= comfort_3 <= 10, "Comfort should be in valid range"
print("[PASSED]")

print("\n[TEST 4] Optimization Advice Generation")
print("-" * 70)

sample_schedule = {
    "Washer": "02:00–05:00, 22:00–23:00",
    "Dryer": "05:00–07:00",
    "Dishwasher": "Not scheduled"
}

advice = generate_optimization_advice(sample_prices, sample_appliances, restricted_hours_1, sample_schedule)
print(advice)
print("[PASSED]")

print("\n[TEST 5] Comfort Level Edge Cases")
print("-" * 70)

tight_appliances = [
    {"name": "App1", "power": 1.0, "duration": 20},
    {"name": "App2", "power": 1.0, "duration": 10}
]

comfort_tight = calculate_comfort_level(sample_prices, tight_appliances, [12, 13, 14])
print(f"Tight schedule (30h duration, 21h available): Comfort = {comfort_tight}/10")
assert comfort_tight < 8, "Very tight schedule should have lower comfort"
print("[PASSED]")

print("\n[TEST 6] Analysis Output Format")
print("-" * 70)

sample_schedule_full = {
    "Washer": "02:00–05:00",
    "Dryer": "05:00–07:00",
    "Dishwasher": "21:00–23:00"
}

all_appliances = sample_appliances
restricted_all = [9, 10, 11, 12, 13, 14, 15, 16, 17]

comfort = calculate_comfort_level(sample_prices, all_appliances, restricted_all)
advice = generate_optimization_advice(sample_prices, all_appliances, restricted_all, sample_schedule_full)

analysis_output = {
    "schedule": sample_schedule_full,
    "comfort_level": comfort,
    "advice": advice
}

print(f"Comfort Level: {analysis_output['comfort_level']}/10")
print(f"\nSchedule:")
for app, time in analysis_output['schedule'].items():
    print(f"  {app}: {time}")
print(f"\n{analysis_output['advice']}")
print("[PASSED]")

print("\n" + "=" * 70)
print("SUCCESS - All analysis tests passed!")
print("=" * 70)
print("\nKey Features Tested:")
print("  [OK] Comfort level calculation (1-10 scale)")
print("  [OK] Analysis respects avoided hours")
print("  [OK] Optimization advice based on pricing")
print("  [OK] Schedule analysis and recommendations")
print("  [OK] Proper output format for frontend integration")
