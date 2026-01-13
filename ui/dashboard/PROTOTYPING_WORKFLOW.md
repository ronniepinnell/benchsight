# Dashboard Prototyping & Design Iteration Workflow

A practical guide for rapidly prototyping, designing, and iterating on dashboard features.

## 🎯 Philosophy

**Start fast, iterate quickly, validate with data.**

1. **Prototype** - Get something working in 15 minutes
2. **Design** - Polish the visual design
3. **Iterate** - Refine based on usage and feedback
4. **Promote** - Move successful prototypes to production

---

## 📋 Workflow: Prototype → Design → Iterate

### Phase 1: Rapid Prototyping (15-30 min)

**Goal:** Get data on screen quickly, test the concept

```bash
# 1. Create new prototype
./scripts/create-dashboard-page.sh analytics/shot-heatmap

# 2. Open in browser
# http://localhost:3000/prototypes/analytics/shot-heatmap
```

**What to build:**
- ✅ Fetch data from Supabase
- ✅ Display raw data (table or simple cards)
- ✅ Basic layout
- ❌ Don't worry about styling yet
- ❌ Don't optimize queries yet

**Example:**
```tsx
export default async function ShotHeatmap() {
  const supabase = await createClient()
  const { data } = await supabase
    .from('fact_events')
    .select('*')
    .eq('event_type', 'Shot')
    .limit(100)
  
  return (
    <PrototypeTemplate title="Shot Heatmap">
      {/* Just get data showing */}
      <pre>{JSON.stringify(data?.slice(0, 5), null, 2)}</pre>
    </PrototypeTemplate>
  )
}
```

**Questions to answer:**
- Does the data exist?
- Is it in the right format?
- What insights are visible?

---

### Phase 2: Design & Visualize (30-60 min)

**Goal:** Make it look good and communicate insights

**Design Principles:**
1. **Use your design system** - Colors, typography, spacing
2. **Hockey color coding:**
   - `text-goal` - Goals, losses, negative
   - `text-assist` - Assists, positive metrics
   - `text-save` - Saves, wins, positive
   - `text-shot` - Shots, attempts
3. **Visual hierarchy:**
   - Most important = largest, most prominent
   - Use cards to group related info
   - White space is your friend

**Design Checklist:**
- [ ] Use `PrototypeTemplate` for consistent header
- [ ] Use `StatCard` for key metrics
- [ ] Use `PrototypeTable` for tabular data
- [ ] Add charts with Recharts
- [ ] Apply hockey color coding
- [ ] Test on mobile (responsive)

**Example:**
```tsx
// After prototyping, add design
<div className="grid grid-cols-1 md:grid-cols-4 gap-4">
  <StatCard 
    label="Total Shots" 
    value={totalShots} 
    icon={Target}
    color="text-shot"
  />
</div>

<div className="bg-card rounded-xl border border-border p-6">
  <h2 className="font-display text-lg font-semibold mb-4">Shot Locations</h2>
  <ResponsiveContainer width="100%" height={400}>
    <ScatterChart data={shotData}>
      {/* Chart config */}
    </ScatterChart>
  </ResponsiveContainer>
</div>
```

---

### Phase 3: Iterate & Refine (Ongoing)

**Goal:** Improve based on usage and feedback

**Iteration Loop:**
1. **Use it** - Actually use the prototype
2. **Identify pain points:**
   - What's confusing?
   - What's missing?
   - What's too slow?
3. **Make one change** - Don't change everything
4. **Test again** - Does it feel better?
5. **Repeat**

**Common Iterations:**
- **Performance:** Add caching, optimize queries
- **UX:** Add filters, sorting, search
- **Visual:** Refine colors, spacing, typography
- **Data:** Add more metrics, different views
- **Interactivity:** Add hover states, tooltips

**Example Iteration:**
```tsx
// V1: Static data
const { data } = await supabase.from('v_standings').select('*')

// V2: Add filtering
const [selectedSeason, setSelectedSeason] = useState('current')
const { data } = await supabase
  .from('v_standings')
  .select('*')
  .eq('season_id', selectedSeason)

// V3: Add sorting
const [sortBy, setSortBy] = useState('standing')
const { data } = await supabase
  .from('v_standings')
  .select('*')
  .order(sortBy, { ascending: true })
```

---

## 🗂️ Organizing Prototypes

### Directory Structure

```
src/app/(dashboard)/prototypes/
├── analytics/          # Analytics & insights
│   ├── shot-heatmap/
│   ├── shift-analysis/
│   └── momentum/
├── visualizations/     # Charts & graphs
│   ├── player-radar/
│   ├── team-comparison/
│   └── trend-analysis/
├── experiments/        # Wild ideas
│   ├── ai-insights/
│   └── predictive/
└── examples/          # Reference implementations
    └── example/
```

### Naming Convention

- Use kebab-case: `shot-heatmap`, not `shotHeatmap`
- Be descriptive: `player-comparison-radar` not `radar`
- Group by category: `analytics/`, `visualizations/`

---

## 🎨 Design System Quick Reference

### Colors

```tsx
// Hockey-specific
text-goal      // Goals, losses, negative
text-assist    // Assists, positive metrics  
text-save      // Saves, wins, positive
text-shot      // Shots, attempts
text-hit       // Hits
text-penalty   // Penalties
text-faceoff   // Faceoffs

// System colors
text-primary   // Primary accent
text-muted     // Secondary text
bg-card        // Card background
bg-muted       // Muted background
border-border  // Borders
```

### Typography

```tsx
font-display   // Headings (Rajdhani)
font-mono      // Numbers, stats (JetBrains Mono)
text-2xl       // Large headings
text-sm        // Body text
text-xs        // Labels, captions
```

### Spacing

