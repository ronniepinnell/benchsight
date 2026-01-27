---
name: ui-ux-design
description: Design and improve UI/UX for BenchSight dashboard, portal, and tracker. Use when planning new pages, improving layouts, or ensuring design consistency.
allowed-tools: Read, Write, WebSearch, WebFetch
argument-hint: [component|page|flow]
---

# UI/UX Design

Design and improve BenchSight user interfaces.

## Design System

### Current Stack
- **Framework:** Next.js 14 + React 18
- **Styling:** Tailwind CSS
- **Components:** shadcn/ui
- **Charts:** Recharts
- **Icons:** Lucide React

### Design Tokens

**Colors (from Tailwind):**
```css
--primary: Hockey blue
--secondary: Ice white
--accent: Goal red
--background: Dark slate
--foreground: Light text
```

**Typography:**
- Headings: Inter/System
- Body: Inter/System
- Mono: JetBrains Mono (stats)

## Component Patterns

### Dashboard Cards
```tsx
<Card>
  <CardHeader>
    <CardTitle>Stat Name</CardTitle>
    <CardDescription>Context</CardDescription>
  </CardHeader>
  <CardContent>
    {/* Data visualization */}
  </CardContent>
</Card>
```

### Data Tables
```tsx
<DataTable
  columns={columns}
  data={data}
  sorting
  filtering
  pagination
/>
```

### Charts
```tsx
<ResponsiveContainer>
  <LineChart data={data}>
    <XAxis dataKey="date" />
    <YAxis />
    <Tooltip />
    <Line dataKey="value" />
  </LineChart>
</ResponsiveContainer>
```

## Page Templates

### List Page (Players, Games)
- Header with title and filters
- Search bar
- Sortable data table
- Pagination
- Export button

### Detail Page (Player Profile)
- Hero section with key stats
- Tab navigation
- Multiple stat sections
- Related content sidebar

### Comparison Page
- Multi-select players
- Side-by-side stats
- Visual comparisons
- Export options

## UX Principles

1. **Data-first:** Show important stats prominently
2. **Progressive disclosure:** Summary → detail
3. **Consistent navigation:** Same patterns everywhere
4. **Fast interactions:** < 100ms feedback
5. **Mobile-friendly:** Responsive at all breakpoints

## Design Process

1. Research competitors: `/competitive-research`
2. Sketch wireframes
3. Build with shadcn components
4. Test with real data
5. Iterate based on feedback

## Output

Design specs go to:
```
docs/design/{component}-spec.md
```

Include:
- Wireframe description
- Component breakdown
- Data requirements
- Interaction patterns
- Responsive behavior
