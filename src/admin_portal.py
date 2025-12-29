"""
=============================================================================
BENCHSIGHT ADMIN PORTAL
=============================================================================
Unified admin interface for:
    - BLB Tables management (upload/edit)
    - Game tracker (with auto-save and publish)
    - ETL pipeline execution
    - Dashboard views
    - Notes/request log

Run: python admin_portal.py
Open: http://localhost:5000
=============================================================================
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify, send_file, redirect, url_for

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / 'data'
RAW_GAMES_DIR = DATA_DIR / 'raw' / 'games'
OUTPUT_DIR = DATA_DIR / 'output'
TRACKER_DIR = PROJECT_ROOT / 'tracker'
BACKUPS_DIR = PROJECT_ROOT / 'backups'
NOTES_FILE = PROJECT_ROOT / 'admin_notes.json'

# Ensure directories exist
BACKUPS_DIR.mkdir(exist_ok=True)
RAW_GAMES_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload

# =============================================================================
# NORAD-STYLE DARK THEME CSS
# =============================================================================
NORAD_CSS = """
:root {
    --bg-dark: #0a0a0f;
    --bg-panel: #12121a;
    --bg-card: #1a1a24;
    --border-color: #2a2a3a;
    --text-primary: #e0e0e0;
    --text-secondary: #888;
    --accent-blue: #00d4ff;
    --accent-green: #00ff88;
    --accent-red: #ff4444;
    --accent-orange: #ff8800;
    --accent-purple: #aa66ff;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: 'Consolas', 'Monaco', monospace;
    background: var(--bg-dark);
    color: var(--text-primary);
    min-height: 100vh;
}

.norad-header {
    background: linear-gradient(180deg, #1a1a2e 0%, #0a0a0f 100%);
    border-bottom: 1px solid var(--accent-blue);
    padding: 15px 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 0 20px rgba(0, 212, 255, 0.1);
}

.norad-title {
    font-size: 24px;
    font-weight: bold;
    color: var(--accent-blue);
    text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
    letter-spacing: 3px;
}

.norad-status {
    display: flex;
    gap: 20px;
    font-size: 12px;
}

.status-item {
    display: flex;
    align-items: center;
    gap: 5px;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    animation: pulse 2s infinite;
}

.status-dot.green { background: var(--accent-green); box-shadow: 0 0 10px var(--accent-green); }
.status-dot.blue { background: var(--accent-blue); box-shadow: 0 0 10px var(--accent-blue); }
.status-dot.orange { background: var(--accent-orange); box-shadow: 0 0 10px var(--accent-orange); }

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.norad-nav {
    display: flex;
    background: var(--bg-panel);
    border-bottom: 1px solid var(--border-color);
}

.nav-item {
    padding: 15px 25px;
    color: var(--text-secondary);
    text-decoration: none;
    border-bottom: 2px solid transparent;
    transition: all 0.3s;
}

.nav-item:hover, .nav-item.active {
    color: var(--accent-blue);
    border-bottom-color: var(--accent-blue);
    background: rgba(0, 212, 255, 0.05);
}

.norad-main {
    display: flex;
    min-height: calc(100vh - 120px);
}

.norad-sidebar {
    width: 250px;
    background: var(--bg-panel);
    border-right: 1px solid var(--border-color);
    padding: 20px;
}

.norad-content {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
}

.panel {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    margin-bottom: 20px;
}

.panel-header {
    padding: 15px 20px;
    border-bottom: 1px solid var(--border-color);
    font-size: 14px;
    color: var(--accent-blue);
    text-transform: uppercase;
    letter-spacing: 2px;
}

.panel-body {
    padding: 20px;
}

.btn {
    padding: 10px 20px;
    border: 1px solid var(--accent-blue);
    background: transparent;
    color: var(--accent-blue);
    cursor: pointer;
    font-family: inherit;
    font-size: 14px;
    transition: all 0.3s;
    border-radius: 4px;
}

.btn:hover {
    background: var(--accent-blue);
    color: var(--bg-dark);
}

.btn-success { border-color: var(--accent-green); color: var(--accent-green); }
.btn-success:hover { background: var(--accent-green); }

.btn-danger { border-color: var(--accent-red); color: var(--accent-red); }
.btn-danger:hover { background: var(--accent-red); }

.btn-warning { border-color: var(--accent-orange); color: var(--accent-orange); }
.btn-warning:hover { background: var(--accent-orange); }

input, select, textarea {
    background: var(--bg-dark);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: 10px;
    font-family: inherit;
    font-size: 14px;
    border-radius: 4px;
    width: 100%;
}

input:focus, select:focus, textarea:focus {
    outline: none;
    border-color: var(--accent-blue);
    box-shadow: 0 0 5px rgba(0, 212, 255, 0.3);
}

.game-card {
    background: var(--bg-panel);
    border: 1px solid var(--border-color);
    padding: 15px;
    margin-bottom: 10px;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s;
}

.game-card:hover {
    border-color: var(--accent-blue);
    transform: translateX(5px);
}

.game-card.tracked { border-left: 3px solid var(--accent-green); }
.game-card.partial { border-left: 3px solid var(--accent-orange); }
.game-card.untracked { border-left: 3px solid var(--accent-red); }

.stat-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px;
}

