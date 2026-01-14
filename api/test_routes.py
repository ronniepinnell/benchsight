"""
Quick script to test API routes
Run: python api/test_routes.py
"""
import requests

BASE_URL = "http://localhost:8000"

print("Testing API routes...")
print()

# Test health endpoint
try:
    r = requests.get(f"{BASE_URL}/api/health")
    print(f"✓ GET /api/health: {r.status_code}")
    if r.status_code == 200:
        print(f"  Response: {r.json()}")
except Exception as e:
    print(f"✗ GET /api/health: ERROR - {e}")

print()

# Test ETL trigger endpoint
try:
    r = requests.post(
        f"{BASE_URL}/api/etl/trigger",
        json={"mode": "full"},
        headers={"Content-Type": "application/json"}
    )
    print(f"✓ POST /api/etl/trigger: {r.status_code}")
    if r.status_code == 202:
        print(f"  Response: {r.json()}")
except Exception as e:
    print(f"✗ POST /api/etl/trigger: ERROR - {e}")
