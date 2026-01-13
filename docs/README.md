# BenchSight Documentation Index

**Complete guide to all BenchSight documentation**

Last Updated: 2026-01-13

**Note:** Temporary handoff documents have been moved to `docs/archive/`. See `docs/archive/README.md` for details.

---

## 🚀 Getting Started

**New users should read these first:**

1. **[QUICK_START.md](QUICK_START.md)** - Get running in 5 minutes
2. **[SETUP.md](SETUP.md)** - Complete installation and configuration
3. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Understand the system design

---

## 📖 Core Documentation

### System Overview
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design, data flow, and architecture
- **[ETL.md](ETL.md)** - ETL pipeline details and phases
- **[DATA_DICTIONARY.md](DATA_DICTIONARY.md)** - Complete table and column definitions
- **[DATA_LINEAGE.md](DATA_LINEAGE.md)** - Data lineage and dependencies

### Development
- **[CODE_STANDARDS.md](CODE_STANDARDS.md)** - Coding standards and best practices
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute to the project
- **[MAINTENANCE.md](MAINTENANCE.md)** - Maintenance procedures and checklists
- **[HANDOFF.md](HANDOFF.md)** - Continuity between development sessions

### Deployment & Integration
- **[SUPABASE.md](SUPABASE.md)** - Supabase setup and configuration
- **[SUPABASE_RESET_GAMEPLAN.md](SUPABASE_RESET_GAMEPLAN.md)** - Step-by-step Supabase deployment
- **[SUPABASE_UPDATE.md](SUPABASE_UPDATE.md)** - Supabase update procedures
- **[NEXTJS_DASHBOARD_GUIDE.md](NEXTJS_DASHBOARD_GUIDE.md)** - Next.js 14 dashboard implementation
- **[DASHBOARD_INTEGRATION.md](DASHBOARD_INTEGRATION.md)** - Dashboard integration guide

---

## 📊 Data Documentation

### Data Definitions
- **[DATA_DICTIONARY.md](DATA_DICTIONARY.md)** - Complete table/column reference
- **[DATA_DICTIONARY_FULL.md](DATA_DICTIONARY_FULL.md)** - Auto-generated full dictionary (enhanced with code extraction)
- **[SRC_MODULES_GUIDE.md](SRC_MODULES_GUIDE.md)** - Complete guide to all src/ modules, data flow, and where to update code
- **[TABLE_INVENTORY.md](TABLE_INVENTORY.md)** - Table inventory and counts
- **[TABLE_MANIFEST.md](TABLE_MANIFEST.md)** - Table manifest and metadata

### Validation
- **[VALIDATION.md](VALIDATION.md)** - Validation procedures
- **[VALIDATION_PLAN.md](VALIDATION_PLAN.md)** - Validation strategy
- **[VALIDATION_FINDINGS.md](VALIDATION_FINDINGS.md)** - Validation results
- **[VALIDATION_LOG.md](VALIDATION_LOG.md)** - Validation history

### Data Quality
- **[TRACKING_ERRORS.md](TRACKING_ERRORS.md)** - Known tracking errors
- **[GOALIE_STATS_LIMITATIONS.md](GOALIE_STATS_LIMITATIONS.md)** - Goalie stats limitations

---

## 🎯 Domain-Specific Documentation

### Hockey Analytics
- **[RUSH_DEFINITIONS.md](RUSH_DEFINITIONS.md)** - Rush event definitions
- **[RUSH_TERMINOLOGY.md](RUSH_TERMINOLOGY.md)** - Rush terminology
- **[TRACKER_DROPDOWN_MAP.md](TRACKER_DROPDOWN_MAP.md)** - Tracker dropdown mappings

### Calculations
- **[CALCULATION_LOG.md](CALCULATION_LOG.md)** - Calculation history and changes
- **[FUTURE_COLUMNS.md](FUTURE_COLUMNS.md)** - Planned future columns

---

## 📝 Project Management

- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes
- **[TODO.md](TODO.md)** - Current tasks and priorities
- **[ROADMAP.md](ROADMAP.md)** - Future development roadmap
- **[HONEST_ASSESSMENT.md](HONEST_ASSESSMENT.md)** - Project assessment
- **[HONEST_OPINIONS.md](HONEST_OPINIONS.md)** - Development opinions

