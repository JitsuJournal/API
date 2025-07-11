# System
import os
import json
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
# Local
from ..models.general import Video
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

    # Initialize the default response
    response: int = 0 
    # If the data + usage limit exists and is expired, return default
    # otherwise simply return the rate and period as retrived and set below
    if len(retrieved)>0:
        last_created = retrieved[0]
        expires_at: str = last_created["expires_at"]
        response: int = last_created['rate']
        if expires_at:
            # convert string to dt w/ utc timezone mapped
            # and check if the dt for expires_at >= today
            expires_dt: datetime = datetime.fromisoformat(expires_at).replace(tzinfo=timezone.utc)
            # if the current limit has already expired, return default 0
            if expires_dt<now: response: int = 0

    return response

def get_usage(client: Client, userid: str)->int:
    """
    This function is responsible for counting the number of attempts
    the user has made since the beggining of their current usage period
    and returning that number for limiting their token consumption.
    """

    # Initialize the current month and nexts dates
    # for using to filter current periods usage records
    today: datetime = datetime.now(timezone.utc)
    start_month: datetime = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month: datetime = (start_month+timedelta(days=32)).replace(day=1)

    # query all the given users usage for a given period (i.e. current month)
    # return the count as the functions response
    response = (
        client.table('usage')
        .select('used_at', count='exact')
        # Filter for requested users data
        .eq('user_id', userid)
        .eq('feature', 'askai')
        # Filter to only return the current periods records
        .gte('used_at', start_month.isoformat()) 
        .lte('used_at', next_month.isoformat()) 
        .execute()
    )

    # Return 0 if no count, or the usage count as is
    return response.count if response.count!=None else 0

def log_use(client: Client, userid: str, feature:str='askai', metadata:dict|None=None)->None:
    """
    This function uses the supabase client and creates
    a record in the usage table to keep track of how much
    the user is using askai or other JitsuJournal features.
    """
    # create payload for inserting a usage record
    # w/ required user_id and metadata if given
    # NOTE: The used_at field defaults to now() db side
    payload = {'user_id': userid, 'feature': feature}
    if metadata: payload['metadata'] = metadata

    # Use Supabase client and pass payload 
    # to insert into usage table
    __ = (
        client.table('usage')
        .insert(payload)
        .execute()
    )
    return

def get_unique_embedded_videoids(client: Client) -> list[str]:
    """
    Given youtube data API client/resource, this function
    returns a list of unique video id's. Used primarily in
    utils.embed for getting metadata for already embedding videos
    and storing their information in the videos table.
    """
    # Connect to existing embeddings table
    # fetch all uniuqe video ID's stored
    response = (
        client.table("embeddings")
        .select("video_id")
        .execute()
    )
    uniqueIds: list[str] = list(dict.fromkeys(d['video_id'] for d in response.data))
    return uniqueIds

def insert_video_record(client: Client, video: Video):
    """
    Given a Video object from general models, 
    this function is responsible for inserting it to the
    videos table. Mostly used as a inside of admin run scripts.
    """
    response = (
        client.table('videos')
        .insert({
            'video_id': video.id,
            'title': video.title,
            'description': video.description,
            'uploaded_at': video.uploaded_at,
        })
        .execute()
    )
    return response

def get_video(client: Client, id: str):
    """
    This function is used for getting the metadata
    from the videos table for any given video's unique ID.
    The response is usually used for recommending tutorials
    or checking if we already have videos stored in our db.
    """
    response = (
        client.table('videos')
        .select('*')
        .eq('video_id', id)
        .execute()
    )
    return response

def update_video_record(client: Client, video: Video):
    """
    Given a video object, this function uses the db client,
    connects to the videos table, and updates the values
    to match the new video object, with the id being used
    to identify which record to update.
    """
    # NOTE: Video.model_dump isn't consistent with the field names
    # used in the database (the id is stored as video_id)
    # so we reshape here before updating the database record
    data = {
        'video_id': video.id, 'title': video.title,
        'description': video.description, 'uploaded_at': video.uploaded_at,
        'uploaded_by': video.uploaded_by, 'thumbnail': video.thumbnail
    }
    response = (
        client.table('videos')
        .update(data)
        .eq('video_id', video.id)
        .execute()
    )
    return response


if __name__=="__main__":    
    # Initialize db connection
    client=conn_supabase()
    
    # Sample/test ID
    videoId = '0iXYmthHzxo'

    # Assuming ID valid and data is available
    response: dict = get_video(client, videoId).data[0]
    print(response)