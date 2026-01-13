"""
BenchSight v11.03 Enhancements

This module addresses:
1. Fix dimension key formatting (PR01, POS01, VN01, ZN01)
2. Consolidate shift tables (keep wide + long, remove duplicates)
3. Enhanced HTML documentation with:
   - Data dictionary per table
   - Net/rink visualizations
   - US Mountain timestamps
   - Subfolder organization
   - Table flowcharts
4. Remove unused CSAHA from dim_league
5. Update schema diagram
6. Update changelog HTML
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import pytz
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent.parent
OUTPUT_DIR = BASE_DIR / 'data' / 'output'
DOCS_DIR = BASE_DIR / 'docs'
HTML_DIR = DOCS_DIR / 'html'
HTML_TABLES_DIR = HTML_DIR / 'tables'

VERSION = "11.03"
MTN_TZ = pytz.timezone('America/Denver')

def get_mtn_timestamp():
    """Get current timestamp in US Mountain time."""
    return datetime.now(MTN_TZ).strftime('%Y-%m-%d %H:%M:%S %Z')


# ============================================================================
# 1. FIX DIMENSION KEY FORMATTING
# ============================================================================

def fix_dimension_keys():
    """Fix dimension keys to use consistent format: PREFIX + PADDED_NUMBER."""
    logger.info("Fixing dimension key formats...")
    
    # Define the format for each dimension
    key_formats = {
        'dim_player_role': ('role_id', 'PR', 2),      # PR01, PR02
        'dim_position': ('position_id', 'POS', 2),    # POS01, POS02
        'dim_venue': ('venue_id', 'VN', 2),           # VN01, VN02
        'dim_zone': ('zone_id', 'ZN', 2),             # ZN01, ZN02
    }
    
    # Track old -> new mappings for FK updates
    all_mappings = {}
    
    for table_name, (pk_col, prefix, pad_width) in key_formats.items():
        path = OUTPUT_DIR / f'{table_name}.csv'
        if not path.exists():
            logger.warning(f"{table_name}.csv not found")
            continue
        
        df = pd.read_csv(path)
        old_values = df[pk_col].tolist()
        
        # Generate new keys
        new_keys = [f"{prefix}{str(i+1).zfill(pad_width)}" for i in range(len(df))]
        df[pk_col] = new_keys
        
        # Store mapping
        all_mappings[pk_col] = dict(zip(old_values, new_keys))
        
        df.to_csv(path, index=False)
        logger.info(f"  Fixed {table_name}: {old_values[:3]} -> {new_keys[:3]}")
    
    return all_mappings


def update_foreign_keys(key_mappings):
    """Update all foreign keys in fact tables to match new dimension keys."""
    logger.info("Updating foreign keys in fact tables...")
    
    # Find all fact tables
    fact_files = list(OUTPUT_DIR.glob('fact_*.csv'))
    
    for fact_file in fact_files:
        df = pd.read_csv(fact_file, low_memory=False)
        updated = False
        
        for fk_col, mapping in key_mappings.items():
            if fk_col in df.columns:
                # Convert to string for mapping
                df[fk_col] = df[fk_col].astype(str).map(lambda x: mapping.get(x, mapping.get(int(float(x)) if x.replace('.','').replace('-','').isdigit() else x, x)))
                updated = True
        
        if updated:
            df.to_csv(fact_file, index=False)
            logger.info(f"  Updated FKs in {fact_file.stem}")


# ============================================================================
# 2. REMOVE UNUSED CSAHA LEAGUE
# ============================================================================

def remove_csaha_league():
    """Remove unused CSAHA from dim_league."""
    logger.info("Removing unused CSAHA league...")
    
    league_path = OUTPUT_DIR / 'dim_league.csv'
    if not league_path.exists():
        return
    
    df = pd.read_csv(league_path)
    original_count = len(df)
    
    # Keep only NORAD
    df = df[df['league_id'] == 'N']
    
    df.to_csv(league_path, index=False)
    logger.info(f"  dim_league: {original_count} -> {len(df)} rows (removed CSAHA)")


# ============================================================================
# 3. CONSOLIDATE SHIFT TABLES
# ============================================================================

def consolidate_shift_tables():
    """
    Consolidate shift tables:
    - Keep fact_shifts (wide, comprehensive - 138 cols)
    - Keep fact_shift_players (long, per-player - 32 cols)
    - Remove fact_shifts (redundant with fact_shifts)
    - Remove fact_shift_players (redundant with fact_shift_players)
    """
    logger.info("Consolidating shift tables...")
    
    # Check what exists
    tracking = OUTPUT_DIR / 'fact_shifts.csv'
    player = OUTPUT_DIR / 'fact_shift_players.csv'
    shifts = OUTPUT_DIR / 'fact_shifts.csv'
    shift_players = OUTPUT_DIR / 'fact_shift_players.csv'
    
    if tracking.exists():
        df = pd.read_csv(tracking, nrows=1)
        logger.info(f"  fact_shifts: {df.shape[1]} cols (KEEPING - wide format)")
    
    if player.exists():
        df = pd.read_csv(player, nrows=1)
        logger.info(f"  fact_shift_players: {df.shape[1]} cols (KEEPING - long format)")
    
    # Remove redundant tables
    if shifts.exists():
        shifts.unlink()
        logger.info("  fact_shifts.csv REMOVED (redundant)")
    
    if shift_players.exists():
        shift_players.unlink()
        logger.info("  fact_shift_players.csv REMOVED (redundant)")


# ============================================================================
# 4. DATA DICTIONARY DEFINITIONS
# ============================================================================

# Comprehensive data dictionary with formulas and derivation info
DATA_DICTIONARY = {
    # Player Stats
    'goals': {
        'description': 'Total goals scored',
        'formula': "COUNT(fact_event_players) WHERE event_type='Goal' AND event_detail='Goal_Scored' AND player_role='event_player_1'",
        'source': 'Explicit from tracking',
        'depends_on': ['fact_event_players'],
    },
    'assists': {
        'description': 'Total assists',
        'formula': "COUNT(fact_event_players) WHERE event_type='Goal' AND player_role IN ('event_player_2', 'event_player_3')",
        'source': 'Explicit from tracking',
        'depends_on': ['fact_event_players'],
    },
    'points': {
        'description': 'Total points (goals + assists)',
        'formula': 'goals + assists',
        'source': 'Calculated',
        'depends_on': ['goals', 'assists'],
    },
    'shots': {
        'description': 'Total shots on goal',
        'formula': "COUNT(fact_event_players) WHERE event_type='Shot' AND player_role='event_player_1'",
        'source': 'Explicit from tracking',
        'depends_on': ['fact_event_players'],
    },
    'shooting_pct': {
        'description': 'Shooting percentage',
        'formula': '(goals / shots) * 100 WHERE shots > 0',
        'source': 'Calculated',
        'depends_on': ['goals', 'shots'],
    },
    'plus_minus': {
        'description': 'Plus/minus differential',
        'formula': 'goals_for_while_on_ice - goals_against_while_on_ice',
        'source': 'Calculated from shifts',
        'depends_on': ['fact_shift_players', 'fact_event_players'],
    },
    'toi': {
        'description': 'Time on ice in seconds',
        'formula': 'SUM(shift_duration) for player',
        'source': 'Calculated from shifts',
        'depends_on': ['fact_shift_players'],
    },
    'faceoff_wins': {
        'description': 'Faceoffs won',
        'formula': "COUNT(fact_event_players) WHERE event_type='Faceoff' AND event_successful='s' AND player_role='event_player_1'",
        'source': 'Explicit from tracking',
        'depends_on': ['fact_event_players'],
    },
    'faceoff_losses': {
        'description': 'Faceoffs lost',
        'formula': "COUNT(fact_event_players) WHERE event_type='Faceoff' AND event_successful='u' AND player_role='event_player_1'",
        'source': 'Explicit from tracking',
        'depends_on': ['fact_event_players'],
    },
    # Add more as needed...
}

# Table derivation flowcharts
TABLE_FLOWCHARTS = {
    'fact_event_players': {
        'sources': ['raw tracking Excel files'],
        'process': [
            '1. Load events sheet from tracking Excel',
            '2. Expand player columns into rows',
            '3. Add dimension FKs (event_type_id, etc.)',
            '4. Calculate event time context (TOI columns)',
            '5. Add event_index and event_player_key',
        ],
        'depends_on': ['dim_event_type', 'dim_event_detail', 'dim_player', 'dim_zone'],
    },
    'fact_shifts': {
        'sources': ['raw tracking Excel files'],
        'process': [
            '1. Load shifts sheet from tracking Excel',
            '2. Calculate shift duration',
            '3. Add player columns (expanded)',
            '4. Add dimension FKs',
            '5. Add shift_duration_id',
        ],
        'depends_on': ['dim_shift_duration', 'dim_player'],
    },
    'fact_shift_players': {
        'sources': ['fact_shifts'],
        'process': [
            '1. Take one row per shift from tracking',
            '2. Expand to one row per player per shift',
            '3. Add player-specific metrics',
            '4. Add venue/slot information',
        ],
        'depends_on': ['fact_shifts', 'dim_player'],
    },
    'fact_player_game_stats': {
        'sources': ['fact_event_players', 'fact_shift_players'],
        'process': [
            '1. Aggregate events by player and game',
            '2. Count goals, assists, shots, etc.',
            '3. Calculate TOI from shifts',
            '4. Calculate derived stats (shooting_pct, etc.)',
        ],
        'depends_on': ['fact_event_players', 'fact_shift_players'],
    },
}


# ============================================================================
# 5. HTML GENERATION WITH VISUALIZATIONS
# ============================================================================

def generate_net_svg():
    """Generate SVG visualization of hockey net zones."""
    return '''
    <svg viewBox="0 0 300 200" style="max-width:400px; border:1px solid #ddd; background:#fff;">
        <!-- Net frame -->
        <rect x="50" y="40" width="200" height="120" fill="none" stroke="#333" stroke-width="3"/>
        
        <!-- Zone lines -->
        <line x1="116" y1="40" x2="116" y2="160" stroke="#999" stroke-width="1" stroke-dasharray="5,5"/>
        <line x1="183" y1="40" x2="183" y2="160" stroke="#999" stroke-width="1" stroke-dasharray="5,5"/>
        <line x1="50" y1="100" x2="250" y2="100" stroke="#999" stroke-width="1" stroke-dasharray="5,5"/>
        
        <!-- Zone labels -->
        <text x="83" y="75" text-anchor="middle" font-size="12" fill="#666">Top</text>
        <text x="83" y="90" text-anchor="middle" font-size="12" fill="#666">Left</text>
        
        <text x="150" y="75" text-anchor="middle" font-size="12" fill="#666">Top</text>
        <text x="150" y="90" text-anchor="middle" font-size="12" fill="#666">Center</text>
        
        <text x="216" y="75" text-anchor="middle" font-size="12" fill="#666">Top</text>
        <text x="216" y="90" text-anchor="middle" font-size="12" fill="#666">Right</text>
        
        <text x="83" y="125" text-anchor="middle" font-size="12" fill="#666">Bottom</text>
        <text x="83" y="140" text-anchor="middle" font-size="12" fill="#666">Left</text>
        
        <text x="150" y="125" text-anchor="middle" font-size="12" fill="#666">Bottom</text>
        <text x="150" y="140" text-anchor="middle" font-size="12" fill="#666">Center</text>
        
        <text x="216" y="125" text-anchor="middle" font-size="12" fill="#666">Bottom</text>
        <text x="216" y="140" text-anchor="middle" font-size="12" fill="#666">Right</text>
        
        <!-- Posts -->
        <circle cx="50" cy="40" r="5" fill="#c00"/>
        <circle cx="250" cy="40" r="5" fill="#c00"/>
        <circle cx="50" cy="160" r="5" fill="#c00"/>
        <circle cx="250" cy="160" r="5" fill="#c00"/>
        
        <!-- Title -->
        <text x="150" y="20" text-anchor="middle" font-size="14" font-weight="bold">Hockey Net - Shot Zones</text>
        <text x="150" y="185" text-anchor="middle" font-size="10" fill="#888">Goalie perspective (looking out)</text>
    </svg>
    '''


def generate_rink_svg():
    """Generate SVG visualization of hockey rink with zones and coordinates."""
    return '''
    <svg viewBox="0 0 600 260" style="max-width:800px; border:1px solid #ddd; background:#fff;">
        <!-- Rink outline -->
        <rect x="10" y="10" width="580" height="240" rx="60" ry="60" fill="#e8f4f8" stroke="#333" stroke-width="2"/>
        
        <!-- Center line -->
        <line x1="300" y1="10" x2="300" y2="250" stroke="#c00" stroke-width="3"/>
        
        <!-- Blue lines -->
        <line x1="175" y1="10" x2="175" y2="250" stroke="#00f" stroke-width="3"/>
        <line x1="425" y1="10" x2="425" y2="250" stroke="#00f" stroke-width="3"/>
        
        <!-- Goal lines -->
        <line x1="60" y1="10" x2="60" y2="250" stroke="#c00" stroke-width="2"/>
        <line x1="540" y1="10" x2="540" y2="250" stroke="#c00" stroke-width="2"/>
        
        <!-- Goal creases -->
        <path d="M 60 105 A 25 25 0 0 1 60 155" fill="none" stroke="#c00" stroke-width="2"/>
        <path d="M 540 105 A 25 25 0 0 0 540 155" fill="none" stroke="#c00" stroke-width="2"/>
        
        <!-- Center circle -->
        <circle cx="300" cy="130" r="30" fill="none" stroke="#00f" stroke-width="2"/>
        
        <!-- Zone labels with coordinates -->
        <text x="40" y="130" text-anchor="middle" font-size="14" font-weight="bold" fill="#333">DZ</text>
        <text x="40" y="150" text-anchor="middle" font-size="10" fill="#666">(0-75)</text>
        
        <text x="117" y="130" text-anchor="middle" font-size="14" font-weight="bold" fill="#333">DZ</text>
        <text x="117" y="150" text-anchor="middle" font-size="10" fill="#666">(Home)</text>
        
        <text x="300" y="180" text-anchor="middle" font-size="14" font-weight="bold" fill="#333">NZ</text>
        <text x="300" y="200" text-anchor="middle" font-size="10" fill="#666">(175-425)</text>
        
        <text x="483" y="130" text-anchor="middle" font-size="14" font-weight="bold" fill="#333">OZ</text>
        <text x="483" y="150" text-anchor="middle" font-size="10" fill="#666">(Away)</text>
        
        <text x="560" y="130" text-anchor="middle" font-size="14" font-weight="bold" fill="#333">OZ</text>
        <text x="560" y="150" text-anchor="middle" font-size="10" fill="#666">(425-600)</text>
        
        <!-- Coordinate system -->
        <text x="10" y="245" font-size="10" fill="#888">X: 0</text>
        <text x="170" y="245" font-size="10" fill="#888">X: 175</text>
        <text x="295" y="245" font-size="10" fill="#888">X: 300</text>
        <text x="420" y="245" font-size="10" fill="#888">X: 425</text>
        <text x="570" y="245" font-size="10" fill="#888">X: 600</text>
        
        <!-- Title -->
        <text x="300" y="30" text-anchor="middle" font-size="16" font-weight="bold">Ice Rink - Zone Coordinates</text>
        
        <!-- Legend -->
        <text x="300" y="50" text-anchor="middle" font-size="11" fill="#666">DZ=Defensive Zone | NZ=Neutral Zone | OZ=Offensive Zone</text>
    </svg>
    '''


def generate_html_documentation():
    """Generate comprehensive HTML documentation."""
    logger.info("Generating HTML documentation...")
    
    # Create directories
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    HTML_TABLES_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = get_mtn_timestamp()
    
    # Get all tables
    csv_files = sorted(OUTPUT_DIR.glob('*.csv'))
    
    # Categorize tables
    dim_tables = [f for f in csv_files if f.stem.startswith('dim_')]
    fact_tables = [f for f in csv_files if f.stem.startswith('fact_')]
    qa_tables = [f for f in csv_files if f.stem.startswith('qa_')]
    
    # Generate main index
    _generate_main_index(dim_tables, fact_tables, qa_tables, timestamp)
    
    # Generate individual table pages in subfolder
    for csv_file in csv_files:
        _generate_table_page(csv_file, timestamp)
    
    # Generate special pages
    _generate_changelog_html(timestamp)
    _generate_schema_diagram_html(timestamp)
    
    logger.info(f"  Generated {len(csv_files)} table pages + index + special pages")


def _generate_main_index(dim_tables, fact_tables, qa_tables, timestamp):
    """Generate main index.html."""
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BenchSight Data Dictionary v{VERSION}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ color: #1a1a2e; border-bottom: 3px solid #4a4e69; padding-bottom: 10px; }}
        h2 {{ color: #4a4e69; margin-top: 30px; }}
        .version-badge {{ background: #4a4e69; color: white; padding: 5px 15px; border-radius: 20px; font-size: 14px; }}
        .timestamp {{ color: #888; font-size: 12px; margin-top: 5px; }}
        .quick-links {{ background: #4a4e69; color: white; padding: 15px 20px; border-radius: 8px; margin: 20px 0; }}
        .quick-links a {{ color: #fff; margin-right: 20px; text-decoration: none; }}
        .quick-links a:hover {{ text-decoration: underline; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }}
        .summary-item {{ background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .summary-number {{ font-size: 36px; font-weight: bold; color: #4a4e69; }}
        .summary-label {{ color: #888; font-size: 14px; }}
        .doc-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; margin: 20px 0; }}
        .doc-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .doc-card h3 {{ margin-top: 0; }}
        .doc-card h3 a {{ color: #4a4e69; text-decoration: none; }}
        .doc-card h3 a:hover {{ text-decoration: underline; }}
        .doc-card p {{ color: #666; font-size: 14px; margin-bottom: 0; }}
        .table-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 10px; }}
        .table-item {{ background: white; padding: 12px 15px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .table-item:hover {{ box-shadow: 0 3px 8px rgba(0,0,0,0.15); }}
        .table-item a {{ color: #4a4e69; text-decoration: none; font-weight: 500; }}
        .table-item a:hover {{ color: #22223b; }}
        .table-meta {{ color: #888; font-size: 11px; margin-top: 3px; }}
        footer {{ margin-top: 40px; padding: 20px; text-align: center; color: #888; font-size: 12px; border-top: 1px solid #ddd; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏒 BenchSight Data Dictionary <span class="version-badge">v{VERSION}</span></h1>
        <p class="timestamp">Generated: {timestamp} (US Mountain Time)</p>
        
        <div class="quick-links">
            <strong>Quick Links:</strong>
            <a href="changelog.html">📝 Changelog</a>
            <a href="schema_diagram.html">🗂️ Schema Diagram</a>
            <a href="../LLM_REQUIREMENTS.md">📋 Requirements</a>
            <a href="../HONEST_ASSESSMENT.md">🔍 Assessment</a>
        </div>
        
        <div class="summary">
            <div class="summary-item">
                <div class="summary-number">{len(dim_tables)}</div>
                <div class="summary-label">Dimensions</div>
            </div>
            <div class="summary-item">
                <div class="summary-number">{len(fact_tables)}</div>
                <div class="summary-label">Facts</div>
            </div>
            <div class="summary-item">
                <div class="summary-number">{len(qa_tables)}</div>
                <div class="summary-label">QA Tables</div>
            </div>
            <div class="summary-item">
                <div class="summary-number">{len(dim_tables) + len(fact_tables) + len(qa_tables)}</div>
                <div class="summary-label">Total Tables</div>
            </div>
        </div>
        
        <h2>📚 Documentation</h2>
        <div class="doc-grid">
            <div class="doc-card">
                <h3><a href="../LLM_REQUIREMENTS.md">LLM Requirements</a></h3>
                <p>Critical rules and constraints for working with BenchSight</p>
            </div>
            <div class="doc-card">
                <h3><a href="changelog.html">Changelog</a></h3>
                <p>Version history and recent changes</p>
            </div>
            <div class="doc-card">
                <h3><a href="schema_diagram.html">Schema Diagram</a></h3>
                <p>Visual representation of table relationships</p>
            </div>
            <div class="doc-card">
                <h3><a href="../HONEST_ASSESSMENT.md">Honest Assessment</a></h3>
                <p>Known issues and technical debt</p>
            </div>
        </div>
        
        <h2>📊 Dimension Tables ({len(dim_tables)})</h2>
        <div class="table-grid">
            {_generate_table_links(dim_tables)}
        </div>
        
        <h2>📈 Fact Tables ({len(fact_tables)})</h2>
        <div class="table-grid">
            {_generate_table_links(fact_tables)}
        </div>
        
        <h2>🔍 QA Tables ({len(qa_tables)})</h2>
        <div class="table-grid">
            {_generate_table_links(qa_tables)}
        </div>
        
        <footer>
            BenchSight v{VERSION} | NORAD Hockey Analytics | {timestamp}
        </footer>
    </div>
</body>
</html>'''
    
    (HTML_DIR / 'index.html').write_text(html)


def _generate_table_links(tables):
    """Generate HTML links for table list."""
    links = []
    for f in tables:
        try:
            row_count = sum(1 for _ in open(f)) - 1
            df = pd.read_csv(f, nrows=1)
            col_count = len(df.columns)
        except:
            row_count = 0
            col_count = 0
        
        links.append(f'''
            <div class="table-item">
                <a href="tables/{f.stem}.html">{f.stem}</a>
                <div class="table-meta">{row_count:,} rows × {col_count} cols</div>
            </div>
        ''')
    
    return '\n'.join(links)


def _generate_table_page(csv_file, timestamp):
    """Generate detailed page for a single table with data dictionary."""
    table_name = csv_file.stem
    
    try:
        df = pd.read_csv(csv_file, low_memory=False)
        row_count = len(df)
        preview = df.head(20)
    except Exception as e:
        logger.warning(f"Error reading {table_name}: {e}")
        return
    
    # Build column info with data dictionary
    col_info = []
    for col in df.columns:
        non_null = df[col].notna().sum()
        null_pct = (1 - non_null / len(df)) * 100 if len(df) > 0 else 0
        dtype = str(df[col].dtype)
        
        # Get data dictionary entry if exists
        dd_entry = DATA_DICTIONARY.get(col, {})
        formula = dd_entry.get('formula', '-')
        source = dd_entry.get('source', 'Explicit' if col.endswith('_id') else 'Derived')
        
        col_info.append({
            'name': col,
            'dtype': dtype,
            'non_null': non_null,
            'null_pct': f'{null_pct:.1f}%',
            'formula': formula,
            'source': source,
        })
    
    # Get flowchart if exists
    flowchart = TABLE_FLOWCHARTS.get(table_name, {})
    flowchart_html = ''
    if flowchart:
        steps = '<br>'.join(flowchart.get('process', []))
        deps = ', '.join(flowchart.get('depends_on', []))
        flowchart_html = f'''
        <div class="flowchart">
            <h3>📊 Table Derivation</h3>
            <p><strong>Sources:</strong> {', '.join(flowchart.get('sources', []))}</p>
            <p><strong>Process:</strong><br>{steps}</p>
            <p><strong>Depends On:</strong> {deps}</p>
        </div>
        '''
    
    # Special visualizations for certain tables
    special_viz = ''
    if table_name == 'dim_net_location':
        special_viz = f'<h3>🥅 Net Zone Visualization</h3>{generate_net_svg()}'
    elif table_name == 'dim_zone':
        special_viz = f'<h3>🏒 Rink Zone Visualization</h3>{generate_rink_svg()}'
    
    # Generate column table rows
    col_rows = '\n'.join([
        f'''<tr>
            <td><code>{c['name']}</code></td>
            <td>{c['dtype']}</td>
            <td>{c['non_null']:,}</td>
            <td>{c['null_pct']}</td>
            <td>{c['source']}</td>
            <td style="font-size:11px;">{c['formula']}</td>
        </tr>'''
        for c in col_info
    ])
    
    # Generate preview table
    preview_html = preview.to_html(classes='preview-table', index=False, na_rep='NULL', max_cols=15)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{table_name} - BenchSight</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1600px; margin: 0 auto; }}
        h1 {{ color: #1a1a2e; }}
        h2, h3 {{ color: #4a4e69; }}
        .breadcrumb {{ margin-bottom: 20px; }}
        .breadcrumb a {{ color: #4a4e69; text-decoration: none; }}
        .breadcrumb a:hover {{ text-decoration: underline; }}
        .meta {{ background: #4a4e69; color: white; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .meta span {{ margin-right: 30px; }}
        table {{ border-collapse: collapse; width: 100%; background: white; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #4a4e69; color: white; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        .preview-table {{ font-size: 12px; overflow-x: auto; display: block; }}
        .flowchart {{ background: #e8f4f8; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        code {{ background: #eee; padding: 2px 6px; border-radius: 3px; font-size: 13px; }}
        .timestamp {{ color: #888; font-size: 12px; }}
        svg {{ margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="breadcrumb">
            <a href="../index.html">← Back to Index</a>
        </div>
        
        <h1>📋 {table_name}</h1>
        <p class="timestamp">Generated: {timestamp} (US Mountain Time)</p>
        
        <div class="meta">
            <span><strong>Rows:</strong> {row_count:,}</span>
            <span><strong>Columns:</strong> {len(df.columns)}</span>
            <span><strong>Type:</strong> {'Dimension' if table_name.startswith('dim_') else 'Fact' if table_name.startswith('fact_') else 'QA'}</span>
        </div>
        
        {special_viz}
        
        {flowchart_html}
        
        <h2>📝 Column Schema & Data Dictionary</h2>
        <table>
            <tr>
                <th>Column</th>
                <th>Type</th>
                <th>Non-Null</th>
                <th>Null %</th>
                <th>Source</th>
                <th>Formula/Derivation</th>
            </tr>
            {col_rows}
        </table>
        
        <h2>👀 Data Preview (First 20 Rows)</h2>
        <div style="overflow-x: auto;">
            {preview_html}
        </div>
    </div>
</body>
</html>'''
    
    (HTML_TABLES_DIR / f'{table_name}.html').write_text(html)


def _generate_changelog_html(timestamp):
    """Generate changelog HTML page."""
    
    # Read markdown changelog
    changelog_md = DOCS_DIR / 'CHANGELOG.md'
    changelog_content = changelog_md.read_text() if changelog_md.exists() else "No changelog found."
    
    # Simple markdown to HTML conversion
    changelog_html = changelog_content.replace('\n## ', '\n<h2>').replace('\n### ', '\n<h3>')
    changelog_html = changelog_html.replace('\n- ', '\n<li>').replace('\n**', '\n<strong>').replace('**', '</strong>')
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Changelog - BenchSight</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #1a1a2e; border-bottom: 3px solid #4a4e69; padding-bottom: 10px; }}
        h2 {{ color: #4a4e69; margin-top: 30px; }}
        h3 {{ color: #666; }}
        li {{ margin: 5px 0; }}
        .breadcrumb a {{ color: #4a4e69; }}
        .timestamp {{ color: #888; font-size: 12px; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <p class="breadcrumb"><a href="index.html">← Back to Index</a></p>
        <h1>📝 Changelog</h1>
        <p class="timestamp">Generated: {timestamp}</p>
        <pre>{changelog_content}</pre>
    </div>
</body>
</html>'''
    
    (HTML_DIR / 'changelog.html').write_text(html)


def _generate_schema_diagram_html(timestamp):
    """Generate schema diagram HTML page."""
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Schema Diagram - BenchSight</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; }}
        h1 {{ color: #1a1a2e; border-bottom: 3px solid #4a4e69; padding-bottom: 10px; }}
        h2 {{ color: #4a4e69; }}
        .breadcrumb a {{ color: #4a4e69; }}
        .timestamp {{ color: #888; font-size: 12px; }}
        .diagram {{ background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .table-box {{ display: inline-block; background: white; border: 2px solid #4a4e69; border-radius: 5px; padding: 10px; margin: 10px; min-width: 150px; }}
        .table-box.dim {{ border-color: #28a745; }}
        .table-box.fact {{ border-color: #007bff; }}
        .table-box.qa {{ border-color: #ffc107; }}
        .table-box h4 {{ margin: 0 0 10px 0; font-size: 12px; }}
        .table-box ul {{ margin: 0; padding-left: 15px; font-size: 11px; }}
        .legend {{ margin: 20px 0; }}
        .legend span {{ display: inline-block; padding: 5px 10px; margin-right: 10px; border-radius: 3px; font-size: 12px; }}
        .legend .dim {{ background: #d4edda; border: 1px solid #28a745; }}
        .legend .fact {{ background: #cce5ff; border: 1px solid #007bff; }}
        .legend .qa {{ background: #fff3cd; border: 1px solid #ffc107; }}
    </style>
</head>
<body>
    <div class="container">
        <p class="breadcrumb"><a href="index.html">← Back to Index</a></p>
        <h1>🗂️ Schema Diagram</h1>
        <p class="timestamp">Generated: {timestamp} (US Mountain Time) | v{VERSION}</p>
        
        <div class="legend">
            <strong>Legend:</strong>
            <span class="dim">Dimension</span>
            <span class="fact">Fact</span>
            <span class="qa">QA</span>
        </div>
        
        <h2>Core Event & Shift Tables</h2>
        <div class="diagram">
            <div class="table-box fact">
                <h4>fact_event_players</h4>
                <ul><li>107 columns</li><li>One row per player-event</li><li>Primary event table</li></ul>
            </div>
            <div class="table-box fact">
                <h4>fact_shifts</h4>
                <ul><li>138 columns</li><li>One row per shift</li><li>Wide format</li></ul>
            </div>
            <div class="table-box fact">
                <h4>fact_shift_players</h4>
                <ul><li>32 columns</li><li>One row per player-shift</li><li>Long format</li></ul>
            </div>
        </div>
        
        <h2>Player Statistics</h2>
        <div class="diagram">
            <div class="table-box fact">
                <h4>fact_player_game_stats</h4>
                <ul><li>Per-game player stats</li><li>Goals, assists, shots</li></ul>
            </div>
            <div class="table-box fact">
                <h4>fact_player_season_stats</h4>
                <ul><li>Season aggregates</li></ul>
            </div>
            <div class="table-box fact">
                <h4>fact_player_career_stats</h4>
                <ul><li>Career totals</li></ul>
            </div>
        </div>
        
        <h2>Key Dimensions</h2>
        <div class="diagram">
            <div class="table-box dim">
                <h4>dim_player</h4>
                <ul><li>Player info</li><li>PK: player_id</li></ul>
            </div>
            <div class="table-box dim">
                <h4>dim_team</h4>
                <ul><li>Team info</li><li>PK: team_id</li></ul>
            </div>
            <div class="table-box dim">
                <h4>dim_schedule</h4>
                <ul><li>Game schedule</li><li>PK: game_id</li></ul>
            </div>
            <div class="table-box dim">
                <h4>dim_event_type</h4>
                <ul><li>Event types</li><li>PK: event_type_id</li></ul>
            </div>
            <div class="table-box dim">
                <h4>dim_zone</h4>
                <ul><li>Ice zones</li><li>PK: zone_id</li></ul>
            </div>
        </div>
        
        <h2>Table Relationships</h2>
        <pre style="background:#f4f4f4; padding:15px; border-radius:5px; font-size:12px;">
fact_event_players
  → dim_player (player_id)
  → dim_event_type (event_type_id)
  → dim_event_detail (event_detail_id)
  → dim_zone (zone_id)
  → dim_schedule (game_id)

fact_shifts
  → dim_player (player columns)
  → dim_shift_duration (shift_duration_id)
  → dim_schedule (game_id)

fact_shift_players
  → fact_shifts (shift_key)
  → dim_player (player_id)

fact_player_game_stats
  → dim_player (player_id)
  → dim_schedule (game_id)
  → dim_team (team_id)
        </pre>
    </div>
</body>
</html>'''
    
    (HTML_DIR / 'schema_diagram.html').write_text(html)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_all_v11_03_enhancements():
    """Run all v11.03 enhancements."""
    logger.info("=" * 60)
    logger.info(f"RUNNING V{VERSION} ENHANCEMENTS")
    logger.info("=" * 60)
    
    # 1. Fix dimension key formatting
    key_mappings = fix_dimension_keys()
    
    # 2. Update foreign keys
    update_foreign_keys(key_mappings)
    
    # 3. Remove unused CSAHA
    remove_csaha_league()
    
    # 4. Consolidate shift tables
    consolidate_shift_tables()
    
    # 5. Generate HTML documentation
    generate_html_documentation()
    
    # 6. Update version stamp
    version_content = f"""BenchSight Data Warehouse
========================
Version: {VERSION}
Last Updated: {get_mtn_timestamp()}
Generated By: ETL Pipeline v{VERSION}

Tables: {len(list(OUTPUT_DIR.glob('*.csv')))}
Timezone: US Mountain Time

This file is automatically updated when the ETL runs.
"""
    (OUTPUT_DIR / 'VERSION.txt').write_text(version_content)
    (DOCS_DIR / 'VERSION.txt').write_text(version_content)
    
    logger.info("\n" + "=" * 60)
    logger.info(f"V{VERSION} ENHANCEMENTS COMPLETE")
    logger.info("=" * 60)


if __name__ == '__main__':
    run_all_v11_03_enhancements()
