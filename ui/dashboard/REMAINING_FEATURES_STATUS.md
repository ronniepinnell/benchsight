# Remaining Features Status

**Last Updated:** 2026-01-15

## ✅ Completed Features

### CSV Export
- ✅ CSV export utility (`lib/export/csv.ts`)
- ✅ Export button component (`components/export/ExportButton.tsx`)
- ✅ Players table with export (`components/players/players-table-export.tsx`)
- ✅ Players page updated with export

### Team Tabs Component
- ✅ Team tabs component created (`components/teams/team-tabs.tsx`)

## 🚧 In Progress

### CSV Export (Continue)
- [ ] Add export to goalies page
- [ ] Add export to teams page
- [ ] Add export to analytics pages
- [ ] Add export to leaderboards

### Team Pages Enhancement
- [ ] Add tab navigation to team page
- [ ] Create Lines tab component (team-specific line combinations)
- [ ] Create Analytics tab component (zone time, WOWY)
- [ ] Create Matchups tab component (H2H records)
- [ ] Update team page to use tabs

## 📋 To Do

### Goalie Pages Enhancement
- [ ] Add Saves Detail tab to goalie profile
- [ ] Add Advanced Metrics breakdown tab
- [ ] Enhance goalie profile with save-by-save data

### Search & Filters
- [ ] Add search bar to players page
- [ ] Add filter dropdowns (position, team, season, min GP)
- [ ] Add search to goalies page
- [ ] Add search to teams page
- [ ] Add sortable columns where missing

### Shift Charts
- [ ] Create shift timeline component
- [ ] Add to game detail pages
- [ ] Visualize shift patterns
- [ ] Show shift duration and events

### Matchup/H2H Analysis
- [ ] Create player vs player matchup page
- [ ] Create team vs team H2H page
- [ ] Display matchup statistics
- [ ] Show head-to-head records

### Quality of Competition (QoC)
- [ ] Add QoC metrics to player profiles
- [ ] Create QoC analysis dashboard
- [ ] Display competition tier breakdowns

### Shot Chains Analysis
- [ ] Create shot sequence visualization
- [ ] Build shot chains dashboard
- [ ] Analyze shot patterns

### Enhanced Visualizations
- [ ] Network graphs for line combinations
- [ ] Heat maps for zone time
- [ ] Sankey diagrams for zone transitions
- [ ] Advanced chart types

## 📝 Notes

- All features should follow existing design patterns
- Use consistent component structure
- Add export buttons to all data tables
- Ensure responsive design
- Add proper error handling
