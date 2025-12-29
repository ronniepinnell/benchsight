"""
=============================================================================
HOCKEY ANALYTICS DASHBOARD
=============================================================================
File: dashboard/app.py

A comprehensive Dash/Plotly dashboard for hockey analytics including:
    - Game status overview
    - Player statistics and box scores
    - Shot charts with XY coordinates
    - Video link integration
    - Head-to-head player comparisons
    - With/without teammate analysis

USAGE:
    python dashboard/app.py
    Then open http://localhost:8050 in your browser

DEPLOYMENT:
    Can be deployed to Render.com, Heroku, or any Python hosting

=============================================================================
"""

import os
import sys
from pathlib import Path

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Check if dash is available
try:
    from dash import Dash, html, dcc, Input, Output, State, callback, dash_table
    import dash_bootstrap_components as dbc
    DASH_AVAILABLE = True
except ImportError:
    DASH_AVAILABLE = False
    print("Dash not installed. Install with: pip install dash dash-bootstrap-components")

# Database imports
from src.database.table_operations import read_query, table_exists, get_row_count

# =============================================================================
# DATA LOADING FUNCTIONS
# =============================================================================

def get_game_list():
    """Get list of games with status."""
    if not table_exists('fact_game_status'):
        return pd.DataFrame()
    return read_query("""
        SELECT 
            gs.game_id, 
            gs.tracking_status,
            gs.events_tracked,
            gs.shifts_tracked,
            gs.xy_tracked,
            gs.video_tracked,
            s.home_team_name,
            s.away_team_name,
            s.game_date
        FROM fact_game_status gs
        LEFT JOIN dim_schedule s ON gs.game_id = s.game_id
        ORDER BY gs.game_id
    """)


def get_box_score(game_id: int = None):
    """Get box score data."""
    if not table_exists('fact_box_score'):
        return pd.DataFrame()
    
    query = "SELECT * FROM fact_box_score"
    if game_id:
        query += f" WHERE game_id = {game_id}"
    return read_query(query)


def get_events(game_id: int = None):
    """Get events data."""
    if not table_exists('fact_events'):
        return pd.DataFrame()
    
    query = "SELECT * FROM fact_events"
    if game_id:
        query += f" WHERE game_id = {game_id}"
    return read_query(query)


def get_xy_events(game_id: int = None):
    """Get XY event coordinates."""
    if not table_exists('fact_xy_events'):
        return pd.DataFrame()
    
    query = "SELECT * FROM fact_xy_events"
    if game_id:
        query += f" WHERE game_id = {game_id}"
    return read_query(query)


def get_xy_shots(game_id: int = None):
    """Get XY shot coordinates."""
    if not table_exists('fact_xy_shots'):
        return pd.DataFrame()
    
    query = "SELECT * FROM fact_xy_shots"
    if game_id:
        query += f" WHERE game_id = {game_id}"
    return read_query(query)


def get_video_links(game_id: int = None):
    """Get video links."""
    if not table_exists('fact_video_links'):
        return pd.DataFrame()
    
    query = "SELECT * FROM fact_video_links"
    if game_id:
        query += f" WHERE game_id = {game_id}"
    return read_query(query)


def get_players():
    """Get player list."""
    if not table_exists('dim_player'):
        return pd.DataFrame()
    return read_query("SELECT * FROM dim_player")


def get_data_issues(game_id: int = None):
    """Get data quality issues."""
    if not table_exists('log_data_issues'):
        return pd.DataFrame()
    
    query = "SELECT * FROM log_data_issues"
    if game_id:
        query += f" WHERE game_id = {game_id}"
    return read_query(query)


# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def create_rink_figure():
    """Create empty rink visualization."""
    fig = go.Figure()
    
    # Rink outline
    fig.add_shape(type="rect", x0=-100, y0=-42.5, x1=100, y1=42.5,
                  line=dict(color="blue", width=2))
    
    # Center line
    fig.add_shape(type="line", x0=0, y0=-42.5, x1=0, y1=42.5,
                  line=dict(color="red", width=2))
    
    # Blue lines
    fig.add_shape(type="line", x0=25, y0=-42.5, x1=25, y1=42.5,
                  line=dict(color="blue", width=2))
    fig.add_shape(type="line", x0=-25, y0=-42.5, x1=-25, y1=42.5,
                  line=dict(color="blue", width=2))
    
    # Goal lines
    fig.add_shape(type="line", x0=89, y0=-42.5, x1=89, y1=42.5,
                  line=dict(color="red", width=1))
    fig.add_shape(type="line", x0=-89, y0=-42.5, x1=-89, y1=42.5,
                  line=dict(color="red", width=1))
    
    # Goals
    for x in [89, -89]:
        fig.add_shape(type="rect", x0=x, y0=-3, x1=x+4 if x > 0 else x-4, y1=3,
                      fillcolor="lightgray", line=dict(color="black"))
    
    fig.update_layout(
        xaxis=dict(range=[-105, 105], showgrid=False, zeroline=False),
        yaxis=dict(range=[-50, 50], showgrid=False, zeroline=False, scaleanchor="x"),
        showlegend=True,
        height=500,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


def create_shot_chart(game_id: int):
    """Create shot chart for a game."""
    fig = create_rink_figure()
    
    shots = get_xy_shots(game_id)
    if len(shots) == 0:
        fig.update_layout(title="No Shot Data Available")
        return fig
    
    # Goals
    goals = shots[shots['is_goal'] == 1]
    if len(goals) > 0:
        fig.add_trace(go.Scatter(
            x=goals['x'], y=goals['y'],
            mode='markers',
            marker=dict(size=15, color='green', symbol='star'),
            name='Goals',
            hovertemplate='Goal<br>Distance: %{customdata[0]:.1f}ft<br>Angle: %{customdata[1]:.1f}°',
            customdata=goals[['distance', 'angle']].values
        ))
    
    # Shots
    non_goals = shots[shots['is_goal'] != 1]
    if len(non_goals) > 0:
        fig.add_trace(go.Scatter(
            x=non_goals['x'], y=non_goals['y'],
            mode='markers',
            marker=dict(size=8, color='red', opacity=0.6),
            name='Shots',
            hovertemplate='Shot<br>Distance: %{customdata[0]:.1f}ft<br>Angle: %{customdata[1]:.1f}°',
            customdata=non_goals[['distance', 'angle']].values
        ))
    
    fig.update_layout(title=f"Shot Chart - Game {game_id}")
    return fig


def create_event_heatmap(game_id: int):
    """Create event location heatmap."""
    fig = create_rink_figure()
    
    events = get_xy_events(game_id)
    if len(events) == 0:
        fig.update_layout(title="No XY Event Data Available")
        return fig
    
    fig.add_trace(go.Histogram2d(
        x=events['x1'],
        y=events['y1'],
        colorscale='Hot',
        nbinsx=40,
        nbinsy=20,
        opacity=0.6,
        name='Events'
    ))
    
    fig.update_layout(title=f"Event Heatmap - Game {game_id}")
    return fig


def create_player_stats_chart(game_id: int):
    """Create player statistics chart."""
    box = get_box_score(game_id)
    if len(box) == 0:
        return go.Figure().update_layout(title="No Box Score Data")
    
    # Top scorers
    fig = px.bar(
        box.nlargest(10, 'points'),
        x='display_name' if 'display_name' in box.columns else 'player_id',
        y='points',
        color='player_team' if 'player_team' in box.columns else None,
        title=f"Top Point Scorers - Game {game_id}"
    )
    
    return fig


# =============================================================================
# HEAD-TO-HEAD ANALYSIS
# =============================================================================

def calculate_head_to_head(player1_id: int, player2_id: int):
    """
    Calculate head-to-head stats when two players are on ice together.
    """
    # This would require shift-level analysis
    # Placeholder for now
    return pd.DataFrame()


def calculate_with_without(target_player: int, teammate: int):
    """
    Calculate player stats with and without a specific teammate.
    """
    # This would require shift-level analysis
    # Placeholder for now
    return pd.DataFrame()


# =============================================================================
# DASH APPLICATION
# =============================================================================

if DASH_AVAILABLE:
    # Initialize app
    app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
    
    # Layout
    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("🏒 Hockey Analytics Dashboard", className="text-center my-4"),
                html.Hr()
            ])
        ]),
        
        # Game selector
        dbc.Row([
            dbc.Col([
                html.H4("Select Game"),
                dcc.Dropdown(
                    id='game-selector',
                    options=[],  # Will be populated by callback
                    placeholder="Select a game..."
                )
            ], width=6),
            dbc.Col([
                html.H4("Game Status"),
                html.Div(id='game-status-display')
            ], width=6)
        ], className="mb-4"),
        
        # Tabs for different views
        dbc.Tabs([
            dbc.Tab(label="📊 Overview", children=[
                dbc.Row([
                    dbc.Col([
                        html.H5("Game Statistics"),
                        html.Div(id='game-stats-table')
                    ])
                ], className="mt-3")
            ]),
            
            dbc.Tab(label="📈 Shot Chart", children=[
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id='shot-chart')
                    ])
                ], className="mt-3")
            ]),
            
            dbc.Tab(label="🔥 Event Heatmap", children=[
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id='event-heatmap')
                    ])
                ], className="mt-3")
            ]),
            
            dbc.Tab(label="👥 Box Score", children=[
                dbc.Row([
                    dbc.Col([
                        html.Div(id='box-score-table')
                    ])
                ], className="mt-3")
            ]),
            
            dbc.Tab(label="🎬 Video Links", children=[
                dbc.Row([
                    dbc.Col([
                        html.H5("Video Links"),
                        html.P("Click a link to watch that moment in the game video"),
                        html.Div(id='video-links-table')
                    ])
                ], className="mt-3")
            ]),
            
            dbc.Tab(label="⚠️ Data Quality", children=[
                dbc.Row([
                    dbc.Col([
                        html.H5("Data Quality Issues"),
                        html.Div(id='data-issues-table')
                    ])
                ], className="mt-3")
            ]),
            
            dbc.Tab(label="🆚 Head-to-Head", children=[
                dbc.Row([
                    dbc.Col([
                        html.H5("Player Comparison"),
                        dbc.Row([
                            dbc.Col([
                                dcc.Dropdown(id='player1-select', placeholder="Player 1")
                            ], width=5),
                            dbc.Col([
                                html.H4("vs", className="text-center")
                            ], width=2),
                            dbc.Col([
                                dcc.Dropdown(id='player2-select', placeholder="Player 2")
                            ], width=5)
                        ]),
                        html.Div(id='h2h-results', className="mt-3")
                    ])
                ], className="mt-3")
            ])
        ]),
        
        # Footer
        dbc.Row([
            dbc.Col([
                html.Hr(),
                html.P("Hockey Analytics ETL System v2.0", className="text-muted text-center")
            ])
        ], className="mt-5")
        
    ], fluid=True)
    
    # Callbacks
    @app.callback(
        Output('game-selector', 'options'),
        Input('game-selector', 'id')  # Trigger on load
    )
    def load_games(_):
        games = get_game_list()
        if len(games) == 0:
            return []
        options = []
        for _, row in games.iterrows():
            label = f"Game {row['game_id']}"
            if pd.notna(row.get('home_team_name')):
                label += f" - {row['home_team_name']} vs {row['away_team_name']}"
            label += f" ({row['tracking_status']})"
            options.append({'label': label, 'value': row['game_id']})
        return options
    
    @app.callback(
        [Output('game-status-display', 'children'),
         Output('shot-chart', 'figure'),
         Output('event-heatmap', 'figure'),
         Output('box-score-table', 'children'),
         Output('video-links-table', 'children'),
         Output('data-issues-table', 'children')],
        Input('game-selector', 'value')
    )
    def update_game_views(game_id):
        if not game_id:
            empty_fig = go.Figure().update_layout(title="Select a game")
            return "No game selected", empty_fig, empty_fig, "", "", ""
        
        # Status
        games = get_game_list()
        game = games[games['game_id'] == game_id].iloc[0] if len(games) > 0 else None
        status = html.Div([
            html.Span(f"Status: {game['tracking_status']}", className="badge bg-success" if game['tracking_status'] == 'FULLY_TRACKED' else "badge bg-warning"),
            html.Br(),
            html.Small(f"Events: {'✓' if game['events_tracked'] else '✗'} | Shifts: {'✓' if game['shifts_tracked'] else '✗'} | XY: {'✓' if game['xy_tracked'] else '✗'} | Video: {'✓' if game['video_tracked'] else '✗'}")
        ]) if game is not None else "Unknown"
        
        # Shot chart
        shot_fig = create_shot_chart(game_id)
        
        # Event heatmap
        heat_fig = create_event_heatmap(game_id)
        
        # Box score
        box = get_box_score(game_id)
        if len(box) > 0:
            display_cols = ['player_id', 'display_name', 'player_team', 'goals', 'assists', 'points', 'shots', 'toi_seconds']
            display_cols = [c for c in display_cols if c in box.columns]
            box_table = dash_table.DataTable(
                data=box[display_cols].to_dict('records'),
                columns=[{'name': c, 'id': c} for c in display_cols],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'backgroundColor': '#303030', 'color': 'white'},
                style_header={'backgroundColor': '#1a1a1a', 'fontWeight': 'bold'}
            )
        else:
            box_table = "No box score data"
        
        # Video links
        videos = get_video_links(game_id)
        if len(videos) > 0:
            # Create clickable links
            video_data = []
            for _, row in videos.head(50).iterrows():
                video_data.append({
                    'type': row['link_type'],
                    'link': row['video_url'],
                    'seconds': row.get('video_seconds', 0)
                })
            video_table = dash_table.DataTable(
                data=video_data,
                columns=[
                    {'name': 'Type', 'id': 'type'},
                    {'name': 'Video Link', 'id': 'link', 'presentation': 'markdown'},
                    {'name': 'Seconds', 'id': 'seconds'}
                ],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'backgroundColor': '#303030', 'color': 'white'},
                style_header={'backgroundColor': '#1a1a1a', 'fontWeight': 'bold'}
            )
        else:
            video_table = "No video links available"
        
        # Data issues
        issues = get_data_issues(game_id)
        if len(issues) > 0:
            issues_summary = issues.groupby('issue_type').size().reset_index(name='count')
            issues_table = dash_table.DataTable(
                data=issues_summary.to_dict('records'),
                columns=[{'name': 'Issue Type', 'id': 'issue_type'}, {'name': 'Count', 'id': 'count'}],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'backgroundColor': '#303030', 'color': 'white'},
                style_header={'backgroundColor': '#1a1a1a', 'fontWeight': 'bold'}
            )
        else:
            issues_table = "No data quality issues detected"
        
        return status, shot_fig, heat_fig, box_table, video_table, issues_table


# =============================================================================
# STATIC VISUALIZATION GENERATION (for non-Dash usage)
# =============================================================================

def generate_static_visualizations(output_dir: Path = None):
    """
    Generate static HTML visualizations using Plotly.
    Can be used without Dash.
    """
    if output_dir is None:
        output_dir = PROJECT_ROOT / 'reports' / 'visualizations'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    games = get_game_list()
    
    for _, game in games.iterrows():
        game_id = game['game_id']
        
        # Shot chart
        fig = create_shot_chart(game_id)
        fig.write_html(output_dir / f'shot_chart_{game_id}.html')
        
        # Player stats
        fig = create_player_stats_chart(game_id)
        fig.write_html(output_dir / f'player_stats_{game_id}.html')
    
    print(f"Generated visualizations in {output_dir}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    if DASH_AVAILABLE:
        print("Starting Hockey Analytics Dashboard...")
        print("Open http://localhost:8050 in your browser")
        app.run_server(debug=True, host='0.0.0.0', port=8050)
    else:
        print("Dash not available. Generating static visualizations...")
        generate_static_visualizations()
