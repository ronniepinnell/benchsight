#!/usr/bin/env python3
"""
=============================================================================
BENCHSIGHT ETL API SERVER
=============================================================================
REST API for triggering ETL operations from web interfaces.

ENDPOINTS:
    GET  /api/health              - Health check
    GET  /api/status              - Pipeline status
    GET  /api/games               - List all games
    GET  /api/games/available     - Games available for processing
    GET  /api/games/processed     - Already processed games
    GET  /api/games/<id>          - Single game details
    POST /api/games/<id>/process  - Process a single game
    POST /api/process             - Process multiple games
    POST /api/upload              - Upload game tracking file
    GET  /api/export              - Trigger CSV export
    GET  /api/tables              - List all tables
    GET  /api/tables/<name>       - Get table data (paginated)

USAGE:
    python -m src.api.server                    # Run on port 5000
    python -m src.api.server --port 8080        # Custom port
    python -m src.api.server --host 0.0.0.0     # Allow external access

=============================================================================
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from functools import wraps
import traceback

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline.orchestrator import PipelineOrchestrator
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize Flask
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload
app.config['UPLOAD_FOLDER'] = PROJECT_ROOT / 'data' / 'raw' / 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls', 'csv'}

# Ensure upload folder exists
app.config['UPLOAD_FOLDER'].mkdir(parents=True, exist_ok=True)

# Global orchestrator instance
orchestrator = None


def get_orchestrator():
    """Get or create orchestrator instance."""
    global orchestrator
    if orchestrator is None:
        orchestrator = PipelineOrchestrator(PROJECT_ROOT)
    return orchestrator


def api_response(data=None, error=None, status=200):
    """Standardized API response format."""
    response = {
        "success": error is None,
        "timestamp": datetime.now().isoformat(),
    }
    if data is not None:
        response["data"] = data
    if error is not None:
        response["error"] = error
    return jsonify(response), status


def handle_errors(f):
    """Decorator to handle exceptions in API endpoints."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"API error in {f.__name__}: {e}")
            logger.error(traceback.format_exc())
            return api_response(error=str(e), status=500)
    return wrapper


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# =============================================================================
# HEALTH & STATUS ENDPOINTS
# =============================================================================

@app.route('/api/health', methods=['GET'])
@handle_errors
def health_check():
    """
    Health check endpoint.
    
    Returns:
        200: {"success": true, "data": {"status": "healthy", ...}}
    """
    from src.database.connection import test_connection
    
    db_ok = test_connection()
    orch = get_orchestrator()
    
    return api_response({
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "output_dir": str(orch.output_dir),
        "games_dir": str(orch.games_dir),
        "version": "16.1"
    })


@app.route('/api/status', methods=['GET'])
@handle_errors
def pipeline_status():
    """
    Get current pipeline status.
    
    Returns:
        200: {"success": true, "data": {"tables": {...}, "games": {...}}}
    """
    orch = get_orchestrator()
    status = orch.get_status()
    
    return api_response({
        "tables": status.get("tables", {}),
        "games": {
            "available": len(orch.get_available_games()),
            "processed": len(orch.get_processed_games()),
            "unprocessed": len(orch.get_unprocessed_games())
        },
        "last_export": _get_last_export_time()
    })


def _get_last_export_time():
    """Get timestamp of most recent CSV export."""
    output_dir = get_orchestrator().output_dir
    csv_files = list(output_dir.glob("*.csv"))
    if not csv_files:
        return None
    latest = max(csv_files, key=lambda f: f.stat().st_mtime)
    return datetime.fromtimestamp(latest.stat().st_mtime).isoformat()


# =============================================================================
# GAMES ENDPOINTS
# =============================================================================

@app.route('/api/games', methods=['GET'])
@handle_errors
def list_games():
    """
    List all games with their status.
    
    Query params:
        status: 'all' | 'available' | 'processed' | 'unprocessed'
    
    Returns:
        200: {"success": true, "data": {"games": [...]}}
    """
    orch = get_orchestrator()
    status_filter = request.args.get('status', 'all')
    
    available = set(orch.get_available_games())
    processed = set(orch.get_processed_games())
    
    games = []
    for game_id in sorted(available | processed):
        game_status = "processed" if game_id in processed else "available"
        if status_filter == 'all' or status_filter == game_status:
            games.append({
                "game_id": game_id,
                "status": game_status
            })
    
    return api_response({
        "games": games,
        "total": len(games),
        "filter": status_filter
    })


