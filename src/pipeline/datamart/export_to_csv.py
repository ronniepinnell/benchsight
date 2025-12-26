"""
=============================================================================
DATAMART: EXPORT TO CSV
=============================================================================
File: src/pipeline/datamart/export_to_csv.py

PURPOSE:
    Export datamart tables to CSV files for Power BI consumption.
    Backs up existing files before overwriting.

=============================================================================
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

from src.database.table_operations import (
    get_tables_by_layer,
    read_table
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


def backup_existing_exports(output_dir: Path) -> Optional[Path]:
    """
    Backup existing CSV files before overwriting.
    
    WHY BACKUP:
        - Preserve historical data exports
        - Enable rollback if issues discovered
        - Track data changes over time
    
    Args:
        output_dir: Directory containing current CSV files.
    
    Returns:
        Path to backup folder, or None if no files to backup.
    """
    # Check if there are any CSV files to backup
    csv_files = list(output_dir.glob('*.csv'))
    
    if not csv_files:
        logger.info("No existing CSV files to backup")
        return None
    
    # Create backup folder with timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    backup_dir = output_dir / 'backups' / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Move all CSV files to backup
    backed_up = 0
    for csv_file in csv_files:
        dest = backup_dir / csv_file.name
        shutil.copy2(csv_file, dest)  # copy2 preserves metadata
        backed_up += 1
    
    logger.info(f"Backed up {backed_up} CSV files to {backup_dir}")
    return backup_dir


def export_datamart_to_csv(
    output_dir: Path,
    backup: bool = True,
    tables: list = None
) -> int:
    """
    Export datamart tables to CSV files.
    
    WHY CSV:
        - Universal format for Power BI import
        - Easy to inspect and validate
        - Compatible with all BI tools
    
    Args:
        output_dir: Directory for CSV output.
        backup: If True, backup existing files first.
        tables: Optional list of specific tables to export.
                If None, exports all datamart tables.
    
    Returns:
        Number of tables exported.
    """
    logger.info(f"Exporting datamart to {output_dir}")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Backup existing files
    if backup:
        backup_existing_exports(output_dir)
    
    # Get tables to export
    if tables is None:
        tables = get_tables_by_layer('datamart')
    
    if not tables:
        logger.warning("No datamart tables found to export")
        return 0
    
    exported = 0
    
    for table_name in tables:
        try:
            # Read table
            df = read_table(table_name)
            
            if len(df) == 0:
                logger.warning(f"Skipping empty table: {table_name}")
                continue
            
            # Add export timestamp
            df['_export_timestamp'] = datetime.now().isoformat()
            
            # Export to CSV
            csv_path = output_dir / f'{table_name}.csv'
            df.to_csv(csv_path, index=False)
            
            exported += 1
            logger.info(f"  Exported {table_name}: {len(df)} rows")
            
        except Exception as e:
            logger.error(f"Failed to export {table_name}: {e}")
    
    logger.info(f"Exported {exported} tables to CSV")
    return exported


def export_to_excel(
    output_dir: Path,
    filename: str = 'hockey_datamart.xlsx',
    tables: list = None,
    max_tables: int = 20
) -> Path:
    """
    Export datamart tables to single Excel workbook.
    
    WHY EXCEL:
        - Single file for all data
        - Easy sharing and review
        - Multiple sheets for organization
    
    Args:
        output_dir: Directory for output.
        filename: Name of Excel file.
        tables: Optional list of specific tables.
        max_tables: Maximum tables to include (Excel sheet limit).
    
    Returns:
        Path to created Excel file.
    """
    import pandas as pd
    
    output_dir.mkdir(parents=True, exist_ok=True)
    excel_path = output_dir / filename
    
    if tables is None:
        tables = get_tables_by_layer('datamart')
    
    # Limit tables
    tables = tables[:max_tables]
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        for table_name in tables:
            try:
                df = read_table(table_name)
                # Sheet names limited to 31 chars
                sheet_name = table_name[:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            except Exception as e:
                logger.warning(f"Could not add {table_name} to Excel: {e}")
    
    logger.info(f"Created Excel workbook: {excel_path}")
    return excel_path


def get_backup_history(output_dir: Path) -> list:
    """
    Get list of backup folders with metadata.
    
    Args:
        output_dir: Output directory containing backups folder.
    
    Returns:
        List of dictionaries with backup info.
    """
    backup_base = output_dir / 'backups'
    
    if not backup_base.exists():
        return []
    
    backups = []
    for folder in sorted(backup_base.iterdir(), reverse=True):
        if folder.is_dir():
            csv_count = len(list(folder.glob('*.csv')))
            backups.append({
                'folder': folder.name,
                'path': str(folder),
                'csv_count': csv_count,
                'created': folder.stat().st_mtime
            })
    
    return backups


def restore_from_backup(backup_path: Path, output_dir: Path) -> int:
    """
    Restore CSV files from a backup.
    
    Args:
        backup_path: Path to backup folder.
        output_dir: Destination directory.
    
    Returns:
        Number of files restored.
    """
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup not found: {backup_path}")
    
    restored = 0
    for csv_file in backup_path.glob('*.csv'):
        dest = output_dir / csv_file.name
        shutil.copy2(csv_file, dest)
        restored += 1
    
    logger.info(f"Restored {restored} files from {backup_path}")
    return restored
