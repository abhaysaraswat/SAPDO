from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_supabase_client():
    """
    Get a Supabase client instance.
    
    Returns:
        A Supabase client instance
    """
    # The newer supabase package doesn't have the 'proxy' issue
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return client
