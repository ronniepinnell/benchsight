# Documentation Update Guide

**For Future LLM Sessions: How to Update All BenchSight Documentation**

**Version:** 12.03  
**Last Updated:** January 7, 2026

---

## Quick Reference: What Needs Updating

| When User Says | Files to Update |
|----------------|-----------------|
| "Update docs" | All files below |
| "Clean up" | Remove outdated, update versions |
| "New version" | All files + CHANGELOG |
| "Fix HTML" | docs/html/*.html |

---

## STEP 1: Update Core Files (ALWAYS)

### 1.1 LLM_REQUIREMENTS.md (Root)
```bash
# Update these values:
- Version number in header
- Quick Reference table counts
- Current version / Next chat version
- Version History table at bottom
```

### 1.2 CHANGELOG.md (Root)
```bash
# Add new entry at TOP:
## v{VERSION} - {DATE}
### {Section Title}
- Change 1
- Change 2
```

### 1.3 docs/VERSION.txt
```bash
# Update:
Version: {VERSION}
Last Updated: {DATE TIME}
Tables: {COUNT}
Games Tracked: {COUNT}
```

---

## STEP 2: Update HTML Documentation

### 2.1 Run the Fix Script
```bash
python scripts/utilities/fix_all_html_docs.py
```

This automatically updates:
- docs/html/index.html
- docs/html/HONEST_ASSESSMENT.html
- docs/html/MODULE_REFERENCE.html
- docs/html/pipeline_visualization.html
- docs/html/KEY_FORMATS.html
- docs/html/LLM_HANDOFF.html
- docs/html/FUTURE_ROADMAP.html
- docs/html/diagrams/ERD_VIEWER.html
- docs/html/schema_diagram.html

### 2.2 Manual HTML Updates (if script doesn't cover)

Every HTML file should have:
```html
<p><strong>Last Updated:</strong> {DATE}</p>
<p><strong>Version:</strong> {VERSION}</p>
```

Update navigation bar in each file if table count changes:
```html
<a href="tables.html">📊 Tables ({COUNT})</a>
```

### 2.3 Regenerate Table HTML (if schema changes)
```bash
python scripts/utilities/generate_enhanced_table_docs.py
```

---

## STEP 3: Update Markdown Files

### Files in docs/

| File | When to Update | What to Change |
|------|----------------|----------------|
| `HONEST_ASSESSMENT.md` | When issues change | Status, table counts, known issues |
| `LLM_HANDOFF.md` | Architecture changes | Stats, version, features |
| `KEY_FORMATS.md` | Key format changes | Key prefixes, examples |
| `FUTURE_ROADMAP.md` | Priority changes | Completed items, new priorities |
| `DATA_DICTIONARY.md` | Column changes | Add/update column definitions |
| `MISSING_TABLES.md` | Tables added | Remove from missing list |
| `MODULE_REFERENCE.md` | Code structure changes | Module paths, descriptions |
| `VERIFICATION_STATUS.md` | Verification changes | Test results, accuracy |

---

## STEP 4: Update Diagram Files

### docs/diagrams/

| File | When to Update |
|------|----------------|
| `ERD_COMPLETE.mermaid` | Schema/table changes |
| `DATA_FLOW.mermaid` | ETL flow changes |
| `SCHEMA_RELATIONSHIPS.mermaid` | FK relationship changes |
| `STAT_CATEGORIES.mermaid` | Stat category changes |
| `TABLE_INVENTORY.csv` | Table list changes |

### docs/ (root)

| File | When to Update |
|------|----------------|
| `benchsight_data_flow.mermaid` | ETL flow changes |
| `schema_diagram.mermaid` | Schema changes |
| `column_metadata.json` | Column definition changes |

### Update Mermaid Files Template

```mermaid
%% Header to update:
%% Version: {VERSION} | {DATE}
%% Tables: {COUNT}
```

### Regenerate TABLE_INVENTORY.csv
```python
python3 << 'EOF'
import pandas as pd
from pathlib import Path

output_dir = Path("data/output")
rows = []
for csv_file in sorted(output_dir.glob("*.csv")):
    if csv_file.name == "VERSION.txt":
        continue
    df = pd.read_csv(csv_file)
    rows.append({
        "table_name": csv_file.stem,
        "type": "dimension" if csv_file.stem.startswith("dim_") else "fact" if csv_file.stem.startswith("fact_") else "qa",
        "rows": len(df),
        "columns": len(df.columns),
        "primary_key": df.columns[0],
        "column_list": ", ".join(df.columns[:5]) + ("..." if len(df.columns) > 5 else "")
    })
pd.DataFrame(rows).to_csv("docs/diagrams/TABLE_INVENTORY.csv", index=False)
print(f"Updated: {len(rows)} tables")
EOF
```

---

## STEP 5: Check for Broken Links

```bash
cd docs/html
# Verify all navigation links exist:
for f in index tables CHANGELOG DATA_DICTIONARY HONEST_ASSESSMENT KEY_FORMATS LLM_HANDOFF MODULE_REFERENCE pipeline_visualization VERIFICATION_STATUS; do
    [ -f "${f}.html" ] && echo "✓ ${f}.html" || echo "✗ ${f}.html MISSING"
done

# Check diagrams:
ls diagrams/ERD_VIEWER.html && echo "✓ ERD exists"
```

---

## STEP 6: Verify Table Counts

```bash
# Get actual counts:
echo "Total: $(ls data/output/*.csv | wc -l)"
echo "Dims:  $(ls data/output/dim_*.csv | wc -l)"
echo "Facts: $(ls data/output/fact_*.csv | wc -l)"
echo "QA:    $(ls data/output/qa_*.csv | wc -l)"
```

Update these counts in:
- LLM_REQUIREMENTS.md (Quick Reference)
- docs/VERSION.txt
- docs/html/index.html (stats grid + nav bar)
- All HTML nav bars

---

## STEP 7: Pre-Export Verification

```bash
# Run tests
python3 -m pytest tests/test_etl.py -v

# Verify ETL status
python -m src.etl_orchestrator status

# Check table count
ls data/output/*.csv | wc -l

# Verify key docs exist
ls LLM_REQUIREMENTS.md CHANGELOG.md README.md
ls docs/VERSION.txt docs/html/index.html
```

---

## Complete Update Checklist

Before every package export:

- [ ] LLM_REQUIREMENTS.md - version, counts, history
- [ ] CHANGELOG.md - new entry at top
- [ ] docs/VERSION.txt - version, date, counts
- [ ] Run: `python scripts/utilities/fix_all_html_docs.py`
- [ ] Verify: docs/html/index.html stats correct
- [ ] Verify: Navigation links work
- [ ] Update any changed .mermaid files
- [ ] Run tests: `pytest tests/test_etl.py -v`
- [ ] Verify table count: `ls data/output/*.csv | wc -l`

---

## Files Summary

### Root Level
```
LLM_REQUIREMENTS.md    # READ FIRST - all rules
CHANGELOG.md           # Version history
README.md              # Quick start
```

### docs/
```
VERSION.txt            # Version stamp
HONEST_ASSESSMENT.md   # Current status
LLM_HANDOFF.md         # AI guide
KEY_FORMATS.md         # Key conventions
FUTURE_ROADMAP.md      # Priorities
DATA_DICTIONARY.md     # Column defs
MISSING_TABLES.md      # Unbuilt tables
MODULE_REFERENCE.md    # Code docs
VERIFICATION_STATUS.md # QA status
column_metadata.json   # Column metadata
schema_diagram.mermaid # Schema
benchsight_data_flow.mermaid # ETL flow
```

### docs/diagrams/
```
ERD_COMPLETE.mermaid        # Full ERD
DATA_FLOW.mermaid           # Data flow
SCHEMA_RELATIONSHIPS.mermaid # Relationships
STAT_CATEGORIES.mermaid     # Stats tree
TABLE_INVENTORY.csv         # Table list
```

### docs/html/
```
index.html                  # Home page
tables.html                 # Table browser
tables/*.html               # Per-table docs
diagrams/ERD_VIEWER.html    # ERD viewer
pipeline_visualization.html # Pipeline
MODULE_REFERENCE.html       # Modules
KEY_FORMATS.html            # Keys
DATA_DICTIONARY.html        # Dictionary
HONEST_ASSESSMENT.html      # Assessment
LLM_HANDOFF.html            # LLM guide
FUTURE_ROADMAP.html         # Roadmap
CHANGELOG.html              # Changelog
VERIFICATION_STATUS.html    # QA
```

---

## Quick Commands

```bash
# Update HTML docs
python scripts/utilities/fix_all_html_docs.py

# Update table HTML
python scripts/utilities/generate_enhanced_table_docs.py

# Update TABLE_INVENTORY.csv
python3 -c "..." # (see script above)

# Run tests
python3 -m pytest tests/test_etl.py -v

# Check ETL status
python -m src.etl_orchestrator status

# Package
zip -r benchsight_v{VERSION}.zip benchsight_v{VERSION}/ -x "*.pyc" -x "*__pycache__*"
```

---

**END OF DOC_UPDATE_GUIDE.md**
