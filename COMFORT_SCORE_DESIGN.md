# Comfort Score Redesign: Cost Efficiency + User Preferences

## Problem with Current Approach
- Returns neutral 5/10 when no avoid hours are set
- Ignores cost efficiency when user has no preferences
- Doesn't reflect the quality of the schedule's cost savings

## New Design: Three-Tier Architecture

### Tier 1: Cost Efficiency Score (Foundation - 0 to 10)

**Purpose**: Measure how well the schedule uses cheap electricity hours

**Formula**:
```
schedule_avg_price = mean(prices[h] for h in scheduled_hours)
daily_avg_price = mean(all_24_prices)
price_range = max(prices) - min(prices)

cost_score = 5 + ((daily_avg_price - schedule_avg_price) / price_range) × 5
cost_score = clamp(cost_score, 0, 10)
```

**Interpretation**:
- `cost_score = 10`: Schedule runs entirely during the cheapest hours → perfect savings
- `cost_score = 5`: Schedule runs at average price → neutral
- `cost_score = 0`: Schedule runs entirely during peak hours → worst savings

**Why this works**:
- Even with NO avoid hours, the score varies based on actual cost efficiency
- Rewards schedules that use low-price periods
- Penalizes schedules during expensive hours

---

### Tier 2: Avoid Hours Adjustment (Penalty Layer - if provided)

**Purpose**: Penalize violations of user's avoid hours

**Formula**:
```
if no avoid_hours provided:
    avoid_adjustment = 0  # No penalty, no bonus
else:
    violations = count(h in scheduled_hours that are in avoid_hours)
    violation_rate = violations / total_scheduled_hours
    
    penalty_weight = 2.0 * preference_strength  # Scales with how important user feels
    avoid_adjustment = -(violation_rate × penalty_weight)
    # Each violation costs 0.5 to 2 points depending on preference strength
```

**Interpretation**:
- No avoid hours set → `adjustment = 0` (no impact)
- All hours respected → `adjustment = 0` (user comfort maintained)
- 50% violations + strength=3 → `adjustment = -3` (costs 3 points)

---

### Tier 3: Preferred Hours Bonus (Incentive Layer - if provided)

**Purpose**: Reward scheduling during user's ideal time windows

**Formula**:
```
if no preferred_hours provided:
    preferred_bonus = 0  # No bonus
else:
    preferred_hits = count(h in scheduled_hours that are in preferred_hours)
    coverage = preferred_hits / total_scheduled_hours
    
    bonus_weight = 0.5  # Small bonus, doesn't override cost/avoid
    preferred_bonus = coverage × bonus_weight × 10
    # Max +5 points if all hours are in preferred range
```

**Interpretation**:
- No preferred hours set → `bonus = 0`
- 50% of schedule in preferred hours → `+2.5` points
- 100% in preferred hours → `+5` points (maximum)

---

## Final Score Calculation

**Combine all three tiers**:
```
comfort_score = cost_score + avoid_adjustment + preferred_bonus
comfort_score = clamp(comfort_score, 0, 10)
```

**Examples**:

| Scenario | Cost Score | Avoid Adj | Preferred | Final | Interpretation |
|----------|-----------|----------|-----------|-------|-----------------|
| Great cost + no preferences | 9.0 | 0 | 0 | **9.0** | Excellent savings |
| Great cost + all avoids respected | 9.0 | 0 | 0 | **9.0** | Perfect! |
| Great cost + 50% avoids violated | 9.0 | -3 | 0 | **6.0** | Good savings, poor comfort |
| Mediocre cost + 50% preferred hours | 5.0 | 0 | 2.5 | **7.5** | Acceptable |
| Poor cost + no preferences | 2.0 | 0 | 0 | **2.0** | Bad scheduling |

---

## Handling Edge Cases

### 1. Empty Schedule
- `comfort_score = 5.0` (neutral, no data to evaluate)

### 2. No Electricity Price Data
- `comfort_score = 5.0` (can't evaluate cost, neutral)

### 3. All Hours Have Same Price
- `price_range = 0` → `cost_score = 5.0` (neutral, can't differentiate)

### 4. Very Few Scheduled Hours
- Percentage-based calculations still work
- 1 hour scheduled in avoid_hours = 100% violation rate

---

## Benefits of This Design

✅ **Responsive**: Score varies 0-10 even without user preferences  
✅ **Cost-Focused**: Rewards efficient use of cheap electricity  
✅ **User-Friendly**: Respects and incentivizes user preferences  
✅ **Transparent**: Each component is independently interpretable  
✅ **Flexible**: Works with any combination of inputs (cost only, cost+avoid, cost+preferred, all three)  
✅ **Fair**: Equally weights cost (foundation) and comfort (adjustments)

---

## Implementation Notes

### When to Use Each Tier:

| Input | Tier 1 | Tier 2 | Tier 3 | Score Range |
|-------|--------|--------|--------|-------------|
| Prices only | ✓ | ✗ | ✗ | 0-10 (cost-driven) |
| Prices + avoid_hours | ✓ | ✓ | ✗ | 0-10 (cost + comfort penalty) |
| Prices + preferred_hours | ✓ | ✗ | ✓ | 0-10 (cost + preference bonus) |
| All inputs | ✓ | ✓ | ✓ | 0-10 (balanced) |

### Preference Strength Scaling:
- `preference_strength = 1 (weak)`: penalties/bonuses are small
- `preference_strength = 3 (medium)`: standard impact
- `preference_strength = 5 (strong)`: large penalties for violations
