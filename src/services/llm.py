# System
import os
from dotenv import load_dotenv
# Local
from ..models.general import Solution, Sequence, Graph
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
        model="gemini-2.5-flash-preview-05-20",
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

def ground(client:genai.Client, problem:str, paragraphs: list[str], solution: str):
    """
    Given a list of paragraphs as strings, a users problem in jiu-jitsu,
    and hypotehtical solution; ground said solution
    to actually use the techniques, positions, and paths from the paragraphs.
    Also refer to the paragraphs to remove contradictions and inconsistences
    from the generated solution.
    """
    grounded = client.models.generate_content(
        model="gemini-2.5-flash-preview-05-20",
        config=types.GenerateContentConfig(
            system_instruction="""
                You are a expert in brazilian gi and no-gi jiu-jitsu and 
                a professional coach capable of evaluating 
                jiu-jitsu sequences and assessing if they solve a 
                user problem.
            """,
            response_mime_type="application/json",
            response_schema=Solution,
            temperature=0.25
        ),
        contents=[problem, paragraphs, solution,
            """
            Given a problem faced by a jiu-jitsu practitioner, 
            a list of paragraphs as potential solutions retrieved
            from youtube tutorials, and a generated solution;
            ground said solution to actually use the techniques, 
            positions, and paths from the relevant paragraphs.
            
            Also refer to the paragraphs to remove any contradictions 
            or inconsistences from the generated solution. Ignore
            paragraphs that don't actually solve the user problem.
            """]
    )
    return grounded

def extract_sequences(client: genai.Client, paragraph: str, single: bool=False):
    """
    Given a paragraph (i.e. transcript), this function 
    returns a list of different Sequence objects 
    (sequence name, list of steps)
    """

    # If single, we use LLM to convert the paragraph into one sequence,
    # preserving the paths and returning one list of steps.
    if single:
        prompt = """
            Your task is to analyze the given jiu-jitsu sequence in a paragraph
            and break it down step by step. Maintain the original tone and phrasing.
            Keep sequence name under 40 characters.
            """
    else: # Else, we extract any sequence into seperate lists of steps
        prompt = """
            Your task is to analyze the given jiu-jitsu tutorial transcript
            and extract any jiu-jitsu sequence, breaking them down step by step.
            Maintain the original transcripts tone and phrasing.
            Keep sequence names under 40 characters.
            """

    # Analyze and extract sequences from the given paragraph
    # isolating key information to create flowcharts with
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction="You are a expert in brazilian gi/no-gi jiu-jitsu capable of breaking down sequences into flowchart like steps.", 
            response_mime_type="application/json",
            response_schema=Sequence if single else list[Sequence],
            temperature=0.25
        ),
        contents=[paragraph,prompt]
    )
    return response

def create_flowchart(client: genai.Client,
                     steps: list, techniques: str):
    """
    Given a list of steps, this function
    returns a Graph object containing a list of nodes
    and edges. This function requires techniques matching
    with the technique model, provided as a JSON str.
    """
    # Create a flowchart/directed graph using the sequences steps,
    # and using appropriate branching where applicable
    flowchart = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Graph,
            temperature=0.25
        ),
        contents=[techniques, steps,
            """
            Create a directed graph that captures the given jiu-jitsu sequence steps 
            using branching where appropriate.

            Requirements:
            - Use only the techniques from the given list, if not possible, give error
            - Each node should be assigned a unique node ID (e.g. 1, 2, etc.)
            - Each node must include:
                - `id`: the node ID
                - `techinque_id`: ID from the provided technique list            
            - Each edge should connect `source` to `target` using node IDs
            - Edge note is for optionally explaining how to go from one node to the next.
            - No duplicate edges: each `source`-`target` pair must appear only once
            - Every node must be connected by at least one edge (either as a source or a target); no disconnected nodes.
            """]
    )
    return flowchart



if __name__=="__main__":
    client = conn_gemini()
    problem = "Simple ways to pass an oppoennts open and closed guard when i'm in top position and go into better positions to then go finish strong with submissions"
    solution = create_paragraph(client, problem)
    print(solution.text)