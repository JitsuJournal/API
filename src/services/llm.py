# System
import os
from dotenv import load_dotenv
# Local
from ..models.general import Sequence, Graph
# Third Party
from google import genai
from google.genai import types, Client

load_dotenv()

# NOTE: Can be cached with lru_cache
# Gemini connection as a shared dependency
# Initilize geni AI client to use Gemini
def conn_gemini() -> Client:
    return genai.Client(api_key=os.getenv('GEMINI'))

def create_paragraph(client: genai.Client, problem: str):
    """
    Given a users jiu-jitsu problem, this function uses Gemini 2.5 
    and generates a hypothetical answer in a paragraph as solution.
    """
    solution = client.models.generate_content(
        model= "gemini-2.5-flash-lite-preview-06-17", #"gemini-2.0-flash-lite",
        config=types.GenerateContentConfig(
            temperature=0.25
        ),
        contents=[problem,
            """
            You are a expert in brazilian gi and no-gi jiu-jitsu and professional coach. 
            This is a problem faced by a jiu-jitsu practitioner. 
            Generate a jiu-jitsu sequence that solves their problem and gives them different techniques, positions, and paths.
            """]
    )
    return solution

def create_embedding(client: genai.Client, paragraph: str):
    """
    Given a paragraph, convert it to a embedding using 
    Gemini text embedding models.
    """
    embedding = client.models.embed_content(
        model='text-embedding-004',
        contents=[paragraph],
    )
    return embedding

def ground(client:genai.Client, problem:str, solution: str, similar: str):
    """
    Given a user's problem, a hyde, and similar documents.
    Ground the hyde to actually use the techniques, positions, 
    and paths from the paragraphs. Remove contradictions 
    and inconsistences or contradictions.
    """
    grounded = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        config=types.GenerateContentConfig(
            temperature=0.25
        ),
        contents=[problem, solution, similar,
            """
            You are an expert in Brazilian Jiu-Jitsu (gi and no-gi) and a professional coach.

            Given:
            - A problem described by a jiu-jitsu practitioner.
            - A hypothetical/proposed solution.
            - A set of relevant paragraphs retrieved from YouTube tutorials.

            Your task:
            - Ignore any paragraphs that do not directly address the problem.
            - Update the proposed solution to use relevant techniques, positions, and transitions from the retrieved paragraphs.
            - Remove contradictions and align the advice with realistic, proven paths from the referenced content.
            """]
    )
    return grounded

def extract_sequences(client: genai.Client, paragraph: str, single: bool=False):
    """
    Given a paragraph (i.e. transcript), this function 
    returns a list of different Sequence objects 
    (sequence name, list of steps)
    """
    # Analyze and extract sequences from the given paragraph
    # isolating key information to create flowcharts with
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Sequence if single else list[Sequence],
            temperature=0.25
        ),
        contents=[paragraph,
            """
            You are a expert in brazilian gi/no-gi jiu-jitsu and a professional coach.

            Break down the solution to a practitioners jiu-jitsu problem into detailed
            steps, containing information about techniques,
            positions, and any other relevant information.
            
            Keep sequence names under 30 characters.
            """]
    )
    return response

def create_flowchart(client: genai.Client, problem: str, sequences: str, techniques: str):
    """
    Given sequences and techniques as a JSON str,
    return a Graph object containing a list of nodes and edges.
    """
    # Create a flowchart/directed graph using the sequences steps,
    # and using appropriate branching where applicable
    flowchart = client.models.generate_content(
        model="gemini-2.0-flash-lite",#"gemini-2.5-flash-preview-05-20",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Graph,
            temperature=0.25
        ),
        contents=[techniques, sequences, problem,
            """
            Your task is to analyze the provided jiu-jitsu `sequences` 
            and merge them into a single, compact, directed graph.
            Prioritize the techniques and pathways relevant to the given user problem.
            The final graph must not exceed 10 nodes and should only contain 1 root node.
            Create branches where the paths diverge to include multiple options.
            
            Requirements:
            - Use only the techniques from the given list, if not possible, give error
            - 'Top' and 'bottom' denote attacker and defender roles respectively within each position.
            - Each node should be assigned a unique node ID (e.g. 1, 2, 3, etc.)
            - Each node must include:
                - `id`: the node ID
                - `techinque_id`: ID from the provided technique list   
            - Each edge should connect `source` to `target` using node IDs
            - Eliminate duplicate steps and pathways.
            """]
    )
    return flowchart

