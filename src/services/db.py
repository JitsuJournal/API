# System
import os
import json
from dotenv import load_dotenv
# Local
# Third Party
from supabase import create_client, Client

load_dotenv()

def conn_supabase(key:str='')->Client:
    # Use anon public key 
    # if no other key (e.x. service role) was provided
    if key=='': key = os.environ.get("SUPABASE_KEY")
    return create_client(
        supabase_url=os.environ.get("SUPABASE_URL"), 
        supabase_key=key
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
            "match_count": match_count, # Top k=10 default
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
        .select("id, name, description, tags (name)") 
        .execute()
    )
    # NOTE: Not using the tag ID anymore since the models
    # go off the tag names more than the tag ID's 
    # tags (id, name)
    # NOTE: Not using cat_id since this is not really used 
    # by the models, and can be automatically fetched from DB
    # when nodes are fetched and rendered in the builder
    #, sub_id(cat_id)")
    # Convert the sub_id into actual cat_id
    # removing the nested structure for subcategory
    """
    data = [
        {**record, "sub_id": record["sub_id"]["cat_id"]}
        for record in response.data
    ]
    """
    return json.dumps(response.data)


def get_user_limit(client: Client):

    return

def get_usage():
    return


if __name__=="__main__":
    client=conn_supabase()
    #techniques = get_techniques(client)
    
    print(client)