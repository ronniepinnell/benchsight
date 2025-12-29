"""
ETL Data Cleaning Tests
=======================
Tests for data cleaning and transformation functions used in upload.

Run: pytest tests/test_etl_upload.py -v
"""

import pytest
import math
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile


# =============================================================================
# FUNCTIONS UNDER TEST (copied from PRODUCTION_ETL.py for isolation)
# =============================================================================

def is_null(val):
    """Comprehensive null detection."""
    if val is None:
        return True
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return True
    if isinstance(val, str):
        v = val.strip().lower()
        if v in ("", "nan", "none", "null", "na", "n/a", "#n/a", "nat",
                 "-", "--", "#value!", "#ref!", "#div/0!", "#name?", "#num!", "<na>"):
            return True
    try:
        if pd.isna(val):
            return True
    except (TypeError, ValueError):
        pass
    return False


def clean_value(val):
    """Clean value for JSON serialization."""
    if is_null(val):
        return None
    
    if isinstance(val, bytes):
        try:
            val = val.decode("utf-8")
        except UnicodeDecodeError:
            val = val.decode("latin-1", errors="ignore")
    
    s = str(val).strip()
    s = s.replace("\ufeff", "").replace("\x00", "")
    
    if len(s) > 10000:
        s = s[:10000]
    
    return s if s else None


def clean_dataframe(df):
    """Clean DataFrame columns."""
    df.columns = [str(c).strip().replace("\ufeff", "") for c in df.columns]
    
    drop_patterns = ["Unnamed:", "_export_timestamp", "_source_file", "index", "level_0"]
    drop_cols = [c for c in df.columns
                 if any(p in c for p in drop_patterns) or c.startswith("_")]
    
    return df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")


def to_records(df):
    """Convert DataFrame to list of clean records."""
    records = []
    for _, row in df.iterrows():
        record = {}
        for col in df.columns:
            val = clean_value(row[col])
            if val is not None:
                record[col] = val
        if record:
            records.append(record)
    return records


def load_csv_safe(filepath):
    """Load CSV with encoding detection."""
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            return pd.read_csv(filepath, encoding=enc, dtype=str, low_memory=False)
        except UnicodeDecodeError:
            continue
        except Exception:
            return None
    return None


# =============================================================================
# TESTS
# =============================================================================

class TestIsNull:
    """Tests for null detection function."""
    
    def test_none_is_null(self):
        assert is_null(None) is True
    
    def test_nan_float_is_null(self):
        assert is_null(float("nan")) is True
    
    def test_inf_is_null(self):
        assert is_null(float("inf")) is True
        assert is_null(float("-inf")) is True
    
    def test_empty_string_is_null(self):
        assert is_null("") is True
        assert is_null("   ") is True
    
    @pytest.mark.parametrize("val", [
        "nan", "NaN", "NAN", "none", "None", "NONE",
        "null", "NULL", "na", "NA", "n/a", "N/A",
        "#N/A", "#n/a", "nat", "NaT", "-", "--",
        "#VALUE!", "#REF!", "#DIV/0!", "#NAME?", "#NUM!", "<NA>"
    ])
    def test_null_strings(self, val):
        assert is_null(val) is True
    
    @pytest.mark.parametrize("val", [
        "hello", "0", "false", "123", "test value"
    ])
    def test_valid_values_not_null(self, val):
        assert is_null(val) is False


class TestCleanValue:
    """Tests for value cleaning function."""
    
    def test_null_returns_none(self):
        assert clean_value(None) is None
        assert clean_value("") is None
        assert clean_value("nan") is None
    
    def test_string_stripped(self):
        assert clean_value("  hello  ") == "hello"
    
    def test_bom_removed(self):
        assert clean_value("\ufeffhello") == "hello"
    
    def test_null_char_removed(self):
        assert clean_value("hel\x00lo") == "hello"
    
    def test_long_string_truncated(self):
        long_str = "x" * 20000
        result = clean_value(long_str)
        assert len(result) == 10000
    
    def test_bytes_decoded(self):
        assert clean_value(b"hello") == "hello"
    
    def test_numpy_int(self):
        assert clean_value(np.int64(42)) == "42"
    
    def test_numpy_float(self):
        assert clean_value(np.float64(3.14)) == "3.14"


class TestCleanDataframe:
    """Tests for DataFrame cleaning function."""
    
    def test_removes_unnamed_columns(self):
        df = pd.DataFrame({"a": [1], "Unnamed: 0": [2], "b": [3]})
        result = clean_dataframe(df)
        assert "Unnamed: 0" not in result.columns
        assert "a" in result.columns
    
    def test_removes_index_column(self):
        df = pd.DataFrame({"a": [1], "index": [2]})
        result = clean_dataframe(df)
        assert "index" not in result.columns
    
    def test_removes_underscore_prefix(self):
        df = pd.DataFrame({"a": [1], "_private": [2], "_meta": [3]})
        result = clean_dataframe(df)
        assert "_private" not in result.columns
        assert "_meta" not in result.columns
    
    def test_strips_column_names(self):
        df = pd.DataFrame({" a ": [1], "b  ": [2]})
        result = clean_dataframe(df)
        assert "a" in result.columns
        assert "b" in result.columns


class TestToRecords:
    """Tests for DataFrame to records transformation."""
    
    def test_basic_transform(self):
        df = pd.DataFrame({"a": ["1"], "b": ["2"]})
        records = to_records(df)
        assert len(records) == 1
        assert records[0] == {"a": "1", "b": "2"}
    
    def test_skips_empty_records(self):
        df = pd.DataFrame({"a": ["", None], "b": [None, ""]})
        records = to_records(df)
        assert len(records) == 0
    
    def test_null_values_excluded(self):
        df = pd.DataFrame({"a": ["1"], "b": [None]})
        records = to_records(df)
        assert records[0] == {"a": "1"}


class TestLoadCSVSafe:
    """Tests for safe CSV loading."""
    
    def test_load_utf8_csv(self, tmp_path):
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("a,b\n1,2\n", encoding="utf-8")
        
        df = load_csv_safe(csv_file)
        assert df is not None
        assert len(df) == 1
    
    def test_load_latin1_csv(self, tmp_path):
        csv_file = tmp_path / "test.csv"
        csv_file.write_bytes("a,b\n1,café\n".encode("latin-1"))
        
        df = load_csv_safe(csv_file)
        assert df is not None
    
    def test_load_nonexistent_returns_none(self, tmp_path):
        df = load_csv_safe(tmp_path / "nonexistent.csv")
        assert df is None


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""
    
    def test_mixed_types_in_column(self):
        df = pd.DataFrame({"a": [1, "two", 3.0, None]})
        records = to_records(df)
        assert len(records) == 3
    
    @pytest.mark.parametrize("val", [
        "#VALUE!", "#REF!", "#DIV/0!", "#NAME?", "#NUM!"
    ])
    def test_excel_errors(self, val):
        assert is_null(val) is True
    
    def test_pandas_nat(self):
        assert is_null(pd.NaT) is True
    
    def test_numpy_nan(self):
        assert is_null(np.nan) is True
    
    def test_infinity_values(self):
        assert is_null(np.inf) is True
        assert is_null(-np.inf) is True
    
    def test_whitespace_only_string(self):
        assert is_null("   \t\n  ") is True
