"""
=============================================================================
VIDEO TIME LINKING MODULE
=============================================================================
File: src/pipeline/stage/load_video_times.py

PURPOSE:
    Load video times data and create timestamped YouTube URLs for events/shifts.
    Enables direct linking from any event or shift to the exact video moment.

YOUTUBE URL FORMAT:
    Base: https://www.youtube.com/watch?v=VIDEO_ID
    With timestamp: https://www.youtube.com/watch?v=VIDEO_ID&t=Xs
    Where X = total seconds from video start

=============================================================================
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re

from src.database.connection import execute_sql
from src.database.table_operations import (
    load_dataframe_to_table,
    table_exists,
    get_row_count,
    read_query,
    drop_table
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


def load_video_times_for_game(game_id: int, game_dir: Path) -> Dict[str, int]:
    """
    Load video times data from Excel file.
    
    Args:
        game_id: Game identifier
        game_dir: Path to game folder
    
    Returns:
        Dictionary with row counts
    """
    logger.info(f"Loading video times for game {game_id}")
    
    video_file = game_dir / f'{game_id}_video_times.xlsx'
    if not video_file.exists():
        logger.info(f"  No video times file found for game {game_id}")
        return {'video_times': 0}
    
    try:
        xlsx = pd.ExcelFile(video_file)
        
        # Look for video sheet
        video_sheet = None
        for sheet in xlsx.sheet_names:
            if 'video' in sheet.lower():
                video_sheet = sheet
                break
        
        if video_sheet is None:
            video_sheet = xlsx.sheet_names[0]
        
        df = pd.read_excel(xlsx, sheet_name=video_sheet)
        
        if len(df) == 0:
            return {'video_times': 0}
        
        # Normalize column names
        df.columns = [str(c).lower().strip().replace(' ', '_') for c in df.columns]
        
        # Add game_id if not present
        if 'game_id' not in df.columns:
            df['game_id'] = game_id
        
        # Add load timestamp
        df['_load_timestamp'] = datetime.now().isoformat()
        
        # Generate video key if not present
        if 'key' not in df.columns and 'index' in df.columns:
            df['video_key'] = df.apply(
                lambda r: f"VD{game_id:05d}{int(r.get('index', 0)):05d}", axis=1
            )
        else:
            df['video_key'] = df.get('key', df.index.map(lambda i: f"VD{game_id:05d}{i:05d}"))
        
        # Extract video ID from URL if present
        if 'url_1' in df.columns:
            df['video_id_extracted'] = df['url_1'].apply(_extract_youtube_id)
        
        load_dataframe_to_table(df, f'stg_video_times_{game_id}', 'replace')
        
        return {'video_times': len(df)}
        
    except Exception as e:
        logger.error(f"Error loading video times for game {game_id}: {e}")
        return {'video_times': 0}


def _extract_youtube_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from URL."""
    if pd.isna(url):
        return None
    
    url = str(url)
    
    # Pattern for youtube.com/watch?v=ID
    match = re.search(r'[?&]v=([a-zA-Z0-9_-]{11})', url)
    if match:
        return match.group(1)
    
    # Pattern for youtu.be/ID
    match = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', url)
    if match:
        return match.group(1)
    
    return None


def create_timestamped_video_url(base_url: str, seconds: int) -> str:
    """
    Create YouTube URL with timestamp.
    
    Args:
        base_url: Base YouTube URL
        seconds: Number of seconds into video
    
    Returns:
        URL with timestamp appended
    """
    if pd.isna(base_url) or pd.isna(seconds):
        return base_url
    
    seconds = int(seconds)
    if seconds <= 0:
        return base_url
    
    # Check if URL already has parameters
    if '?' in base_url:
        return f"{base_url}&t={seconds}s"
    else:
        return f"{base_url}?t={seconds}s"


def generate_event_video_links(game_id: int) -> int:
    """
    Generate video links for all events in a game.
    
    Uses event_running_start_seconds to create timestamped URLs.
    
    Args:
        game_id: Game identifier
    
    Returns:
        Number of links generated
    """
    if not table_exists(f'stg_video_times_{game_id}'):
        logger.info(f"No video times for game {game_id}")
        return 0
    
    if not table_exists(f'int_events_{game_id}'):
        logger.info(f"No events for game {game_id}")
        return 0
    
    # Get video URL
    video_df = read_query(f"""
        SELECT url_1, video_id_extracted 
        FROM stg_video_times_{game_id}
        WHERE url_1 IS NOT NULL
        LIMIT 1
    """)
    
    if len(video_df) == 0:
        return 0
    
    base_url = video_df.iloc[0]['url_1']
    
    # Get events with running time
    events_df = read_query(f"""
        SELECT event_index, event_key, time_total_seconds
        FROM int_events_{game_id}
        WHERE time_total_seconds IS NOT NULL
    """)
    
    # Create video links table
    links = []
    for _, row in events_df.iterrows():
        # Calculate running seconds (assuming period time needs conversion)
        # This depends on how event_running_start is stored in your data
        running_seconds = row['time_total_seconds']
        
        video_url = create_timestamped_video_url(base_url, running_seconds)
        
        links.append({
            'game_id': game_id,
            'event_index': row['event_index'],
            'event_key': row['event_key'],
            'video_url': video_url,
            'video_seconds': running_seconds,
            'link_type': 'event',
            '_processed_timestamp': datetime.now().isoformat()
        })
    
    if links:
        df = pd.DataFrame(links)
        load_dataframe_to_table(df, f'int_event_video_links_{game_id}', 'replace')
    
    return len(links)


