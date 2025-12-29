import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding='utf-8') as f:
        f.write(content.strip())
    print(f"✅ Created: {path}")

# --- 1. Database Connection (src/database/connector.py) ---
db_code = """
import os
from supabase import create_client, Client

class Database:
    _instance = None

    @staticmethod
    def get_client() -> Client:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("❌ Missing Supabase credentials in .env file")
            
        if Database._instance is None:
            Database._instance = create_client(url, key)
            
        return Database._instance
"""

# --- 2. ETL Processor (src/etl/processor.py) ---
etl_code = """
import pandas as pd
import os
from src.database.connector import Database

class ETLProcessor:
    def __init__(self, game_id):
        self.game_id = game_id
        self.db = Database.get_client()

    def run(self):
        print(f"🚀 Processing Game {self.game_id}...")
        
        # 1. Look for files
        base_path = f"data/raw/games/{self.game_id}"
        if not os.path.exists(base_path):
            print(f"⚠️ Game folder not found: {base_path}")
            return

        # 2. Mock Ingestion (Replace this with your Excel logic later)
        print(f"   - Reading events from {base_path}/events/")
        print(f"   - Reading shifts from {base_path}/shifts/")
        
        # 3. Mock Upload to Supabase
        # data = {'game_id': self.game_id, 'status': 'processed'}
        # self.db.table('fact_game_status').upsert(data).execute()
        
        print(f"✅ Game {self.game_id} ETL Complete.")
"""

# --- 3. Main Orchestrator (src/main.py) ---
main_code = """
import os
from dotenv import load_dotenv
from src.etl.processor import ETLProcessor

# Load keys from .env file (Security Best Practice)
load_dotenv()

def main():
    print("=== BenchSight Engine Starting ===")
    
    # Simple auto-discovery of games
    raw_games_dir = "data/raw/games"
    if os.path.exists(raw_games_dir):
        games = [d for d in os.listdir(raw_games_dir) if d.isdigit()]
        print(f"Found games: {games}")
        
        for game_id in games:
            processor = ETLProcessor(game_id)
            processor.run()
    else:
        print(f"❌ No data found in {raw_games_dir}")

if __name__ == "__main__":
    main()
"""

# --- 4. Dashboard App (dashboard/app.py) ---
dash_code = """
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("BenchSight Analytics", className="text-center my-4 text-light"))
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Game Selector", className="card-title"),
                    dcc.Dropdown(
                        id='game-select',
                        options=[{'label': 'Game 18955', 'value': '18955'}],
                        value='18955',
                        className="text-dark"
                    )
                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Recent Activity", className="card-title"),
                    html.Div("ETL Pipeline: Online", className="text-success")
                ])
            ])
        ], width=8)
    ])
], fluid=True)

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
"""

# --- 5. Secure .env Template (.env) ---
env_code = """
SUPABASE_URL=https://uuaowslhpgyiudmbvqze.supabase.co
# REPLACE THIS WITH YOUR NEW KEY AFTER ROTATING IT
SUPABASE_KEY=paste_new_service_role_key_here
"""

def run_rescue():
    print("🚑 Restoring BenchSight Core Files...")
    create_file("src/database/connector.py", db_code)
    create_file("src/etl/processor.py", etl_code)
    create_file("src/main.py", main_code)
    create_file("dashboard/app.py", dash_code)
    create_file(".env", env_code)
    print("\n✅ Restore Complete.")
    print("👉 ACTION REQUIRED: Open '.env' and paste your NEW Supabase key.")

if __name__ == "__main__":
    run_rescue()