#!/usr/bin/env python3
"""
Create .env.local for dashboard from config/config_local.ini
"""
import configparser
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_FILE = PROJECT_ROOT / "config" / "config_local.ini"
ENV_FILE = PROJECT_ROOT / "ui" / "dashboard" / ".env.local"

def main():
    # Read config
    if not CONFIG_FILE.exists():
        print(f"❌ Error: {CONFIG_FILE} not found")
        return 1
    
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    
    if 'supabase' not in config:
        print("❌ Error: No [supabase] section in config file")
        return 1
    
    supabase_url = config.get('supabase', 'url', fallback='')
    
    if not supabase_url:
        print("❌ Error: No 'url' found in [supabase] section")
        return 1
    
    print(f"✅ Found Supabase URL: {supabase_url}")
    
    # Check if .env.local exists
    if ENV_FILE.exists():
        response = input(f"⚠️  {ENV_FILE} already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("   Keeping existing file")
            return 0
    
    # Create .env.local
    env_content = f"""# Dashboard Environment Variables
# Auto-generated from config/config_local.ini

NEXT_PUBLIC_SUPABASE_URL={supabase_url}
NEXT_PUBLIC_SUPABASE_ANON_KEY=REPLACE_WITH_YOUR_ANON_KEY

# IMPORTANT: Get your anon key from Supabase Dashboard:
# 1. Go to: https://supabase.com/dashboard/project/{supabase_url.replace('https://', '').replace('.supabase.co', '')}/settings/api
# 2. Copy the "anon public" key (NOT the service_role key)
# 3. Replace REPLACE_WITH_YOUR_ANON_KEY above
"""
    
    ENV_FILE.parent.mkdir(parents=True, exist_ok=True)
    ENV_FILE.write_text(env_content)
    
    print(f"✅ Created {ENV_FILE}")
    print("")
    print("⚠️  IMPORTANT: You need to add your Supabase ANON KEY")
    print("")
    project_id = supabase_url.replace('https://', '').replace('.supabase.co', '')
    print(f"   1. Go to: https://supabase.com/dashboard/project/{project_id}/settings/api")
    print("   2. Find 'anon public' key (NOT service_role)")
    print(f"   3. Edit {ENV_FILE} and replace REPLACE_WITH_YOUR_ANON_KEY")
    print("")
    
    return 0

if __name__ == '__main__':
    exit(main())
