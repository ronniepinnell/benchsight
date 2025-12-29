#!/usr/bin/env python3
"""
Quick setup verification for Supabase connection
"""
import requests

SUPABASE_URL = "https://uuaowslhpgyiudmbvqze.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV1YW93c2xocGd5aXVkbWJ2cXplIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY4NTQ5ODcsImV4cCI6MjA4MjQzMDk4N30.9WjZcLzB555vKaiDeby8nYJ3Ce9L-SCkFrYH1Ts4ILU"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}

print("Testing Supabase connection...")
try:
    resp = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=HEADERS)
    if resp.status_code == 200:
        print("✓ Connection successful")
        print(f"\nURL: {SUPABASE_URL}")
        print("\nNext steps:")
        print("1. Run sql/schema_v2.sql in Supabase SQL Editor")
        print("2. Run: python3 src/etl_pipeline.py")
    else:
        print(f"✗ Connection failed: {resp.status_code}")
        print(resp.text)
except Exception as e:
    print(f"✗ Error: {e}")
