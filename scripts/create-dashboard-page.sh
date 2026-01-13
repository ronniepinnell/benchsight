#!/bin/bash
# =============================================================================
# Create a new dashboard prototype page
# =============================================================================
# Usage: ./scripts/create-dashboard-page.sh <page-name>
# Example: ./scripts/create-dashboard-page.sh analytics/shot-analysis
# =============================================================================

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <page-name>"
  echo "Example: $0 analytics/shot-analysis"
  exit 1
fi

PAGE_NAME="$1"
DASHBOARD_DIR="ui/dashboard"
PAGE_DIR="${DASHBOARD_DIR}/src/app/(dashboard)/prototypes/${PAGE_NAME}"
PAGE_FILE="${PAGE_DIR}/page.tsx"

# Create directory
mkdir -p "$PAGE_DIR"

# Create page file
cat > "$PAGE_FILE" << 'EOF'
// src/app/(dashboard)/prototypes/[page-name]/page.tsx
import { PrototypeTemplate, StatCard } from '@/components/prototypes/prototype-template'
import { createClient } from '@/lib/supabase/server'
import { BarChart3 } from 'lucide-react'

export const revalidate = 300

export const metadata = {
  title: 'Prototype | BenchSight',
  description: 'Dashboard prototype',
}

export default async function PrototypePage() {
  const supabase = await createClient()
  
  // Example: Fetch data
  // const { data } = await supabase
  //   .from('v_standings_current')
  //   .select('*')
  //   .order('standing', { ascending: true })

  return (
    <PrototypeTemplate 
      title="Prototype Page" 
      description="Quick prototype for testing new visualizations"
    >
      {/* Example stat cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard 
          label="Example Stat" 
          value={0} 
          icon={BarChart3}
        />
      </div>

      {/* Your prototype content here */}
      <div className="bg-card rounded-xl border border-border p-6">
        <p className="text-muted-foreground">Start prototyping here!</p>
      </div>
    </PrototypeTemplate>
  )
}
EOF

# Replace placeholder with actual page name
PAGE_TITLE=$(echo "$PAGE_NAME" | sed 's/\// /g' | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1')
sed -i '' "s/Prototype Page/${PAGE_TITLE}/g" "$PAGE_FILE"

echo "✅ Created prototype page: ${PAGE_FILE}"
echo ""
echo "Next steps:"
echo "1. Edit: ${PAGE_FILE}"
echo "2. Add to sidebar: ui/dashboard/src/components/layout/sidebar.tsx"
echo "3. Visit: http://localhost:3000/prototypes/${PAGE_NAME}"
echo ""
