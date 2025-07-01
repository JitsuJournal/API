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
        model="gemini-2.0-flash-lite",#"gemini-2.5-flash-preview-05-20",
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

def create_flowchart(client: genai.Client, sequences: str, techniques: str):
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
        contents=[techniques, sequences,
            """
            Your task is to analyze the provided jiu-jitsu `sequences` 
            and merge them into a single, compact, directed graph.

            Requirements:
            - Use only the techniques from the given list, if not possible, give error
            - Each node should be assigned a unique node ID (e.g. 1, 2, etc.)
            - Each node must include:
                - `id`: the node ID
                - `techinque_id`: ID from the provided technique list            
            - Each edge should connect `source` to `target` using node IDs
            - Create branches where the paths diverge.
            - Eliminate duplicate steps and pathways to create a single, connected graph.
            - The final graph must not exceed 8 nodes. If the merged sequences create more than 8 nodes, prioritize the most common techniques and pathways, pruning the less frequent ones.
            """]
    )
    return flowchart

def rename_add_notes(client: genai.Client, flowchart: str, 
        sequences:str, similar:str, techniques: str
    ) :
    """
    Given the flowchart, list of techinques, sequence in text form, and paragraphs 
    of other similar sequences. Rename the flowchart and create detailed notes.
    """
    renamed = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Graph,
            temperature=0.75
        ),
        contents=[
            flowchart, techniques, 
            sequences, similar,
            """
            Given the following flowchart which is a directed graph along with a
            list of techniques, the original, and the similar sequences paragraphs:
                - Analyze the sequence and rename the flowchart (max 30 characters).
                - The name should be based on the sequences underlying solution.
                - Create notes (max 400 characters each) that add detail.
                - Notes should help practitioners understand how to execute the sequence.
                - Notes should contain text from the similar and original sequence in text.
            """
        ]
    )
    return renamed


if __name__=="__main__":
    import json
    from .db import conn_supabase, similarity_search, get_techniques

    client = conn_gemini()
    problem = "Simple ways to pass an oppoennts open and closed guard when i'm in top position and go into better positions to then go finish strong with submissions"
    solution = create_paragraph(client, problem) # NOTE: Need to switch to stronger model

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
    flowchart: Graph = create_flowchart(client, sequences, techniques).parsed

    # Pass the flowchart back to the model
    # along with the techniques, similar sequences 
    # and extracted grounded sequences
    # to generate a name w/ updated/refined notes
    renamed: Graph = rename_add_notes(
        client=client,
        flowchart=flowchart.model_dump_json(),
        sequences=sequences, similar=similar,
        techniques=techniques,
    ).parsed

    
    print('-'*15)
    print(renamed.model_dump_json(indent=2))