"""BLB table upload service - handles Excel file uploads."""
import sys
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..services.staging_service import staging_service
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

# Get project root (parent of api/)
PROJECT_ROOT = Path(__file__).parent.parent.parent
BLB_PATH = PROJECT_ROOT / "data" / "raw" / "BLB_Tables.xlsx"


def upload_blb_table_from_excel(
    table_name: str,
    excel_path: Optional[Path] = None,
    replace: bool = False
) -> Dict[str, Any]:
    """
    Upload BLB table from Excel file to staging.
    
    This is a helper function that reads from Excel and uploads to staging.
    
    Args:
        table_name: BLB table name (e.g., 'dim_player')
        excel_path: Path to BLB_Tables.xlsx (default: data/raw/BLB_Tables.xlsx)
        replace: If True, replace existing data
        
    Returns:
        Dict with upload results
    """
    if excel_path is None:
        excel_path = BLB_PATH
    
    if not excel_path.exists():
        raise FileNotFoundError(f"Excel file not found: {excel_path}")
    
    try:
        # Read Excel sheet
        df = pd.read_excel(excel_path, sheet_name=table_name, dtype=str)
        
        # Convert to records
        data = df.to_dict(orient='records')
        
        # Upload to staging
        result = staging_service.upload_blb_table(
            table_name=table_name,
            data=data,
            replace=replace
        )
        
        logger.info(f"Uploaded {len(data)} rows from Excel to {result['staging_table']}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to upload BLB table from Excel: {e}", exc_info=True)
        raise
