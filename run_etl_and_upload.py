#!/usr/bin/env python3
"""
Run ETL and upload to Supabase in sequence.

Usage:
    python run_etl_and_upload.py
"""

import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def run_command(cmd, description):
    """Run a command and return success status."""
    print("\n" + "=" * 70)
    print(description)
    print("=" * 70)
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            shell=True,
            check=False,
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def main():
    print("\n" + "=" * 70)
    print("BENCHSIGHT: ETL + SUPABASE UPLOAD")
    print("=" * 70)
    
    # Step 1: Run ETL
    print("\nStep 1: Running ETL...")
    etl_success = run_command("python3 run_etl.py", "RUNNING ETL")
    
    if not etl_success:
        print("\n❌ ETL failed. Stopping.")
        sys.exit(1)
    
    print("\n✓ ETL completed successfully!")
    
    # Step 2: Upload to Supabase
    print("\nStep 2: Uploading to Supabase...")
    upload_success = run_command("python3 upload.py", "UPLOADING TO SUPABASE")
    
    if not upload_success:
        print("\n❌ Upload failed.")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("✓ COMPLETE: ETL and Upload finished successfully!")
    print("=" * 70)

if __name__ == "__main__":
    main()
