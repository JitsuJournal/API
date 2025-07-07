# Two processes to complete the embedding script:

# 1) 
# Take the existing video id's, collect more metadata required for 
# passing onto frontend when recommending tutorials

# 2)
# Review the usage script, mainly the queries
# fetch relevant tutorials for the queries using their hyde solutions
# use the tutorials id (cross check with db to avoid duplicates)
# and store their embedding with metadata.



if __name__=="__main__":
    from ..services.db import conn_supabase

    # Connect to existing embeddings table
    # fetch all uniuqe video ID's stored
    client = conn_supabase()
    response = (
        client.table("embeddings")
        .select("video_id")
        .execute()
    )
    # Length: 181
    uniqueVideoIds = list(dict.fromkeys(d['video_id'] for d in response.data))
    print(uniqueVideoIds)

    # Grab metadata using youtube data API
    # create records in videos table


    # NOTE: Need to match sample data and contain any other metadata/info to Video model
    # NOTE/TODO: Make sure to set the embeddings videoId
    # as foreign key, making it easier to reference between
    # youtube videos and their sequence's embeddings.
    # Maybe in the future we can expand embeddings with timestamps
    # and redirect users with timestamped urls.