---

## 🔧 Technical Reference

### Code Documentation
- **[SRC_MANIFEST.md](SRC_MANIFEST.md)** - Source code manifest
- **[CODE_STANDARDS.md](CODE_STANDARDS.md)** - Coding standards

### SQL Reference
- See `../sql/` directory for SQL scripts
- **[sql/views/VIEW_CATALOG.md](../sql/views/VIEW_CATALOG.md)** - View documentation

### Cleanup & Audit
- **[CLEANUP_AUDIT.md](CLEANUP_AUDIT.md)** - Code cleanup audit

---

## 📁 Documentation Structure

```
docs/
├── README.md (this file)          # Documentation index
├── QUICK_START.md                  # 5-minute quick start
├── SETUP.md                        # Installation guide
├── ARCHITECTURE.md                 # System design
├── ETL.md                          # ETL pipeline
├── DATA_DICTIONARY.md              # Table definitions
├── CODE_STANDARDS.md               # Coding standards
├── CONTRIBUTING.md                 # Contribution guide
├── CHANGELOG.md                    # Version history
├── TODO.md                         # Current tasks
├── validated_tables/               # Validated table docs
├── html/                           # Generated HTML docs
└── archive/                        # Archived temporary/handoff docs
```

---

## 🔍 Finding What You Need

### "How do I..."
- **Set up the project?** → [SETUP.md](SETUP.md)
- **Run the ETL?** → [QUICK_START.md](QUICK_START.md) or [ETL.md](ETL.md)
- **Understand the architecture?** → [ARCHITECTURE.md](ARCHITECTURE.md)
- **Find table definitions?** → [DATA_DICTIONARY.md](DATA_DICTIONARY.md)
- **Contribute code?** → [CONTRIBUTING.md](CONTRIBUTING.md)
- **Deploy to Supabase?** → [SUPABASE_RESET_GAMEPLAN.md](SUPABASE_RESET_GAMEPLAN.md)
- **Build the dashboard?** → [NEXTJS_DASHBOARD_GUIDE.md](NEXTJS_DASHBOARD_GUIDE.md)

### "What is..."
- **A rush event?** → [RUSH_DEFINITIONS.md](RUSH_DEFINITIONS.md)
- **The goal counting rule?** → [CODE_STANDARDS.md](CODE_STANDARDS.md) (Critical Rules section)
- **The current version?** → [CHANGELOG.md](CHANGELOG.md)
- **The project status?** → [TODO.md](TODO.md) and [ROADMAP.md](ROADMAP.md)

### "I need to..."
- **Fix a bug** → [CODE_STANDARDS.md](CODE_STANDARDS.md) and [CONTRIBUTING.md](CONTRIBUTING.md)
- **Add a feature** → [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_STANDARDS.md](CODE_STANDARDS.md)
- **Validate data** → [VALIDATION.md](VALIDATION.md)
- **Update documentation** → [CONTRIBUTING.md](CONTRIBUTING.md) (Documentation section)

---

## 📚 Documentation Standards

All documentation should:
- Be clear and concise
- Include code examples where helpful
- Cross-reference related documents
- Update "Last Updated" dates when changed
- Follow consistent formatting

---

## 🔄 Keeping Documentation Current

**When to update docs:**
- Adding new features → Update relevant docs + CHANGELOG.md
- Changing behavior → Update affected docs
- Fixing bugs → Update known issues in HANDOFF.md
- Improving clarity → Update any relevant docs

**Documentation checklist:**
- [ ] Updated relevant documentation files
- [ ] Updated CHANGELOG.md (if significant)
- [ ] Updated "Last Updated" dates
- [ ] Added cross-references
- [ ] Verified links work

---

## 💡 Tips

1. **Start with Quick Start** - Don't skip the basics
2. **Read Architecture** - Understand the system before diving in
3. **Check CODE_STANDARDS** - Follow the rules, especially goal counting
4. **Use Search** - Most docs are searchable
5. **Check CHANGELOG** - See what changed recently

---

*Last updated: 2026-01-13*
