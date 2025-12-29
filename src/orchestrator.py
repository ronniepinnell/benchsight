#!/usr/bin/env python3
"""
=============================================================================
BENCHSIGHT ORCHESTRATOR - Web-Based Control Center
=============================================================================
File: orchestrator.py

PURPOSE:
    Single web UI for all BenchSight operations. Run this file and open
    your browser to control everything from loading data to exporting.

USAGE:
    python orchestrator.py
    Then open: http://localhost:5001

FEATURES:
    - Load/refresh BLB_Tables.xlsx
    - View and manage tracked games
    - Extract rosters for tracker
    - Run data export pipeline
    - View output files and stats
    - Open tracker for any game
    - PostgreSQL database setup
    - One-click Wix deployment prep

=============================================================================
"""

import os
import sys
import json
import shutil
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime
from io import StringIO

# Check for Flask
try:
    from flask import Flask, render_template_string, request, jsonify, redirect, url_for, send_file
except ImportError:
    print("\n❌ Flask not installed. Run: pip install flask")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("\n❌ pandas not installed. Run: pip install pandas openpyxl")
    sys.exit(1)

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = DATA_DIR / 'output'
RAW_GAMES_DIR = DATA_DIR / 'raw' / 'games'
BLB_FILE = DATA_DIR / 'BLB_Tables.xlsx'
TRACKER_FILE = BASE_DIR / 'tracker' / 'tracker_v16.html'
HTML_DIR = BASE_DIR / 'html'
SQL_DIR = BASE_DIR / 'sql'

app = Flask(__name__)

# =============================================================================
# DATA FUNCTIONS
# =============================================================================

def get_blb_info():
    """Get BLB_Tables information."""
    info = {
        'exists': BLB_FILE.exists(),
        'path': str(BLB_FILE),
        'sheets': [],
        'total_rows': 0,
        'last_modified': None
    }
    
    if info['exists']:
        info['last_modified'] = datetime.fromtimestamp(
            BLB_FILE.stat().st_mtime
        ).strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            xl = pd.ExcelFile(BLB_FILE)
            for sheet in xl.sheet_names:
                df = pd.read_excel(xl, sheet_name=sheet)
                sheet_info = {'name': sheet, 'rows': len(df), 'cols': len(df.columns)}
                info['sheets'].append(sheet_info)
                info['total_rows'] += len(df)
        except Exception as e:
            info['error'] = str(e)
    
    return info


def get_games_list():
    """Get list of all games with their status."""
    games = []
    
    if not RAW_GAMES_DIR.exists():
        return games
    
    for game_dir in sorted(RAW_GAMES_DIR.iterdir()):
        if not game_dir.is_dir() or game_dir.name.startswith('.'):
            continue
        
        game = {
            'id': game_dir.name,
            'path': str(game_dir),
            'has_tracking': False,
            'has_roster': False,
            'tracking_file': None,
            'events': 0,
            'shifts': 0,
            'roster_home': 0,
            'roster_away': 0
        }
        
        # Check for tracking file
        tracking_files = list(game_dir.glob('*tracking*.xlsx')) + list(game_dir.glob('*_tracking.xlsx'))
        if tracking_files:
            game['has_tracking'] = True
            game['tracking_file'] = tracking_files[0].name
            
            try:
                xl = pd.ExcelFile(tracking_files[0])
                if 'events' in xl.sheet_names:
                    game['events'] = len(pd.read_excel(xl, 'events'))
                if 'shifts' in xl.sheet_names:
                    game['shifts'] = len(pd.read_excel(xl, 'shifts'))
            except:
                pass
        
        # Check for roster
        roster_file = game_dir / 'roster.json'
        if roster_file.exists():
            game['has_roster'] = True
            try:
                with open(roster_file) as f:
                    roster = json.load(f)
                    game['roster_home'] = len(roster.get('homeRoster', []))
                    game['roster_away'] = len(roster.get('awayRoster', []))
            except:
                pass
        
        games.append(game)
    
    return games


