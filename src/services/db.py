# System
import os
import json
from dotenv import load_dotenv
from datetime import datetime, timezone
# Local
# Third Party
from supabase import create_client, Client

load_dotenv()

def conn_supabase()->Client:
    return create_client(
        supabase_url=os.environ.get("SUPABASE_URL"), 
        supabase_key=os.environ.get("SUPABASE_SERVICE_KEY")
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


def get_user_limit(client: Client, userid: str) -> int:
    """
    Given a User ID, this function users the Supabase client
    under a service role to return the usage record limit rate,
    only if it is effective_from <= today and effective till >= today or null.
    """
    # Initialize the time now as a iso string to filter queries by
    now: datetime = datetime.now(timezone.utc)

    # Assuming user ID is valid, query the usage limit record
    # sorted by created_at in descending order
    # and select the last created
    retrieved = (
        client.table('user_limits')
        .select('rate, period, expires_at')
        .eq('user_id', userid)
        .eq('feature', 'askai')
        .lte("effective_from", now.isoformat())
        .order("created_at", desc=True)
        .execute()
    ).data

    response: int = 0
    if len(retrieved)>0:
        last_created = retrieved[0]
        # If the usage limit exists and is expired, return default
        # otherwise simply return the rate and period as retrived n set below
        expires_at: str = last_created["expires_at"]
        response: int = last_created['rate']
        if expires_at:
            # convert string to dt w/ utc timezone mapped
            # and check if the dt for expires_at >= today
            expires_dt: datetime = datetime.fromisoformat(expires_at).replace(tzinfo=timezone.utc)
            # if it is low, return default 0
            if expires_dt<now:
                response: int = 0

    return response

def get_usage(client: Client, userid: str)->int:
    """
    This function is responsible for counting the number of attempts
    the user has made since the beggining of their current usage period
    and returning that number for controlling the users usage.
    """

    # query all the given users usage for a given period (i.e. current month)
    # return the count as the functions response

    return


if __name__=="__main__":
    TEST_UID:str = os.environ.get('HARRI_UID')
    TEST2_UID:str = os.environ.get('HARRI2_UID')
    
    client=conn_supabase()
    #techniques = get_techniques(client)
    
    # Given a user ID
    # Get their usage limit record
    response = get_user_limit(client, TEST_UID)
    print(response)