def rename_add_notes(client: genai.Client, problem: str, flowchart: str, 
        sequences:str, similar:str, techniques: str
    ):
    """
    Given the flowchart, list of techinques, sequence in text form, and paragraphs 
    of other similar sequences. Rename the flowchart and create detailed notes.
    """
    renamed = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction="""
            You're a black belt jiu-jitsu coach capable of
            analyzing a sequence and giving practitioners (users)
            advice/details on how to execute and transition between techniques,
            or any other supplementary information that may be valuable for increasing
            the success of the sequence they're trying to implement/execute. 
            """,
            response_mime_type="application/json",
            response_schema=Graph,
            temperature=0.75
        ),
        contents=[
            problem, flowchart, techniques, 
            sequences, similar,
            """
            Given the following flowchart which is a directed graph along with a
            list of techniques, the original, and the similar sequences paragraphs:
                - Analyze the sequence and rename the flowchart (max 30 characters).
                - The name should be based on the problem, flowchart and its underlying sequences solutions.
                - Recreate notes (max 400 characters each) that add detail to the edges and related nodes.
                - Notes should help practitioners understand how to execute the sequence.
                - Notes should contain text from the similar and original sequence in text.
            """
        ]
    )
    return renamed


def extract_paragraph(client: genai.Client, nodes: str, edges: str):
    """
    Given a sequence represented by nodes and edges, forming a
    directed graph, this function is responsible for creating
    the text representation of the sequence. The representation
    must be high in correctness, effectively capturing the branching
    and nodes, from the root to leaf nodes. 

    Response is generally used for performing similarity searches
    and identifying tutorials teaching how to execute the sequence.
    """
    extracted = client.models.generate_content(
        model='gemini-2.5-flash',
        config=types.GenerateContentConfig(
            system_instruction="You're a black belt/expert coach in brazilian jiu-jitsu, gi and no-gi.",
            response_mime_type="application/json",
            response_schema=list[str],
            temperature=0.25,
        ),
        contents=[
            nodes, edges, """
            Convert the given nodes and edges that represent a jiu-jitsu sequence
            from a direct graph into paragraphs for each branch, going from the root nodes
            to the leaf nodes while taking the notes into consideration.
            """
        ]
    )
    return extracted


# Driver functions for testing/developing above
def _main():
    import json
    from .db import conn_supabase, similarity_search, get_techniques
    # LLM functions are simply directly referenced from the above code

    client = conn_gemini()

    problem = "Simple ways to pass an oppoennts open and closed guard when i'm in top position and go into better positions to then go finish strong with submissions"
    solution = create_paragraph(client, problem)

    # Initialize supabase client
    supabase = conn_supabase()

    # Create embedding to perform similarity search
    embedding = create_embedding(client, paragraph=solution.text)
    vector: list[float] = embedding.embeddings[0].values

    # Retrive records similar to the generated solution from Supabase
    # NOTE: Using default match threshold and count for searching
    results = similarity_search(client=supabase, vector=vector)
    # Flatten into a json string to pass to LLM for grounding
    similar: str = json.dumps([{
            'name': sequence['name'],
            'paragraph': sequence['content']
        } for sequence in results.data]
    )

    # Ground the generated response using similar sequences
    # from actual youtube tutorials and coaches
    grounded = ground(client=client, problem=problem, 
                      similar=similar,
                      solution=solution.text)

    # extract each sequence in grounded paragraph into steps w/ names
    extracted: list[Sequence] = extract_sequences(client=client, paragraph=grounded.text).parsed

    # iterate over parsed sequences and dump into dict
    # for passing back into model as json string
    sequences: str = json.dumps([sequence.model_dump() for sequence in extracted])

    # import techniques as json string
    techniques: str = get_techniques(supabase)

    # pass sequences and techniques to model
    # and create a flowchart without inconsistencies
    # or duplicates, which would be the APIs response
    flowchart: Graph = create_flowchart(client, problem, sequences, techniques).parsed

    # Pass the flowchart back to the model
    # along with the techniques, similar sequences 
    # and extracted grounded sequences
    # to generate a name w/ updated/refined notes
    renamed: Graph = rename_add_notes(
        client=client, problem=problem,
        flowchart=flowchart.model_dump_json(),
        sequences=sequences, similar=similar,
        techniques=techniques,
    ).parsed
    

    print('-'*15)
    print(renamed.model_dump_json(indent=2))
    return


