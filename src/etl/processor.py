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