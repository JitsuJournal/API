# System
import time
# Local
from ..models.general import Video
from ..services.db import conn_supabase, get_unique_embedded_videoids, insert_video_record
from .. services.youtube import conn_youtube, get_basic_info
# Third party

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

# 2) 
# Given a jiu jitsu sequence branch represented
# by a graph, perform a embedded similarity search
# and return with another video for video info from videos table
# NOTE: Complete the driver for this in the llm.py file

# 3)
# Review the usage script, mainly the queries
# fetch relevant tutorials for the queries using their hyde solutions
# use the tutorials id (cross check with db to avoid duplicates)
# and store their embeddings with metadata.

if __name__=="__main__":    
    # For actually fetching and passing the thumbnail 
    # along with the channel title, we need to 
    # expand the videos table with fields for these values
    # and then write a simple script for fetching data
    # using the existing youtube data api serivce function
    # and updating the video record
    


    # Create new rows for storing the channel title
    # as uploaded_by and the thumbnail url as thumbnail
    # NOTE: We can set the columns as not null later on

    
    # Fetch all the unique videos by video ID in the videos table

    # Iterate over each of the id's and fetch their basic info 
    # using the already created API

    # With the fetched basic info, extract required values
    # and update the table to contain the values


    # TODO/NOTE: Verify the new columns are updated with values
    
    # TODO/NOTE: Once all data is upadated, go ahead
    # and set the uploaded_by and thumbnail columns to NOT NULL    
    pass