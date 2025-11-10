#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("SMARTENERGY SYSTEM - COMPLETE DATABASE TEST")
print("=" * 70)

try:
    print("\n[STEP 1] Initializing Database...")
    from backend.database import init_db, SessionLocal
    init_db()
    print("  OK - Database tables created/verified")
except Exception as e:
    print(f"  ERROR - {e}")
    sys.exit(1)

try:
    print("\n[STEP 2] Testing Preferences API...")
    from fastapi.testclient import TestClient
    from backend.app.main import app
    
    client = TestClient(app)
    
    response = client.get("/api/preferences")
    assert response.status_code == 200
    default_prefs = response.json()
    print(f"  OK - Retrieved default preferences")
    print(f"       Comfort level: {default_prefs['comfort_level']}/10")
    print(f"       Max concurrent: {default_prefs['max_concurrent_appliances']}")
    
    new_prefs = {
        "comfort_level": 8,
        "avoid_hours": [22, 23, 0, 1, 2, 3],
        "preferred_operating_hours": {"Washer": [10, 11, 12]},
        "priority_appliances": ["Washer", "Dryer"],
        "max_concurrent_appliances": 2
    }
    
    response = client.post("/api/preferences", json=new_prefs)
    assert response.status_code == 200
    print(f"  OK - Saved new preferences to database")
    
    response = client.get("/api/preferences")
    assert response.status_code == 200
    retrieved = response.json()
    assert retrieved['comfort_level'] == 8
    print(f"  OK - Preferences persisted correctly")
    print(f"       Comfort level: {retrieved['comfort_level']}/10")
    print(f"       Avoid hours: {retrieved['avoid_hours']}")
    
except AssertionError as e:
    print(f"  ERROR - Assertion failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"  ERROR - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n[STEP 3] Testing Live Prices & History...")
    
    response = client.get("/api/live-prices")
    assert response.status_code == 200
    prices_data = response.json()
    print(f"  OK - Retrieved {len(prices_data['prices'])} live prices")
    print(f"       Price range: ${prices_data['min_price']:.4f} - ${prices_data['max_price']:.4f}")
    print(f"       Average: ${prices_data['avg_price']:.4f}")
    
    response = client.get("/api/price-history")
    assert response.status_code == 200
    history_data = response.json()
    print(f"  OK - Retrieved price history ({len(history_data['history'])} records)")
    print(f"       Database min: ${history_data['min_price']:.4f}")
    print(f"       Database avg: ${history_data['avg_price']:.4f}")
    print(f"       Database max: ${history_data['max_price']:.4f}")
    
except AssertionError as e:
    print(f"  ERROR - Assertion failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"  ERROR - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n[STEP 4] Testing Optimization with Database...")
    
    response = client.post("/api/optimize", json={
        "appliances": [
            {"name": "Washer", "power": 0.5, "duration": 2},
            {"name": "Dryer", "power": 2.5, "duration": 1}
        ],
        "optimization_type": "lp"
    })
    assert response.status_code == 200
    opt_result = response.json()
    print(f"  OK - LP Optimization ran")
    print(f"       Total cost: ${opt_result['total_cost']:.4f}")
    print(f"       Savings: {opt_result['savings_percentage']:.2f}%")
    
except AssertionError as e:
    print(f"  ERROR - Assertion failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"  ERROR - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n[STEP 5] Testing Frontend API Compatibility...")
    
    response = client.get("/api/analyze")
    assert response.status_code == 200
    print(f"  OK - Analysis endpoint working")
    
    response = client.get("/api/price-trends")
    assert response.status_code == 200
    print(f"  OK - Price trends endpoint working")
    
except AssertionError as e:
    print(f"  ERROR - Assertion failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"  ERROR - {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("SUCCESS - All database operations working correctly!")
print("=" * 70)
print("\nDatabase File: backend/energy_optimizer.db")
print("\nTo start the system:")
print("  1. Terminal 1: python start_backend.py")
print("  2. Terminal 2: cd frontend && npm install && npm run dev")
print("\nFrontend will be at: http://localhost:5173")
print("API Docs at: http://localhost:8000/docs")
print("=" * 70)
