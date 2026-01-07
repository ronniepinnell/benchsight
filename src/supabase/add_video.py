"""
Add Video Script
Adds video links for a game to Supabase.

Usage:
    python3 src/add_video.py 19045 "https://www.youtube.com/watch?v=XXXXX"
    python3 src/add_video.py 19045 "https://www.youtube.com/watch?v=XXXXX" --type Broadcast
"""

import sys
import re

try:
    from supabase import create_client
except ImportError:
    print("Install supabase: pip3 install supabase")
    sys.exit(1)

# Config
SUPABASE_URL = "https://uuaowslhpgyiudmbvqze.supabase.co"
SUPABASE_KEY = "sb_publishable_t1lIOebbbCjAu_YBKc8tLg_B_zH_l73"


def extract_youtube_id(url):
    """Extract YouTube video ID from URL."""
    patterns = [
        r'v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'embed/([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 src/add_video.py <game_id> <youtube_url> [--type <video_type>]")
        print("")
        print("Examples:")
        print("  python3 src/add_video.py 19045 'https://www.youtube.com/watch?v=XXXXX'")
        print("  python3 src/add_video.py 19045 'https://www.youtube.com/watch?v=XXXXX' --type Broadcast")
        print("")
        print("Video types: Full_Ice, Broadcast, Highlights, Other")
        sys.exit(1)
    
    game_id = int(sys.argv[1])
    url = sys.argv[2]
    
    # Parse video type
    video_type = "Full_Ice"
    if '--type' in sys.argv:
        idx = sys.argv.index('--type')
        if idx + 1 < len(sys.argv):
            video_type = sys.argv[idx + 1]
    
    # Extract YouTube ID
    video_id = extract_youtube_id(url)
    
    print(f"Adding video for game {game_id}")
    print(f"  URL: {url}")
    print(f"  Type: {video_type}")
    print(f"  Video ID: {video_id}")
    
    # Connect
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Check if video exists for this game/type
    existing = supabase.table('dim_video').select('*').eq('game_id', game_id).eq('video_type', video_type).execute()
    
    if existing.data:
        print(f"\nVideo already exists for game {game_id} type {video_type}")
        response = input("Update it? (y/n): ")
        if response.lower() == 'y':
            supabase.table('dim_video').update({
                'url_1': url,
                'video_id': video_id,
                'extension': f'v={video_id}' if video_id else None
            }).eq('game_id', game_id).eq('video_type', video_type).execute()
            print("✓ Updated")
        else:
            print("Aborted")
    else:
        # Insert new
        record = {
            'game_id': game_id,
            'video_type': video_type,
            'video_category': video_type,
            'url_1': url,
            'video_id': video_id,
            'extension': f'v={video_id}' if video_id else None,
            'key': f'V{game_id}{video_type[:4]}'
        }
        supabase.table('dim_video').insert(record).execute()
        print("✓ Added")


if __name__ == "__main__":
    main()