def get_output_info():
    """Get information about output files."""
    info = {
        'exists': OUTPUT_DIR.exists(),
        'files': [],
        'total_files': 0,
        'total_size': 0
    }
    
    if info['exists']:
        for f in sorted(OUTPUT_DIR.glob('*.csv')):
            file_info = {
                'name': f.name,
                'size': f.stat().st_size,
                'rows': 0
            }
            try:
                df = pd.read_csv(f)
                file_info['rows'] = len(df)
            except:
                pass
            info['files'].append(file_info)
            info['total_size'] += file_info['size']
        
        info['total_files'] = len(info['files'])
    
    return info


def extract_roster_for_game(game_id):
    """Extract roster for a specific game from BLB_Tables."""
    result = {'success': False, 'message': '', 'home': 0, 'away': 0}
    
    if not BLB_FILE.exists():
        result['message'] = 'BLB_Tables.xlsx not found'
        return result
    
    try:
        xl = pd.ExcelFile(BLB_FILE)
        
        # Find roster sheet
        roster_sheet = None
        for sheet in ['fact_gameroster', 'gameroster', 'roster', 'GameRoster']:
            if sheet in xl.sheet_names:
                roster_sheet = sheet
                break
        
        if not roster_sheet:
            result['message'] = f'No roster sheet found. Available: {xl.sheet_names}'
            return result
        
        roster_df = pd.read_excel(xl, sheet_name=roster_sheet)
        
        # Find game_id column
        game_col = None
        for col in ['game_id', 'GameID', 'game_id_num', 'GAME_ID']:
            if col in roster_df.columns:
                game_col = col
                break
        
        if not game_col:
            result['message'] = f'No game_id column found. Columns: {list(roster_df.columns)}'
            return result
        
        # Filter for game
        game_roster = roster_df[roster_df[game_col] == int(game_id)]
        
        if len(game_roster) == 0:
            result['message'] = f'No roster data for game {game_id}'
            return result
        
        # Build roster JSON
        roster_data = {'gid': str(game_id), 'homeRoster': [], 'awayRoster': []}
        
        # Column mappings
        num_col = next((c for c in ['player_game_number', 'player_number', 'jersey', 'number'] if c in game_roster.columns), None)
        name_col = next((c for c in ['player_full_name', 'display_name', 'name', 'Player'] if c in game_roster.columns), None)
        venue_col = next((c for c in ['team_venue', 'venue', 'home_away'] if c in game_roster.columns), None)
        pos_col = next((c for c in ['player_position', 'position', 'pos'] if c in game_roster.columns), None)
        skill_col = next((c for c in ['skill_rating', 'skill', 'rating'] if c in game_roster.columns), None)
        
        for _, row in game_roster.iterrows():
            try:
                num = int(row[num_col]) if num_col and pd.notna(row[num_col]) else 0
            except:
                num = 0
            
            player = {
                'n': num,
                'name': str(row[name_col]) if name_col and pd.notna(row[name_col]) else f'#{num}',
                'pos': str(row[pos_col])[0].upper() if pos_col and pd.notna(row[pos_col]) else 'F',
                'skill': int(row[skill_col]) if skill_col and pd.notna(row[skill_col]) else 4
            }
            
            venue = str(row[venue_col]).lower() if venue_col and pd.notna(row[venue_col]) else ''
            
            if 'home' in venue or venue == 'h':
                roster_data['homeRoster'].append(player)
            else:
                roster_data['awayRoster'].append(player)
        
        # Save roster
        game_dir = RAW_GAMES_DIR / str(game_id)
        game_dir.mkdir(parents=True, exist_ok=True)
        
        roster_file = game_dir / 'roster.json'
        with open(roster_file, 'w') as f:
            json.dump(roster_data, f, indent=2)
        
        result['success'] = True
        result['home'] = len(roster_data['homeRoster'])
        result['away'] = len(roster_data['awayRoster'])
        result['message'] = f'Extracted {result["home"]} home, {result["away"]} away players'
        
    except Exception as e:
        result['message'] = str(e)
    
    return result


