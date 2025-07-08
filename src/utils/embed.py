# System
import time
# Local
from ..models.general import Video
from ..services.db import conn_supabase, get_unique_embedded_videoids, insert_video_record
from .. services.youtube import conn_youtube, get_basic_info
# Third party

def set_embedding_basic_info(timeout:int=5):
    """
    Function for collecting the basic information for all unique
    videos in the embedding table and storing that in the videos
    table. The function and data collection is used once as a script.

    No error handling is in place at the moment. Safer to run function
    in batches to avoid timeout errors regardless of the timeout value.
    """
    # Initalize supabase connection to create db client
    # and fetch a list of unique video id's from the embedding table
    db_client = conn_supabase()
    uniqueIds: list[str] = get_unique_embedded_videoids(client=db_client)
    # Initialize client for using the youtube data API
    yt_client = conn_youtube()
    # Iterate over the video Id's, grab their basic info
    # and insert records into the video table
    # NOTE: No error handling at the moment to catch duplicates
    # but enforcing unique values in the database layer
    for id in uniqueIds: # NOTE: Run in batch to avoid timeout errors
        metadata: Video = get_basic_info(yt_client, id)        
        # Handle cases where no metadata is available 
        # by skipping the video and passing a msg to the terminal
        if metadata==None:
            print(f'{id}: No metadata available. Skipped')
            continue
        # Else create a record in the videos table
        insert_video_record(metadata)
        # Call time.sleep to avoid rate-limit errors
        time.sleep(timeout)
    return

# 2)
# Review the usage script, mainly the queries
# fetch relevant tutorials for the queries using their hyde solutions
# use the tutorials id (cross check with db to avoid duplicates)
# and store their embedding with metadata.



if __name__=="__main__":    
    # NOTE/TODO: Make sure to set the embeddings videoId
    # as foreign key, making it easier to reference between
    # youtube videos and their sequence's embeddings.
    # Maybe in the future we can expand embeddings with timestamps
    # and redirect users with timestamped urls.
    pass