@app.route('/api/games/available', methods=['GET'])
@handle_errors
def list_available_games():
    """List games available for processing."""
    orch = get_orchestrator()
    games = orch.get_available_games()
    return api_response({"games": games, "count": len(games)})


@app.route('/api/games/processed', methods=['GET'])
@handle_errors
def list_processed_games():
    """List already processed games."""
    orch = get_orchestrator()
    games = orch.get_processed_games()
    return api_response({"games": games, "count": len(games)})


@app.route('/api/games/unprocessed', methods=['GET'])
@handle_errors
def list_unprocessed_games():
    """List games available but not yet processed."""
    orch = get_orchestrator()
    games = orch.get_unprocessed_games()
    return api_response({"games": games, "count": len(games)})


@app.route('/api/games/<int:game_id>', methods=['GET'])
@handle_errors
def get_game(game_id):
    """
    Get details for a specific game.
    
    Returns:
        200: {"success": true, "data": {"game_id": ..., "status": ..., ...}}
        404: {"success": false, "error": "Game not found"}
    """
    orch = get_orchestrator()
    available = orch.get_available_games()
    processed = orch.get_processed_games()
    
    if game_id not in available and game_id not in processed:
        return api_response(error=f"Game {game_id} not found", status=404)
    
    # Get game data from schedule if available
    game_data = _get_game_from_schedule(game_id)
    
    return api_response({
        "game_id": game_id,
        "status": "processed" if game_id in processed else "available",
        "has_tracking_file": game_id in available,
        **game_data
    })


def _get_game_from_schedule(game_id):
    """Get game details from dim_schedule."""
    import pandas as pd
    schedule_file = get_orchestrator().output_dir / "dim_schedule.csv"
    if not schedule_file.exists():
        return {}
    
    df = pd.read_csv(schedule_file, dtype=str)
    game_row = df[df["game_id"] == str(game_id)]
    if len(game_row) == 0:
        return {}
    
    row = game_row.iloc[0]
    return {
        "date": row.get("game_date_str"),
        "home_team": row.get("home_team_name"),
        "away_team": row.get("away_team_name"),
        "home_goals": row.get("home_total_goals"),
        "away_goals": row.get("away_total_goals")
    }


# =============================================================================
# PROCESSING ENDPOINTS
# =============================================================================

@app.route('/api/games/<int:game_id>/process', methods=['POST'])
@handle_errors
def process_single_game(game_id):
    """
    Process a single game.
    
    Request body (optional):
        {"force": true}  - Force reprocess even if already done
    
    Returns:
        200: {"success": true, "data": {"game_id": ..., "result": ...}}
        404: {"success": false, "error": "Game not found"}
    """
    orch = get_orchestrator()
    available = orch.get_available_games()
    
    if game_id not in available:
        return api_response(error=f"Game {game_id} not available for processing", status=404)
    
    body = request.get_json() or {}
    force = body.get("force", False)
    
    logger.info(f"API: Processing game {game_id} (force={force})")
    result = orch.process_games([game_id], force_reload=force)
    
    return api_response({
        "game_id": game_id,
        "result": result,
        "processed": game_id in result.get("games_processed", [])
    })


@app.route('/api/process', methods=['POST'])
@handle_errors
def process_games():
    """
    Process multiple games.
    
    Request body:
        {
            "game_ids": [18969, 18970],  // Optional - specific games
            "all_unprocessed": true,      // Optional - process all unprocessed
            "force": false                // Optional - force reprocess
        }
    
    Returns:
        200: {"success": true, "data": {"games_processed": [...], ...}}
    """
    orch = get_orchestrator()
    body = request.get_json() or {}
    
    game_ids = body.get("game_ids", [])
    all_unprocessed = body.get("all_unprocessed", False)
    force = body.get("force", False)
    
    if all_unprocessed:
        game_ids = orch.get_unprocessed_games()
    
    if not game_ids:
        return api_response(error="No games specified", status=400)
    
    logger.info(f"API: Processing {len(game_ids)} games (force={force})")
    result = orch.process_games(game_ids, force_reload=force)
    
    return api_response({
        "requested": game_ids,
        "result": result
    })


