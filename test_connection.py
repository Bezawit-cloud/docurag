# test_connection.py
from src.database import supabase

try:
    response = supabase.table('chunks').select('id').limit(1).execute()
    print("✅ Connection successful!")
    print(f"Response: {response.data}")
except Exception as e:
    print(f"❌ Connection failed: {e}")