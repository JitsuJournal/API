# System
import os
import json
from dotenv import load_dotenv
# Local
# Third Party
from supabase import create_client, Client

load_dotenv()

def conn_supabase()->Client:
    return create_client(
        supabase_url=os.environ.get("SUPABASE_URL"), 
        supabase_key=os.environ.get("SUPABASE_KEY")
    )

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

# Function for returning techniques as json string
# to use as context when creating basic graph datastructure
# NOTE: String returned since Gemini only accepts this type
def get_techniques(client: Client)->str:
    response = (
        client.table("techniques")
        .select("id, name, description, tags (id, name), sub_id(cat_id)")
        .execute()
    )
    # Convert the sub_id into actual cat_id
    # removing the nested structure for subcategory
    data = [
        {**record, "sub_id": record["sub_id"]["cat_id"]}
        for record in response.data
    ]
    return json.dumps(data)


if __name__=="__main__":
    client=conn_supabase()
    techniques = get_techniques(client)
    
    # get nodes and edges from sequence 581
    # pack them into nodes/edges

    # move variables into main.py's test endpoint