@app.route('/api/process/full', methods=['POST'])
@handle_errors
def run_full_pipeline():
    """
    Run the complete ETL pipeline.
    
    Request body (optional):
        {
            "reload_blb": false,   // Force reload BLB tables
            "export_csv": true     // Export to CSV after processing
        }
    
    Returns:
        200: {"success": true, "data": {"stages": {...}, ...}}
    """
    orch = get_orchestrator()
    body = request.get_json() or {}
    
    reload_blb = body.get("reload_blb", False)
    export_csv = body.get("export_csv", True)
    
    logger.info(f"API: Running full pipeline (reload_blb={reload_blb}, export_csv={export_csv})")
    result = orch.run_full_pipeline(reload_blb=reload_blb, export_csv=export_csv)
    
    return api_response(result)


# =============================================================================
# FILE UPLOAD ENDPOINT
# =============================================================================

@app.route('/api/upload', methods=['POST'])
@handle_errors
def upload_file():
    """
    Upload a game tracking file.
    
    Form data:
        file: The tracking file (xlsx, xls, csv)
        game_id: Optional game ID to associate with file
    
    Returns:
        200: {"success": true, "data": {"filename": ..., "path": ...}}
        400: {"success": false, "error": "No file provided"}
    """
    if 'file' not in request.files:
        return api_response(error="No file provided", status=400)
    
    file = request.files['file']
    if file.filename == '':
        return api_response(error="No file selected", status=400)
    
    if not allowed_file(file.filename):
        return api_response(
            error=f"File type not allowed. Allowed: {app.config['ALLOWED_EXTENSIONS']}", 
            status=400
        )
    
    # Secure the filename
    filename = secure_filename(file.filename)
    
    # Optionally prefix with game_id
    game_id = request.form.get('game_id')
    if game_id:
        filename = f"{game_id}_{filename}"
    
    # Save file
    filepath = app.config['UPLOAD_FOLDER'] / filename
    file.save(filepath)
    
    logger.info(f"API: Uploaded file {filename}")
    
    return api_response({
        "filename": filename,
        "path": str(filepath),
        "size": filepath.stat().st_size,
        "game_id": game_id
    })


# =============================================================================
# EXPORT ENDPOINT
# =============================================================================

@app.route('/api/export', methods=['GET', 'POST'])
@handle_errors
def export_to_csv():
    """
    Trigger CSV export of all datamart tables.
    
    Returns:
        200: {"success": true, "data": {"tables_exported": ..., "output_dir": ...}}
    """
    orch = get_orchestrator()
    
    from src.pipeline.datamart.export_to_csv import export_datamart_to_csv
    
    logger.info("API: Exporting datamart to CSV")
    result = export_datamart_to_csv(orch.output_dir)
    
    return api_response({
        "tables_exported": result.get("tables_exported", 0),
        "output_dir": str(orch.output_dir),
        "timestamp": datetime.now().isoformat()
    })


# =============================================================================
# TABLE DATA ENDPOINTS
# =============================================================================

@app.route('/api/tables', methods=['GET'])
@handle_errors
def list_tables():
    """
    List all exported tables with row counts.
    
    Returns:
        200: {"success": true, "data": {"tables": [{"name": ..., "rows": ...}, ...]}}
    """
    import pandas as pd
    output_dir = get_orchestrator().output_dir
    
    tables = []
    for csv_file in sorted(output_dir.glob("*.csv")):
        df = pd.read_csv(csv_file, nrows=0)
        row_count = sum(1 for _ in open(csv_file)) - 1  # Subtract header
        tables.append({
            "name": csv_file.stem,
            "columns": len(df.columns),
            "rows": row_count,
            "category": "dim" if csv_file.stem.startswith("dim_") else 
                       "fact" if csv_file.stem.startswith("fact_") else "other"
        })
    
    return api_response({
        "tables": tables,
        "total": len(tables)
    })


