# Comfort Score Quick Reference Card

## Problem Solved ✅
- ~~Score always returns 5/10 when no preferences are set~~
- ✅ Now varies 0-10 based on cost efficiency
- ✅ Reflects both savings AND user comfort
- ✅ Independent, interpretable tiers

---

## Three Tiers at a Glance

### 🔴 **Tier 1: Cost Efficiency** (Always On)
- **Range**: 0-10
- **What**: How cheap are the scheduled hours?
- **Formula**: `5 + (daily_avg - schedule_avg) / price_range × 5`
- **Examples**:
  - Run at 2-4 AM (cheapest) = **9/10**
  - Run at noon (average) = **5/10**
  - Run at 6 PM (expensive) = **1/10**

### 🟡 **Tier 2: Avoid Hours** (If Set)
- **Range**: -6 to 0 points
- **What**: Penalty for violating user's avoid hours
- **Formula**: `-(violation_rate × preference_strength × 2.0)`
- **Examples**:
  - 0% violations = **0** (no penalty)
  - 50% violations, strength=3 = **-3.0**
  - 100% violations, strength=3 = **-6.0**

### 🟢 **Tier 3: Preferred Hours** (If Set)
- **Range**: +0 to +5 points
- **What**: Bonus for running during user's preferred times
- **Formula**: `(coverage_rate × preference_strength × 5.0)`
- **Examples**:
  - 0% in preferred = **+0** (no bonus)
  - 50% in preferred, strength=3 = **+2.5**
  - 100% in preferred, strength=3 = **+5.0**

---

## Final Score

```
comfort_score = cost_score + avoid_penalty + preferred_bonus
comfort_score = clamp(comfort_score, 0, 10)
```

---

## Score Interpretation

| Score | Meaning |
|-------|---------|
| **9-10** | Excellent: Optimal cost + respects preferences |
| **7-8** | Great: Good savings, comfortable |
| **5-6** | Fair: Average cost, some compromises |
| **3-4** | Poor: High cost, conflicts |
| **0-2** | Terrible: Expensive + preferences ignored |

---

## When to Use Each Function

### `calculate_comfort_level()` - train_agent.py
- **Use when**: You have prices, appliances, avoid_hours
- **Inputs**: prices, appliances, avoid_hours, schedule?, preferences?
- **Returns**: Single comfort score
- **Legacy**: Still supports old avoid_hours parameter

### `calculate_comfort_score()` - train_agent_with_preferences.py
- **Use when**: You have detailed appliance preferences
- **Inputs**: schedule, preferences, prices?, appliances?
- **Returns**: Single comfort score
- **Modern**: Full three-tier implementation

---

## API Call Examples

### ✅ Correct (Full Three-Tier)
```python
score = calculate_comfort_score(
    schedule,
    preferences,
    prices,              # ← Include for Tier 1!
    appliances           # ← Include for reference
)
# Result: 8.5/10 (cost + comfort calculated)
```

### ⚠️ Missing Prices (Tier 1 Disabled)
```python
score = calculate_comfort_score(
    schedule,
    preferences
    # No prices = no cost efficiency calculation!
)
# Result: Only Tier 2 & 3 (incomplete)
```

### ✅ Backward Compatible (Legacy)
```python
score = calculate_comfort_level(
    prices,
    appliances,
    avoid_hours  # Old way still works
)
# Result: 6.5/10 (avoid_hours vs prices only)
```

---

## Real-World Scenarios

### Scenario 1: Budget-Conscious User
```
Preferences: None (no constraints)
Schedule: Dishwasher at 2-4 AM (cheapest)
Prices: Low at 2-4 AM, high at 6-9 PM

Tier 1 (Cost): +9.0 ← Savings priority
Tier 2 (Avoid): 0
Tier 3 (Preferred): 0
SCORE: 9.0/10 ✓ Excellent savings
```

### Scenario 2: Comfort-Conscious User
```
Preferences:
  - Avoid: 20-23 (night hours, quiet)
  - Preferred: 2-5 AM (early morning)
Schedule: Dishwasher at 2-4 AM
Prices: Low at 2-4 AM

Tier 1 (Cost): +9.0
Tier 2 (Avoid): 0 (no violations)
Tier 3 (Preferred): +5.0 (100% match)
SCORE: 10/10 ✓ Perfect!
```

### Scenario 3: Conflicting Preferences
```
Preferences:
  - Avoid: 9-12 (working hours)
  - Preferred: 10-12
Schedule: Dishwasher at 10-12
Prices: High at 10-12

Tier 1 (Cost): +1.0 (expensive)
Tier 2 (Avoid): -6.0 (100% violation)
Tier 3 (Preferred): +5.0 (100% match)
SCORE: 0/10 ⚠️ Conflicts override benefits
```

---

## Implementation Checklist

- [x] Three-tier algorithm implemented
- [x] Backend routes updated with prices parameter
- [x] Cost efficiency (Tier 1) always active
- [x] Avoid hours penalty (Tier 2) optional
- [x] Preferred hours bonus (Tier 3) optional
- [x] Score normalized to 0-10
- [x] Documentation complete
- [x] Testing verified

---

## Key Improvements

| Before | After |
|--------|-------|
| No preferences = 5/10 always | Cost efficiency varies 0-10 |
| Ignored price data | Uses prices for Tier 1 |
| Binary (good/bad) | Granular scale 0-10 |
| Unclear tradeoffs | Clear three-tier breakdown |
| Limited flexibility | Works with any input combo |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Score always 5 | Pass `prices` to function |
| Score doesn't penalize avoids | Check `avoid_hours` list exists |
| Score too high | Reduce `preference_strength` (1-5) |
| Score too low | Verify prices are realistic |
| Scores vary wildly | Each appliance scored independently (normal) |

---

## Files to Reference

| File | Purpose |
|------|---------|
| `COMFORT_SCORE_DESIGN.md` | Detailed technical design |
| `COMFORT_ALGORITHM_SUMMARY.md` | Real-world examples & math |
| `IMPLEMENTATION_GUIDE.md` | Code integration guide |
| `START.md` | Quick start (updated) |
| `train_agent.py` | `calculate_comfort_level()` |
| `train_agent_with_preferences.py` | `calculate_comfort_score()` |

---

**Quick Test**: Does your score vary 0-10 with just prices? ✅ Yes! It should now.
