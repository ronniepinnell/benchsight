# BenchSight Project Scope

**Complete project scope definition**

Last Updated: 2026-01-15  
Version: 29.0

---

## Overview

This document defines the complete scope of the BenchSight project, including what's in scope, what's out of scope, component responsibilities, and success criteria.

---

## Project Vision

**Mission:** Build a comprehensive hockey analytics platform that makes game tracking fast and easy, provides advanced analytics, and scales to commercial SaaS for junior hockey teams.

**End Goal:**
1. Full-stack web application
2. Video recording support (multiple angles per game)
3. Easy-to-use game tracking application
4. Web admin portal for ETL management
5. Public dashboard with comprehensive analytics
6. Commercial multi-tenant SaaS for junior hockey teams
7. ML/CV integration for automated tracking

**Target Users:**
- Junior hockey teams and leagues
- Coaches and team managers
- Players and parents
- Analysts and scouts

---

## Component Scope

### ETL Pipeline

**In Scope:**
- Process game data from BLB tables and tracking files
- Generate 139 tables (dimensions, facts, QA)
- Calculate comprehensive stats (317 columns for players, 128 for goalies)
- Advanced metrics (Corsi, Fenwick, xG, WAR/GAR, QoC/QoT)
- Data validation and quality checks
- Supabase integration
- Formula management system
- Performance optimization (target: < 90 seconds for 4 games)

**Out of Scope (Current Phase):**
- Real-time data processing
- Incremental ETL (currently full rebuild)
- Automated ML feature engineering
- Multi-tenant data isolation

**Responsibilities:**
- Data ingestion from raw sources
- Data transformation and calculation
- Table generation
- Data validation
- Schema management

**Success Criteria:**
- 139 tables generated correctly
- All calculations accurate
- Validation passing
- Performance targets met

---

### Dashboard

**In Scope:**
- Public-facing analytics dashboard
- 50+ pages (players, teams, games, goalies, standings, leaders)
- Season and game type filtering
- Historical data support
- Responsive design
- Sortable tables
- Searchable dropdowns
- Enhanced visualizations (shot maps, charts)
- Live data connection to Supabase

**Out of Scope (Current Phase):**
- User authentication (future)
- Private/team-specific dashboards (future)
- Real-time updates (future)
- Mobile app (future)
- Advanced ML visualizations (future phase)

**Responsibilities:**
- Display analytics data
- Provide user interface for data exploration
- Visualize statistics
- Enable data filtering and search

**Success Criteria:**
- All pages functional
- Data loads correctly
- Performance targets met (< 2 seconds page load)
- Responsive design working

---

### Tracker

**In Scope (Current):**
- HTML/JavaScript tracker (v23.5)
- Event tracking (15+ event types)
- Shift tracking
- Video integration (HTML5, YouTube)
- XY positioning on rink
- Export to Excel
- Supabase sync capability

**In Scope (Planned):**
- Rust/Next.js conversion
- Feature parity with HTML tracker
- Improved performance
- Better state management
- Real-time collaboration (future)

**Out of Scope (Current Phase):**
- ML/CV integration (future phase)
- Mobile app (future)
- Offline mode (future)
- Multi-user real-time sync (future)

**Responsibilities:**
- Game event tracking
- Shift tracking
- Video synchronization
- Data export for ETL

**Success Criteria:**
- All features working
- Export format matches ETL expectations
- Performance acceptable
- User-friendly interface

---

### Portal

**In Scope:**
- Admin interface for ETL management
- ETL trigger functionality
- Job status monitoring
- Data upload interface
- Game management (future)
- Data browser (future)
- Team/coach administration (future)

**Out of Scope (Current Phase):**
- User authentication (future)
- Multi-tenant support (future)
- Advanced analytics (future)
- Real-time collaboration (future)

**Responsibilities:**
- ETL control and monitoring
- Data management
- System administration
- User management (future)

**Success Criteria:**
- ETL can be triggered via UI
- Job status visible
- Data upload working
- User-friendly interface

---

### API

**In Scope:**
- ETL endpoints (trigger, status, history)
- Upload endpoints (tables, schema)
- Staging endpoints (BLB, tracking)
- Health check
- Background job processing
- Job status tracking

**Out of Scope (Current Phase):**
- Game management endpoints (planned)
- Data browser endpoints (planned)
- Authentication endpoints (future)
- Real-time WebSocket (future)
- Rate limiting (future)

**Responsibilities:**
- Provide REST API for ETL operations
- Handle background jobs
- Manage job status
- Provide data upload interface

**Success Criteria:**
- All endpoints functional
- Performance targets met (< 200ms response)
- Error handling working
- Documentation complete

---

## Feature Scope

### In Scope (Current Phase)

**Data Processing:**
- ETL pipeline execution
- Table generation
- Data validation
- Supabase upload

**Analytics:**
- Player statistics
- Team statistics
- Game statistics
- Goalie statistics
- Advanced metrics (Corsi, Fenwick, xG, WAR/GAR)

**Visualization:**
- Tables and charts
- Shot maps
- Leaderboards
- Standings

**Tracking:**
- Event tracking
- Shift tracking
- Video integration
- XY positioning

**Administration:**
- ETL control
- Job monitoring
- Data upload

### Out of Scope (Current Phase)