.stat-box {
    background: var(--bg-panel);
    border: 1px solid var(--border-color);
    padding: 15px;
    text-align: center;
    border-radius: 4px;
}

.stat-value {
    font-size: 28px;
    font-weight: bold;
    color: var(--accent-blue);
}

.stat-label {
    font-size: 12px;
    color: var(--text-secondary);
    margin-top: 5px;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 10px;
    text-align: left;
    border-bottom: 1px solid var(--border-color);
}

th {
    background: var(--bg-panel);
    color: var(--accent-blue);
    font-size: 12px;
    text-transform: uppercase;
}

tr:hover {
    background: rgba(0, 212, 255, 0.05);
}

.alert {
    padding: 15px;
    border-radius: 4px;
    margin-bottom: 15px;
}

.alert-success { background: rgba(0, 255, 136, 0.1); border: 1px solid var(--accent-green); color: var(--accent-green); }
.alert-error { background: rgba(255, 68, 68, 0.1); border: 1px solid var(--accent-red); color: var(--accent-red); }
.alert-info { background: rgba(0, 212, 255, 0.1); border: 1px solid var(--accent-blue); color: var(--accent-blue); }

.log-entry {
    padding: 10px;
    border-left: 3px solid var(--border-color);
    margin-bottom: 10px;
    background: var(--bg-panel);
}

.log-entry.info { border-left-color: var(--accent-blue); }
.log-entry.success { border-left-color: var(--accent-green); }
.log-entry.warning { border-left-color: var(--accent-orange); }
.log-entry.error { border-left-color: var(--accent-red); }

.log-time {
    font-size: 11px;
    color: var(--text-secondary);
}

