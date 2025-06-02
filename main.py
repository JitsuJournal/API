# System
from typing import Annotated
# Local
from src.models import Reactflow
from src.models.general import Solution
from src.services.llm import get_gemini, create_paragraph, create_embedding
from src.services.db import get_supabase
# Third party
from fastapi import FastAPI, Depends
from google.genai import Client as LlmClient
from supabase import Client as DbClient

# Initialize fast APi
app = FastAPI()

# Placeholder endpoint for webservice root
@app.get('/')
async def root():
    return{"message": "Hello world"}

# Actual endpoint for processing a given user problem
@app.get('/solve/{problem}')#, response_model=Reactflow)
def solve(
        problem: str, 
        gemini: Annotated[LlmClient, Depends(get_gemini)],
        supabase: Annotated[DbClient, Depends(get_supabase)],
    ):
    """
    Given a problem faced by the user in their jiu-jitsu practice,
    return a jitsu-journal friendly directed graph/flowchart.
    Passed into the app for creating initial nodes and edges.
    """

    # Create a hypothetical solution paragraph using the users problem
    hypothetical: Solution = create_paragraph(gemini, problem).parsed

    # Create embedding using the hypothetical solution
    # Used for searching tutorials with similar content
    embedding = create_embedding(gemini, paragraph=hypothetical.paragraph)
    vector: list[float] = embedding.embeddings[0].values

    print(vector)


    print(supabase)
    # Retrive similar records to the generated solution from Supabase


    # Use similar records to ground generated answer (rerank if necessary)
    # Convert grounded answer into steps in a sequence
    # Load techniques into memory for passing as context in next stage
    # Map steps into a light weight list of nodes and edges
    # Parse lists into react-flow friendly shapes
    # Pack response into model declared above and send with code
    # NOTE: Handle any errors in the middle, passing msgs w/ appropriate error codes


    return{"problem": problem, "response": str(hypothetical.paragraph)}