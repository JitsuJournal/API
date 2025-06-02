# System
import os
from dotenv import load_dotenv
# Local
# Third Party
from supabase import create_client, Client

load_dotenv()

def get_supabase()->Client:
    return create_client(
        supabase_url=os.environ.get("SUPABASE_URL"), 
        supabase_key=os.environ.get("SUPABASE_KEY")
    )



# function for getting techniques
# instead of storing it as a static file
# to avoid having to recreate
# in case we make changes upstream