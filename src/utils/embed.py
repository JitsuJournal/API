# System
import time
# Local
from ..models.general import Video
from ..services.db import conn_supabase, get_unique_embedded_videoids, insert_video_record, update_video_record
from .. services.youtube import conn_youtube, get_basic_info
# Third party
from supabase import Client # imported for types since update_videos.. uses custom query

def set_embedding_basic_info(start: int, timeout:int=5):
    """
    Function for collecting the basic information for all unique
    videos in the embedding table and storing that in the videos
    table. The function and data collection is used once as a script.
    NOTE: Safer to run function in batches to avoid timeout errors.
    """
    # Initalize supabase connection to create db client
    # and fetch a list of unique video id's from the embedding table
    db_client = conn_supabase()
    uniqueIds: list[str] = get_unique_embedded_videoids(client=db_client)
    # Initialize client for using the youtube data API
    yt_client = conn_youtube()
    # Iterate over the video Id's, grab their basic info
    # and insert records into the video table
    for id in uniqueIds[start:]: # NOTE: Run in batch to avoid timeout errors
        print(f'{id}: Fetching metadata')
        metadata: Video = get_basic_info(yt_client, id)        
        # Handle cases where no metadata is available 
        # by skipping the video and passing a msg to the terminal
        if metadata==None:
            print(f'\tNo metadata available. Skipped')
            continue
        # Else create a record in the videos table
        try:
            insert_video_record(client=db_client, video=metadata)
            print(f'\tInserted record to video table.')
        except: print(f'\tFailed to insert video record to db.')
        # Call time.sleep to avoid rate-limit errors
        time.sleep(timeout)
    return

def update_videos_thumbnail_channel(start:int, timeout: int=2):
    """
    For fetching and passing the thumbnail 
    along with the channel title, we need to 
    expand the videos table with fields for these values
    and then write a simple script for fetching data
    using the existing youtube data api serivce function
    and updating the video record
    """
    # Initialize client for using the supabase 
    # and the youtube data API's
    db_client: Client = conn_supabase()
    yt_client = conn_youtube()
    
    # Fetch all the unique videos by video ID in the videos table
    response = (
        db_client.table('videos')
        .select('video_id')
        .execute()
    )

    # Iterate over each of the id's 
    # NOTE: Length is 180 rn (Jul 10, 2025)
    # Going to run in batches to avoid hitting rate limits
    for video in response.data[start:]:
        # Fetch their basic info using the already
        # created youtube service function
        id = video['video_id']
        metadata: Video = get_basic_info(yt_client, id)

        # With the fetched basic info, extract required values
        # and update the videos table to contain the values
        response = update_video_record(db_client, metadata)
        # Adding sleep to avoid hitting rate limits
        time.sleep(timeout)
    return

# 3)
# Review the usage script, mainly the queries
# fetch relevant tutorials for the queries using their hyde solutions
# use the tutorials id (cross check with db to avoid duplicates)
# and store their embeddings with metadata.

if __name__=="__main__":    
    pass