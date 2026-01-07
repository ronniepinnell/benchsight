"""
=============================================================================
SCHEMA VALIDATOR
=============================================================================
File: src/validators/schema_validator.py
Created: 2024-12-30
Author: Production Hardening Sprint

PURPOSE:
    Validate CSV data against expected database schema BEFORE loading.
    Catches schema mismatches early to prevent silent data loss or corruption.

WHAT IT VALIDATES:
    1. Column presence - CSV columns exist in DB schema
    2. Required columns - Critical columns are not missing
    3. Type compatibility - Values match expected types
    4. Primary key validity - PK column exists and has no nulls

USAGE:
    from src.validators.schema_validator import SchemaValidator
    
    validator = SchemaValidator()
    
    # Validate before loading
    is_valid, errors = validator.validate_table("fact_events", records)
    if not is_valid:
        raise SchemaValidationError("fact_events", errors=errors)

WHY THIS EXISTS:
    Without pre-validation, the ETL might:
    - Silently drop columns that don't exist in DB
    - Insert NULL where NOT NULL was expected
    - Coerce types incorrectly (e.g., "12.5" -> 12)
    - Fail mid-load leaving partial data

=============================================================================
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import json

from src.exceptions import SchemaValidationError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SchemaValidator:
    """
    Validates data against expected schema before loading.
    
    The validator uses a schema definition file that maps tables to their
    expected columns, types, and constraints.
    
    Attributes:
        schema_definitions: Dict mapping table names to column definitions
        strict_mode: If True, extra columns cause errors. If False, warnings.
    """
    
    # Columns that are auto-generated and don't need to be in CSV
    AUTO_GENERATED_COLUMNS = {
        "created_at", "updated_at", "modified_at", 
        "id", "row_id", "_id"
    }
    
    # Type mapping from Python types to expected DB types
    PYTHON_TO_DB_TYPES = {
        str: ["TEXT", "VARCHAR", "CHAR", "UUID"],
        int: ["INTEGER", "INT", "BIGINT", "SMALLINT"],
        float: ["DECIMAL", "NUMERIC", "REAL", "DOUBLE", "FLOAT"],
        bool: ["BOOLEAN", "BOOL"],
    }
    
    def __init__(self, schema_file: Path = None, strict_mode: bool = False):
        """
        Initialize the schema validator.
        
        Args:
            schema_file: Path to JSON schema definition file.
                        If None, uses built-in definitions from TABLE_DEFINITIONS.
            strict_mode: If True, extra columns in CSV cause validation failure.
        """
        self.strict_mode = strict_mode
        self.schema_definitions = {}
        
        if schema_file and schema_file.exists():
            self._load_schema_file(schema_file)
        else:
            self._build_from_table_definitions()
    
    def _load_schema_file(self, schema_file: Path):
        """Load schema definitions from JSON file."""
        with open(schema_file, 'r') as f:
            self.schema_definitions = json.load(f)
        logger.info(f"Loaded schema definitions for {len(self.schema_definitions)} tables")
    
    def _build_from_table_definitions(self):
        """
        Build minimal schema from CSV files.
        
        This is a fallback when no schema file exists. It reads column names
        from actual CSV files and assumes first column is primary key.
        """
        try:
            output_dir = Path(__file__).parent.parent.parent / "data" / "output"
            if not output_dir.exists():
                logger.warning("Output directory not found")
                return
            
            for csv_file in output_dir.glob("*.csv"):
                table_name = csv_file.stem
                import pandas as pd
                df = pd.read_csv(csv_file, nrows=0)
                pk = df.columns[0] if len(df.columns) > 0 else None
                
                self.schema_definitions[table_name] = {
                    "pk": pk,
                    "category": "dim" if table_name.startswith("dim_") else "fact",
                    "columns": {col: "TEXT" for col in df.columns},
                    "required": [pk] if pk else []
                }
            
            logger.info(f"Built schema definitions for {len(self.schema_definitions)} tables from CSV files")
        except Exception as e:
            logger.warning(f"Could not build schema from CSVs: {e}")
    
    def validate_table(self, table_name: str, records: List[Dict], 
                       db_schema: Dict[str, str] = None) -> Tuple[bool, List[str]]:
        """
        Validate records against expected schema.
        
        Args:
            table_name: Name of the target table
            records: List of record dicts to validate
            db_schema: Optional dict of {column_name: db_type} from actual DB.
                      If provided, enables type validation.
        
        Returns:
            Tuple of (is_valid: bool, errors: List[str])
        
        Raises:
            SchemaValidationError: If validation fails and strict_mode is True
        """
        errors = []
        warnings = []
        
        if not records:
            return True, []
        
        # Get expected schema for this table
        table_schema = self.schema_definitions.get(table_name, {})
        pk_column = table_schema.get("pk")
        required_columns = set(table_schema.get("required", []))
        
        # Get actual columns from CSV
        csv_columns = set(records[0].keys())
        
        # Validate primary key exists
        if pk_column:
            if pk_column not in csv_columns:
                errors.append(f"Primary key column '{pk_column}' missing from CSV")
            else:
                # Check for null PKs
                null_pks = sum(1 for r in records if r.get(pk_column) is None or r.get(pk_column) == "")
                if null_pks > 0:
                    errors.append(f"Primary key '{pk_column}' has {null_pks} null/empty values")
                
                # Check for duplicate PKs
                pk_values = [r.get(pk_column) for r in records]
                unique_pks = set(pk_values)
                if len(unique_pks) < len(pk_values):
                    dup_count = len(pk_values) - len(unique_pks)
                    errors.append(f"Primary key '{pk_column}' has {dup_count} duplicate values")
        
        # Validate required columns exist
        missing_required = required_columns - csv_columns
        if missing_required:
            errors.append(f"Missing required columns: {sorted(missing_required)}")
        
        # If we have DB schema, do deeper validation
        if db_schema:
            db_columns = set(db_schema.keys()) - self.AUTO_GENERATED_COLUMNS
            
            # Check for columns in CSV but not in DB
            extra_in_csv = csv_columns - db_columns - self.AUTO_GENERATED_COLUMNS
            if extra_in_csv:
                msg = f"Columns in CSV but not in DB schema: {sorted(extra_in_csv)}"
                if self.strict_mode:
                    errors.append(msg)
                else:
                    warnings.append(msg)
            
            # Check for required DB columns missing from CSV
            # (excluding auto-generated columns)
            missing_in_csv = db_columns - csv_columns - self.AUTO_GENERATED_COLUMNS
            # Filter to only truly required columns (non-nullable)
            # For now, just warn about all missing columns
            if missing_in_csv:
                warnings.append(f"DB columns not in CSV: {sorted(missing_in_csv)}")
            
            # Type validation (sample first 100 records)
            type_errors = self._validate_types(records[:100], db_schema)
            if type_errors:
                errors.extend(type_errors)
        
        # Log results
        if warnings:
            for w in warnings:
                logger.warning(f"Schema warning for {table_name}: {w}")
        
        if errors:
            logger.error(f"Schema validation failed for {table_name}: {len(errors)} errors")
            if self.strict_mode:
                raise SchemaValidationError(
                    table_name=table_name,
                    missing_in_csv=list(missing_required),
                    type_mismatches={e.split(":")[0]: e for e in errors if "type" in e.lower()}
                )
        
        return len(errors) == 0, errors
    
    def _validate_types(self, records: List[Dict], db_schema: Dict[str, str]) -> List[str]:
        """
        Validate that record values match expected database types.
        
        Args:
            records: Sample records to validate
            db_schema: Dict of {column_name: db_type}
        
        Returns:
            List of type mismatch error messages
        """
        errors = []
        
        for column, db_type in db_schema.items():
            if column in self.AUTO_GENERATED_COLUMNS:
                continue
            
            # Get sample values (non-null)
            values = [r.get(column) for r in records if r.get(column) is not None]
            if not values:
                continue
            
            # Check type compatibility
            db_type_upper = db_type.upper()
            
            for value in values[:10]:  # Check first 10 non-null values
                if not self._is_type_compatible(value, db_type_upper):
                    errors.append(
                        f"Column '{column}': value '{value}' ({type(value).__name__}) "
                        f"incompatible with DB type {db_type}"
                    )
                    break  # One error per column is enough
        
        return errors
    
    def _is_type_compatible(self, value: Any, db_type: str) -> bool:
        """
        Check if a Python value is compatible with a database type.
        
        Args:
            value: The Python value
            db_type: The database type (e.g., "TEXT", "INTEGER")
        
        Returns:
            True if compatible, False otherwise
        """
        if value is None:
            return True  # NULL is compatible with any type
        
        # TEXT accepts anything
        if "TEXT" in db_type or "VARCHAR" in db_type or "CHAR" in db_type:
            return True
        
        # Integer types
        if any(t in db_type for t in ["INT", "INTEGER", "BIGINT", "SMALLINT"]):
            if isinstance(value, int):
                return True
            if isinstance(value, str):
                try:
                    int(value)
                    return True
                except ValueError:
                    return False
            return False
        
        # Decimal/float types
        if any(t in db_type for t in ["DECIMAL", "NUMERIC", "REAL", "DOUBLE", "FLOAT"]):
            if isinstance(value, (int, float)):
                return True
            if isinstance(value, str):
                try:
                    float(value)
                    return True
                except ValueError:
                    return False
            return False
        
        # Boolean
        if "BOOL" in db_type:
            if isinstance(value, bool):
                return True
            if isinstance(value, str):
                return value.lower() in ("true", "false", "1", "0", "t", "f")
            return False
        
        # Timestamp/Date
        if any(t in db_type for t in ["TIMESTAMP", "DATE", "TIME"]):
            if isinstance(value, str):
                # Basic date pattern check
                date_patterns = [
                    r"\d{4}-\d{2}-\d{2}",  # 2024-01-15
                    r"\d{4}/\d{2}/\d{2}",  # 2024/01/15
                    r"\d{2}/\d{2}/\d{4}",  # 01/15/2024
                ]
                return any(re.match(p, str(value)) for p in date_patterns)
            return False
        
        # UUID
        if "UUID" in db_type:
            if isinstance(value, str):
                uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
                return bool(re.match(uuid_pattern, value.lower()))
            return False
        
        # Default: accept if we don't know the type
        return True
    
    def validate_foreign_keys(self, table_name: str, records: List[Dict],
                              fk_definitions: Dict[str, Tuple[str, str]],
                              reference_data: Dict[str, set]) -> Tuple[bool, List[str]]:
        """
        Validate foreign key references exist in parent tables.
        
        Args:
            table_name: Name of the table being validated
            records: Records to validate
            fk_definitions: Dict of {fk_column: (parent_table, parent_column)}
            reference_data: Dict of {parent_table: set(valid_pk_values)}
        
        Returns:
            Tuple of (is_valid, errors)
        
        Example:
            fk_defs = {"game_id": ("dim_schedule", "game_id")}
            ref_data = {"dim_schedule": {"18969", "18970", "18971"}}
            valid, errors = validator.validate_foreign_keys(
                "fact_events", records, fk_defs, ref_data
            )
        """
        errors = []
        
        for fk_column, (parent_table, parent_column) in fk_definitions.items():
            if parent_table not in reference_data:
                errors.append(f"Reference data not provided for {parent_table}")
                continue
            
            valid_values = reference_data[parent_table]
            
            # Find orphaned records
            orphans = []
            for i, record in enumerate(records):
                fk_value = record.get(fk_column)
                if fk_value is not None and str(fk_value) not in valid_values:
                    orphans.append((i, fk_value))
            
            if orphans:
                sample = orphans[:5]
                errors.append(
                    f"Column '{fk_column}' has {len(orphans)} orphaned references to {parent_table}. "
                    f"Sample invalid values: {[v for _, v in sample]}"
                )
        
        return len(errors) == 0, errors


def validate_csv_before_load(table_name: str, csv_path: Path, 
                             strict: bool = False) -> Tuple[bool, List[str]]:
    """
    Convenience function to validate a CSV file before loading.
    
    Args:
        table_name: Target table name
        csv_path: Path to CSV file
        strict: Whether to use strict mode
    
    Returns:
        Tuple of (is_valid, errors)
    
    Example:
        is_valid, errors = validate_csv_before_load("fact_events", Path("data/output/fact_events.csv"))
        if not is_valid:
            print(f"Validation failed: {errors}")
    """
    import csv
    
    if not csv_path.exists():
        return False, [f"CSV file not found: {csv_path}"]
    
    # Read CSV
    records = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    
    if not records:
        return True, []  # Empty file is technically valid
    
    # Validate
    validator = SchemaValidator(strict_mode=strict)
    return validator.validate_table(table_name, records)


def generate_schema_file(output_path: Path, csv_dir: Path):
    """
    Generate a schema definition file from existing CSV files.
    
    Useful for bootstrapping schema validation from existing data.
    
    Args:
        output_path: Where to write the schema JSON
        csv_dir: Directory containing CSV files
    """
    import csv
    
    schema = {}
    
    for csv_file in csv_dir.glob("*.csv"):
        table_name = csv_file.stem
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            # Sample first 100 rows for type inference
            rows = []
            for i, row in enumerate(reader):
                if i >= 100:
                    break
                rows.append(row)
        
        # Infer types from sample data
        columns = {}
        for col in headers:
            values = [r.get(col) for r in rows if r.get(col)]
            inferred_type = _infer_type(values)
            columns[col] = inferred_type
        
        # Detect primary key (first column ending in _key or _id)
        pk = None
        for col in headers:
            if col.endswith("_key") or col == "player_id" or col == "game_id":
                pk = col
                break
        
        schema[table_name] = {
            "pk": pk,
            "columns": columns,
            "required": [pk] if pk else []
        }
    
    with open(output_path, 'w') as f:
        json.dump(schema, f, indent=2)
    
    logger.info(f"Generated schema file with {len(schema)} tables: {output_path}")


def _infer_type(values: List[str]) -> str:
    """Infer database type from sample string values."""
    if not values:
        return "TEXT"
    
    # Try integer
    try:
        for v in values[:10]:
            if v:
                int(v)
        return "INTEGER"
    except ValueError:
        pass
    
    # Try float
    try:
        for v in values[:10]:
            if v:
                float(v)
        return "DECIMAL"
    except ValueError:
        pass
    
    # Try boolean
    bool_values = {"true", "false", "1", "0", "t", "f"}
    if all(v.lower() in bool_values for v in values[:10] if v):
        return "BOOLEAN"
    
    # Default to text
    return "TEXT"
