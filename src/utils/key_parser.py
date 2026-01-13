"""
=============================================================================
KEY PARSING UTILITIES
=============================================================================
File: src/utils/key_parser.py
Version: 19.10
Created: January 9, 2026

Centralized utilities for parsing BenchSight keys.
All key parsing should use these functions - DO NOT use inline slicing.

Key Formats:
  - shift_key: SH{game_id:5}{shift_index:variable} e.g., "SH1896900001"
  - event_key: EV{game_id:5}{event_index:variable} e.g., "EV1896900123"
  - player_key: P{id:6} e.g., "P100001"
  - sequence_key: SQ{game_id:5}{seq_num:variable}
  - linked_event_key: LV{game_id:5}{...}
=============================================================================
"""

import logging
from typing import Optional, Tuple, NamedTuple

logger = logging.getLogger(__name__)


class ShiftKeyParts(NamedTuple):
    """Parsed components of a shift key."""
    game_id: int
    shift_index: int
    raw: str


class EventKeyParts(NamedTuple):
    """Parsed components of an event key."""
    game_id: int
    event_index: int
    raw: str


def parse_shift_key(shift_key: str) -> Optional[ShiftKeyParts]:
    """
    Parse a shift key into its components.
    
    Format: SH{game_id:5}{shift_index:variable}
    Example: "SH1896900001" -> game_id=18969, shift_index=1
    
    Args:
        shift_key: The shift key string (e.g., "SH1896900001")
    
    Returns:
        ShiftKeyParts namedtuple or None if parsing fails
    
    Example:
        >>> parts = parse_shift_key("SH1896900001")
        >>> parts.game_id
        18969
        >>> parts.shift_index
        1
    """
    if not shift_key or not isinstance(shift_key, str):
        return None
    
    shift_key = str(shift_key).strip()
    
    if len(shift_key) < 8:  # Minimum: "SH" + 5 digit game + 1 digit index
        logger.debug(f"Shift key too short: {shift_key}")
        return None
    
    if not shift_key.startswith('SH'):
        logger.debug(f"Shift key doesn't start with 'SH': {shift_key}")
        return None
    
    try:
        game_id = int(shift_key[2:7])
        shift_index = int(shift_key[7:])
        return ShiftKeyParts(game_id=game_id, shift_index=shift_index, raw=shift_key)
    except (ValueError, IndexError) as e:
        logger.debug(f"Failed to parse shift key '{shift_key}': {e}")
        return None


def parse_event_key(event_key: str) -> Optional[EventKeyParts]:
    """
    Parse an event key into its components.
    
    Format: EV{game_id:5}{event_index:variable}
    Example: "EV1896900123" -> game_id=18969, event_index=123
    
    Args:
        event_key: The event key string
    
    Returns:
        EventKeyParts namedtuple or None if parsing fails
    """
    if not event_key or not isinstance(event_key, str):
        return None
    
    event_key = str(event_key).strip()
    
    if len(event_key) < 8:
        return None
    
    if not event_key.startswith('EV'):
        return None
    
    try:
        game_id = int(event_key[2:7])
        event_index = int(event_key[7:])
        return EventKeyParts(game_id=game_id, event_index=event_index, raw=event_key)
    except (ValueError, IndexError):
        return None


def make_shift_key(game_id: int, shift_index: int) -> str:
    """
    Create a shift key from components.
    
    Args:
        game_id: The game ID (5 digits)
        shift_index: The shift index within the game
    
    Returns:
        Shift key string (e.g., "SH1896900001")
    """
    return f"SH{game_id:05d}{shift_index:05d}"


def make_event_key(game_id: int, event_index: int) -> str:
    """
    Create an event key from components.
    
    Args:
        game_id: The game ID (5 digits)
        event_index: The event index within the game
    
    Returns:
        Event key string (e.g., "EV1896900123")
    """
    return f"EV{game_id:05d}{event_index:05d}"


def make_player_key(player_num: int) -> str:
    """
    Create a player key from player number.
    
    Args:
        player_num: The player number
    
    Returns:
        Player key string (e.g., "P100001")
    """
    return f"P{player_num:06d}"


def extract_game_id_from_key(key: str) -> Optional[int]:
    """
    Extract game_id from any BenchSight key.
    
    Works with: shift_key (SH), event_key (EV), sequence_key (SQ), etc.
    
    Args:
        key: Any BenchSight key string
    
    Returns:
        game_id as int or None if extraction fails
    """
    if not key or not isinstance(key, str) or len(key) < 7:
        return None
    
    try:
        return int(key[2:7])
    except (ValueError, IndexError):
        return None


def convert_le_to_lv_key(le_key: str) -> Optional[str]:
    """
    Convert LE (linked event) format to LV format.
    
    Format: LE18969009001 -> LV1896909001
    (Removes the leading zero from the middle section)
    
    Args:
        le_key: Linked event key in LE format
    
    Returns:
        Key in LV format, or None if conversion fails
    
    Example:
        >>> convert_le_to_lv_key("LE18969009001")
        'LV1896909001'
    """
    if not le_key or not isinstance(le_key, str):
        return None
    
    le_key = str(le_key).strip()
    
    if len(le_key) < 9 or not le_key.startswith('LE'):
        logger.debug(f"Invalid LE key format: {le_key}")
        return None
    
    try:
        # LE18969009001 -> LV + 18969 + 09001 (skip position 7 which is '0')
        # Original: 'LV' + le_key[2:7] + le_key[8:]
        game_id = le_key[2:7]  # "18969"
        remainder = le_key[8:]  # "9001" (skip the '0' at position 7)
        return f'LV{game_id}{remainder}'
    except (ValueError, IndexError) as e:
        logger.debug(f"Failed to convert LE key '{le_key}': {e}")
        return None