if __name__=="__main__":
    import json
    from ..models.reactflow import Node, Edge
    from ..models.general import Video
    from ..services.db import conn_supabase, similarity_search, get_video

    # Driver code for running the sequence building
    # from user jiu-jitsu problem pipeline
    #_main() # old driver code in func, commented out
    nodes: list[Node] = [
        {
            "id": "0625afa9-4998-43b5-9689-460786cefdff",
            "name": "Knee Slice",
            "tags": [
                "trip",
                "pass"
            ]
        },
        {
            "id": "10982656-8943-4ab4-bfe5-f7482c1adb55",
            "name": "Standard Back Control",
            "tags": [
                "top"
            ]
        },
        {
            "id": "918e7f75-2db2-47eb-bc8c-835936d92f0a",
            "name": "Triangle",
            "tags": [
                "artery"
            ]
        },
        {
            "id": "229f395b-3201-457c-a963-7e9a04dcab64",
            "name": "Double Under",
            "tags": [
                "top",
                "pass",
                "standing"
            ]
        },
        {
            "id": "5a3d6df5-60c3-40d7-9e78-28a8731958b2",
            "name": "Standard Side Control",
            "tags": [
                "seated",
                "top"
            ]
        },
        {
            "id": "63a7913c-f3da-431f-8701-e18984762e59",
            "name": "Arm Bar",
            "tags": [
                "elbow"
            ]
        },
        {
            "id": "65aa745b-41b5-442c-a99a-b9192f44350e",
            "name": "Rear Naked Choke",
            "tags": [
                "artery"
            ]
        },
        {
            "id": "90e8e114-64ef-47b4-9895-9db8eb14d857",
            "name": "Blast Double",
            "tags": [
                "wrestling"
            ]
        }
    ]
    edges: list[Edge] = [
        {
            "id": "xy-edge_90e8e114-64ef-47b4-9895-9db8eb14d857-b_0625afa9-4998-43b5-9689-460786cefdff-a",
            "source_id": "90e8e114-64ef-47b4-9895-9db8eb14d857",
            "target_id": "0625afa9-4998-43b5-9689-460786cefdff",
            "note": "From standing, use a blast double to drive forward. Execute a penetration step, driving the opponent's weight over their leg. Transition to a knee slice guard pass by driving your knee across the opponent's thigh, splitting their guard."
        },
        {
            "id": "xy-edge_0625afa9-4998-43b5-9689-460786cefdff-b_5a3d6df5-60c3-40d7-9e78-28a8731958b2-a",
            "source_id": "0625afa9-4998-43b5-9689-460786cefdff",
            "target_id": "5a3d6df5-60c3-40d7-9e78-28a8731958b2",
            "note": "Secure standard side control by pinning the opponent's shoulders and hips, maintaining chest-to-chest contact. Ensure a tight cross-side position by replacing your knee with your hand."
        },
        {
            "id": "xy-edge_5a3d6df5-60c3-40d7-9e78-28a8731958b2-b_63a7913c-f3da-431f-8701-e18984762e59-a",
            "source_id": "5a3d6df5-60c3-40d7-9e78-28a8731958b2",
            "target_id": "63a7913c-f3da-431f-8701-e18984762e59",
            "note": "From side control, control their arm across their body. Apply pressure for a straight arm bar by isolating their arm and controlling their head. Hyperextend the elbow."
        },
        {
            "id": "xy-edge_5a3d6df5-60c3-40d7-9e78-28a8731958b2-b_918e7f75-2db2-47eb-bc8c-835936d92f0a-a",
            "source_id": "5a3d6df5-60c3-40d7-9e78-28a8731958b2",
            "target_id": "918e7f75-2db2-47eb-bc8c-835936d92f0a",
            "note": "Alternatively, from side control, transition to the triangle choke by isolating an arm and controlling their head, using your legs to encircle the opponent's neck and one arm, constricting blood flow."
        },
        {
            "id": "xy-edge_90e8e114-64ef-47b4-9895-9db8eb14d857-b_229f395b-3201-457c-a963-7e9a04dcab64-a",
            "source_id": "90e8e114-64ef-47b4-9895-9db8eb14d857",
            "target_id": "229f395b-3201-457c-a963-7e9a04dcab64",
            "note": "From standing, if the knee cut is defended, transition to a double under pass. Side-step and level change, executing a penetration step. Pummel your hands inside while pushing the opponent's legs down."
        },
        {
            "id": "xy-edge_229f395b-3201-457c-a963-7e9a04dcab64-b_10982656-8943-4ab4-bfe5-f7482c1adb55-a",
            "source_id": "229f395b-3201-457c-a963-7e9a04dcab64",
            "target_id": "10982656-8943-4ab4-bfe5-f7482c1adb55",
            "note": "After the double under pass, transition to standard back control by securing both hooks and maintaining tight upper body control. Focus on clamping down and retracting the hip to finish."
        },
        {
            "id": "xy-edge_10982656-8943-4ab4-bfe5-f7482c1adb55-b_65aa745b-41b5-442c-a99a-b9192f44350e-a",
            "source_id": "10982656-8943-4ab4-bfe5-f7482c1adb55",
            "target_id": "65aa745b-41b5-442c-a99a-b9192f44350e",
            "note": "From back control, secure a rear naked choke (RNC) by wrapping one arm around their neck and using the other to tighten the grip, cutting off blood flow. Ensure you have a secure RNC grip before applying pressure."
        }
    ]

    str_nodes: str = json.dumps(nodes)
    str_edges:str = json.dumps(edges)

    # Initialize supabase and gemini clients
    llm_client = conn_gemini()
    db_client = conn_supabase()

    # Pass nodes/edges to extract paragraph 
    # and retrieve paragraphs representing going from
    # each root node to the leaf, taking notes into account
    extracted: list[str] = extract_paragraph(llm_client, str_nodes, str_edges).parsed

    tutorials: dict[str, Video] = {}
    for paragraph in extracted:
        # Create an embedded representation for each branch/paragraph
        embedding: list[float] = create_embedding(llm_client, paragraph=paragraph).embeddings[0].values

        # Perform a similarity search to retrive simlar sequences
        similar: list[dict] = similarity_search(client=db_client, vector=embedding, 
                                    match_threshold=0.75, match_count=3).data

        # Iterate over the similar sequences and 
        # use their tutorial id's to get metadata from video table
        for sequence in similar:
            videoId: str = sequence['video_id']
            # If it's data doesn't already exist in the tutorials dict
            if videoId not in tutorials: # checks keys
                # Use the unique video id to get the video metadata
                # from the videos table and pack into the video model/object
                videoInfo: dict = get_video(client=db_client, id=videoId).data[0]
                video = Video(
                    id=videoId, title=videoInfo['title'],
                    description=videoInfo['description'],
                    uploaded_at=videoInfo['uploaded_at'],
                )
                # set video id as key and model as value 
                # to add to the tutorials dict
                tutorials[videoId] = video

    # Flatten data into a list of Video objects
    # to match the response model defined in the tutorials endpoint
    flattened: list[Video] = list(tutorials.values())
    print(f'Retrieved {len(flattened)} videos as recommendations')