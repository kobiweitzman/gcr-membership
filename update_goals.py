#!/usr/bin/env python3
"""
Update GCR Goals data.

Usage:
    python3 update_goals.py              # uploads existing goals.json to Supabase

Edit goals.json to change targets, then run this script to push changes live.
The app will show updated goals on next launch — no Netlify re-upload needed.
"""

import sys
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GOALS_PATH = os.path.join(SCRIPT_DIR, "goals.json")
ENV_PATH = os.path.join(SCRIPT_DIR, ".env")

def load_env():
    config = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    config[key.strip()] = val.strip()
    return config

def main():
    if not os.path.exists(GOALS_PATH):
        print(f"Goals file not found: {GOALS_PATH}")
        sys.exit(1)

    with open(GOALS_PATH) as f:
        goals = json.load(f)

    print(f"Region goal: {goals.get('regionGoal')} total members")
    print(f"New member goal: {goals.get('totalNewGoal')} total recruits")
    print(f"Months tracked: {', '.join(goals.get('months', []))}")
    print(f"Chapter goals: {len(goals.get('chapters', {}))}")
    for name, data in sorted(goals.get("chapters", {}).items()):
        monthly = data.get("monthly", [])
        total = data.get("total", 0)
        months_str = " ".join(f"{m}:{g}" for m, g in zip(goals.get("months", []), monthly))
        print(f"  {name}: {months_str} (Total: {total})")

    # Upload to Supabase
    import urllib.request

    config = load_env()
    supabase_url = config.get("SUPABASE_URL", "")
    service_key = config.get("SUPABASE_SERVICE_ROLE_KEY", "")

    if not supabase_url or not service_key:
        print("\nSupabase not configured. Edit .env to add credentials.")
        return

    json_bytes = json.dumps(goals, indent=2).encode("utf-8")
    upload_url = f"{supabase_url}/storage/v1/object/membership/goals.json"

    print(f"\nUploading goals...")
    req = urllib.request.Request(
        upload_url,
        data=json_bytes,
        method="PUT",
        headers={
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
            "x-upsert": "true",
        },
    )

    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status in (200, 201):
                print("Goals uploaded successfully!")
                print("The app will show updated goals on next launch.")
            else:
                print(f"Upload returned status {resp.status}")
    except Exception as e:
        print(f"Upload failed: {e}")

if __name__ == "__main__":
    main()