```tsx
space-y-6      // Vertical spacing between sections
gap-4          // Grid gaps
p-6            // Card padding
p-4            // Smaller padding
```

### Components

```tsx
// Page wrapper
<PrototypeTemplate title="..." description="...">

// Metrics
<StatCard label="..." value={...} icon={...} />

// Tables
<PrototypeTable data={...} columns={...} />

// Cards
<div className="bg-card rounded-xl border border-border p-6">
```

---

## 🚀 Rapid Prototyping Techniques

### 1. Start with Mock Data

```tsx
// Quick mock data to test layout
const mockData = [
  { name: 'Team A', wins: 10, losses: 5 },
  { name: 'Team B', wins: 8, losses: 7 },
]

// Replace with real data later
const { data } = await supabase.from('...').select('*')
```

### 2. Use Console Logging

```tsx
const { data } = await supabase.from('...').select('*')
console.log('Data shape:', data?.[0]) // See structure
console.log('Count:', data?.length)   // See volume
```

### 3. Build Incrementally

```tsx
// Step 1: Get data
const { data } = await supabase.from('...').select('*')

// Step 2: Show raw data
<pre>{JSON.stringify(data, null, 2)}</pre>

// Step 3: Add table
<PrototypeTable data={data} columns={...} />

// Step 4: Add chart
<BarChart data={data} />

// Step 5: Add styling
// Polish colors, spacing, etc.
```

### 4. Copy & Modify

```bash
# Copy existing prototype
cp -r src/app/(dashboard)/prototypes/example \
       src/app/(dashboard)/prototypes/my-new-prototype

# Modify as needed
```

---

## 📊 Chart Selection Guide

**When to use what:**

| Chart Type | Use For | Example |
|------------|---------|---------|
| **Bar Chart** | Comparing categories | Team wins, player goals |
| **Line Chart** | Trends over time | Season progression, game-by-game |
| **Scatter Plot** | Relationships | Shot location, xG vs goals |
| **Radar Chart** | Multi-dimensional comparison | Player skill profiles |
| **Heatmap** | Density/patterns | Shot locations, shift zones |
| **Pie/Donut** | Proportions | Shot types, zone distribution |

**Recharts Examples:**
```tsx
// Bar Chart
<BarChart data={data}>
  <Bar dataKey="wins" fill="hsl(var(--save))" />
</BarChart>

// Line Chart
<LineChart data={data}>
  <Line dataKey="points" stroke="hsl(var(--primary))" />
</LineChart>

// Scatter Plot
<ScatterChart data={data}>
  <Scatter dataKey="x" dataKey="y" />
</ScatterChart>
```

---

## ✅ Promotion Checklist

**When a prototype is ready to become a real page:**

- [ ] Data queries are optimized
- [ ] Error handling is in place
- [ ] Loading states implemented
- [ ] Responsive design tested
- [ ] Performance is acceptable
- [ ] Design matches system standards
- [ ] Added to sidebar navigation
- [ ] Moved from `/prototypes/` to main routes

**Promotion Process:**
```bash
# 1. Move from prototypes to main
mv src/app/(dashboard)/prototypes/shot-heatmap \
   src/app/(dashboard)/analytics/shot-heatmap

# 2. Update sidebar
# Add to main navigation in sidebar.tsx

# 3. Remove prototype badge/indicator
# Update page title, remove "Prototype" label
```

---

## 🎯 Weekly Prototyping Schedule

**Monday:** New ideas - Create 2-3 quick prototypes
**Tuesday-Thursday:** Design & refine - Pick best, polish it
**Friday:** Review & promote - Move successful ones to production

**Goal:** 1-2 new features per week

---

## 💡 Prototyping Ideas

**Analytics:**
- Shot heatmaps by zone
- Shift analysis
- Momentum tracking
- Player usage charts
- Line combination effectiveness

**Visualizations:**
- Player radar charts
- Team comparison matrices
- Game flow diagrams
- Season progression graphs
- Head-to-head breakdowns

**Experiments:**
- AI-powered insights
- Predictive models
- Advanced filtering
- Custom dashboards
- Real-time updates

---

## 🔧 Tools & Resources

**Design:**
- Tailwind CSS (already set up)
- Lucide Icons (already installed)
- Recharts (already installed)

**Development:**
- Next.js hot reload (instant feedback)
- TypeScript (type safety)
- Supabase (real data)

**Inspiration:**
- Look at existing pages (`/standings`, `/leaders`)
- Check example prototype (`/prototypes/example`)
- Review design system colors and components

---

## 📝 Prototype Template

```tsx
// src/app/(dashboard)/prototypes/[name]/page.tsx
import { PrototypeTemplate, StatCard } from '@/components/prototypes/prototype-template'
import { createClient } from '@/lib/supabase/server'

export default async function MyPrototype() {
  // 1. Fetch data
  const supabase = await createClient()
  const { data } = await supabase.from('...').select('*')
  
  // 2. Calculate metrics
  const total = data?.length || 0
  
  // 3. Render
  return (
    <PrototypeTemplate title="My Prototype">
      {/* Stat cards */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard label="Total" value={total} />
      </div>
      
      {/* Visualizations */}
      <div className="bg-card rounded-xl border border-border p-6">
        {/* Your content */}
      </div>
    </PrototypeTemplate>
  )
}
```

---

## 🎓 Best Practices

1. **One prototype = one idea** - Don't mix concepts
2. **Use real data** - Mock data hides problems
3. **Test early** - Show others, get feedback
4. **Keep it simple** - Start minimal, add complexity later
5. **Document decisions** - Add comments explaining why
6. **Delete failures** - Don't keep everything
7. **Promote successes** - Move good ones to production

---

**Remember:** Prototyping is about speed and learning. Don't perfect it, just get it working and iterate!