**Future Features:**
- ML/CV integration
- Real-time collaboration
- Mobile applications
- Multi-tenancy
- User authentication
- Advanced predictive analytics
- Automated play detection
- Real-time game tracking

---

## Technical Scope

### Technologies

**In Scope:**
- Python 3.11+ (ETL)
- Next.js 14 (Dashboard, Portal)
- TypeScript (Frontend)
- FastAPI (API)
- Supabase (Database)
- PostgreSQL (Database)
- Tailwind CSS (Styling)
- shadcn/ui (UI Components)
- Recharts (Charts)

**Out of Scope (Current Phase):**
- Rust (Tracker conversion - planned)
- ML frameworks (future)
- Computer vision libraries (future)
- Mobile frameworks (future)

### Constraints

**Performance:**
- ETL: < 90 seconds for 4 games
- Dashboard: < 2 seconds page load
- API: < 200ms endpoint response

**Scalability:**
- Current: Single tenant
- Future: Multi-tenant (out of scope for now)

**Data:**
- Current: NORAD league data
- Future: Multi-league support (out of scope for now)

---

## Data Scope

### Data Sources

**In Scope:**
- BLB tables (Excel file)
- Tracking files (JSON per game)
- Supabase database

**Out of Scope:**
- External APIs (future)
- Real-time data feeds (future)
- Video processing (future phase)

### Data Outputs

**In Scope:**
- 139 tables (dimensions, facts, QA)
- Supabase database
- CSV files (intermediate)
- Excel exports (tracker)

**Out of Scope:**
- Real-time streams (future)
- External data exports (future)
- API data feeds (future)

---

## User Scope

### Target Users

**In Scope:**
- Analysts (primary)
- Coaches (secondary)
- Team managers (secondary)
- Players/parents (tertiary)

**Out of Scope (Current Phase):**
- General public (future)
- Multiple leagues (future)
- Commercial customers (future phase)

### Use Cases

**In Scope:**
- View player statistics
- View team statistics
- View game statistics
- Track games manually
- Run ETL pipeline
- Monitor ETL jobs

**Out of Scope (Current Phase):**
- Automated game tracking
- Real-time game updates
- Mobile game tracking
- Multi-user collaboration

---

## Timeline Scope

### Current Phase: Pre-Deployment & Data Collection

**Timeline:** Weeks 5-8  
**Focus:** Integration, polish, data collection

**Deliverables:**
- ETL cleanup and optimization
- Dashboard enhancements
- Portal API integration
- Documentation completion

### Next Phase: Advanced Analytics

**Timeline:** Weeks 9-12  
**Focus:** Advanced analytics, ML preparation

**Deliverables:**
- Complete xG analysis
- Complete WAR/GAR analysis
- RAPM analysis
- ML feature engineering

### Future Phases: Production & Scale

**Timeline:** Weeks 13-16+  
**Focus:** Production deployment, ML/CV integration

**Deliverables:**
- Production deployment
- ML/CV integration
- Multi-tenancy
- Commercial launch

---

## Success Criteria

### Functional Success

- [ ] All 139 tables generated correctly
- [ ] All calculations accurate
- [ ] All pages functional
- [ ] ETL can be triggered via API/Portal
- [ ] Tracker exports correct format
- [ ] Data validation passing

### Performance Success

- [ ] ETL: < 90 seconds for 4 games
- [ ] Dashboard: < 2 seconds page load
- [ ] API: < 200ms endpoint response
- [ ] No memory leaks
- [ ] Scalable architecture

### Quality Success

- [ ] Code coverage > 80% (critical functions)
- [ ] All tests passing
- [ ] Documentation complete
- [ ] No critical bugs
- [ ] Code maintainable

### User Success

- [ ] Users can view analytics
- [ ] Users can track games
- [ ] Users can run ETL
- [ ] Interface is intuitive
- [ ] Performance is acceptable

---

## Boundaries

### What's NOT in Scope

**Current Phase:**
- User authentication
- Multi-tenancy
- ML/CV integration
- Mobile applications
- Real-time collaboration
- External integrations
- Commercial features

**Future Phases:**
- These features are planned but not in current scope
- Will be added in future phases
- See [MASTER_ROADMAP.md](MASTER_ROADMAP.md) for timeline

---

## Dependencies

### External Dependencies

- Supabase (database hosting)
- Vercel (dashboard hosting)
- Railway/Render (API hosting)
- Python packages (ETL)
- Node.js packages (Dashboard)

### Internal Dependencies

- ETL → Dashboard (data flow)
- Tracker → ETL (data flow)
- Portal → API → ETL (control flow)
- API → Supabase (data flow)

---

## Constraints

### Technical Constraints

- Single database instance (Supabase)
- Python 3.11+ required
- Node.js 18+ required
- Browser compatibility (modern browsers)

### Business Constraints

- NORAD league data only (current)
- Single tenant (current)
- Manual tracking (current)
- No real-time updates (current)

---

## Related Documentation

- [MASTER_ROADMAP.md](MASTER_ROADMAP.md) - Project roadmap
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Current status
- [STRATEGIC_ASSESSMENT.md](STRATEGIC_ASSESSMENT.md) - Strategic assessment
- [MASTER_PROJECT_MANAGEMENT.md](MASTER_PROJECT_MANAGEMENT.md) - Project management

---

*Last Updated: 2026-01-15*