def generate_shift_video_links(game_id: int) -> int:
    """
    Generate video links for all shifts in a game.
    
    Args:
        game_id: Game identifier
    
    Returns:
        Number of links generated
    """
    if not table_exists(f'stg_video_times_{game_id}'):
        return 0
    
    if not table_exists(f'int_shifts_{game_id}'):
        return 0
    
    # Get video URL
    video_df = read_query(f"""
        SELECT url_1 FROM stg_video_times_{game_id}
        WHERE url_1 IS NOT NULL
        LIMIT 1
    """)
    
    if len(video_df) == 0:
        return 0
    
    base_url = video_df.iloc[0]['url_1']
    
    # Get shifts with start time
    shifts_df = read_query(f"""
        SELECT shift_index, shift_key, shift_start_total_seconds
        FROM int_shifts_{game_id}
        WHERE shift_start_total_seconds IS NOT NULL
    """)
    
    links = []
    for _, row in shifts_df.iterrows():
        running_seconds = row['shift_start_total_seconds']
        video_url = create_timestamped_video_url(base_url, running_seconds)
        
        links.append({
            'game_id': game_id,
            'shift_index': row['shift_index'],
            'shift_key': row['shift_key'],
            'video_url': video_url,
            'video_seconds': running_seconds,
            'link_type': 'shift',
            '_processed_timestamp': datetime.now().isoformat()
        })
    
    if links:
        df = pd.DataFrame(links)
        load_dataframe_to_table(df, f'int_shift_video_links_{game_id}', 'replace')
    
    return len(links)


def publish_video_links_to_datamart(game_id: int) -> Dict[str, int]:
    """
    Publish video links to datamart fact table.
    
    Args:
        game_id: Game identifier
    
    Returns:
        Dictionary with row counts
    """
    # Create table if needed
    execute_sql("""
        CREATE TABLE IF NOT EXISTS fact_video_links (
            link_id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            link_type TEXT,
            event_index INTEGER,
            event_key TEXT,
            shift_index INTEGER,
            shift_key TEXT,
            video_url TEXT,
            video_seconds INTEGER,
            _processed_timestamp TEXT
        )
    """)
    
    # Delete existing for this game
    execute_sql("DELETE FROM fact_video_links WHERE game_id = :gid", {'gid': game_id})
    
    results = {}
    
    # Insert event links
    if table_exists(f'int_event_video_links_{game_id}'):
        execute_sql(f"""
            INSERT INTO fact_video_links 
                (game_id, link_type, event_index, event_key, video_url, video_seconds, _processed_timestamp)
            SELECT 
                game_id, link_type, event_index, event_key, video_url, video_seconds, _processed_timestamp
            FROM int_event_video_links_{game_id}
        """)
    
    # Insert shift links
    if table_exists(f'int_shift_video_links_{game_id}'):
        execute_sql(f"""
            INSERT INTO fact_video_links 
                (game_id, link_type, shift_index, shift_key, video_url, video_seconds, _processed_timestamp)
            SELECT 
                game_id, link_type, shift_index, shift_key, video_url, video_seconds, _processed_timestamp
            FROM int_shift_video_links_{game_id}
        """)
    
    results['fact_video_links'] = get_row_count('fact_video_links')
    
    return results


def process_video_for_game(game_id: int, game_dir: Path) -> Dict[str, int]:
    """
    Full video processing for a game.
    
    Args:
        game_id: Game identifier
        game_dir: Path to game folder
    
    Returns:
        Dictionary with all results
    """
    results = {}
    
    # Load video times
    load_result = load_video_times_for_game(game_id, game_dir)
    results.update(load_result)
    
    # Generate event links
    event_links = generate_event_video_links(game_id)
    results['event_video_links'] = event_links
    
    # Generate shift links
    shift_links = generate_shift_video_links(game_id)
    results['shift_video_links'] = shift_links
    
    # Publish to datamart
    if event_links > 0 or shift_links > 0:
        publish_results = publish_video_links_to_datamart(game_id)
        results.update(publish_results)
    
    return results
