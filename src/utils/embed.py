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
    import time
    from ..models.general import Video
    from ..services.db import conn_supabase
    from .. services.youtube import conn_youtube, get_basic_info

    # Connect to existing embeddings table
    # fetch all uniuqe video ID's stored
    db_client = conn_supabase()
    idFetchResponse = (
        db_client.table("embeddings")
        .select("video_id")
        .execute()
    )

    # Length: 181
    uniqueVideoIds = list(dict.fromkeys(d['video_id'] for d in idFetchResponse.data))
    print("Fetched videoId's to mem:", len(uniqueVideoIds))

    # Initialize client for using the youtube data API
    yt_client = conn_youtube()

    for videoId in uniqueVideoIds[101:]:
        print('Fetching basic info for:', videoId)
        # Iterate over the video Id's and
        # grab metadata using youtube data API
        metadata: Video = get_basic_info(yt_client, videoId)
        print('\tFetched metadata')

        print('Creating records for', videoId)
        # create records in videos table
        # time.sleep to avoid any rate-limit errors
        createRecordResponse = (
            db_client.table('videos')
            .insert({
                'video_id': metadata.id,
                'title': metadata.title,
                'description': metadata.description,
                'uploaded_at': metadata.uploaded_at,
            })
            .execute()
        )

        print('\tcreated response:')
        print(createRecordResponse)
        print('--'*50)

        time.sleep(5)
        
    # NOTE/TODO: Make sure to set the embeddings videoId
    # as foreign key, making it easier to reference between
    # youtube videos and their sequence's embeddings.
    # Maybe in the future we can expand embeddings with timestamps
    # and redirect users with timestamped urls.