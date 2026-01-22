---
name: competitive-research
description: Research competitor hockey analytics platforms (ESPN, NHL, MoneyPuck, Natural Stat Trick, Elite Prospects) for feature ideas, UI patterns, and market positioning. Use when planning new features or improving existing ones.
allowed-tools: WebSearch, WebFetch, Read, Write
argument-hint: [platform|feature|comparison]
---

# Competitive Research

Research competitor platforms to inform BenchSight development.

## Key Competitors

### Tier 1: Major Platforms
| Platform | Focus | Strengths |
|----------|-------|-----------|
| **NHL.com/Stats** | Official stats | Authority, real-time, video |
| **ESPN Hockey** | Mass market | UX, mobile, integration |
| **The Athletic** | Premium content | Analysis, writing, depth |

### Tier 2: Analytics Specialists
| Platform | Focus | Strengths |
|----------|-------|-----------|
| **MoneyPuck** | Advanced analytics | xG models, predictions |
| **Natural Stat Trick** | Shot data | Heat maps, situational |
| **Evolving Hockey** | WAR/GAR models | Player value metrics |
| **Hockey Reference** | Historical | Completeness, search |

### Tier 3: Scouting/Tracking
| Platform | Focus | Strengths |
|----------|-------|-----------|
| **Elite Prospects** | Scouting | Player profiles, history |
| **InStat** | Video analysis | Professional tracking |
| **Sportlogiq** | Enterprise | ML, tracking data |

## Research Commands

**Platform deep-dive:**
```
/competitive-research ESPN hockey stats page
```

**Feature comparison:**
```
/competitive-research player comparison tools
```

**UI/UX patterns:**
```
/competitive-research dashboard layouts
```

## Research Areas

### 1. Data Visualization
- Shot charts and heat maps
- Player comparison tools
- Game flow visualizations
- Statistical tables

### 2. User Experience
- Navigation patterns
- Mobile responsiveness
- Filter/search functionality
- Data export options

### 3. Features
- Real-time updates
- Video integration
- Custom reports
- API access

### 4. Monetization
- Subscription tiers
- Premium features
- API pricing
- Advertising

## Output Format

Create research notes in:
```
docs/research/competitive/{platform}-analysis.md
```

Include:
- Screenshots (describe, don't include)
- Feature inventory
- UX observations
- Differentiation opportunities
- Ideas for BenchSight
