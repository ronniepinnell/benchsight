"""
ETL Phases Module
=================

This module contains the extracted, modularized components of the ETL pipeline.
Each submodule handles a specific phase or category of functionality.

Modules:
- utilities: Common utility functions (drop columns, validate keys, save tables)
- derived_columns: Calculate derived columns from minimal input data
- validation: ETL validation functions
- event_enhancers: Event table enhancement functions (Phase 5.5, 5.6)
- shift_enhancers: Shift table enhancement functions (Phase 5.11, 5.12)
- derived_event_tables: Derived event table creation (Phase 5.9)
- reference_tables: Reference/dimension table creation

All public functions are re-exported here for convenience.
"""

from .utilities import (
    drop_underscore_columns,
    drop_index_and_unnamed,
    drop_all_null_columns,
    clean_numeric_index,
    validate_key,
    save_table,
    correct_venue_from_schedule,
)

from .derived_columns import calculate_derived_columns

from .validation import validate_all

from .event_enhancers import (
    enhance_event_tables,
    enhance_events_with_flags,
    enhance_derived_event_tables,
)

from .shift_enhancers import (
    enhance_shift_tables,
    enhance_shift_players,
    update_roster_positions_from_shifts,
)

from .derived_event_tables import (
    create_derived_event_tables,
    create_fact_sequences,
    create_fact_plays,
)

from .reference_tables import create_reference_tables

__all__ = [
    # Utilities
    'drop_underscore_columns',
    'drop_index_and_unnamed',
    'drop_all_null_columns',
    'clean_numeric_index',
    'validate_key',
    'save_table',
    'correct_venue_from_schedule',
    # Derived columns
    'calculate_derived_columns',
    # Validation
    'validate_all',
    # Event enhancers
    'enhance_event_tables',
    'enhance_events_with_flags',
    'enhance_derived_event_tables',
    # Shift enhancers
    'enhance_shift_tables',
    'enhance_shift_players',
    'update_roster_positions_from_shifts',
    # Derived event tables
    'create_derived_event_tables',
    'create_fact_sequences',
    'create_fact_plays',
    # Reference tables
    'create_reference_tables',
]
