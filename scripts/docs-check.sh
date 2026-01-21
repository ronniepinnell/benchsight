#!/bin/bash
# =============================================================================
# Documentation Consistency Check
# =============================================================================
# Check documentation for broken links, outdated content, etc.
# =============================================================================

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

ERRORS=0
WARNINGS=0

print_header "Documentation Consistency Check"

# Check for broken markdown links
print_info "Checking for broken markdown links..."

find docs -name "*.md" -type f | while read -r file; do
    # Extract markdown links
    grep -o '\[.*\](.*)' "$file" | sed 's/.*(\(.*\))/\1/' | while read -r link; do
        # Skip external links
        if [[ $link == http* ]]; then
            continue
        fi
        
        # Skip anchor links
        if [[ $link == \#* ]]; then
            continue
        fi
        
        # Check if file exists
        LINK_FILE=$(dirname "$file")/$link
        if [ ! -f "$LINK_FILE" ] && [ ! -d "$LINK_FILE" ]; then
            print_error "Broken link in $file: $link"
            ((ERRORS++)) || true
        fi
    done
done

# Check for outdated "Last Updated" dates (older than 3 months)
print_info "Checking for outdated documentation..."

THREE_MONTHS_AGO=$(date -v-3m +%Y-%m-%d 2>/dev/null || date -d "3 months ago" +%Y-%m-%d)

find docs -name "*.md" -type f | while read -r file; do
    if grep -q "Last Updated:" "$file"; then
        LAST_UPDATED=$(grep "Last Updated:" "$file" | sed 's/.*Last Updated: *//' | head -1)
        if [ -n "$LAST_UPDATED" ]; then
            if [[ "$LAST_UPDATED" < "$THREE_MONTHS_AGO" ]]; then
                print_warning "Potentially outdated: $file (Last Updated: $LAST_UPDATED)"
                ((WARNINGS++)) || true
            fi
        fi
    fi
done

# Check for missing master index entries
print_info "Checking master index..."

if [ -f "docs/MASTER_INDEX.md" ]; then
    # Get all markdown files in docs
    find docs -name "*.md" -type f | while read -r file; do
        FILE_NAME=$(basename "$file")
        if ! grep -q "$FILE_NAME" docs/MASTER_INDEX.md; then
            print_warning "File not in master index: $file"
            ((WARNINGS++)) || true
        fi
    done
else
    print_error "Master index not found: docs/MASTER_INDEX.md"
    ((ERRORS++)) || true
fi

# Check for duplicate documentation
print_info "Checking for potential duplicates..."

# This is a simple check - could be enhanced
find docs -name "*.md" -type f | while read -r file; do
    FILE_NAME=$(basename "$file" .md)
    COUNT=$(find docs -name "${FILE_NAME}.md" -type f | wc -l)
    if [ "$COUNT" -gt 1 ]; then
        print_warning "Potential duplicate: $FILE_NAME.md (found $COUNT times)"
        ((WARNINGS++)) || true
    fi
done

# Summary
echo ""
print_header "Summary"

if [ "$ERRORS" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
    print_success "All checks passed!"
    exit 0
elif [ "$ERRORS" -eq 0 ]; then
    print_warning "Found $WARNINGS warning(s)"
    exit 0
else
    print_error "Found $ERRORS error(s) and $WARNINGS warning(s)"
    exit 1
fi
