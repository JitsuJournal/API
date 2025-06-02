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

# function for performing similarity search
# used to find relevant documents and ground hyde answer
def similarity_search(
        client: Client, vector: list[float], 
        match_threshold:float=0.51,match_count:int=10
    ):
    response = (
        client.rpc(fn='match_documents', params={
            "query_embedding": vector,
            "match_threshold": match_threshold, # Over 51% Match in similarity
            "match_count": match_count, # Top k=10
        })
        .execute()
    )
    return response