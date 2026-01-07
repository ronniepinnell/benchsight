#!/usr/bin/env python3
"""
Update All HTML Documentation - BenchSight v12.03
Consolidates, updates, and links all HTML documentation.
"""

from pathlib import Path
from datetime import datetime

VERSION = "12.03"
DATE = "January 7, 2026"
TABLES_COUNT = 62
GAMES_COUNT = 4
DIMS_COUNT = 34
FACTS_COUNT = 25
QA_COUNT = 2

HTML_DIR = Path("docs/html")
DOCS_DIR = Path("docs")

# Common HTML header
def get_header(title, nav_active=""):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - BenchSight v{VERSION}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f8f9fa; color: #333; line-height: 1.6; }}
        .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #4a4e69 100%); color: white; padding: 25px 40px; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .header .version {{ background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 15px; font-size: 12px; margin-left: 10px; }}
        .nav {{ background: #4a4e69; padding: 0 40px; display: flex; flex-wrap: wrap; }}
        .nav a {{ color: white; text-decoration: none; padding: 12px 18px; font-size: 14px; font-weight: 500; }}
        .nav a:hover {{ background: rgba(255,255,255,0.1); }}
        .nav a.active {{ background: rgba(255,255,255,0.2); }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 30px; }}
        h1, h2, h3 {{ color: #1a1a2e; }}
        h2 {{ border-bottom: 2px solid #4a4e69; padding-bottom: 8px; margin-top: 40px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #4a4e69; color: white; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        code {{ background: #e9ecef; padding: 2px 6px; border-radius: 3px; font-family: 'Consolas', monospace; font-size: 0.9em; }}
        pre {{ background: #2d2d2d; color: #f8f8f2; padding: 20px; border-radius: 8px; overflow-x: auto; }}
        pre code {{ background: transparent; color: inherit; }}
        a {{ color: #4a4e69; }}
        .card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 20px 0; }}
        .card h3 {{ margin-top: 0; color: #1a1a2e; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
        .alert {{ padding: 15px 20px; border-radius: 8px; margin: 20px 0; }}
        .alert-info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
        .alert-warning {{ background: #fff3cd; color: #856404; border: 1px solid #ffc107; }}
        .alert-success {{ background: #d4edda; color: #155724; border: 1px solid #28a745; }}
        .badge {{ display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }}
        .badge-green {{ background: #28a745; color: white; }}
        .badge-blue {{ background: #007bff; color: white; }}
        .badge-yellow {{ background: #ffc107; color: #333; }}
        .badge-red {{ background: #dc3545; color: white; }}
        .mermaid {{ background: white; padding: 20px; border-radius: 8px; overflow-x: auto; }}
        footer {{ text-align: center; padding: 30px; color: #888; font-size: 12px; border-top: 1px solid #ddd; margin-top: 40px; }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({{startOnLoad:true, theme:'default'}});</script>
</head>
<body>
    <div class="header">
        <h1>🏒 BenchSight <span class="version">v{VERSION}</span></h1>
    </div>
    <nav class="nav">
        <a href="index.html" {"class='active'" if nav_active=="home" else ""}>Home</a>
        <a href="tables.html" {"class='active'" if nav_active=="tables" else ""}>📊 Tables ({TABLES_COUNT})</a>
        <a href="diagrams/ERD_VIEWER.html" {"class='active'" if nav_active=="schema" else ""}>🗂️ Schema</a>
        <a href="MODULE_REFERENCE.html" {"class='active'" if nav_active=="modules" else ""}>📦 Modules</a>
        <a href="pipeline_visualization.html" {"class='active'" if nav_active=="pipeline" else ""}>⚡ Pipeline</a>
        <a href="DATA_DICTIONARY.html" {"class='active'" if nav_active=="dict" else ""}>📖 Dictionary</a>
        <a href="VERIFICATION_STATUS.html" {"class='active'" if nav_active=="verify" else ""}>✅ Verification</a>
        <a href="LLM_HANDOFF.html" {"class='active'" if nav_active=="handoff" else ""}>🤖 LLM Guide</a>
        <a href="CHANGELOG.html" {"class='active'" if nav_active=="changelog" else ""}>📝 Changelog</a>
    </nav>
    <div class="container">
'''

FOOTER = f'''
    </div>
    <footer>
        BenchSight v{VERSION} | NORAD Hockey Analytics<br>
        Generated: {DATE} | <a href="index.html">Documentation Home</a>
    </footer>
</body>
</html>
'''


def create_index():
    """Create comprehensive index.html with all links."""
    return get_header("Documentation Home", "home") + f'''
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; margin: 30px 0;">
            <div class="card" style="text-align: center;">
                <div style="font-size: 42px; font-weight: bold; color: #4a4e69;">{DIMS_COUNT}</div>
                <div style="color: #888; font-size: 14px;">Dimensions</div>
            </div>
            <div class="card" style="text-align: center;">
                <div style="font-size: 42px; font-weight: bold; color: #4a4e69;">{FACTS_COUNT}</div>
                <div style="color: #888; font-size: 14px;">Facts</div>
            </div>
            <div class="card" style="text-align: center;">
                <div style="font-size: 42px; font-weight: bold; color: #4a4e69;">{QA_COUNT}</div>
                <div style="color: #888; font-size: 14px;">QA Tables</div>
            </div>
            <div class="card" style="text-align: center;">
                <div style="font-size: 42px; font-weight: bold; color: #4a4e69;">{GAMES_COUNT}</div>
                <div style="color: #888; font-size: 14px;">Games</div>
            </div>
        </div>
        
        <div class="alert alert-success">✅ All {GAMES_COUNT} games verified against noradhockey.com - 100% goal accuracy</div>
        
        <h2>📚 Core Documentation</h2>
        <div class="grid">
            <div class="card">
                <h3><a href="tables.html">📊 Table Browser</a></h3>
                <p>Browse all {TABLES_COUNT} tables with schemas, sample data, and detailed column documentation.</p>
            </div>
            <div class="card">
                <h3><a href="diagrams/ERD_VIEWER.html">🗂️ Schema / ERD</a></h3>
                <p>Interactive entity-relationship diagram showing all table connections.</p>
            </div>
            <div class="card">
                <h3><a href="DATA_DICTIONARY.html">📖 Data Dictionary</a></h3>
                <p>Complete column definitions, types, and relationships for all tables.</p>
            </div>
            <div class="card">
                <h3><a href="MODULE_REFERENCE.html">📦 Module Reference</a></h3>
                <p>Source code documentation with flowcharts and function descriptions.</p>
            </div>
        </div>
        
        <h2>⚙️ Technical Documentation</h2>
        <div class="grid">
            <div class="card">
                <h3><a href="pipeline_visualization.html">⚡ ETL Pipeline</a></h3>
                <p>Visual flowchart of the ETL process from raw data to final tables.</p>
            </div>
            <div class="card">
                <h3><a href="KEY_FORMATS.html">🔑 Key Formats</a></h3>
                <p>Primary key conventions and composite key generation rules.</p>
            </div>
            <div class="card">
                <h3><a href="VERIFICATION_STATUS.html">✅ Verification Status</a></h3>
                <p>QA results, goal verification, and data quality metrics.</p>
            </div>
            <div class="card">
                <h3><a href="STAT_CALCS.html">📈 Stat Calculations</a></h3>
                <p>Formulas and logic for all calculated statistics.</p>
            </div>
        </div>
        
        <h2>📋 Table Logic Documentation</h2>
        <div class="grid">
            <div class="card">
                <h3><a href="TABLE_LOGIC_EVENTS.html">🎯 Events Logic</a></h3>
                <p>How fact_events and fact_events_tracking are generated.</p>
            </div>
            <div class="card">
                <h3><a href="TABLE_LOGIC_SHIFTS.html">🔄 Shifts Logic</a></h3>
                <p>Shift tracking, duration bucketing, and player assignments.</p>
            </div>
            <div class="card">
                <h3><a href="TABLE_LOGIC_CYCLES.html">🔁 Cycles Logic</a></h3>
                <p>Offensive zone cycle detection and tracking.</p>
            </div>
            <div class="card">
                <h3><a href="TABLE_LOGIC_RATINGS.html">⭐ Ratings Logic</a></h3>
                <p>Player ratings, competition tiers, and matchup adjustments.</p>
            </div>
        </div>
        
        <h2>🤖 LLM / Developer Handoff</h2>
        <div class="grid">
            <div class="card">
                <h3><a href="LLM_HANDOFF.html">🤖 LLM Handoff Guide</a></h3>
                <p>Complete context and rules for AI assistants working on this project.</p>
            </div>
            <div class="card">
                <h3><a href="HONEST_ASSESSMENT.html">💯 Honest Assessment</a></h3>
                <p>Current status, known issues, and technical debt.</p>
            </div>
            <div class="card">
                <h3><a href="FUTURE_ROADMAP.html">🚀 Future Roadmap</a></h3>
                <p>Planned features, improvements, and development priorities.</p>
            </div>
            <div class="card">
                <h3><a href="CHANGELOG.html">📝 Changelog</a></h3>
                <p>Version history with all changes documented.</p>
            </div>
        </div>
        
        <h2>📁 Additional Resources</h2>
        <div class="grid">
            <div class="card">
                <h3><a href="MISSING_TABLES.html">📋 Missing Tables</a></h3>
                <p>Tables planned but not yet implemented.</p>
            </div>
            <div class="card">
                <h3><a href="OUTCOME_DIMENSIONS.html">🎯 Outcome Dimensions</a></h3>
                <p>Shot, pass, save, and zone outcome classifications.</p>
            </div>
            <div class="card">
                <h3><a href="STAT_DICTIONARY.html">📊 Stat Dictionary</a></h3>
                <p>All statistics with definitions and formulas.</p>
            </div>
            <div class="card">
                <h3><a href="SUPABASE_DEPLOYMENT.html">☁️ Supabase Deployment</a></h3>
                <p>Cloud database setup and configuration.</p>
            </div>
        </div>
        
        <h2>🚀 Quick Start</h2>
        <div class="card">
            <pre># Run full ETL pipeline
python -m src.etl_orchestrator full

# Check status
python -m src.etl_orchestrator status

# Run tests
python3 -m pytest tests/test_etl.py -v

# Single game processing
python -m src.etl_orchestrator single 18969</pre>
        </div>
        
        <div class="alert alert-info">
            <strong>📋 First Time?</strong> Start with <a href="LLM_HANDOFF.html">LLM Handoff Guide</a> for complete project context, 
            then review <a href="tables.html">Table Browser</a> to explore the data model.
        </div>
''' + FOOTER


def create_module_reference():
    """Create consolidated MODULE_REFERENCE.html with flowcharts."""
    return get_header("Module Reference", "modules") + '''
        <h1>📦 Module Reference</h1>
        <p><strong>Last Updated:</strong> ''' + DATE + ''' | <strong>Version:</strong> ''' + VERSION + '''</p>
        
        <div class="alert alert-info">
            This document provides a visual overview of all source modules and their relationships.
        </div>
        
        <h2>🏗️ Architecture Overview</h2>
        <div class="mermaid">
graph TB
    subgraph "Entry Points"
        A[run_etl.py] --> B[ETLOrchestrator]
        CLI[CLI Commands] --> B
    end
    
    subgraph "Core ETL"
        B --> C[base_etl.py]
        C --> D[key_utils.py]
        C --> E[add_all_fkeys.py]
    end
    
    subgraph "Data Processing"
        C --> F[transformation/]
        F --> F1[data_transformer.py]
        F --> F2[standardize_play_details.py]
    end
    
    subgraph "Advanced Tables"
        C --> G[advanced/]
        G --> G1[extended_tables.py]
        G --> G2[create_additional_tables.py]
        G --> G3[event_time_context.py]
    end
    
    subgraph "Data Sources"
        H[BLB_Tables.xlsx] --> C
        I[tracking.xlsx] --> C
        J[roster.json] --> C
    end
    
    subgraph "Output"
        C --> K[data/output/*.csv]
        G --> K
    end
        </div>
        
        <h2>📁 Module Directory</h2>
        
        <h3>src/core/ - Core ETL Engine</h3>
        <table>
            <tr><th>Module</th><th>Purpose</th><th>Key Functions</th></tr>
            <tr>
                <td><code>base_etl.py</code></td>
                <td>Main ETL engine - creates all base tables</td>
                <td>load_tracking_data(), create_derived_tables(), run_full_etl()</td>
            </tr>
            <tr>
                <td><code>key_utils.py</code></td>
                <td>Key generation and data normalization</td>
                <td>format_key(), generate_event_id(), normalize_code()</td>
            </tr>
            <tr>
                <td><code>add_all_fkeys.py</code></td>
                <td>Foreign key column population</td>
                <td>add_all_fkeys(), build_lookup_tables()</td>
            </tr>
            <tr>
                <td><code>safe_csv.py</code></td>
                <td>Safe CSV operations with type handling</td>
                <td>safe_read_csv(), safe_to_csv()</td>
            </tr>
        </table>
        
        <h3>src/advanced/ - Extended Analytics</h3>
        <table>
            <tr><th>Module</th><th>Purpose</th><th>Tables Created</th></tr>
            <tr>
                <td><code>extended_tables.py</code></td>
                <td>Creates 15+ extended analytics tables</td>
                <td>fact_h2h, fact_wowy, fact_line_combos, fact_matchup_*</td>
            </tr>
            <tr>
                <td><code>create_additional_tables.py</code></td>
                <td>Creates supplementary tables</td>
                <td>fact_player_period_stats, fact_team_zone_time</td>
            </tr>
            <tr>
                <td><code>event_time_context.py</code></td>
                <td>Adds time-based context to events</td>
                <td>Adds TOI columns, time_to_next_* columns</td>
            </tr>
            <tr>
                <td><code>enhance_all_stats.py</code></td>
                <td>Enhances player/goalie stats</td>
                <td>Enhanced fact_player_game_stats, fact_goalie_game_stats</td>
            </tr>
        </table>
        
        <h3>src/transformation/ - Data Transformation</h3>
        <table>
            <tr><th>Module</th><th>Purpose</th></tr>
            <tr>
                <td><code>data_transformer.py</code></td>
                <td>Core transformation logic for events and shifts</td>
            </tr>
            <tr>
                <td><code>standardize_play_details.py</code></td>
                <td>Normalizes play_detail values across games</td>
            </tr>
            <tr>
                <td><code>transform_pipeline.py</code></td>
                <td>Orchestrates transformation steps</td>
            </tr>
        </table>
        
        <h2>🔄 ETL Pipeline Flow</h2>
        <div class="mermaid">
sequenceDiagram
    participant User
    participant Orchestrator
    participant BaseETL
    participant Advanced
    participant Output
    
    User->>Orchestrator: run_full()
    Orchestrator->>BaseETL: load_blb_data()
    BaseETL->>BaseETL: create_dimensions()
    BaseETL->>BaseETL: load_tracking_data()
    BaseETL->>BaseETL: create_derived_tables()
    BaseETL->>Output: Save 53 base tables
    
    Orchestrator->>Advanced: extended_tables.py
    Advanced->>Output: Save 15+ tables
    
    Orchestrator->>Advanced: create_additional_tables.py
    Advanced->>Output: Save additional tables
    
    Orchestrator->>Advanced: event_time_context.py
    Advanced->>Output: Add TOI columns
    
    Orchestrator-->>User: Complete (62 tables)
        </div>
        
        <h2>🔑 Key Generation Rules</h2>
        <div class="card">
            <p>All keys follow the format: <code>{PREFIX}{game_id}{index:05d}</code></p>
            <table>
                <tr><th>Prefix</th><th>Table</th><th>Example</th></tr>
                <tr><td>EV</td><td>event_id</td><td>EV1896901000</td></tr>
                <tr><td>SH</td><td>shift_id</td><td>SH1896900001</td></tr>
                <tr><td>SQ</td><td>sequence_key</td><td>SQ1896905001</td></tr>
                <tr><td>PL</td><td>play_key</td><td>PL1896906001</td></tr>
                <tr><td>TV</td><td>tracking_event_key</td><td>TV1896901000</td></tr>
                <tr><td>LV</td><td>linked_event_key</td><td>LV1896909001</td></tr>
                <tr><td>ZC</td><td>zone_change_key</td><td>ZC1896900001</td></tr>
            </table>
        </div>
        
        <h2>⚠️ Critical Rules</h2>
        <div class="alert alert-warning">
            <strong>Goal Counting:</strong> Goals are counted ONLY where <code>event_type='Goal' AND event_detail='Goal_Scored'</code>.<br>
            <code>Shot_Goal</code> is the SHOT that led to a goal, NOT the goal itself!
        </div>
        
        <div class="alert alert-warning">
            <strong>Player Roles:</strong> <code>event_player_1</code> is ALWAYS the primary player (scorer, shooter, passer).
            Assists are tracked via <code>event_player_2</code> and <code>event_player_3</code>.
        </div>
''' + FOOTER


def create_pipeline_visualization():
    """Create updated pipeline visualization."""
    return get_header("ETL Pipeline", "pipeline") + '''
        <h1>⚡ ETL Pipeline Visualization</h1>
        <p><strong>Last Updated:</strong> ''' + DATE + ''' | <strong>Version:</strong> ''' + VERSION + '''</p>
        
        <h2>📊 Data Flow Overview</h2>
        <div class="mermaid">
flowchart TB
    subgraph Sources["📁 Data Sources"]
        BLB[BLB_Tables.xlsx<br/>Master reference data]
        TRACK[tracking.xlsx<br/>Per-game event data]
        ROSTER[roster.json<br/>Per-game rosters]
        NORAD[noradhockey.com<br/>Schedule & verification]
    end
    
    subgraph Phase1["Phase 1: Dimensions"]
        BLB --> D1[dim_player<br/>337 players]
        BLB --> D2[dim_team<br/>Teams & divisions]
        BLB --> D3[dim_schedule<br/>Game schedule]
        BLB --> D4[Reference dims<br/>30+ lookup tables]
    end
    
    subgraph Phase2["Phase 2: Core Facts"]
        TRACK --> F1[fact_events_tracking<br/>11,181 rows]
        F1 --> F2[fact_events<br/>5,831 rows]
        TRACK --> F3[fact_shifts<br/>398 shifts]
        ROSTER --> F4[fact_gameroster<br/>14,471 rows]
    end
    
    subgraph Phase3["Phase 3: Derived Facts"]
        F2 --> D5[fact_faceoffs<br/>171 rows]
        F2 --> D6[fact_rushes<br/>314 rows]
        F2 --> D7[fact_zone_entries<br/>508 rows]
        F2 --> D8[fact_scoring_chances<br/>455 rows]
        F3 --> D9[fact_shift_players<br/>4,613 rows]
    end
    
    subgraph Phase4["Phase 4: Analytics"]
        F2 --> A1[fact_sequences<br/>397 sequences]
        F2 --> A2[fact_plays<br/>1,956 plays]
        D5 --> A3[Player game stats]
        D6 --> A3
    end
    
    subgraph Output["📤 Output"]
        A1 --> CSV[data/output/*.csv<br/>62 tables]
        A2 --> CSV
        A3 --> CSV
    end
        </div>
        
        <h2>🔄 Processing Stages</h2>
        
        <h3>Stage 1: Load BLB Master Data</h3>
        <div class="card">
            <p>Source: <code>data/BLB_Tables.xlsx</code></p>
            <ul>
                <li><strong>dim_player</strong> - 337 registered players with ratings</li>
                <li><strong>dim_team</strong> - Team definitions and divisions</li>
                <li><strong>dim_schedule</strong> - Complete game schedule</li>
                <li><strong>30+ reference dimensions</strong> - Event types, zones, positions, etc.</li>
            </ul>
        </div>
        
        <h3>Stage 2: Load Tracking Data</h3>
        <div class="card">
            <p>Source: <code>data/raw/games/{game_id}/{game_id}_tracking.xlsx</code></p>
            <ul>
                <li>Reads <strong>events</strong> sheet → fact_events_tracking</li>
                <li>Reads <strong>shifts</strong> sheet → fact_shifts_tracking</li>
                <li>Generates composite keys (event_id, shift_id, etc.)</li>
                <li>Links player_id via jersey number lookup</li>
            </ul>
        </div>
        
        <h3>Stage 3: Create Derived Tables</h3>
        <div class="card">
            <ul>
                <li><strong>fact_events</strong> - Grouped by event_id (one row per event)</li>
                <li><strong>fact_faceoffs</strong> - Filtered where event_type='Faceoff'</li>
                <li><strong>fact_rushes</strong> - Events with play_detail containing 'Rush'</li>
                <li><strong>fact_zone_entries/exits</strong> - Zone transition events</li>
                <li><strong>fact_scoring_chances</strong> - High danger opportunities</li>
            </ul>
        </div>
        
        <h3>Stage 4: Add Context & Analytics</h3>
        <div class="card">
            <ul>
                <li>Add time context (time_to_next_goal, time_from_last_stoppage)</li>
                <li>Add TOI context (player_toi at event time)</li>
                <li>Calculate sequences and plays</li>
                <li>Generate player/team game stats</li>
            </ul>
        </div>
        
        <h2>⏱️ Processing Timeline</h2>
        <div class="mermaid">
gantt
    title ETL Processing Order
    dateFormat X
    axisFormat %s
    
    section Phase 1
    Load BLB Data           :0, 5
    Create Dimensions       :5, 10
    
    section Phase 2
    Load Game 18969         :10, 15
    Load Game 18977         :15, 20
    Load Game 18981         :20, 25
    Load Game 18987         :25, 30
    
    section Phase 3
    Create Derived Tables   :30, 40
    Add FK Columns          :40, 45
    
    section Phase 4
    Extended Tables         :45, 55
    Time Context            :55, 60
    QA Validation           :60, 65
        </div>
        
        <h2>🎯 Key Transformations</h2>
        <table>
            <tr><th>Transformation</th><th>Input</th><th>Output</th><th>Logic</th></tr>
            <tr>
                <td>Event Grouping</td>
                <td>fact_events_tracking<br/>(11,181 rows)</td>
                <td>fact_events<br/>(5,831 rows)</td>
                <td>GROUP BY event_id, priority: Goal > Shot > Faceoff</td>
            </tr>
            <tr>
                <td>Goal Identification</td>
                <td>fact_events</td>
                <td>is_goal column</td>
                <td>event_type='Goal' AND event_detail='Goal_Scored'</td>
            </tr>
            <tr>
                <td>Shift Duration</td>
                <td>fact_shifts</td>
                <td>shift_duration</td>
                <td>shift_end_total_seconds - shift_start_total_seconds</td>
            </tr>
            <tr>
                <td>Player TOI</td>
                <td>fact_shifts</td>
                <td>cumulative_toi</td>
                <td>SUM(shift_duration) WHERE player AND game</td>
            </tr>
        </table>
''' + FOOTER


def create_key_formats():
    """Create comprehensive KEY_FORMATS.html."""
    return get_header("Key Formats", "") + '''
        <h1>🔑 Key Format Reference</h1>
        <p><strong>Last Updated:</strong> ''' + DATE + ''' | <strong>Version:</strong> ''' + VERSION + '''</p>
        
        <h2>Primary Key Format Standard</h2>
        <div class="card">
            <p>All composite keys follow the format:</p>
            <pre>{PREFIX}{game_id}{index:05d}</pre>
            <p>Where:</p>
            <ul>
                <li><code>PREFIX</code> = 2-character type identifier</li>
                <li><code>game_id</code> = Game ID from noradhockey.com (e.g., 18969)</li>
                <li><code>index</code> = Zero-padded 5-digit sequential number</li>
            </ul>
        </div>
        
        <h2>Key Prefix Reference</h2>
        <table>
            <tr><th>Prefix</th><th>Key Name</th><th>Table</th><th>Example</th><th>Description</th></tr>
            <tr>
                <td><code>EV</code></td>
                <td>event_id</td>
                <td>fact_events</td>
                <td>EV1896901000</td>
                <td>Unique event identifier. One per game event.</td>
            </tr>
            <tr>
                <td><code>SH</code></td>
                <td>shift_id</td>
                <td>fact_shifts</td>
                <td>SH1896900001</td>
                <td>Unique shift identifier. One per line change.</td>
            </tr>
            <tr>
                <td><code>SQ</code></td>
                <td>sequence_key</td>
                <td>fact_sequences</td>
                <td>SQ1896905001</td>
                <td>Groups consecutive events into possession sequences.</td>
            </tr>
            <tr>
                <td><code>PL</code></td>
                <td>play_key</td>
                <td>fact_plays</td>
                <td>PL1896906001</td>
                <td>Groups events into offensive/defensive plays.</td>
            </tr>
            <tr>
                <td><code>TV</code></td>
                <td>tracking_event_key</td>
                <td>fact_events_tracking</td>
                <td>TV1896901000</td>
                <td>Tracking-level key. May differ from event_id for zone entries.</td>
            </tr>
            <tr>
                <td><code>LV</code></td>
                <td>linked_event_key</td>
                <td>fact_events</td>
                <td>LV1896909001</td>
                <td>Links causally related events (e.g., shot to goal).</td>
            </tr>
            <tr>
                <td><code>ZC</code></td>
                <td>zone_change_key</td>
                <td>fact_zone_entries</td>
                <td>ZC1896900001</td>
                <td>Zone entry/exit identifier.</td>
            </tr>
            <tr>
                <td><code>EP</code></td>
                <td>event_player_key</td>
                <td>fact_events_tracking</td>
                <td>EP1896901000_1</td>
                <td>Unique player-event combination (event_id + role).</td>
            </tr>
            <tr>
                <td><code>GK</code></td>
                <td>goalie_game_key</td>
                <td>fact_goalie_game_stats</td>
                <td>GK18969_P_SMITH</td>
                <td>Unique goalie-game combination.</td>
            </tr>
        </table>
        
        <h2>Dimension Key Formats</h2>
        <table>
            <tr><th>Dimension</th><th>Key Column</th><th>Format</th><th>Example</th></tr>
            <tr><td>dim_player</td><td>player_id</td><td>P_LASTNAME_N</td><td>P_SMITH_1, P_JONES_2</td></tr>
            <tr><td>dim_team</td><td>team_id</td><td>Team code</td><td>TEAM1, REDWINGS</td></tr>
            <tr><td>dim_season</td><td>season_id</td><td>NORAD_YYYY_SS</td><td>NORAD_2024_FA</td></tr>
            <tr><td>dim_period</td><td>period_id</td><td>P{N}</td><td>P1, P2, P3, POT</td></tr>
            <tr><td>dim_zone</td><td>zone_id</td><td>Z_{zone}</td><td>Z_O, Z_D, Z_N</td></tr>
            <tr><td>dim_position</td><td>position_id</td><td>Position code</td><td>C, LW, RW, D, G</td></tr>
        </table>
        
        <h2>Foreign Key Relationships</h2>
        <div class="mermaid">
erDiagram
    fact_events ||--o{ fact_events_tracking : "event_id"
    fact_events ||--o{ fact_faceoffs : "event_id"
    fact_events ||--o{ fact_rushes : "event_id"
    
    dim_player ||--o{ fact_events_tracking : "player_id"
    dim_team ||--o{ fact_events : "home_team_id"
    dim_team ||--o{ fact_events : "away_team_id"
    dim_period ||--o{ fact_events : "period_id"
    dim_zone ||--o{ fact_events : "event_zone_id"
    
    fact_shifts ||--o{ fact_shift_players : "shift_id"
    dim_player ||--o{ fact_shift_players : "player_id"
        </div>
        
        <h2>Key Generation Functions</h2>
        <div class="card">
            <p>All keys are generated in <code>src/core/key_utils.py</code>:</p>
            <pre>def format_key(prefix: str, game_id, index) -> str:
    """Create key: {prefix}{game_id}{index:05d}"""
    return f"{prefix}{game_id}{int(index):05d}"

# Usage examples:
event_id = format_key('EV', 18969, 1000)  # EV1896901000
shift_id = format_key('SH', 18969, 1)     # SH1896900001</pre>
        </div>
''' + FOOTER


def create_future_roadmap():
    """Create updated FUTURE_ROADMAP.html."""
    return get_header("Future Roadmap", "") + '''
        <h1>🚀 Future Roadmap</h1>
        <p><strong>Last Updated:</strong> ''' + DATE + ''' | <strong>Version:</strong> ''' + VERSION + '''</p>
        
        <h2>Current Status</h2>
        <div class="alert alert-success">
            <strong>✅ v12.03 Complete:</strong> 62 working tables, 4 games processed, 100% goal verification accuracy.
        </div>
        
        <h2>🎯 Priority 1: Data Expansion</h2>
        <div class="card">
            <h3>More Games</h3>
            <ul>
                <li>Process remaining Fall 2024 games (15+ games available)</li>
                <li>Add historical seasons for trend analysis</li>
                <li>Implement automated game addition workflow</li>
            </ul>
            
            <h3>XY Coordinate Data</h3>
            <ul>
                <li>Integrate shot location data (xy_tables.py exists but not connected)</li>
                <li>Create heat maps and shot charts</li>
                <li>Calculate expected goals (xG) from location</li>
            </ul>
        </div>
        
        <h2>🎯 Priority 2: Missing Tables</h2>
        <div class="card">
            <h3>Statistical Tables</h3>
            <table>
                <tr><th>Table</th><th>Purpose</th><th>Status</th></tr>
                <tr><td>fact_player_game_stats</td><td>Per-game player statistics</td><td><span class="badge badge-yellow">Partial</span></td></tr>
                <tr><td>fact_player_season_stats</td><td>Season aggregate stats</td><td><span class="badge badge-red">Missing</span></td></tr>
                <tr><td>fact_team_game_stats</td><td>Per-game team statistics</td><td><span class="badge badge-yellow">Partial</span></td></tr>
                <tr><td>fact_goalie_game_stats</td><td>Goalie performance</td><td><span class="badge badge-red">Missing</span></td></tr>
            </table>
            
            <h3>Advanced Analytics</h3>
            <ul>
                <li>fact_player_trends - Rolling averages and momentum</li>
                <li>fact_line_combos - Line combination effectiveness</li>
                <li>fact_special_teams - PP/PK detailed stats</li>
            </ul>
        </div>
        
        <h2>🎯 Priority 3: Dashboard & Visualization</h2>
        <div class="card">
            <ul>
                <li>Complete Streamlit dashboard (dashboard/app.py exists)</li>
                <li>Player profile pages with career stats</li>
                <li>Game summary reports</li>
                <li>Team comparison tools</li>
                <li>Leaderboards and rankings</li>
            </ul>
        </div>
        
        <h2>🎯 Priority 4: Production Deployment</h2>
        <div class="card">
            <ul>
                <li>Supabase schema finalization (SQL exists in sql/)</li>
                <li>Automated ETL scheduling</li>
                <li>Data validation pipeline</li>
                <li>User authentication for dashboard</li>
            </ul>
        </div>
        
        <h2>🛠️ Technical Improvements</h2>
        <div class="card">
            <h3>Code Quality</h3>
            <ul>
                <li>Replace remaining f-string SQL with parameterized queries</li>
                <li>Add comprehensive type hints</li>
                <li>Increase test coverage (currently 23 tests)</li>
            </ul>
            
            <h3>Performance</h3>
            <ul>
                <li>Optimize large table joins</li>
                <li>Add caching for derived calculations</li>
                <li>Parallelize game processing</li>
            </ul>
        </div>
        
        <h2>📅 Suggested Timeline</h2>
        <table>
            <tr><th>Phase</th><th>Tasks</th><th>Est. Effort</th></tr>
            <tr><td>v12.x</td><td>Process all Fall 2024 games, fix missing stats tables</td><td>2-3 sessions</td></tr>
            <tr><td>v13.x</td><td>XY coordinate integration, shot charts</td><td>2-3 sessions</td></tr>
            <tr><td>v14.x</td><td>Dashboard completion</td><td>3-4 sessions</td></tr>
            <tr><td>v15.x</td><td>Supabase deployment</td><td>2-3 sessions</td></tr>
        </table>
        
        <h2>💡 Ideas for Future Features</h2>
        <div class="card">
            <ul>
                <li><strong>Video Integration:</strong> Link events to video timestamps (video_times files exist)</li>
                <li><strong>Player Comparison Tool:</strong> Head-to-head statistical comparisons</li>
                <li><strong>Draft Analysis:</strong> Pre-season roster building insights</li>
                <li><strong>Game Prediction:</strong> ML model for game outcome prediction</li>
                <li><strong>Notification System:</strong> Alerts for milestones, records</li>
            </ul>
        </div>
''' + FOOTER


def create_llm_handoff():
    """Create updated LLM_HANDOFF.html."""
    return get_header("LLM Handoff", "handoff") + '''
        <h1>🤖 LLM Handoff Guide</h1>
        <p><strong>Last Updated:</strong> ''' + DATE + ''' | <strong>Version:</strong> ''' + VERSION + '''</p>
        
        <div class="alert alert-warning">
            <strong>📋 CRITICAL:</strong> Always read <code>LLM_REQUIREMENTS.md</code> first! It contains all rules and conventions.
        </div>
        
        <h2>Project Overview</h2>
        <div class="card">
            <p><strong>BenchSight</strong> is a hockey analytics ETL platform for the NORAD recreational league.</p>
            <table>
                <tr><td>Tables</td><td><strong>''' + str(TABLES_COUNT) + '''</strong> (''' + str(DIMS_COUNT) + ''' dim, ''' + str(FACTS_COUNT) + ''' fact, ''' + str(QA_COUNT) + ''' QA)</td></tr>
                <tr><td>Games</td><td><strong>''' + str(GAMES_COUNT) + '''</strong> (18969, 18977, 18981, 18987)</td></tr>
                <tr><td>Players</td><td><strong>337</strong> registered</td></tr>
                <tr><td>Events</td><td><strong>5,831</strong> tracked events</td></tr>
            </table>
        </div>
        
        <h2>⚠️ Critical Rules</h2>
        <div class="alert alert-warning">
            <h3>Goal Counting</h3>
            <p>Goals are counted ONLY where:</p>
            <pre>event_type = 'Goal' AND event_detail = 'Goal_Scored'</pre>
            <p><strong>NEVER</strong> use <code>Shot_Goal</code> to count goals - that's the SHOT that led to a goal!</p>
        </div>
        
        <div class="alert alert-warning">
            <h3>Player Roles</h3>
            <ul>
                <li><code>event_player_1</code> = PRIMARY player (scorer, shooter, passer)</li>
                <li><code>event_player_2</code> = SECONDARY player (primary assist, receiver)</li>
                <li><code>event_player_3</code> = TERTIARY player (secondary assist)</li>
            </ul>
        </div>
        
        <h2>🚀 Quick Start</h2>
        <div class="card">
            <pre># Run full ETL
python -m src.etl_orchestrator full

# Check status
python -m src.etl_orchestrator status

# Run tests
python3 -m pytest tests/test_etl.py -v

# Process single game
python -m src.etl_orchestrator single 18969</pre>
        </div>
        
        <h2>📁 Key Files</h2>
        <table>
            <tr><th>File</th><th>Purpose</th><th>Priority</th></tr>
            <tr><td><code>LLM_REQUIREMENTS.md</code></td><td>All rules and conventions</td><td><span class="badge badge-red">READ FIRST</span></td></tr>
            <tr><td><code>src/etl_orchestrator.py</code></td><td>Main ETL entry point</td><td><span class="badge badge-green">Primary</span></td></tr>
            <tr><td><code>src/core/base_etl.py</code></td><td>Core ETL engine</td><td><span class="badge badge-green">Primary</span></td></tr>
            <tr><td><code>src/core/key_utils.py</code></td><td>Key generation</td><td><span class="badge badge-blue">Important</span></td></tr>
            <tr><td><code>docs/html/</code></td><td>All HTML documentation</td><td><span class="badge badge-blue">Reference</span></td></tr>
        </table>
        
        <h2>📚 Documentation Links</h2>
        <div class="grid">
            <div class="card">
                <h3><a href="tables.html">📊 Table Browser</a></h3>
                <p>Browse all tables with schemas and sample data.</p>
            </div>
            <div class="card">
                <h3><a href="MODULE_REFERENCE.html">📦 Module Reference</a></h3>
                <p>Source code documentation with flowcharts.</p>
            </div>
            <div class="card">
                <h3><a href="pipeline_visualization.html">⚡ ETL Pipeline</a></h3>
                <p>Visual flowchart of data processing.</p>
            </div>
            <div class="card">
                <h3><a href="HONEST_ASSESSMENT.html">💯 Honest Assessment</a></h3>
                <p>Current status and known issues.</p>
            </div>
        </div>
        
        <h2>📋 Output Requirements</h2>
        <p>Every output MUST:</p>
        <ol>
            <li>Update version in ALL docs (including HTML)</li>
            <li>Update ALL HTML timestamps</li>
            <li>Add entry to CHANGELOG.md</li>
            <li>Verify all tables exist</li>
            <li>Run tests: <code>python3 -m pytest tests/test_etl.py -v</code></li>
        </ol>
        
        <h2>🔢 Version Convention</h2>
        <div class="card">
            <p>Format: <code>benchsight_v{CHAT}.{OUTPUT}</code></p>
            <ul>
                <li><strong>CHAT</strong> = Increments each NEW chat session</li>
                <li><strong>OUTPUT</strong> = Increments each package within same chat</li>
            </ul>
            <p>Current: <strong>v12.03</strong> (Chat 12, Output 03)</p>
        </div>
        
        <h2>🚨 Never Do</h2>
        <ul>
            <li>Delete code without running tests first</li>
            <li>Use <code>Shot_Goal</code> to count goals</li>
            <li>Skip updating timestamps on docs</li>
            <li>Output without incrementing version number</li>
            <li>Hard-code game IDs (system must be dynamic)</li>
        </ul>
''' + FOOTER


def create_erd_viewer():
    """Create ERD viewer with current schema."""
    return get_header("Schema / ERD", "schema") + '''
        <h1>🗂️ Entity Relationship Diagram</h1>
        <p><strong>Last Updated:</strong> ''' + DATE + ''' | <strong>Version:</strong> ''' + VERSION + '''</p>
        
        <h2>Core Tables Overview</h2>
        <div class="mermaid">
erDiagram
    dim_player {
        string player_id PK
        string player_first_name
        string player_last_name
        int current_skill_rating
    }
    
    dim_team {
        string team_id PK
        string team_name
        string team_code
    }
    
    dim_schedule {
        int game_id PK
        string home_team FK
        string away_team FK
        date game_date
    }
    
    fact_events {
        string event_id PK
        int game_id FK
        string event_type
        string event_detail
        int is_goal
    }
    
    fact_events_tracking {
        string event_player_key PK
        string event_id FK
        string player_id FK
        string player_role
    }
    
    fact_shifts {
        string shift_id PK
        int game_id FK
        int shift_duration
    }
    
    fact_gameroster {
        string player_id FK
        int game_id FK
        string team
        int jersey_number
    }
    
    dim_player ||--o{ fact_events_tracking : player_id
    dim_player ||--o{ fact_gameroster : player_id
    dim_team ||--o{ dim_schedule : home_team
    dim_team ||--o{ dim_schedule : away_team
    dim_schedule ||--o{ fact_events : game_id
    dim_schedule ||--o{ fact_shifts : game_id
    fact_events ||--o{ fact_events_tracking : event_id
        </div>
        
        <h2>Event Processing Flow</h2>
        <div class="mermaid">
flowchart LR
    subgraph Input
        A[tracking.xlsx]
    end
    
    subgraph "Tracking Level"
        B[fact_events_tracking<br/>11,181 rows<br/>One per player-event]
    end
    
    subgraph "Event Level"
        C[fact_events<br/>5,831 rows<br/>One per event]
    end
    
    subgraph "Derived Tables"
        D1[fact_faceoffs<br/>171]
        D2[fact_rushes<br/>314]
        D3[fact_zone_entries<br/>508]
        D4[fact_saves<br/>212]
        D5[fact_penalties<br/>20]
    end
    
    A --> B
    B --> C
    C --> D1
    C --> D2
    C --> D3
    C --> D4
    C --> D5
        </div>
        
        <h2>Shift Processing Flow</h2>
        <div class="mermaid">
flowchart LR
    subgraph Input
        A[tracking.xlsx<br/>shifts sheet]
    end
    
    subgraph "Shift Tables"
        B[fact_shifts<br/>398 shifts]
        C[fact_shift_players<br/>4,613 rows]
    end
    
    subgraph "Derived"
        D[Player TOI]
        E[Team strength]
    end
    
    A --> B
    B --> C
    C --> D
    B --> E
        </div>
        
        <h2>Table Categories</h2>
        <table>
            <tr><th>Category</th><th>Count</th><th>Examples</th></tr>
            <tr>
                <td><strong>Dimensions</strong></td>
                <td>''' + str(DIMS_COUNT) + '''</td>
                <td>dim_player, dim_team, dim_event_type, dim_zone</td>
            </tr>
            <tr>
                <td><strong>Core Facts</strong></td>
                <td>4</td>
                <td>fact_events, fact_events_tracking, fact_shifts, fact_gameroster</td>
            </tr>
            <tr>
                <td><strong>Derived Facts</strong></td>
                <td>''' + str(FACTS_COUNT - 4) + '''</td>
                <td>fact_faceoffs, fact_rushes, fact_zone_entries, fact_saves</td>
            </tr>
            <tr>
                <td><strong>QA Tables</strong></td>
                <td>''' + str(QA_COUNT) + '''</td>
                <td>qa_goal_accuracy, qa_data_completeness</td>
            </tr>
        </table>
        
        <p><a href="../diagrams/ERD_COMPLETE.mermaid">View Full ERD Mermaid Source</a></p>
''' + FOOTER


def main():
    """Generate all HTML documentation."""
    print("Updating all HTML documentation...")
    
    # Create index
    (HTML_DIR / "index.html").write_text(create_index())
    print("  ✓ index.html")
    
    # Create MODULE_REFERENCE
    (HTML_DIR / "MODULE_REFERENCE.html").write_text(create_module_reference())
    print("  ✓ MODULE_REFERENCE.html")
    
    # Create pipeline_visualization
    (HTML_DIR / "pipeline_visualization.html").write_text(create_pipeline_visualization())
    print("  ✓ pipeline_visualization.html")
    
    # Create KEY_FORMATS
    (HTML_DIR / "KEY_FORMATS.html").write_text(create_key_formats())
    print("  ✓ KEY_FORMATS.html")
    
    # Create FUTURE_ROADMAP
    (HTML_DIR / "FUTURE_ROADMAP.html").write_text(create_future_roadmap())
    print("  ✓ FUTURE_ROADMAP.html")
    
    # Create LLM_HANDOFF
    (HTML_DIR / "LLM_HANDOFF.html").write_text(create_llm_handoff())
    print("  ✓ LLM_HANDOFF.html")
    
    # Create ERD_VIEWER in diagrams/
    (HTML_DIR / "diagrams" / "ERD_VIEWER.html").write_text(create_erd_viewer())
    print("  ✓ diagrams/ERD_VIEWER.html")
    
    # Remove redundant DATA_DICTIONARY_v12.html
    redundant = HTML_DIR / "DATA_DICTIONARY_v12.html"
    if redundant.exists():
        redundant.unlink()
        print("  ✓ Removed redundant DATA_DICTIONARY_v12.html")
    
    # Remove redundant MODULE_REFERENCE_v12.html
    redundant2 = HTML_DIR / "MODULE_REFERENCE_v12.html"
    if redundant2.exists():
        redundant2.unlink()
        print("  ✓ Removed redundant MODULE_REFERENCE_v12.html")
    
    print("\nDone! All HTML docs updated.")


if __name__ == "__main__":
    main()