def run_data_export():
    """Run the data export pipeline."""
    result = {'success': False, 'message': '', 'details': []}
    
    try:
        # Import export functions
        from export_all_data import Config as ExportConfig, run_export, load_blb_tables
        
        # Load BLB
        result['details'].append('Loading BLB_Tables.xlsx...')
        blb_data = load_blb_tables(BLB_FILE)
        
        if not blb_data:
            result['message'] = 'Failed to load BLB_Tables.xlsx'
            return result
        
        result['details'].append(f'Loaded {len(blb_data)} sheets from BLB_Tables')
        
        # Find games
        games = []
        for game_dir in RAW_GAMES_DIR.iterdir():
            if game_dir.is_dir():
                games.append(game_dir)
        
        result['details'].append(f'Found {len(games)} game directories')
        
        # Run export
        export_result = run_export(games, OUTPUT_DIR, blb_data)
        
        result['success'] = True
        result['message'] = f'Export complete! {export_result.get("events", 0)} events, {export_result.get("shifts", 0)} shifts'
        result['details'].append(result['message'])
        
    except ImportError:
        # Fallback: run as subprocess
        try:
            export_script = BASE_DIR / 'export_all_data.py'
            if export_script.exists():
                proc = subprocess.run(
                    [sys.executable, str(export_script)],
                    capture_output=True,
                    text=True,
                    cwd=str(BASE_DIR)
                )
                result['success'] = proc.returncode == 0
                result['message'] = 'Export completed via subprocess'
                result['details'] = proc.stdout.split('\n')
                if proc.stderr:
                    result['details'].extend(proc.stderr.split('\n'))
            else:
                result['message'] = 'export_all_data.py not found'
        except Exception as e:
            result['message'] = f'Subprocess error: {str(e)}'
    
    except Exception as e:
        result['message'] = str(e)
    
    return result


# =============================================================================
# HTML TEMPLATE
# =============================================================================

