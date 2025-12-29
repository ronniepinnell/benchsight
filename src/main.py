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