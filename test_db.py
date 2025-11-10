#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing Database Integration")
print("=" * 60)

try:
    print("\n[1] Initializing database...")
    from backend.database import init_db, SessionLocal
    init_db()
    print("OK - Database initialized")
except Exception as e:
    print(f"ERROR - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n[2] Testing preferences service...")
    from backend.app.services.database_service import PreferenceService
    
    db = SessionLocal()
    
    test_prefs = {
        "comfort_level": 7,
        "avoid_hours": [23, 0, 1, 2, 3],
        "preferred_operating_hours": {"Washer": [10, 11, 12]},
        "priority_appliances": ["Washer"],
        "max_concurrent_appliances": 2
    }
    
    PreferenceService.save_preferences(db, test_prefs)
    print("OK - Preferences saved to database")
    
    retrieved = PreferenceService.get_preferences(db)
    print(f"OK - Preferences retrieved: comfort_level={retrieved['comfort_level']}, avoid_hours={retrieved['avoid_hours']}")
    
    db.close()
except Exception as e:
    print(f"ERROR - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n[3] Testing price service...")
    import pandas as pd
    from backend.app.services.database_service import PriceService
    
    db = SessionLocal()
    
    sample_prices = pd.DataFrame({
        "time": [f"{h:02d}:00" for h in range(24)],
        "price": [0.05 + (0.03 * abs((h-14)/12)) for h in range(24)]
    })
    
    PriceService.save_prices(db, sample_prices)
    print("OK - Prices saved to database")
    
    all_prices = PriceService.get_all_prices(db)
    print(f"OK - Retrieved {len(all_prices)} prices from database")
    print(f"   Price range: ${min(p['price'] for p in all_prices):.4f} - ${max(p['price'] for p in all_prices):.4f}")
    
    db.close()
except Exception as e:
    print(f"ERROR - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n[4] Testing API with database...")
    from fastapi.testclient import TestClient
    from backend.app.main import app
    
    client = TestClient(app)
    
    response = client.get("/api/preferences")
    print(f"GET /api/preferences: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   comfort_level: {data.get('comfort_level')}")
        print(f"   avoid_hours: {data.get('avoid_hours')}")
    
    new_prefs = {
        "comfort_level": 8,
        "avoid_hours": [22, 23, 0, 1, 2, 3],
        "preferred_operating_hours": {"Dryer": [14, 15, 16]},
        "priority_appliances": ["Dryer"],
        "max_concurrent_appliances": 3
    }
    
    response = client.post("/api/preferences", json=new_prefs)
    print(f"POST /api/preferences: {response.status_code}")
    if response.status_code == 200:
        print("   Preferences saved successfully")
    
    response = client.get("/api/live-prices")
    print(f"GET /api/live-prices: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Available prices: {len(data.get('prices', []))}")
        print(f"   Price range: ${data.get('min_price', 0):.4f} - ${data.get('max_price', 0):.4f}")
    
    response = client.get("/api/price-history")
    print(f"GET /api/price-history: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Historical records: {len(data.get('history', []))}")
    
except Exception as e:
    print(f"ERROR - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("All database tests passed!")
print("=" * 60)