ORCHESTRATOR_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BenchSight Orchestrator</title>
    <style>
        :root {
            --bg-dark: #0a0a0f;
            --bg-card: #12121a;
            --bg-hover: #1a1a24;
            --border: #2a2a3a;
            --text: #e0e0e0;
            --text-dim: #888;
            --accent: #00d4ff;
            --success: #00ff88;
            --warning: #ff8800;
            --danger: #ff4466;
            --purple: #aa66ff;
        }
        
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-dark);
            color: var(--text);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container { max-width: 1400px; margin: 0 auto; }
        
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 0;
            border-bottom: 1px solid var(--border);
            margin-bottom: 30px;
        }
        
        h1 {
            font-size: 28px;
            color: var(--accent);
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        h1 .logo { font-size: 32px; }
        
        .status-bar {
            display: flex;
            gap: 20px;
            font-size: 14px;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }
        
        .status-dot.green { background: var(--success); }
        .status-dot.yellow { background: var(--warning); }
        .status-dot.red { background: var(--danger); }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }
        
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border);
        }
        
        .card-title {
            font-size: 16px;
            font-weight: 600;
            color: var(--accent);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .card-title .icon { font-size: 20px; }
        
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        
        .btn-primary {
            background: var(--accent);
            color: #000;
        }
        
        .btn-primary:hover {
            background: #00b8e0;
            transform: translateY(-1px);
        }
        
        .btn-success {
            background: var(--success);
            color: #000;
        }
        
        .btn-warning {
            background: var(--warning);
            color: #000;
        }
        
        .btn-secondary {
            background: var(--bg-hover);
            color: var(--text);
            border: 1px solid var(--border);
        }
        
        .btn-secondary:hover {
            background: var(--border);
        }
        
        .btn-sm {
            padding: 5px 10px;
            font-size: 12px;
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .stat-box {
            background: var(--bg-dark);
            border-radius: 8px;
            padding: 12px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 24px;
            font-weight: 700;
            color: var(--accent);
        }
        
        .stat-label {
            font-size: 11px;
            color: var(--text-dim);
            text-transform: uppercase;
            margin-top: 4px;
        }
        
        .table-wrapper {
            max-height: 300px;
            overflow-y: auto;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        
        th, td {
            padding: 10px 12px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }
        
        th {
            background: var(--bg-dark);
            color: var(--text-dim);
            font-weight: 500;
            text-transform: uppercase;
            font-size: 11px;
            position: sticky;
            top: 0;
        }
        
        tr:hover { background: var(--bg-hover); }
        
        .badge {
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 500;
        }
        
        .badge-success { background: rgba(0, 255, 136, 0.2); color: var(--success); }
        .badge-warning { background: rgba(255, 136, 0, 0.2); color: var(--warning); }
        .badge-danger { background: rgba(255, 68, 102, 0.2); color: var(--danger); }
        
        .action-buttons {
            display: flex;
            gap: 6px;
        }
        
        .log-output {
            background: var(--bg-dark);
            border-radius: 8px;
            padding: 15px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 12px;
            max-height: 200px;
            overflow-y: auto;
            white-space: pre-wrap;
            color: var(--text-dim);
        }
        
        .log-output .success { color: var(--success); }
        .log-output .error { color: var(--danger); }
        .log-output .info { color: var(--accent); }
        
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .input-group input, .input-group select {
            flex: 1;
            padding: 10px 14px;
            background: var(--bg-dark);
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text);
            font-size: 14px;
        }
        
        .input-group input:focus, .input-group select:focus {
            outline: none;
            border-color: var(--accent);
        }
        
        .quick-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px;
        }
        
        .full-width { grid-column: 1 / -1; }
        
        .loading {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid transparent;
            border-top-color: currentColor;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .section-title {
            font-size: 12px;
            color: var(--text-dim);
            text-transform: uppercase;
            margin: 15px 0 10px;
        }
        
        .file-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .file-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 12px;
            background: var(--bg-dark);
            border-radius: 6px;
        }
        
        .file-name { font-size: 13px; }
        .file-meta { font-size: 11px; color: var(--text-dim); }
        
        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            font-size: 14px;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        }
        
        .toast.success { background: var(--success); color: #000; }
        .toast.error { background: var(--danger); color: #fff; }
        
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        
        .modal.active { display: flex; }
        
        .modal-content {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 25px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .modal-close {
            background: none;
            border: none;
            color: var(--text-dim);
            font-size: 24px;
            cursor: pointer;
        }
        
        .workflow-steps {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .workflow-step {
            display: flex;
            align-items: flex-start;
            gap: 15px;
            padding: 15px;
            background: var(--bg-dark);
            border-radius: 8px;
            border-left: 3px solid var(--border);
        }
        
        .workflow-step.active { border-left-color: var(--accent); }
        .workflow-step.complete { border-left-color: var(--success); }
        
        .step-number {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: var(--border);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 14px;
        }
        
        .workflow-step.active .step-number { background: var(--accent); color: #000; }
        .workflow-step.complete .step-number { background: var(--success); color: #000; }
        
        .step-content { flex: 1; }
        .step-title { font-weight: 600; margin-bottom: 5px; }
        .step-desc { font-size: 13px; color: var(--text-dim); }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>
                <span class="logo">🏒</span>
                BenchSight Orchestrator
            </h1>
            <div class="status-bar">
                <div class="status-item">
                    <span class="status-dot {{ 'green' if blb_info.exists else 'red' }}"></span>
                    <span>BLB Data</span>
                </div>
                <div class="status-item">
                    <span class="status-dot {{ 'green' if games|length > 0 else 'yellow' }}"></span>
                    <span>{{ games|length }} Games</span>
                </div>
                <div class="status-item">
                    <span class="status-dot {{ 'green' if output_info.total_files > 0 else 'yellow' }}"></span>
                    <span>{{ output_info.total_files }} Output Files</span>
                </div>
            </div>
        </header>
        
        <div class="grid">
            <!-- BLB TABLES CARD -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">
                        <span class="icon">📊</span>
                        Master Data (BLB_Tables)
                    </div>
                    <button class="btn btn-primary btn-sm" onclick="refreshBLB()">
                        🔄 Refresh
                    </button>
                </div>
                
                {% if blb_info.exists %}
                <div class="stat-grid">
                    <div class="stat-box">
                        <div class="stat-value">{{ blb_info.sheets|length }}</div>
                        <div class="stat-label">Sheets</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{{ blb_info.total_rows|default(0) }}</div>
                        <div class="stat-label">Total Rows</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{{ blb_info.last_modified[:10] if blb_info.last_modified else 'N/A' }}</div>
                        <div class="stat-label">Last Modified</div>
                    </div>
                </div>
                
                <div class="section-title">Sheets</div>
                <div class="table-wrapper" style="max-height: 150px;">
                    <table>
                        <thead>
                            <tr>
                                <th>Sheet Name</th>
                                <th>Rows</th>
                                <th>Cols</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for sheet in blb_info.sheets[:10] %}
                            <tr>
                                <td>{{ sheet.name }}</td>
                                <td>{{ sheet.rows }}</td>
                                <td>{{ sheet.cols }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="log-output">
                    <span class="error">❌ BLB_Tables.xlsx not found</span><br>
                    Expected location: {{ blb_info.path }}
                </div>
                {% endif %}
            </div>
            
            <!-- GAMES MANAGEMENT CARD -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">
                        <span class="icon">🎮</span>
                        Tracked Games
                    </div>
                    <button class="btn btn-success btn-sm" onclick="extractAllRosters()">
                        👥 Extract All Rosters
                    </button>
                </div>
                
                <div class="stat-grid">
                    <div class="stat-box">
                        <div class="stat-value">{{ games|length }}</div>
                        <div class="stat-label">Games</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{{ games|selectattr('has_tracking')|list|length }}</div>
                        <div class="stat-label">With Tracking</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{{ games|selectattr('has_roster')|list|length }}</div>
                        <div class="stat-label">With Roster</div>
                    </div>
                </div>
                
                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th>Game ID</th>
                                <th>Events</th>
                                <th>Shifts</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for game in games %}
                            <tr>
                                <td><strong>{{ game.id }}</strong></td>
                                <td>{{ game.events }}</td>
                                <td>{{ game.shifts }}</td>
                                <td>
                                    {% if game.has_tracking %}
                                    <span class="badge badge-success">Tracked</span>
                                    {% else %}
                                    <span class="badge badge-warning">No Data</span>
                                    {% endif %}
                                    {% if game.has_roster %}
                                    <span class="badge badge-success">Roster</span>
                                    {% endif %}
                                </td>
                                <td class="action-buttons">
                                    <button class="btn btn-secondary btn-sm" onclick="openTracker('{{ game.id }}')">
                                        🎯 Track
                                    </button>
                                    <button class="btn btn-secondary btn-sm" onclick="extractRoster('{{ game.id }}')">
                                        👥
                                    </button>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                
                <div class="input-group" style="margin-top: 15px;">
                    <input type="text" id="newGameId" placeholder="Enter new Game ID...">
                    <button class="btn btn-primary" onclick="createGame()">
                        ➕ Create Game Folder
                    </button>
                </div>
            </div>
            
            <!-- EXPORT & PIPELINE CARD -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">
                        <span class="icon">⚙️</span>
                        Data Pipeline
                    </div>
                </div>
                
                <div class="workflow-steps">
                    <div class="workflow-step complete">
                        <div class="step-number">1</div>
                        <div class="step-content">
                            <div class="step-title">Load BLB_Tables</div>
                            <div class="step-desc">Master data with players, teams, schedule</div>
                        </div>
                        <span class="badge badge-success">Ready</span>
                    </div>
                    
                    <div class="workflow-step {{ 'complete' if games|selectattr('has_tracking')|list|length > 0 else '' }}">
                        <div class="step-number">2</div>
                        <div class="step-content">
                            <div class="step-title">Track Games</div>
                            <div class="step-desc">{{ games|selectattr('has_tracking')|list|length }} games tracked</div>
                        </div>
                    </div>
                    
                    <div class="workflow-step">
                        <div class="step-number">3</div>
                        <div class="step-content">
                            <div class="step-title">Export Data</div>
                            <div class="step-desc">Generate CSV files for analysis</div>
                        </div>
                        <button class="btn btn-primary btn-sm" onclick="runExport()" id="exportBtn">
                            ▶️ Run Export
                        </button>
                    </div>
                </div>
                
                <div class="section-title">Export Log</div>
                <div class="log-output" id="exportLog">
                    Ready to export. Click "Run Export" to process all games.
                </div>
            </div>
            
            <!-- OUTPUT FILES CARD -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">
                        <span class="icon">📁</span>
                        Output Files
                    </div>
                    <span class="file-meta">{{ (output_info.total_size / 1024 / 1024)|round(2) }} MB total</span>
                </div>
                
                <div class="stat-grid">
                    <div class="stat-box">
                        <div class="stat-value">{{ output_info.total_files }}</div>
                        <div class="stat-label">CSV Files</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{{ output_info.files|sum(attribute='rows') if output_info.files else 0 }}</div>
                        <div class="stat-label">Total Rows</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{{ (output_info.total_size / 1024)|round(0)|int }} KB</div>
                        <div class="stat-label">Size</div>
                    </div>
                </div>
                
                <div class="table-wrapper" style="max-height: 200px;">
                    <table>
                        <thead>
                            <tr>
                                <th>File</th>
                                <th>Rows</th>
                                <th>Size</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for file in output_info.files[:15] %}
                            <tr>
                                <td>{{ file.name }}</td>
                                <td>{{ file.rows }}</td>
                                <td>{{ (file.size / 1024)|round(1) }} KB</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- QUICK ACTIONS CARD (FULL WIDTH) -->
            <div class="card full-width">
                <div class="card-header">
                    <div class="card-title">
                        <span class="icon">🚀</span>
                        Quick Actions
                    </div>
                </div>
                
                <div class="quick-actions">
                    <button class="btn btn-primary" onclick="openTracker()">
                        🎯 Open Tracker
                    </button>
                    <button class="btn btn-success" onclick="openGamesBrowser()">
                        📋 All Games Browser
                    </button>
                    <button class="btn btn-success" onclick="openAdminPortal()">
                        🖥️ Admin Portal
                    </button>
                    <button class="btn btn-warning" onclick="runExport()">
                        📤 Export All Data
                    </button>
                    <button class="btn btn-secondary" onclick="openDashboard()">
                        📊 View Dashboard
                    </button>
                    <button class="btn btn-secondary" onclick="showPostgreSQLSetup()">
                        🗄️ PostgreSQL Setup
                    </button>
                    <button class="btn btn-secondary" onclick="showGitHubGuide()">
                        🐙 GitHub Deploy
                    </button>
                    <button class="btn btn-secondary" onclick="showWixGuide()">
                        🌐 Wix Embed
                    </button>
                    <button class="btn btn-secondary" onclick="openDocs()">
                        📖 Documentation
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- MODAL -->
    <div class="modal" id="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 id="modalTitle">Modal Title</h3>
                <button class="modal-close" onclick="closeModal()">×</button>
            </div>
            <div id="modalBody"></div>
        </div>
    </div>
    
    <!-- TOAST -->
    <div class="toast" id="toast" style="display: none;"></div>
    
    <script>
        // Toast notification
        function showToast(message, type = 'success') {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.className = 'toast ' + type;
            toast.style.display = 'block';
            setTimeout(() => { toast.style.display = 'none'; }, 3000);
        }
        
        // Modal
        function showModal(title, content) {
            document.getElementById('modalTitle').textContent = title;
            document.getElementById('modalBody').innerHTML = content;
            document.getElementById('modal').classList.add('active');
        }
        
        function closeModal() {
            document.getElementById('modal').classList.remove('active');
        }
        
        // Refresh BLB
        function refreshBLB() {
            location.reload();
        }
        
        // Open Tracker
        function openTracker(gameId = '') {
            let url = '/open-tracker';
            if (gameId) url += '?game=' + gameId;
            fetch(url).then(() => {
                showToast('Tracker opened in browser');
            });
        }
        
        // Open Games Browser
        function openGamesBrowser() {
            fetch('/open-games-browser').then(() => {
                showToast('Games Browser opened');
            });
        }
        
        // Open Admin Portal
        function openAdminPortal() {
            window.open('http://localhost:5000', '_blank');
            showToast('Opening Admin Portal...');
        }
        
        // Open Dashboard
        function openDashboard() {
            fetch('/open-dashboard').then(() => {
                showToast('Dashboard opened');
            });
        }
        
        // Open Docs
        function openDocs() {
            fetch('/open-docs').then(() => {
                showToast('Documentation opened');
            });
        }
        
        // Extract roster for single game
        function extractRoster(gameId) {
            fetch('/api/extract-roster?game=' + gameId)
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        showToast(data.message, 'success');
                        location.reload();
                    } else {
                        showToast(data.message, 'error');
                    }
                });
        }
        
        // Extract all rosters
        function extractAllRosters() {
            fetch('/api/extract-all-rosters')
                .then(r => r.json())
                .then(data => {
                    showToast(data.message, data.success ? 'success' : 'error');
                    if (data.success) location.reload();
                });
        }
        
        // Create new game folder
        function createGame() {
            const gameId = document.getElementById('newGameId').value.trim();
            if (!gameId) {
                showToast('Please enter a game ID', 'error');
                return;
            }
            fetch('/api/create-game?game=' + gameId)
                .then(r => r.json())
                .then(data => {
                    showToast(data.message, data.success ? 'success' : 'error');
                    if (data.success) location.reload();
                });
        }
        
        // Run export
        function runExport() {
            const btn = document.getElementById('exportBtn');
            const log = document.getElementById('exportLog');
            
            btn.disabled = true;
            btn.innerHTML = '<span class="loading"></span> Running...';
            log.innerHTML = '<span class="info">Starting export...</span>\\n';
            
            fetch('/api/run-export')
                .then(r => r.json())
                .then(data => {
                    btn.disabled = false;
                    btn.innerHTML = '▶️ Run Export';
                    
                    if (data.success) {
                        log.innerHTML = '<span class="success">✅ ' + data.message + '</span>\\n';
                        data.details.forEach(d => {
                            log.innerHTML += d + '\\n';
                        });
                        showToast('Export complete!', 'success');
                    } else {
                        log.innerHTML = '<span class="error">❌ ' + data.message + '</span>\\n';
                        showToast('Export failed', 'error');
                    }
                    
                    setTimeout(() => location.reload(), 2000);
                })
                .catch(err => {
                    btn.disabled = false;
                    btn.innerHTML = '▶️ Run Export';
                    log.innerHTML = '<span class="error">Error: ' + err + '</span>';
                });
        }
        
        // PostgreSQL setup guide
        function showPostgreSQLSetup() {
            showModal('PostgreSQL Setup', `
                <div class="log-output" style="max-height: 400px;">
<span class="info"># 1. Install PostgreSQL</span>
brew install postgresql   # macOS
sudo apt install postgresql   # Ubuntu

<span class="info"># 2. Start PostgreSQL</span>
brew services start postgresql   # macOS
sudo systemctl start postgresql  # Ubuntu

<span class="info"># 3. Create database</span>
psql -U postgres -c "CREATE DATABASE benchsight;"

<span class="info"># 4. Run setup script</span>
psql -U postgres -d benchsight -f sql/setup_complete_database.sql

<span class="success"># This creates:</span>
#   - staging schema (raw data)
#   - intermediate schema (transformed)
#   - hockey_mart schema (star schema)
                </div>
                <button class="btn btn-primary" style="margin-top: 15px;" onclick="copySQL()">
                    📋 Copy SQL File Path
                </button>
            `);
        }
        
        // GitHub guide
        function showGitHubGuide() {
            showModal('GitHub Deployment', `
                <div class="log-output" style="max-height: 400px;">
<span class="info"># 1. Initialize Git</span>
cd benchsight_merged
git init
git add .
git commit -m "Initial commit"

<span class="info"># 2. Create GitHub repo and push</span>
git remote add origin https://github.com/YOUR_USERNAME/benchsight.git
git branch -M main
git push -u origin main

<span class="info"># 3. Enable GitHub Pages</span>
# Go to Settings → Pages
# Source: Deploy from branch
# Branch: main / root

<span class="success"># Your URLs will be:</span>
https://YOUR_USERNAME.github.io/benchsight/html/dashboard_static.html
https://YOUR_USERNAME.github.io/benchsight/html/tracker_v16.html
                </div>
            `);
        }
        
        // Wix guide
        function showWixGuide() {
            showModal('Wix Embed Guide', `
                <div class="log-output" style="max-height: 400px;">
<span class="info"># 1. In Wix Editor, add HTML iframe</span>
Click Add (+) → Embed → HTML iframe

<span class="info"># 2. Paste this code:</span>
&lt;iframe 
    src="https://YOUR_USERNAME.github.io/benchsight/html/dashboard_static.html" 
    width="100%" 
    height="800px" 
    frameborder="0"&gt;
&lt;/iframe&gt;

<span class="info"># 3. Available pages to embed:</span>
/html/dashboard_static.html   - Main dashboard
/html/games_browser.html      - <span class="success">ALL games (552!)</span>
/html/game_summary.html       - Single game view
/html/player_card.html        - Player cards
/html/tracker_v16.html        - Game tracker

<span class="info"># 4. Games Browser shows:</span>
- All 552 games from BLB schedule
- 8 fully tracked games (green badge)
- 544 games with basic stats (orange badge)
- Filter by season, team, data type
- Click any game for roster + stats
                </div>
            `);
        }
        
        function copySQL() {
            navigator.clipboard.writeText('sql/setup_complete_database.sql');
            showToast('Path copied to clipboard');
        }
    </script>
</body>
</html>
"""


# =============================================================================
# ROUTES
# =============================================================================

@app.route('/')
def index():
    """Main orchestrator page."""
    return render_template_string(
        ORCHESTRATOR_HTML,
        blb_info=get_blb_info(),
        games=get_games_list(),
        output_info=get_output_info()
    )


@app.route('/api/extract-roster')
def api_extract_roster():
    """API endpoint to extract roster for a game."""
    game_id = request.args.get('game', '')
    if not game_id:
        return jsonify({'success': False, 'message': 'No game ID provided'})
    
    result = extract_roster_for_game(game_id)
    return jsonify(result)


@app.route('/api/extract-all-rosters')
def api_extract_all_rosters():
    """Extract rosters for all games."""
    games = get_games_list()
    success_count = 0
    
    for game in games:
        result = extract_roster_for_game(game['id'])
        if result['success']:
            success_count += 1
    
    return jsonify({
        'success': True,
        'message': f'Extracted rosters for {success_count}/{len(games)} games'
    })


@app.route('/api/create-game')
def api_create_game():
    """Create a new game folder."""
    game_id = request.args.get('game', '')
    if not game_id:
        return jsonify({'success': False, 'message': 'No game ID provided'})
    
    game_dir = RAW_GAMES_DIR / game_id
    
    if game_dir.exists():
        return jsonify({'success': False, 'message': f'Game {game_id} already exists'})
    
    try:
        game_dir.mkdir(parents=True, exist_ok=True)
        (game_dir / 'events').mkdir(exist_ok=True)
        (game_dir / 'shots').mkdir(exist_ok=True)
        (game_dir / 'bkups').mkdir(exist_ok=True)
        
        # Try to extract roster
        extract_roster_for_game(game_id)
        
        return jsonify({'success': True, 'message': f'Created game folder for {game_id}'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/run-export')
def api_run_export():
    """Run the data export."""
    result = run_data_export()
    return jsonify(result)


@app.route('/open-tracker')
def open_tracker():
    """Open tracker in browser."""
    game_id = request.args.get('game', '')
    tracker_path = TRACKER_FILE
    
    if tracker_path.exists():
        webbrowser.open(f'file://{tracker_path}')
    
    return jsonify({'success': True})


@app.route('/open-games-browser')
def open_games_browser():
    """Open games browser in browser."""
    browser_path = HTML_DIR / 'games_browser.html'
    
    if browser_path.exists():
        webbrowser.open(f'file://{browser_path}')
    
    return jsonify({'success': True})


@app.route('/open-dashboard')
def open_dashboard():
    """Open dashboard in browser."""
    dashboard_path = HTML_DIR / 'dashboard_static.html'
    
    if dashboard_path.exists():
        webbrowser.open(f'file://{dashboard_path}')
    
    return jsonify({'success': True})


@app.route('/open-docs')
def open_docs():
    """Open documentation in browser."""
    docs_path = HTML_DIR / 'system_guide.html'
    
    if docs_path.exists():
        webbrowser.open(f'file://{docs_path}')
    else:
        # Try markdown
        md_path = BASE_DIR / 'GETTING_STARTED.md'
        if md_path.exists():
            webbrowser.open(f'file://{md_path}')
    
    return jsonify({'success': True})


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  🏒 BENCHSIGHT ORCHESTRATOR")
    print("=" * 60)
    print(f"\n  Open in browser: http://localhost:5001")
    print(f"\n  Press Ctrl+C to stop\n")
    print("=" * 60 + "\n")
    
    # Auto-open browser
    webbrowser.open('http://localhost:5001')
    
    # Run Flask
    app.run(host='0.0.0.0', port=5001, debug=False)
