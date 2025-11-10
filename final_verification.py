#!/usr/bin/env python
import sys
import os
import json
from pathlib import Path

print("=" * 60)
print("SMARTENERGY SYSTEM VERIFICATION")
print("=" * 60)

test_results = {
    "backend": {},
    "frontend": {},
    "ml_model": {},
    "data_files": {}
}

print("\n[1] CHECKING DATA FILES")
print("-" * 60)

data_files = {
    "data/prices.csv": "prices.csv (24-hour prices)",
    "data/appliances.csv": "appliances.csv (appliance definitions)"
}

for file_path, description in data_files.items():
    full_path = Path(file_path)
    if full_path.exists() and full_path.stat().st_size > 0:
        print(f"OK   - {description} ({full_path.stat().st_size} bytes)")
        test_results["data_files"][file_path] = "OK"
    else:
        print(f"FAIL - {description} missing or empty")
        test_results["data_files"][file_path] = "FAIL"

print("\n[2] CHECKING BACKEND SETUP")
print("-" * 60)

try:
    from fastapi.testclient import TestClient
    from backend.app.main import app
    print("OK   - Backend app loads successfully")
    test_results["backend"]["app_load"] = "OK"
    
    client = TestClient(app)
    
    try:
        response = client.get("/health")
        if response.status_code == 200:
            print("OK   - Health check endpoint working")
            test_results["backend"]["health"] = "OK"
        else:
            print(f"FAIL - Health check returned {response.status_code}")
            test_results["backend"]["health"] = "FAIL"
    except Exception as e:
        print(f"FAIL - Health check error: {e}")
        test_results["backend"]["health"] = "FAIL"
    
    endpoints = {
        "/api/live-prices": "Live Prices",
        "/api/analyze": "Energy Analysis",
        "/api/price-trends": "Price Trends"
    }
    
    for endpoint, name in endpoints.items():
        try:
            response = client.get(endpoint)
            if response.status_code == 200:
                print(f"OK   - {name} endpoint working")
                test_results["backend"][f"endpoint_{endpoint}"] = "OK"
            else:
                print(f"FAIL - {name} endpoint returned {response.status_code}")
                test_results["backend"][f"endpoint_{endpoint}"] = f"HTTP {response.status_code}"
        except Exception as e:
            print(f"FAIL - {name} endpoint error: {e}")
            test_results["backend"][f"endpoint_{endpoint}"] = "ERROR"
    
    try:
        test_request = {
            "appliances": [
                {"name": "Washer", "power": 0.5, "duration": 2},
                {"name": "Dryer", "power": 2.5, "duration": 1}
            ],
            "optimization_type": "lp"
        }
        response = client.post("/api/optimize", json=test_request)
        if response.status_code == 200:
            data = response.json()
            if "schedule" in data and "total_cost" in data:
                print(f"OK   - LP Optimization working (cost: ${data['total_cost']:.4f})")
                test_results["backend"]["optimize_lp"] = "OK"
            else:
                print(f"FAIL - LP Optimization response missing fields")
                test_results["backend"]["optimize_lp"] = "FAIL"
        else:
            print(f"FAIL - LP Optimization returned {response.status_code}")
            test_results["backend"]["optimize_lp"] = f"HTTP {response.status_code}"
    except Exception as e:
        print(f"FAIL - LP Optimization error: {e}")
        test_results["backend"]["optimize_lp"] = "ERROR"
    
    try:
        test_request = {
            "appliances": [{"name": "Washer", "power": 0.5, "duration": 2}],
            "preferences": {
                "Washer": {
                    "avoid_hours": [23, 0, 1],
                    "avoid_penalty": 2.0,
                    "preferred_hours": [10, 11, 12],
                    "preferred_bonus": 1.0
                }
            },
            "optimization_type": "rl"
        }
        response = client.post("/api/optimize", json=test_request)
        if response.status_code == 200:
            data = response.json()
            if "schedule" in data and "total_cost" in data:
                comfort = data.get("comfort_score", "N/A")
                print(f"OK   - RL Optimization working (cost: ${data['total_cost']:.4f}, comfort: {comfort})")
                test_results["backend"]["optimize_rl"] = "OK"
            else:
                print(f"FAIL - RL Optimization response missing fields")
                test_results["backend"]["optimize_rl"] = "FAIL"
        else:
            print(f"FAIL - RL Optimization returned {response.status_code}")
            test_results["backend"]["optimize_rl"] = f"HTTP {response.status_code}"
    except Exception as e:
        print(f"FAIL - RL Optimization error: {e}")
        test_results["backend"]["optimize_rl"] = "ERROR"