@app.route('/api/tables/<table_name>', methods=['GET'])
@handle_errors
def get_table_data(table_name):
    """
    Get data from a specific table (paginated).
    
    Query params:
        limit: Max rows to return (default 100, max 1000)
        offset: Rows to skip (default 0)
        columns: Comma-separated column names to include
    
    Returns:
        200: {"success": true, "data": {"table": ..., "rows": [...], ...}}
        404: {"success": false, "error": "Table not found"}
    """
    import pandas as pd
    output_dir = get_orchestrator().output_dir
    
    csv_file = output_dir / f"{table_name}.csv"
    if not csv_file.exists():
        return api_response(error=f"Table {table_name} not found", status=404)
    
    # Parse query params
    limit = min(int(request.args.get('limit', 100)), 1000)
    offset = int(request.args.get('offset', 0))
    columns = request.args.get('columns', '').split(',') if request.args.get('columns') else None
    
    # Read data
    df = pd.read_csv(csv_file, dtype=str)
    total_rows = len(df)
    
    # Filter columns
    if columns and columns[0]:
        valid_cols = [c for c in columns if c in df.columns]
        df = df[valid_cols]
    
    # Paginate
    df = df.iloc[offset:offset + limit]
    
    return api_response({
        "table": table_name,
        "columns": list(df.columns),
        "rows": df.to_dict(orient='records'),
        "total_rows": total_rows,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total_rows
    })


@app.route('/api/tables/<table_name>/download', methods=['GET'])
@handle_errors
def download_table(table_name):
    """
    Download a table as CSV file.
    
    Returns:
        200: CSV file download
        404: {"success": false, "error": "Table not found"}
    """
    output_dir = get_orchestrator().output_dir
    csv_file = output_dir / f"{table_name}.csv"
    
    if not csv_file.exists():
        return api_response(error=f"Table {table_name} not found", status=404)
    
    return send_file(
        csv_file,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f"{table_name}.csv"
    )


# =============================================================================
# STATS ENDPOINTS (for dashboards)
# =============================================================================

@app.route('/api/stats/players', methods=['GET'])
@handle_errors
def get_player_stats():
    """
    Get player statistics summary.
    
    Query params:
        game_id: Filter by game (optional)
        player_id: Filter by player (optional)
        limit: Max rows (default 50)
    
    Returns:
        200: {"success": true, "data": {"players": [...]}}
    """
    import pandas as pd
    output_dir = get_orchestrator().output_dir
    
    stats_file = output_dir / "fact_player_game_stats.csv"
    if not stats_file.exists():
        return api_response(error="Player stats not available", status=404)
    
    df = pd.read_csv(stats_file)
    
    # Filters
    game_id = request.args.get('game_id')
    player_id = request.args.get('player_id')
    limit = int(request.args.get('limit', 50))
    
    if game_id:
        df = df[df['game_id'].astype(str) == str(game_id)]
    if player_id:
        df = df[df['player_id'].astype(str) == str(player_id)]
    
    # Select key columns
    cols = ['player_game_key', 'game_id', 'player_id', 'player_name', 
            'goals', 'assists', 'points', 'shots', 'toi_minutes']
    cols = [c for c in cols if c in df.columns]
    
    df = df[cols].head(limit)
    
    return api_response({
        "players": df.to_dict(orient='records'),
        "count": len(df)
    })


@app.route('/api/stats/teams', methods=['GET'])
@handle_errors
def get_team_stats():
    """
    Get team statistics summary.
    
    Query params:
        game_id: Filter by game (optional)
    
    Returns:
        200: {"success": true, "data": {"teams": [...]}}
    """
    import pandas as pd
    output_dir = get_orchestrator().output_dir
    
    stats_file = output_dir / "fact_team_game_stats.csv"
    if not stats_file.exists():
        return api_response(error="Team stats not available", status=404)
    
    df = pd.read_csv(stats_file)
    
    game_id = request.args.get('game_id')
    if game_id:
        df = df[df['game_id'].astype(str) == str(game_id)]
    
    return api_response({
        "teams": df.to_dict(orient='records'),
        "count": len(df)
    })


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def not_found(e):
    return api_response(error="Endpoint not found", status=404)


@app.errorhandler(500)
def server_error(e):
    return api_response(error="Internal server error", status=500)


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='BenchSight ETL API Server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║             BENCHSIGHT ETL API SERVER v16.1                   ║
╠═══════════════════════════════════════════════════════════════╣
║  Endpoints:                                                   ║
║    GET  /api/health              - Health check               ║
║    GET  /api/status              - Pipeline status            ║
║    GET  /api/games               - List games                 ║
║    POST /api/games/<id>/process  - Process single game        ║
║    POST /api/process             - Process multiple games     ║
║    POST /api/upload              - Upload tracking file       ║
║    GET  /api/tables              - List tables                ║
║    GET  /api/tables/<name>       - Get table data             ║
║    GET  /api/stats/players       - Player stats               ║
║    GET  /api/stats/teams         - Team stats                 ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    print(f"Starting server at http://{args.host}:{args.port}")
    
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
