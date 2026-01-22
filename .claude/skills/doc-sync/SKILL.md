---
name: doc-sync
description: Synchronize documentation with code changes. Detects outdated docs, generates updates, and ensures documentation stays current. Run after code changes.
allowed-tools: Bash, Read, Write, Grep, Glob
argument-hint: [check|update|generate]
---

# Documentation Sync

Keep documentation synchronized with code.

## Documentation Locations

| Type | Location | Update Trigger |
|------|----------|----------------|
| ETL docs | `docs/etl/` | src/calculations/, src/tables/ |
| Dashboard docs | `docs/dashboard/` | ui/dashboard/src/ |
| API docs | `docs/api/` | api/routes/, api/services/ |
| Data dictionary | `docs/data/` | Schema changes |
| Setup guides | `docs/setup/` | Dependencies, config |

## Sync Workflow

### 1. Detect Changes

```bash
# Get recently changed files
git diff --name-only HEAD~5

# Categorize changes
ETL_CHANGES=$(git diff --name-only HEAD~5 | grep "^src/")
DASHBOARD_CHANGES=$(git diff --name-only HEAD~5 | grep "^ui/dashboard/")
API_CHANGES=$(git diff --name-only HEAD~5 | grep "^api/")
```

### 2. Check Doc Freshness

```bash
# Find docs older than related code
for doc in docs/**/*.md; do
    # Get related code file
    code_file=$(extract_code_reference "$doc")
    if [ -f "$code_file" ]; then
        doc_time=$(stat -f %m "$doc")
        code_time=$(stat -f %m "$code_file")
        if [ $code_time -gt $doc_time ]; then
            echo "STALE: $doc (code: $code_file)"
        fi
    fi
done
```

### 3. Generate Updates

**For Python files:**
```bash
# Extract docstrings
python -c "
import ast
import sys

with open(sys.argv[1]) as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
        docstring = ast.get_docstring(node)
        if docstring:
            print(f'### {node.name}')
            print(docstring)
            print()
" "$file"
```

**For TypeScript files:**
```bash
# Extract JSDoc comments
grep -B1 -A10 '/\*\*' "$file"
```

### 4. Update Specific Docs

**ETL Calculation Docs:**
```markdown
## {function_name}

**File:** `src/calculations/{file}.py:{line}`

**Purpose:** {docstring}

**Parameters:**
{parameters}

**Returns:**
{return_type}

**Example:**
```python
{example}
```
```

**API Endpoint Docs:**
```markdown
## {method} {path}

**File:** `api/routes/{file}.py:{line}`

**Description:** {docstring}

**Request:**
```json
{request_schema}
```

**Response:**
```json
{response_schema}
```
```

## Auto-Update Rules

| Code Change | Doc Update |
|-------------|------------|
| New function in src/calculations/ | Add to docs/etl/calculations.md |
| New API endpoint | Add to docs/api/endpoints.md |
| New dashboard page | Add to docs/dashboard/pages.md |
| Schema change | Update docs/data/schema.md |
| New config option | Update docs/setup/configuration.md |

## Doc Templates

### Function Documentation
```markdown
## function_name

**Purpose:** Brief description

**Location:** `file/path.py:123`

**Parameters:**
- `param1` (type): Description
- `param2` (type): Description

**Returns:** type - Description

**Example:**
```python
result = function_name(arg1, arg2)
```

**Notes:**
- Important consideration 1
- Important consideration 2
```

### API Endpoint Documentation
```markdown
## METHOD /path/to/endpoint

**Purpose:** Brief description

**Authentication:** Required/Optional

**Request Body:**
```json
{
  "field": "type"
}
```

**Response:**
```json
{
  "field": "type"
}
```

**Errors:**
- 400: Bad request
- 401: Unauthorized
- 500: Server error
```

## Output

Report format:
```
DOC SYNC REPORT
===============
Checked: 47 documentation files
Updated: 3 files
  - docs/etl/calculations.md (new function)
  - docs/api/endpoints.md (new endpoint)
  - docs/data/schema.md (column added)
Stale: 2 files (manual review needed)
  - docs/dashboard/components.md
  - docs/setup/installation.md
```