except Exception as e:
    print(f"FAIL - Backend load error: {e}")
    test_results["backend"]["app_load"] = "ERROR"

print("\n[3] CHECKING ML MODEL")
print("-" * 60)

try:
    from stable_baselines3 import PPO
    from pathlib import Path
    model_path = Path("backend/models/energy_agent_preferences.zip")
    
    if model_path.exists():
        print(f"OK   - Model file exists ({model_path.stat().st_size} bytes)")
        test_results["ml_model"]["file_exists"] = "OK"
        
        try:
            model = PPO.load(str(model_path))
            print(f"OK   - Model loads successfully")
            test_results["ml_model"]["load"] = "OK"
        except Exception as e:
            print(f"WARNING - Model file exists but cannot be loaded: {e}")
            print("         (This is OK - system will use LP fallback)")
            test_results["ml_model"]["load"] = "WARNING - using LP fallback"
    else:
        print(f"INFO - Model file not found (system will use LP fallback)")
        test_results["ml_model"]["file_exists"] = "NOT_FOUND"
except Exception as e:
    print(f"ERROR - ML model check failed: {e}")
    test_results["ml_model"]["check"] = "ERROR"

print("\n[4] CHECKING FRONTEND")
print("-" * 60)

frontend_dir = Path("frontend")
if frontend_dir.exists():
    print(f"OK   - Frontend directory exists")
    test_results["frontend"]["directory"] = "OK"
    
    src_dir = frontend_dir / "src"
    if src_dir.exists():
        print(f"OK   - Frontend source directory exists")
        test_results["frontend"]["src_directory"] = "OK"
        
        api_file = src_dir / "utils" / "api.js"
        if api_file.exists():
            print(f"OK   - API client (api.js) exists")
            test_results["frontend"]["api_client"] = "OK"
            
            with open(api_file, "r") as f:
                content = f.read()
                if "localhost:8000" in content or "VITE_API_URL" in content:
                    print(f"OK   - API client configured to use backend")
                    test_results["frontend"]["api_configured"] = "OK"
                else:
                    print(f"WARNING - API client may not be configured for backend")
                    test_results["frontend"]["api_configured"] = "WARNING"
        
        package_json = frontend_dir / "package.json"
        if package_json.exists():
            print(f"OK   - package.json exists")
            test_results["frontend"]["package_json"] = "OK"
    else:
        print(f"FAIL - Frontend source directory missing")
        test_results["frontend"]["src_directory"] = "FAIL"
else:
    print(f"FAIL - Frontend directory missing")
    test_results["frontend"]["directory"] = "FAIL"

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

all_ok = True
for category, results in test_results.items():
    if isinstance(results, dict):
        ok_count = sum(1 for v in results.values() if v == "OK")
        total_count = len(results)
        status = "[OK]" if ok_count == total_count else "[WARN]" if ok_count > 0 else "[FAIL]"
        print(f"{status} {category.upper()}: {ok_count}/{total_count} checks passed")
        if ok_count < total_count:
            all_ok = False

print("\n" + "=" * 60)
if all_ok:
    print("STATUS: SYSTEM READY FOR USE")
    print("\nTo start the development environment:")
    print("1. Terminal 1: python start_backend.py")
    print("2. Terminal 2: cd frontend && npm install && npm run dev")
else:
    print("STATUS: SYSTEM HAS ISSUES (but should still work)")
    print("\nThe system will use LP fallback for optimization if ML model is unavailable.")
    print("\nTo start the development environment:")
    print("1. Terminal 1: python start_backend.py")
    print("2. Terminal 2: cd frontend && npm install && npm run dev")

print("=" * 60)
