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