.loading {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 2px solid var(--border-color);
    border-top-color: var(--accent-blue);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

iframe {
    border: 1px solid var(--border-color);
    border-radius: 4px;
}

.flex { display: flex; }
.gap-10 { gap: 10px; }
.gap-20 { gap: 20px; }
.mt-10 { margin-top: 10px; }
.mt-20 { margin-top: 20px; }
.mb-10 { margin-bottom: 10px; }
.mb-20 { margin-bottom: 20px; }
.p-20 { padding: 20px; }
.w-full { width: 100%; }
.text-center { text-align: center; }
.text-right { text-align: right; }
"""

# =============================================================================
# HTML TEMPLATES
# =============================================================================

BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BenchSight Admin Portal</title>
    <style>{{ css }}</style>
</head>
<body>
    <header class="norad-header">
        <div class="norad-title">◈ BENCHSIGHT COMMAND</div>
        <div class="norad-status">
            <div class="status-item">
                <div class="status-dot green"></div>
                <span>SYSTEM ONLINE</span>
            </div>
            <div class="status-item">
                <div class="status-dot blue"></div>
                <span>{{ current_time }}</span>
            </div>
            <div class="status-item">
                <div class="status-dot orange"></div>
                <span>{{ game_count }} GAMES</span>
            </div>
        </div>
    </header>
    
    <nav class="norad-nav">
        <a href="/" class="nav-item {{ 'active' if active == 'dashboard' else '' }}">◉ DASHBOARD</a>
        <a href="/blb" class="nav-item {{ 'active' if active == 'blb' else '' }}">◉ BLB TABLES</a>
        <a href="/tracker" class="nav-item {{ 'active' if active == 'tracker' else '' }}">◉ TRACKER</a>
        <a href="/etl" class="nav-item {{ 'active' if active == 'etl' else '' }}">◉ ETL PIPELINE</a>
        <a href="/reports" class="nav-item {{ 'active' if active == 'reports' else '' }}">◉ REPORTS</a>
        <a href="/notes" class="nav-item {{ 'active' if active == 'notes' else '' }}">◉ NOTES</a>
    </nav>
    
    <main class="norad-main">
        {{ content }}
    </main>
    
    <script>
        // Auto-refresh status every 30 seconds
        setTimeout(() => location.reload(), 300000);
    </script>
</body>
</html>
"""

DASHBOARD_CONTENT = """
<div class="norad-content">
    <h2 style="color: var(--accent-blue); margin-bottom: 20px;">◈ SYSTEM OVERVIEW</h2>
    
    <div class="stat-grid">
        <div class="stat-box">
            <div class="stat-value">{{ stats.players }}</div>
            <div class="stat-label">PLAYERS</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{{ stats.teams }}</div>
            <div class="stat-label">TEAMS</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{{ stats.games }}</div>
            <div class="stat-label">TOTAL GAMES</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{{ stats.tracked }}</div>
            <div class="stat-label">TRACKED</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{{ stats.events }}</div>
            <div class="stat-label">EVENTS</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{{ stats.output_files }}</div>
            <div class="stat-label">OUTPUT FILES</div>
        </div>
    </div>
    
    <div class="panel mt-20">
        <div class="panel-header">◈ TRACKED GAMES</div>
        <div class="panel-body">
            {% for game in games %}
            <div class="game-card {{ game.status }}">
                <div class="flex" style="justify-content: space-between;">
                    <div>
                        <strong>Game {{ game.id }}</strong> - {{ game.home }} vs {{ game.away }}
                    </div>
                    <div style="color: var(--text-secondary);">
                        {{ game.events }} events | {{ game.shifts }} shifts
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <div class="panel">
        <div class="panel-header">◈ QUICK ACTIONS</div>
        <div class="panel-body flex gap-10">
            <a href="/tracker" class="btn">Open Tracker</a>
            <a href="/etl" class="btn btn-success">Run ETL</a>
            <a href="/blb" class="btn btn-warning">Update BLB Tables</a>
        </div>
    </div>
</div>
"""

BLB_CONTENT = """
<div class="norad-content">
    <h2 style="color: var(--accent-blue); margin-bottom: 20px;">◈ BLB TABLES MANAGEMENT</h2>
    
    {% if message %}
    <div class="alert alert-{{ message_type }}">{{ message }}</div>
    {% endif %}
    
    <div class="panel">
        <div class="panel-header">◈ UPLOAD BLB_TABLES.XLSX</div>
        <div class="panel-body">
            <form action="/blb/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="blb_file" accept=".xlsx" class="mb-10">
                <button type="submit" class="btn btn-success">Upload & Replace</button>
            </form>
            <p style="color: var(--text-secondary); margin-top: 10px; font-size: 12px;">
                Current file: {{ blb_file_info }}
            </p>
        </div>
    </div>
    
    <div class="panel">
        <div class="panel-header">◈ AVAILABLE SHEETS</div>
        <div class="panel-body">
            <div class="flex gap-10" style="flex-wrap: wrap;">
                {% for sheet in sheets %}
                <a href="/blb/view/{{ sheet }}" class="btn">{{ sheet }}</a>
                {% endfor %}
            </div>
        </div>
    </div>
    
    {% if sheet_data %}
    <div class="panel">
        <div class="panel-header">◈ {{ current_sheet }} ({{ sheet_rows }} rows)</div>
        <div class="panel-body" style="overflow-x: auto;">
            <table>
                <thead>
                    <tr>
                        {% for col in sheet_cols %}
                        <th>{{ col }}</th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for row in sheet_data %}
                    <tr>
                        {% for val in row %}
                        <td>{{ val }}</td>
                        {% endfor %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endif %}
</div>
"""

TRACKER_CONTENT = """
<div class="norad-content" style="padding: 0;">
    <div style="background: var(--bg-panel); padding: 15px 20px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center;">
        <div>
            <span style="color: var(--accent-blue);">◈ GAME TRACKER</span>
            <span style="color: var(--text-secondary); margin-left: 20px;">Game ID: <input type="text" id="gameIdInput" value="{{ game_id }}" style="width: 80px; display: inline;"></span>
        </div>
        <div class="flex gap-10">
            <button onclick="loadGame()" class="btn">Load Game</button>
            <button onclick="saveBackup()" class="btn btn-warning">Save Backup</button>
            <button onclick="publishGame()" class="btn btn-success">Publish to Data</button>
        </div>
    </div>
    
    <iframe src="/tracker/html" style="width: 100%; height: calc(100vh - 180px); border: none;"></iframe>
    
    <script>
        function loadGame() {
            const gameId = document.getElementById('gameIdInput').value;
            window.location.href = '/tracker?game_id=' + gameId;
        }
        
        function saveBackup() {
            const gameId = document.getElementById('gameIdInput').value;
            // Get data from iframe
            const iframe = document.querySelector('iframe');
            try {
                const trackerData = iframe.contentWindow.exportGameData();
                fetch('/api/backup', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({game_id: gameId, data: trackerData})
                }).then(r => r.json()).then(d => alert(d.message));
            } catch(e) {
                alert('Export function not available in tracker. Use tracker export button.');
            }
        }
        
        function publishGame() {
            const gameId = document.getElementById('gameIdInput').value;
            if (!confirm('Publish game ' + gameId + ' to data folder?')) return;
            fetch('/api/publish/' + gameId, {method: 'POST'})
                .then(r => r.json())
                .then(d => alert(d.message));
        }
    </script>
</div>
"""

ETL_CONTENT = """
<div class="norad-content">
    <h2 style="color: var(--accent-blue); margin-bottom: 20px;">◈ ETL PIPELINE CONTROL</h2>
    
    {% if message %}
    <div class="alert alert-{{ message_type }}">{{ message }}</div>
    {% endif %}
    
    <div class="panel">
        <div class="panel-header">◈ PIPELINE STAGES</div>
        <div class="panel-body">
            <div class="stat-grid">
                <div class="stat-box">
                    <div style="color: var(--accent-green); font-size: 20px;">STAGE</div>
                    <div class="stat-label">Load raw data</div>
                    <button onclick="runStage('stage')" class="btn mt-10">Run Stage</button>
                </div>
                <div class="stat-box">
                    <div style="color: var(--accent-orange); font-size: 20px;">INTERMEDIATE</div>
                    <div class="stat-label">Transform data</div>
                    <button onclick="runStage('intermediate')" class="btn mt-10">Run Intermediate</button>
                </div>
                <div class="stat-box">
                    <div style="color: var(--accent-blue); font-size: 20px;">DATAMART</div>
                    <div class="stat-label">Build outputs</div>
                    <button onclick="runStage('datamart')" class="btn mt-10">Run Datamart</button>
                </div>
                <div class="stat-box">
                    <div style="color: var(--accent-purple); font-size: 20px;">FULL</div>
                    <div class="stat-label">All stages</div>
                    <button onclick="runStage('full')" class="btn btn-success mt-10">Run All</button>
                </div>
            </div>
        </div>
    </div>
    
    <div class="panel">
        <div class="panel-header">◈ GAME SELECTION</div>
        <div class="panel-body">
            <div class="flex gap-10 mb-10">
                <select id="gameSelect" style="flex: 1;">
                    <option value="all">All Unprocessed Games</option>
                    {% for game in games %}
                    <option value="{{ game.id }}">Game {{ game.id }} - {{ game.home }} vs {{ game.away }}</option>
                    {% endfor %}
                </select>
                <button onclick="runForGame()" class="btn btn-success">Process Selected</button>
            </div>
        </div>
    </div>
    
    <div class="panel">
        <div class="panel-header">◈ ETL LOG</div>
        <div class="panel-body" id="etlLog" style="max-height: 400px; overflow-y: auto;">
            {% for log in logs %}
            <div class="log-entry {{ log.level }}">
                <div class="log-time">{{ log.time }}</div>
                <div>{{ log.message }}</div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <script>
        function runStage(stage) {
            if (!confirm('Run ' + stage + ' pipeline?')) return;
            document.getElementById('etlLog').innerHTML = '<div class="loading"></div> Running...';
            fetch('/api/etl/' + stage, {method: 'POST'})
                .then(r => r.json())
                .then(d => {
                    alert(d.message);
                    location.reload();
                });
        }
        
        function runForGame() {
            const gameId = document.getElementById('gameSelect').value;
            if (!confirm('Process game ' + gameId + '?')) return;
            fetch('/api/etl/game/' + gameId, {method: 'POST'})
                .then(r => r.json())
                .then(d => {
                    alert(d.message);
                    location.reload();
                });
        }
    </script>
</div>
"""

REPORTS_CONTENT = """
<div class="norad-content">
    <h2 style="color: var(--accent-blue); margin-bottom: 20px;">◈ DASHBOARD & REPORTS</h2>
    
    <div class="panel">
        <div class="panel-header">◈ AVAILABLE VIEWS</div>
        <div class="panel-body flex gap-10" style="flex-wrap: wrap;">
            <a href="/reports/game" class="btn">Game Summary</a>
            <a href="/reports/player" class="btn">Player Cards</a>
            <a href="/reports/team" class="btn">Team Stats</a>
            <a href="/reports/shots" class="btn">Shot Charts</a>
        </div>
    </div>
    
    <div class="panel">
        <div class="panel-header">◈ OUTPUT FILES ({{ output_count }} files)</div>
        <div class="panel-body" style="max-height: 500px; overflow-y: auto;">
            <table>
                <thead>
                    <tr>
                        <th>File</th>
                        <th>Size</th>
                        <th>Modified</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for file in output_files %}
                    <tr>
                        <td>{{ file.name }}</td>
                        <td>{{ file.size }}</td>
                        <td>{{ file.modified }}</td>
                        <td>
                            <a href="/download/{{ file.name }}" class="btn" style="padding: 5px 10px; font-size: 12px;">Download</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
"""

NOTES_CONTENT = """
<div class="norad-content">
    <h2 style="color: var(--accent-blue); margin-bottom: 20px;">◈ NOTES & REQUEST LOG</h2>
    
    {% if message %}
    <div class="alert alert-success">{{ message }}</div>
    {% endif %}
    
    <div class="panel">
        <div class="panel-header">◈ ADD NEW NOTE</div>
        <div class="panel-body">
            <form action="/notes/add" method="post">
                <div class="mb-10">
                    <select name="category" style="width: 200px;">
                        <option value="request">Feature Request</option>
                        <option value="bug">Bug Report</option>
                        <option value="idea">Idea</option>
                        <option value="todo">To-Do</option>
                        <option value="note">General Note</option>
                    </select>
                </div>
                <div class="mb-10">
                    <input type="text" name="title" placeholder="Title" required>
                </div>
                <div class="mb-10">
                    <textarea name="content" rows="4" placeholder="Details..."></textarea>
                </div>
                <button type="submit" class="btn btn-success">Add Note</button>
            </form>
        </div>
    </div>
    
    <div class="panel">
        <div class="panel-header">◈ ALL NOTES ({{ notes|length }})</div>
        <div class="panel-body">
            {% for note in notes %}
            <div class="log-entry {{ note.category }}" style="margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <div>
                        <strong style="color: var(--accent-blue);">[{{ note.category|upper }}]</strong>
                        <span style="color: var(--text-primary);">{{ note.title }}</span>
                    </div>
                    <div class="log-time">{{ note.time }}</div>
                </div>
                <div style="color: var(--text-secondary);">{{ note.content }}</div>
                <div class="mt-10">
                    <form action="/notes/delete/{{ note.id }}" method="post" style="display: inline;">
                        <button type="submit" class="btn btn-danger" style="padding: 3px 8px; font-size: 11px;">Delete</button>
                    </form>
                    {% if note.category != 'done' %}
                    <form action="/notes/complete/{{ note.id }}" method="post" style="display: inline;">
                        <button type="submit" class="btn btn-success" style="padding: 3px 8px; font-size: 11px;">Mark Done</button>
                    </form>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
            
            {% if not notes %}
            <p style="color: var(--text-secondary);">No notes yet. Add your first note above!</p>
            {% endif %}
        </div>
    </div>
</div>
"""

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_game_count():
    """Count game folders"""
    if not RAW_GAMES_DIR.exists():
        return 0
    return len([d for d in RAW_GAMES_DIR.iterdir() if d.is_dir() and d.name.isdigit()])

def get_output_file_count():
    """Count output CSV files"""
    if not OUTPUT_DIR.exists():
        return 0
    return len(list(OUTPUT_DIR.glob('*.csv')))

def get_game_list():
    """Get list of games with basic info"""
    games = []
    if not RAW_GAMES_DIR.exists():
        return games
    
    for game_dir in sorted(RAW_GAMES_DIR.iterdir()):
        if not game_dir.is_dir() or not game_dir.name.isdigit():
            continue
        
        game_id = game_dir.name
        tracking_file = None
        for f in game_dir.glob('*tracking*.xlsx'):
            if not f.name.startswith('~$'):
                tracking_file = f
                break
        
        events = 0
        shifts = 0
        status = 'untracked'
        
        if tracking_file:
            try:
                import pandas as pd
                xl = pd.ExcelFile(tracking_file)
                if 'events' in xl.sheet_names:
                    events = len(pd.read_excel(xl, 'events'))
                if 'shifts' in xl.sheet_names:
                    shifts = len(pd.read_excel(xl, 'shifts'))
                status = 'tracked' if events > 100 else 'partial'
            except:
                pass
        
        games.append({
            'id': game_id,
            'home': 'Home',  # Could load from BLB_Tables
            'away': 'Away',
            'events': events,
            'shifts': shifts,
            'status': status
        })
    
    return games

def get_output_files():
    """Get list of output files with info"""
    files = []
    if not OUTPUT_DIR.exists():
        return files
    
    for f in sorted(OUTPUT_DIR.glob('*.csv')):
        stat = f.stat()
        files.append({
            'name': f.name,
            'size': f"{stat.st_size / 1024:.1f} KB",
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
        })
    
    return files

def load_notes():
    """Load notes from JSON file"""
    if not NOTES_FILE.exists():
        return []
    try:
        with open(NOTES_FILE) as f:
            return json.load(f)
    except:
        return []

def save_notes(notes):
    """Save notes to JSON file"""
    with open(NOTES_FILE, 'w') as f:
        json.dump(notes, f, indent=2)

def get_etl_logs():
    """Get recent ETL logs"""
    log_dir = PROJECT_ROOT / 'logs'
    logs = []
    
    if log_dir.exists():
        for log_file in sorted(log_dir.glob('*.log'), reverse=True)[:1]:
            try:
                with open(log_file) as f:
                    for line in f.readlines()[-20:]:
                        if ' - ' in line:
                            parts = line.strip().split(' - ')
                            level = 'info'
                            if 'ERROR' in line: level = 'error'
                            elif 'WARNING' in line: level = 'warning'
                            elif 'SUCCESS' in line: level = 'success'
                            logs.append({
                                'time': parts[0] if len(parts) > 0 else '',
                                'message': ' - '.join(parts[1:]) if len(parts) > 1 else line,
                                'level': level
                            })
            except:
                pass
    
    return logs[-15:]

def render_page(content, active='dashboard', **kwargs):
    """Render a page with the base template"""
    from jinja2 import Template
    
    base = Template(BASE_TEMPLATE)
    content_template = Template(content)
    
    rendered_content = content_template.render(**kwargs)
    
    return base.render(
        css=NORAD_CSS,
        content=rendered_content,
        active=active,
        current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        game_count=get_game_count()
    )

# =============================================================================
# ROUTES
# =============================================================================

@app.route('/')
def dashboard():
    """Main dashboard"""
    games = get_game_list()
    
    # Load stats
    stats = {
        'players': 0,
        'teams': 0,
        'games': len(games),
        'tracked': len([g for g in games if g['status'] == 'tracked']),
        'events': sum(g['events'] for g in games),
        'output_files': get_output_file_count()
    }
    
    # Try to get actual counts from CSVs
    try:
        import pandas as pd
        player_file = OUTPUT_DIR / 'dim_player.csv'
        if player_file.exists():
            stats['players'] = len(pd.read_csv(player_file))
        team_file = OUTPUT_DIR / 'dim_team.csv'
        if team_file.exists():
            stats['teams'] = len(pd.read_csv(team_file))
    except:
        pass
    
    return render_page(DASHBOARD_CONTENT, 'dashboard', stats=stats, games=games)

@app.route('/blb')
@app.route('/blb/view/<sheet>')
def blb_tables(sheet=None):
    """BLB Tables management"""
    blb_file = DATA_DIR / 'BLB_Tables.xlsx'
    sheets = []
    sheet_data = None
    sheet_cols = []
    sheet_rows = 0
    current_sheet = sheet
    
    blb_file_info = "Not found"
    if blb_file.exists():
        stat = blb_file.stat()
        blb_file_info = f"{blb_file.name} ({stat.st_size / 1024 / 1024:.1f} MB, modified {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')})"
        
        try:
            import pandas as pd
            xl = pd.ExcelFile(blb_file)
            sheets = xl.sheet_names
            
            if sheet and sheet in sheets:
                df = pd.read_excel(xl, sheet_name=sheet)
                sheet_rows = len(df)
                sheet_cols = list(df.columns)
                sheet_data = df.head(50).values.tolist()
        except Exception as e:
            sheets = [f"Error: {str(e)}"]
    
    return render_page(BLB_CONTENT, 'blb', 
                      blb_file_info=blb_file_info,
                      sheets=sheets,
                      sheet_data=sheet_data,
                      sheet_cols=sheet_cols,
                      sheet_rows=sheet_rows,
                      current_sheet=current_sheet,
                      message=request.args.get('message'),
                      message_type=request.args.get('type', 'info'))

@app.route('/blb/upload', methods=['POST'])
def upload_blb():
    """Upload new BLB_Tables file"""
    if 'blb_file' not in request.files:
        return redirect('/blb?message=No file selected&type=error')
    
    file = request.files['blb_file']
    if file.filename == '':
        return redirect('/blb?message=No file selected&type=error')
    
    if not file.filename.endswith('.xlsx'):
        return redirect('/blb?message=File must be .xlsx&type=error')
    
    # Backup existing file
    blb_file = DATA_DIR / 'BLB_Tables.xlsx'
    if blb_file.exists():
        backup_name = f"BLB_Tables_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        shutil.copy(blb_file, BACKUPS_DIR / backup_name)
    
    # Save new file
    file.save(blb_file)
    
    return redirect('/blb?message=BLB_Tables uploaded successfully&type=success')

@app.route('/tracker')
def tracker():
    """Tracker interface"""
    game_id = request.args.get('game_id', '')
    return render_page(TRACKER_CONTENT, 'tracker', game_id=game_id)

@app.route('/tracker/html')
def tracker_html():
    """Serve the tracker HTML file"""
    tracker_file = TRACKER_DIR / 'tracker_v16.html'
    if tracker_file.exists():
        return send_file(tracker_file)
    return "Tracker file not found", 404

@app.route('/etl')
def etl():
    """ETL pipeline control"""
    games = get_game_list()
    logs = get_etl_logs()
    
    return render_page(ETL_CONTENT, 'etl', 
                      games=games, 
                      logs=logs,
                      message=request.args.get('message'),
                      message_type=request.args.get('type', 'info'))

@app.route('/api/etl/<stage>', methods=['POST'])
def run_etl(stage):
    """Run ETL pipeline stage"""
    try:
        # For now, just log the action
        # In production, would run: subprocess.run(['python', 'main.py', '--stage', stage])
        
        log_file = PROJECT_ROOT / 'logs' / f"hockey_analytics_{datetime.now().strftime('%Y-%m-%d')}.log"
        log_file.parent.mkdir(exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()} - INFO - ETL stage '{stage}' triggered from admin portal\n")
        
        return jsonify({'status': 'success', 'message': f'ETL stage {stage} started. Check logs for progress.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/publish/<game_id>', methods=['POST'])
def publish_game(game_id):
    """Publish tracker data to data folder"""
    try:
        # Create game folder if needed
        game_dir = RAW_GAMES_DIR / game_id
        game_dir.mkdir(exist_ok=True)
        
        return jsonify({'status': 'success', 'message': f'Game {game_id} folder ready at {game_dir}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/backup', methods=['POST'])
def save_backup():
    """Save tracker backup"""
    try:
        data = request.json
        game_id = data.get('game_id', 'unknown')
        tracker_data = data.get('data', {})
        
        backup_file = BACKUPS_DIR / f"tracker_{game_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_file, 'w') as f:
            json.dump(tracker_data, f, indent=2)
        
        return jsonify({'status': 'success', 'message': f'Backup saved: {backup_file.name}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/reports')
def reports():
    """Reports dashboard"""
    output_files = get_output_files()
    return render_page(REPORTS_CONTENT, 'reports', 
                      output_files=output_files,
                      output_count=len(output_files))

@app.route('/download/<filename>')
def download_file(filename):
    """Download output file"""
    file_path = OUTPUT_DIR / filename
    if file_path.exists():
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

@app.route('/notes')
def notes():
    """Notes and request log"""
    all_notes = load_notes()
    return render_page(NOTES_CONTENT, 'notes', 
                      notes=all_notes,
                      message=request.args.get('message'))

@app.route('/notes/add', methods=['POST'])
def add_note():
    """Add a new note"""
    notes = load_notes()
    new_note = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'category': request.form.get('category', 'note'),
        'title': request.form.get('title', ''),
        'content': request.form.get('content', ''),
        'time': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    notes.insert(0, new_note)
    save_notes(notes)
    return redirect('/notes?message=Note added successfully')

@app.route('/notes/delete/<note_id>', methods=['POST'])
def delete_note(note_id):
    """Delete a note"""
    notes = load_notes()
    notes = [n for n in notes if n['id'] != note_id]
    save_notes(notes)
    return redirect('/notes?message=Note deleted')

@app.route('/notes/complete/<note_id>', methods=['POST'])
def complete_note(note_id):
    """Mark note as done"""
    notes = load_notes()
    for n in notes:
        if n['id'] == note_id:
            n['category'] = 'done'
            n['title'] = '✓ ' + n['title']
    save_notes(notes)
    return redirect('/notes?message=Note marked as done')

# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  BENCHSIGHT ADMIN PORTAL")
    print("="*60)
    print(f"  Open: http://localhost:5000")
    print(f"  Data: {DATA_DIR}")
    print(f"  Games: {get_game_count()}")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
