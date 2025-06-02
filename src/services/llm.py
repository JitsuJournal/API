# System
import os
from dotenv import load_dotenv
# Local
from ..models.general import Solution
# Third Party
from google import genai
from google.genai import types, Client

load_dotenv()

# NOTE: Can be cached with lru_cache
# Gemini connection as a shared dependency
# Initilize geni AI client to use Gemini
def get_gemini() -> Client:
    return genai.Client(api_key=os.getenv('GEMINI'))

def create_paragraph(client: genai.Client, problem: str):
    """
    Given a users jiu-jitsu problem, this function uses Gemini 2.5 
    and generates a hypothetical answer in a paragraph as solution.
    """
    solution = client.models.generate_content(
        model="gemini-2.5-flash-preview-05-20",
        config=types.GenerateContentConfig(
            system_instruction="You are a expert in brazilian gi and no-gi jiu-jitsu and professional coach capable of coming up with jiu-jitsu sequences containing multiple techniques, positions, and conditional branching.",
            response_mime_type="application/json",
            response_schema=Solution,
            temperature=0.25
        ),
        contents=[problem,
            """
            This is a problem faced by a jiu-jitsu practitioner.
            Create a paragraph describing the jiu-jitsu
            sequence that addresses their problem and gives them different techniques,
            positions, and paths to solve the problem.
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
