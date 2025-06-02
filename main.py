# System
from typing import Annotated
# Local
from src.models import Reactflow
from src.services.llm import get_gemini
# Third party
from fastapi import FastAPI, Depends
from google.genai import Client

# Initialize fast APi
app = FastAPI()

# Placeholder endpoint for webservice root
@app.get('/')
async def root():
    return{"message": "Hello world"}

# Actual endpoint for processing a given user problem
@app.get('/solve/{problem}')#, response_model=Reactflow)
def solve(problem: str, client: Annotated[Client, Depends(get_gemini)]):
    """
    Given a problem faced by the user in their jiu-jitsu practice,
    return a jitsu-journal friendly directed graph/flowchart.
    Passed into the app for creating initial nodes and edges.
    """
    print(problem)
    print(str(client))

    # Generate a hypothetical solution using the user's problem
    # Retrive similar records to the generated solution from Supabase
    # Use similar records to ground generated answer (rerank if necessary)
    # Convert grounded answer into steps in a sequence
    # Load techniques into memory for passing as context in next stage
    # Map steps into a light weight list of nodes and edges
    # Parse lists into react-flow friendly shapes
    # Pack response into model declared above and send with code
    # NOTE: Handle any errors in the middle, passing msgs w/ appropriate error codes


    return{"problem": problem}